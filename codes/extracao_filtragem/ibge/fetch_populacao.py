"""
Baixa a população residente municipal (estimativas anuais IBGE) via API pública do
SIDRA — tabela 6579, variável 9324 — para os municípios com DEAM do painel.

A tabela 6579 não publica anos censitários (2010 ausente): o valor de 2010 é obtido
por INTERPOLAÇÃO LINEAR entre 2009 e 2011, mantendo a série de estimativas coerente
(evita o degrau metodológico de misturar a contagem do Censo com as estimativas).

Saída: dados/ibge/populacao_municipios.csv  (id_municipio, ano, populacao)
"""

import json
import time
import urllib.request
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
PATH_PAINEL = ROOT / "dados/consolidado/painel_deam_anual.csv"
OUT = ROOT / "dados/ibge/populacao_municipios.csv"

ANOS = list(range(2009, 2020))      # período do estudo
BATCH = 50                          # municípios por requisição (limita tamanho da URL)
TABELA, VARIAVEL = 6579, 9324


def fetch_lote(ids: list[int]) -> list[dict]:
    """Consulta o SIDRA para um lote de municípios, todos os anos disponíveis."""
    ids_str = ",".join(str(i) for i in ids)
    url = (f"https://apisidra.ibge.gov.br/values/t/{TABELA}"
           f"/n6/{ids_str}/v/{VARIAVEL}/p/all")
    with urllib.request.urlopen(url, timeout=120) as r:
        data = json.load(r)
    return data[1:]  # descarta a linha de cabeçalho


def main() -> None:
    ids = sorted(pd.read_csv(PATH_PAINEL)["id_municipio"].unique().tolist())
    print(f"Buscando população de {len(ids)} municípios no SIDRA (tabela {TABELA})...")

    registros: list[dict] = []
    for i in range(0, len(ids), BATCH):
        lote = ids[i:i + BATCH]
        linhas = fetch_lote(lote)
        for row in linhas:
            val = row["V"]
            if val in ("-", "...", "..", None):
                continue
            registros.append({
                "id_municipio": int(row["D1C"]),
                "ano": int(row["D3N"]),
                "populacao": int(val),
            })
        print(f"  lote {i // BATCH + 1}: {len(lote)} municípios")
        time.sleep(0.3)  # cortesia com a API

    pop = pd.DataFrame(registros)

    # Interpolação do ano censitário ausente (2010) por município
    grid = pd.DataFrame(
        [(m, a) for m in ids for a in range(2008, 2022)],
        columns=["id_municipio", "ano"],
    )
    pop = grid.merge(pop, on=["id_municipio", "ano"], how="left")
    pop = pop.sort_values(["id_municipio", "ano"])
    pop["populacao"] = (
        pop.groupby("id_municipio")["populacao"]
        .apply(lambda s: s.interpolate(method="linear", limit_direction="both"))
        .reset_index(level=0, drop=True)
    )
    pop["populacao"] = pop["populacao"].round().astype("Int64")

    pop = pop[pop["ano"].isin(ANOS)].reset_index(drop=True)

    falt = pop["populacao"].isna().sum()
    print(f"Linhas: {len(pop)} | faltantes após interpolação: {falt}")
    print(f"Cobertura: {pop['id_municipio'].nunique()} municípios x {pop['ano'].nunique()} anos")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    pop.to_csv(OUT, index=False, encoding="utf-8")
    print(f"Salvo: {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
