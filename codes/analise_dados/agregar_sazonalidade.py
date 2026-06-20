"""
Pré-agrega os microdados nacionais do SINAN (violência contra a mulher) nas
dimensões TEMPORAIS necessárias para a análise de horário e sazonalidade do
estudo DEAM 24h, gerando CSVs leves para o app Streamlit.

Pergunta de pesquisa subjacente: DEAMs em regime de plantão 24h captam mais
notificações FORA do horário comercial (noite/madrugada/fim de semana)?
Para responder, cruzamos cada notificação com:
  - grupo do município (24h x comercial)
  - período relativo à adoção do plantão (Antes 24h / Depois 24h / Comercial)

Restringe-se a:
  - sexo feminino           (sexo_paciente == 0, ver memória sexo_coding_sim_sinan)
  - 2009-2019
  - municípios com DEAM (24h ou comercial), via painel consolidado

Saídas (dados/consolidado/):
  saz_hora.csv  -> contagem por (grupo, periodo, hora 0-23)
  saz_mes.csv   -> contagem por (grupo, periodo, mes 1-12)
  saz_dow.csv   -> contagem por (grupo, periodo, dia_semana 0=Seg..6=Dom)
  saz_resumo.csv-> agregados comercial x fora do horário comercial por grupo/periodo
"""

import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

PATH_SINAN  = ROOT / "dados/sinan/sinan_violencia_br_detalhada.csv"
PATH_PAINEL = ROOT / "dados/consolidado/painel_deam_anual.csv"
OUT_DIR     = ROOT / "dados/consolidado"

ANO_MIN, ANO_MAX = 2009, 2019
SEXO_FEM_SINAN = 0          # basedosdados: 0=F, 1=M
HORARIO_COMERCIAL = range(8, 18)   # 08:00-17:59 considerado "horário comercial"


def carregar_referencia() -> pd.DataFrame:
    """1 linha por município DEAM: grupo, coorte (ano de adoção), uf, regiao."""
    pa = pd.read_csv(PATH_PAINEL, usecols=["id_municipio", "grupo", "coorte", "uf", "regiao"])
    return pa.drop_duplicates("id_municipio").set_index("id_municipio")


def classificar_periodo(grupo: str, ano: int, coorte: int) -> str:
    """Janela relativa à adoção do plantão 24h."""
    if grupo != "24h":
        return "Comercial"
    return "Depois 24h" if (coorte > 0 and ano >= coorte) else "Antes 24h"


def main() -> None:
    ref = carregar_referencia()
    ids_deam = set(ref.index)
    print(f"Municípios DEAM: {len(ids_deam)}")

    cols = ["ano", "data_ocorrencia", "hora_ocorrencia",
            "id_municipio_ocorrencia", "sexo_paciente"]

    acc = []  # lista de DataFrames já enxutos por chunk
    total = 0
    for i, chunk in enumerate(pd.read_csv(PATH_SINAN, usecols=cols, chunksize=400_000)):
        chunk = chunk[
            (chunk["sexo_paciente"] == SEXO_FEM_SINAN)
            & (chunk["ano"].between(ANO_MIN, ANO_MAX))
            & (chunk["id_municipio_ocorrencia"].isin(ids_deam))
        ].copy()
        if chunk.empty:
            continue

        chunk["id_municipio"] = chunk["id_municipio_ocorrencia"].astype(int)
        chunk = chunk.join(ref, on="id_municipio")

        chunk["periodo"] = [
            classificar_periodo(g, a, c)
            for g, a, c in zip(chunk["grupo"], chunk["ano"], chunk["coorte"])
        ]

        # Hora do dia (0-23); descarta horas ausentes
        hora = pd.to_datetime(chunk["hora_ocorrencia"], format="%H:%M:%S", errors="coerce")
        chunk["hora"] = hora.dt.hour

        # Mês e dia da semana a partir da data
        data = pd.to_datetime(chunk["data_ocorrencia"], errors="coerce")
        chunk["mes"] = data.dt.month
        chunk["dow"] = data.dt.dayofweek  # 0=Seg .. 6=Dom

        acc.append(chunk[["grupo", "periodo", "hora", "mes", "dow"]])
        total += len(chunk)
        print(f"  chunk {i}: +{len(chunk)} (acumulado {total})")

    df = pd.concat(acc, ignore_index=True)
    print(f"Notificações femininas em municípios DEAM: {len(df)}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # ── Hora do dia ──────────────────────────────────────────────────
    saz_hora = (
        df.dropna(subset=["hora"])
        .groupby(["grupo", "periodo", "hora"]).size()
        .reset_index(name="n")
    )
    saz_hora["hora"] = saz_hora["hora"].astype(int)
    saz_hora.to_csv(OUT_DIR / "saz_hora.csv", index=False, encoding="utf-8")

    # ── Mês (sazonalidade anual) ─────────────────────────────────────
    saz_mes = (
        df.dropna(subset=["mes"])
        .groupby(["grupo", "periodo", "mes"]).size()
        .reset_index(name="n")
    )
    saz_mes["mes"] = saz_mes["mes"].astype(int)
    saz_mes.to_csv(OUT_DIR / "saz_mes.csv", index=False, encoding="utf-8")

    # ── Dia da semana ────────────────────────────────────────────────
    saz_dow = (
        df.dropna(subset=["dow"])
        .groupby(["grupo", "periodo", "dow"]).size()
        .reset_index(name="n")
    )
    saz_dow["dow"] = saz_dow["dow"].astype(int)
    saz_dow.to_csv(OUT_DIR / "saz_dow.csv", index=False, encoding="utf-8")

    # ── Resumo: dentro x fora do horário comercial ───────────────────
    h = df.dropna(subset=["hora"]).copy()
    h["faixa"] = h["hora"].astype(int).apply(
        lambda x: "Comercial (08-17h)" if x in HORARIO_COMERCIAL else "Fora do comercial"
    )
    resumo = (
        h.groupby(["grupo", "periodo", "faixa"]).size()
        .reset_index(name="n")
    )
    resumo.to_csv(OUT_DIR / "saz_resumo.csv", index=False, encoding="utf-8")

    print("\nArquivos gerados:")
    for f in ["saz_hora.csv", "saz_mes.csv", "saz_dow.csv", "saz_resumo.csv"]:
        print(f"  dados/consolidado/{f}")
    print(f"\nCobertura de hora preenchida: {df['hora'].notna().mean():.1%}")


if __name__ == "__main__":
    main()
