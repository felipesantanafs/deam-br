"""
Pareia os nomes de municípios das planilhas de DEAMs com id_municipio do IBGE.

Estratégia:
  1. Aplica CORRECOES — typos, UFs erradas e nomes abreviados identificados na análise inicial
  2. Join exato por (municipio normalizado, uf) = (nome normalizado, sigla_uf)
  3. Para não-casados remanescentes: sugestões via difflib dentro do mesmo estado
  4. Salva arquivos enriquecidos com coluna id_municipio

Saídas:
  dados/info_delegacias/dados_deams_24h_com_id.xlsx
  dados/info_delegacias/dados_deams_comercial_com_id.xlsx
"""

import unicodedata
import difflib
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

PATH_24H  = ROOT / "dados/info_delegacias/dados_deams_24h.xlsx"
PATH_COM  = ROOT / "dados/info_delegacias/dados_deams_comercial.xlsx"
PATH_IBGE = ROOT / "dados/ibge/municipios_br.csv"

PATH_24H_OUT = ROOT / "dados/info_delegacias/dados_deams_24h_com_id.xlsx"
PATH_COM_OUT = ROOT / "dados/info_delegacias/dados_deams_comercial_com_id.xlsx"

# Correções manuais: (municipio_original, uf_original) -> (municipio_correto, uf_correta)
# Motivação: typos de digitação, UF errada, nome abreviado, renomeação IBGE
CORRECOES: dict[tuple[str, str], tuple[str, str]] = {
    # DEAMs 24h — UF errada
    ("Taguatinga",    "DF"): ("Brasília",              "DF"),  # RA do DF, IBGE só tem Brasília
    ("Santo Amaro",   "PE"): ("Santo Amaro",           "BA"),  # município existe em BA, não PE
    ("Ariquemes",     "TO"): ("Ariquemes",             "RO"),  # município é em RO, não TO
    # DEAMs Comercial — typos de nome
    ("Valparaíso",            "GO"): ("Valparaíso de Goiás",   "GO"),
    ("Guabira",               "PB"): ("Guarabira",             "PB"),
    ("Vitória de Santo Abraão","PE"): ("Vitória de Santo Antão","PE"),
    ("Foz do Iguaçi",         "PR"): ("Foz do Iguaçu",         "PR"),
    ("Pato Brancp",           "PR"): ("Pato Branco",           "PR"),
    ("Guarajá Mirim",         "RO"): ("Guajará-Mirim",         "RO"),
    ("Jaraguá do Su",         "SC"): ("Jaraguá do Sul",        "SC"),
    ("Embu",                  "SP"): ("Embu das Artes",        "SP"),  # renomeado em 2011
    ("Colinas",               "TO"): ("Colinas do Tocantins",  "TO"),
    # "Parque Piauí" (PI): não é município IBGE — mantido sem id_municipio
}


def normalizar(texto: str) -> str:
    """Lowercase + remove diacríticos para comparação case/accent-insensitive."""
    nfd = unicodedata.normalize("NFD", str(texto))
    return "".join(c for c in nfd if unicodedata.category(c) != "Mn").lower().strip()


def parear_com_ibge(
    df: pd.DataFrame,
    ibge: pd.DataFrame,
    label: str,
) -> pd.DataFrame:
    """
    Adiciona coluna id_municipio ao df pela chave (municipio, uf).
    Imprime relatório de não-casados com sugestões dentro do mesmo estado.
    """
    # Lookup: (nome_normalizado, sigla_uf) -> id_municipio
    ibge_lookup: dict[tuple[str, str], int] = {
        (normalizar(row["nome"]), row["sigla_uf"]): int(row["id_municipio"])
        for _, row in ibge.iterrows()
    }

    # Nomes originais por UF para sugestões
    nomes_por_uf: dict[str, list[str]] = (
        ibge.groupby("sigla_uf")["nome"].apply(list).to_dict()
    )

    ids: list[int | None] = []
    nao_casados: list[tuple[str, str]] = []
    corrigidos: list[tuple[str, str, str, str]] = []  # (orig_mun, orig_uf, new_mun, new_uf)

    for _, row in df.iterrows():
        mun, uf = row["municipio"], row["uf"]
        if (mun, uf) in CORRECOES:
            mun_c, uf_c = CORRECOES[(mun, uf)]
            corrigidos.append((mun, uf, mun_c, uf_c))
            mun, uf = mun_c, uf_c
        chave = (normalizar(mun), uf)
        if chave in ibge_lookup:
            ids.append(ibge_lookup[chave])
        else:
            ids.append(None)
            # Evita duplicar a mesma entrada no relatório
            entrada = (row["municipio"], row["uf"])
            if entrada not in nao_casados:
                nao_casados.append(entrada)

    df = df.copy()
    df.insert(0, "id_municipio", ids)

    total     = len(df)
    casados   = df["id_municipio"].notna().sum()

    print(f"\n{'='*50}")
    print(f"  {label}")
    print(f"{'='*50}")
    print(f"  Linhas totais   : {total}")
    print(f"  Com id_municipio: {casados}")
    print(f"  Sem id_municipio: {total - casados}")

    if corrigidos:
        vistos: set[tuple[str, str]] = set()
        print(f"\n  Correcoes aplicadas:")
        for orig_m, orig_u, new_m, new_u in corrigidos:
            if (orig_m, orig_u) not in vistos:
                print(f"    '{orig_m}' ({orig_u})  ->  '{new_m}' ({new_u})")
                vistos.add((orig_m, orig_u))

    if nao_casados:
        print(f"\n  Municipios nao casados (sugestoes IBGE no mesmo estado):")
        for mun, uf in nao_casados:
            candidatos = nomes_por_uf.get(uf, [])
            matches = difflib.get_close_matches(
                mun, candidatos, n=3, cutoff=0.55
            )
            sugestoes = " | ".join(matches) if matches else "(sem sugestao)"
            print(f"    '{mun}' ({uf})  ->  {sugestoes}")
    else:
        print("  Todos os municipios casaram com o IBGE.")

    return df


def main() -> None:
    ibge = pd.read_csv(PATH_IBGE)

    df24  = pd.read_excel(PATH_24H)
    df24_out = parear_com_ibge(df24, ibge, "DEAMs 24h")
    df24_out.to_excel(PATH_24H_OUT, index=False)
    print(f"\n  Salvo: {PATH_24H_OUT.relative_to(ROOT)}")

    dfc   = pd.read_excel(PATH_COM)
    dfc_out = parear_com_ibge(dfc, ibge, "DEAMs Comercial")
    dfc_out.to_excel(PATH_COM_OUT, index=False)
    print(f"\n  Salvo: {PATH_COM_OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
