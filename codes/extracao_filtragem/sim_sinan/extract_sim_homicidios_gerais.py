"""
extract_sim_homicidios_gerais.py
Extrai homicídios (agressões, CIDs X85-Y09) do SIM via BigQuery para uso como
covariável de violência basal no modelo CS DiD (Callaway & Sant'Anna 2021).

Produz DUAS taxas por município-ano:
  - homicidios_gerais : ambos os sexos (referência/descritivo)
  - homicidios_masc   : apenas masculino (sexo == '1' no SIM)  <- COVARIÁVEL DO MODELO

Por que masculino e não geral? O outcome de letalidade (taxa_feminicidios) é o
SUBCONJUNTO feminino dos mesmos CIDs X85-Y09. Condicionar em homicídios "gerais"
controlaria parcialmente pelo próprio outcome (containment mecânico), atenuando o
ATT artificialmente. Homicídios masculinos não têm essa sobreposição e são um
proxy mais limpo de violência estrutural ambiente (crime organizado, tráfico,
letalidade policial) — exatamente o que motiva a adoção reativa da DEAM 24h.

Sobre time-varying vs baseline: a coluna é anual (time-varying), mas o estimador CS
da lib `diff_diff` recupera a covariável no BASE PERIOD de cada comparação (g-1),
nunca no valor pós-tratamento. Logo a coluna anual já funciona como baseline
pré-tratamento cohort-specific, sem risco de bad control. Ver staggered.py:730.

Codificação de sexo no SIM: 1 = masculino, 2 = feminino (ver memória do projeto).

Saídas:
  dados/sim/sim_homicidios_gerais_br_detalhada.csv  — microdados brutos
  dados/consolidado/homicidios_gerais_anual.csv     — taxas /100k por município-ano
                                                       (restrito a municípios com DEAM)
"""

import sys
from pathlib import Path

import basedosdados as bd
import pandas as pd

# bd_config.py está em codes/extracao_filtragem/
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bd_config import BILLING_ID

ROOT = Path(__file__).resolve().parents[3]

PATH_24H = ROOT / "dados/info_delegacias/dados_deams_24h_com_id.xlsx"
PATH_COM = ROOT / "dados/info_delegacias/dados_deams_comercial_com_id.xlsx"
PATH_POP = ROOT / "dados/ibge/populacao_municipios.csv"

OUT_RAW = ROOT / "dados/sim/sim_homicidios_gerais_br_detalhada.csv"
OUT_AGG = ROOT / "dados/consolidado/homicidios_gerais_anual.csv"

ANO_MIN, ANO_MAX = 2009, 2019
SEXO_MASC = 1  # SIM: 1 = masculino

QUERY = f"""
SELECT
    dados.ano,
    dados.id_municipio_ocorrencia,
    dados.sexo,
    dados.causa_basica
FROM `basedosdados.br_ms_sim.microdados` AS dados
WHERE
    (
        dados.causa_basica LIKE 'X8%'
        OR dados.causa_basica LIKE 'X9%'
        OR dados.causa_basica LIKE 'Y0%'
    )
    AND dados.id_municipio_ocorrencia IS NOT NULL
    AND dados.ano BETWEEN {ANO_MIN} AND {ANO_MAX}
"""


def _ids_municipios_deam() -> set[int]:
    """Conjunto de id_municipio (7 dígitos) de cidades com DEAM (24h ou comercial)."""
    ids: set[int] = set()
    for path in (PATH_24H, PATH_COM):
        df = pd.read_excel(path).dropna(subset=["id_municipio"])
        ids.update(df["id_municipio"].astype(int).tolist())
    return ids


def main() -> None:
    OUT_RAW.parent.mkdir(parents=True, exist_ok=True)
    OUT_AGG.parent.mkdir(parents=True, exist_ok=True)

    # 1. Extração via BigQuery
    print("Extraindo homicídios (X85-Y09) do SIM via BigQuery...")
    df = bd.read_sql(query=QUERY, billing_project_id=BILLING_ID)
    df["id_municipio_ocorrencia"] = df["id_municipio_ocorrencia"].astype(int)
    df["sexo"] = pd.to_numeric(df["sexo"], errors="coerce")  # '1'/'2' -> 1/2
    print(f"  {len(df):,} registros extraídos ({ANO_MIN}-{ANO_MAX}).")

    df.to_csv(OUT_RAW, index=False, encoding="utf-8")
    print(f"  Microdados brutos salvos: {OUT_RAW.relative_to(ROOT)}")

    # 2. Matching com municípios DEAM
    ids_deam = _ids_municipios_deam()
    print(f"  Municípios com DEAM: {len(ids_deam)}")
    dd = df[df["id_municipio_ocorrencia"].isin(ids_deam)].copy()

    # 3. Agregação por município-ano: total (ambos sexos) e masculino
    def _contar(sub: pd.DataFrame, nome: str) -> pd.DataFrame:
        return (
            sub.groupby(["id_municipio_ocorrencia", "ano"])
            .size()
            .reset_index(name=nome)
            .rename(columns={"id_municipio_ocorrencia": "id_municipio"})
        )

    geral = _contar(dd, "homicidios_gerais")
    masc = _contar(dd[dd["sexo"] == SEXO_MASC], "homicidios_masc")

    # Painel balanceado: 0 para município-anos sem ocorrência
    grade = pd.DataFrame({"id_municipio": sorted(ids_deam)}).merge(
        pd.DataFrame({"ano": range(ANO_MIN, ANO_MAX + 1)}), how="cross"
    )
    agg = grade.merge(geral, on=["id_municipio", "ano"], how="left")
    agg = agg.merge(masc, on=["id_municipio", "ano"], how="left")
    agg[["homicidios_gerais", "homicidios_masc"]] = (
        agg[["homicidios_gerais", "homicidios_masc"]].fillna(0).astype(int)
    )

    # 4. Taxas por 100 mil habitantes
    pop = pd.read_csv(PATH_POP)
    agg = agg.merge(pop[["id_municipio", "ano", "populacao"]], on=["id_municipio", "ano"], how="left")
    agg["taxa_homicidios_gerais"] = (agg["homicidios_gerais"] / agg["populacao"] * 100_000).round(4)
    agg["taxa_homicidios_masc"] = (agg["homicidios_masc"] / agg["populacao"] * 100_000).round(4)

    out = agg[[
        "id_municipio", "ano",
        "homicidios_gerais", "taxa_homicidios_gerais",
        "homicidios_masc", "taxa_homicidios_masc",
    ]]
    out.to_csv(OUT_AGG, index=False, encoding="utf-8")

    print(f"  Covariável agregada salva: {OUT_AGG.relative_to(ROOT)}")
    print(f"  Municípios com DEAM no output: {out['id_municipio'].nunique()}")
    print(f"  Homicídios no período  -> geral: {int(out['homicidios_gerais'].sum()):,} | "
          f"masc: {int(out['homicidios_masc'].sum()):,}")
    print(f"  Taxa média /100k       -> geral: {out['taxa_homicidios_gerais'].mean():.2f} | "
          f"masc: {out['taxa_homicidios_masc'].mean():.2f}")


if __name__ == "__main__":
    main()
