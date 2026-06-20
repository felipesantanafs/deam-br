"""
Agrega SIM (feminicídios) e SINAN (violência contra a mulher) de forma ANUAL
por município, restrito às cidades que possuem DEAM (24h ou comercial).

Produz um painel municipal balanceado (município × ano 2009-2019) pronto para:
  - Inferência causal (Callaway & Sant'Anna 2021 / staggered DiD)
  - Consumo pelo app Streamlit

Chave de cruzamento: id_municipio (7 dígitos IBGE), presente em:
  - dados_deams_24h_com_id.xlsx / dados_deams_comercial_com_id.xlsx (coluna id_municipio)
  - SIM:   id_municipio_ocorrencia   (sexo == 2  -> feminino, CID)
  - SINAN: id_municipio_ocorrencia   (sexo_paciente == 0 -> feminino)

Saídas (em dados/consolidado/):
  painel_deam_anual.csv          -> painel mestre (1 linha por município-ano)
  feminicidios_anual.csv         -> série anual de feminicídios (tidy)
  notificacoes_anual.csv         -> série anual de notificações + desagregações (tidy)
"""

import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

PATH_24H   = ROOT / "dados/info_delegacias/dados_deams_24h_com_id.xlsx"
PATH_COM   = ROOT / "dados/info_delegacias/dados_deams_comercial_com_id.xlsx"
PATH_IBGE  = ROOT / "dados/ibge/municipios_br.csv"
PATH_POP   = ROOT / "dados/ibge/populacao_municipios.csv"
PATH_SIM   = ROOT / "dados/sim/sim_feminicidios_br_detalhada.csv"
PATH_SINAN = ROOT / "dados/sinan/sinan_violencia_br_detalhada.csv"

OUT_DIR = ROOT / "dados/consolidado"

ANO_MIN, ANO_MAX = 2009, 2019

# Codificações de sexo feminino em cada base (ver docstring)
SEXO_FEM_SIM   = 2   # CID/IBGE: 1=M, 2=F
SEXO_FEM_SINAN = 0   # basedosdados: 0=F, 1=M (desambiguado via gestante_paciente)

# Autoria por parceiro íntimo (proxy de violência doméstica)
COLS_PARCEIRO = [
    "autor_conjugue", "autor_ex_conjugue",
    "autor_namorado_a", "autor_ex_namorado_a",
]


def construir_referencia_municipios() -> pd.DataFrame:
    """
    Tabela de referência: 1 linha por município com DEAM.
    Cidades em ambas as listas (comercial -> 24h) contam como TRATADAS (24h vence).
    Adiciona região do IBGE e a coorte de tratamento (ano de virada para 24h).
    """
    d24 = pd.read_excel(PATH_24H)
    dco = pd.read_excel(PATH_COM)
    ibge = pd.read_csv(PATH_IBGE)[["id_municipio", "regiao"]]

    d24 = d24.dropna(subset=["id_municipio"]).copy()
    d24["id_municipio"] = d24["id_municipio"].astype(int)
    d24["grupo"] = "24h"
    d24 = d24[["id_municipio", "municipio", "uf", "grupo", "ano_implementacao"]]
    # Se a cidade aparece 2x na lista 24h, mantém a implementação mais antiga
    d24 = d24.sort_values("ano_implementacao").drop_duplicates("id_municipio", keep="first")

    dco = dco.dropna(subset=["id_municipio"]).copy()
    dco["id_municipio"] = dco["id_municipio"].astype(int)
    dco["grupo"] = "comercial"
    dco["ano_implementacao"] = pd.NA
    dco = dco[["id_municipio", "municipio", "uf", "grupo", "ano_implementacao"]]
    dco = dco.drop_duplicates("id_municipio", keep="first")

    # 24h tem precedência sobre comercial nas cidades em ambas as listas
    ids_24h = set(d24["id_municipio"])
    dco = dco[~dco["id_municipio"].isin(ids_24h)]

    ref = pd.concat([d24, dco], ignore_index=True)
    ref = ref.merge(ibge, on="id_municipio", how="left")

    # Variável de coorte para CS DiD: ano de adoção (0 = nunca tratado / controle)
    ref["coorte"] = ref["ano_implementacao"].fillna(0).astype(int)
    return ref


def agregar_sim(ids_deam: set[int]) -> pd.DataFrame:
    """Conta feminicídios (óbitos femininos) por município-ano nas cidades DEAM."""
    df = pd.read_csv(
        PATH_SIM,
        usecols=["ano", "id_municipio_ocorrencia", "sexo"],
    )
    df = df[
        (df["sexo"] == SEXO_FEM_SIM)
        & (df["ano"].between(ANO_MIN, ANO_MAX))
        & (df["id_municipio_ocorrencia"].isin(ids_deam))
    ]
    out = (
        df.groupby(["id_municipio_ocorrencia", "ano"])
        .size()
        .reset_index(name="feminicidios")
        .rename(columns={"id_municipio_ocorrencia": "id_municipio"})
    )
    return out


def agregar_sinan(ids_deam: set[int]) -> pd.DataFrame:
    """
    Conta notificações de violência contra a mulher (sexo feminino) por município-ano,
    com desagregações por tipo de violência e autoria de parceiro íntimo.
    Lê em chunks por causa do tamanho do arquivo (~320 MB).
    """
    cols = [
        "ano", "id_municipio_ocorrencia", "sexo_paciente",
        "ocorreu_violencia_fisica", "ocorreu_violencia_sexual",
        "ocorreu_violencia_psicologica",
    ] + COLS_PARCEIRO

    parciais: list[pd.DataFrame] = []
    for chunk in pd.read_csv(PATH_SINAN, usecols=cols, chunksize=300_000):
        chunk = chunk[
            (chunk["sexo_paciente"] == SEXO_FEM_SINAN)
            & (chunk["ano"].between(ANO_MIN, ANO_MAX))
            & (chunk["id_municipio_ocorrencia"].isin(ids_deam))
        ]
        if chunk.empty:
            continue
        # Notificação por parceiro íntimo: qualquer autoria de (ex-)cônjuge/namorado(a)
        chunk = chunk.copy()
        chunk["viol_parceiro"] = (chunk[COLS_PARCEIRO].fillna(0) == 1).any(axis=1).astype(int)
        grp = chunk.groupby(["id_municipio_ocorrencia", "ano"]).agg(
            notificacoes=("sexo_paciente", "size"),
            viol_fisica=("ocorreu_violencia_fisica", lambda s: (s == 1).sum()),
            viol_sexual=("ocorreu_violencia_sexual", lambda s: (s == 1).sum()),
            viol_psicologica=("ocorreu_violencia_psicologica", lambda s: (s == 1).sum()),
            viol_parceiro=("viol_parceiro", "sum"),
        )
        parciais.append(grp)

    if not parciais:
        return pd.DataFrame(
            columns=["id_municipio", "ano", "notificacoes", "viol_fisica",
                     "viol_sexual", "viol_psicologica", "viol_parceiro"]
        )

    # Soma as agregações parciais dos chunks (mesmo município-ano pode estar em vários)
    out = (
        pd.concat(parciais)
        .groupby(level=[0, 1])
        .sum()
        .reset_index()
        .rename(columns={"id_municipio_ocorrencia": "id_municipio"})
    )
    return out


def montar_painel(ref: pd.DataFrame, sim: pd.DataFrame, sinan: pd.DataFrame) -> pd.DataFrame:
    """
    Painel balanceado: produto cartesiano (município DEAM × ano) com os agregados
    preenchidos a zero onde não houve eventos, mais as variáveis de tratamento DiD.
    """
    anos = pd.DataFrame({"ano": range(ANO_MIN, ANO_MAX + 1)})
    painel = ref.merge(anos, how="cross")

    painel = painel.merge(sim, on=["id_municipio", "ano"], how="left")
    painel = painel.merge(sinan, on=["id_municipio", "ano"], how="left")

    metricas = ["feminicidios", "notificacoes", "viol_fisica",
                "viol_sexual", "viol_psicologica", "viol_parceiro"]
    painel[metricas] = painel[metricas].fillna(0).astype(int)

    # População municipal anual (estimativas IBGE/SIDRA) e taxas por 100 mil habitantes
    pop = pd.read_csv(PATH_POP)
    painel = painel.merge(pop, on=["id_municipio", "ano"], how="left")
    for m in metricas:
        painel[f"taxa_{m}"] = (painel[m] / painel["populacao"] * 100_000).round(4)

    # Variáveis de tratamento (staggered adoption)
    painel["tratado"] = (painel["grupo"] == "24h").astype(int)
    painel["pos_tratamento"] = (
        (painel["coorte"] > 0) & (painel["ano"] >= painel["coorte"])
    ).astype(int)
    painel["tratamento_ativo"] = painel["tratado"] * painel["pos_tratamento"]

    cols = [
        "id_municipio", "municipio", "uf", "regiao", "grupo",
        "ano_implementacao", "coorte", "ano", "populacao",
        "tratado", "pos_tratamento", "tratamento_ativo",
        "feminicidios", "notificacoes",
        "viol_fisica", "viol_sexual", "viol_psicologica", "viol_parceiro",
        "taxa_feminicidios", "taxa_notificacoes",
        "taxa_viol_fisica", "taxa_viol_sexual",
        "taxa_viol_psicologica", "taxa_viol_parceiro",
    ]
    return painel[cols].sort_values(["id_municipio", "ano"]).reset_index(drop=True)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    ref = construir_referencia_municipios()
    ids_deam = set(ref["id_municipio"])
    print(f"Municípios DEAM com id: {len(ids_deam)} "
          f"({(ref['grupo'] == '24h').sum()} tratados 24h, "
          f"{(ref['grupo'] == 'comercial').sum()} controle comercial)")

    sim = agregar_sim(ids_deam)
    print(f"SIM   -> {sim['feminicidios'].sum()} feminicídios em "
          f"{sim['id_municipio'].nunique()} municípios")

    sinan = agregar_sinan(ids_deam)
    print(f"SINAN -> {int(sinan['notificacoes'].sum())} notificações (mulheres) em "
          f"{sinan['id_municipio'].nunique()} municípios")

    painel = montar_painel(ref, sim, sinan)

    # Saída mestre
    p_painel = OUT_DIR / "painel_deam_anual.csv"
    painel.to_csv(p_painel, index=False, encoding="utf-8")

    # Saídas tidy para o Streamlit
    cols_id = ["id_municipio", "municipio", "uf", "regiao", "grupo", "coorte", "ano", "populacao"]
    p_fem = OUT_DIR / "feminicidios_anual.csv"
    painel[cols_id + ["feminicidios", "taxa_feminicidios"]].to_csv(
        p_fem, index=False, encoding="utf-8")

    p_not = OUT_DIR / "notificacoes_anual.csv"
    painel[cols_id + ["notificacoes", "viol_fisica", "viol_sexual",
                       "viol_psicologica", "viol_parceiro",
                       "taxa_notificacoes", "taxa_viol_fisica", "taxa_viol_sexual",
                       "taxa_viol_psicologica", "taxa_viol_parceiro"]].to_csv(
        p_not, index=False, encoding="utf-8")

    print(f"\nPainel: {painel.shape[0]} linhas x {painel.shape[1]} colunas")
    print(f"  {p_painel.relative_to(ROOT)}")
    print(f"  {p_fem.relative_to(ROOT)}")
    print(f"  {p_not.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
