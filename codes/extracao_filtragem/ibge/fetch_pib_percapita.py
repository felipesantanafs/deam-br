"""
Baixa o PIB municipal a preços correntes (IBGE, tabela SIDRA 5938, variável 37,
em Mil Reais) para os municípios com DEAM do painel e deriva o PIB PER CAPITA.

Per capita = (PIB em mil reais * 1000) / população, usando a MESMA população de
populacao_municipios.csv — mantém o denominador consistente com as demais taxas do
painel (taxa_feminicidios, taxa_homicidios_masc, etc.).

A covariável usada no modelo causal é o LOG do PIB per capita: o PIB per capita é
fortemente assimétrico entre municípios, e em log fica ~simétrico, evitando que
poucos municípios muito ricos dominem o escore de propensão (mesma lógica do
log_populacao). A coluna `pib_per_capita` (nível, R$) é mantida para referência.

Saída: dados/ibge/pib_percapita_municipios.csv
       (id_municipio, ano, pib_per_capita, log_pib_per_capita)
"""

import json
import time
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
PATH_PAINEL = ROOT / "dados/consolidado/painel_deam_anual.csv"
PATH_POP = ROOT / "dados/ibge/populacao_municipios.csv"
OUT = ROOT / "dados/ibge/pib_percapita_municipios.csv"

ANOS = list(range(2009, 2020))      # período do estudo
BATCH = 50                          # municípios por requisição (limita tamanho da URL)
TABELA, VARIAVEL = 5938, 37         # 5938 = PIB municipal; var 37 = PIB (Mil Reais)


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
    print(f"Buscando PIB de {len(ids)} municípios no SIDRA (tabela {TABELA}, var {VARIAVEL})...")

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
                "pib_mil_reais": float(val),
            })
        print(f"  lote {i // BATCH + 1}: {len(lote)} municípios")
        time.sleep(0.3)  # cortesia com a API

    pib = pd.DataFrame(registros)
    pib = pib[pib["ano"].isin(ANOS)]

    # PIB per capita (R$) usando a mesma população do painel
    pop = pd.read_csv(PATH_POP)[["id_municipio", "ano", "populacao"]]
    pib = pib.merge(pop, on=["id_municipio", "ano"], how="left")
    pib["pib_per_capita"] = (pib["pib_mil_reais"] * 1000 / pib["populacao"]).round(2)
    pib["log_pib_per_capita"] = np.log(pib["pib_per_capita"]).round(4)

    out = pib[["id_municipio", "ano", "pib_per_capita", "log_pib_per_capita"]].sort_values(
        ["id_municipio", "ano"]
    ).reset_index(drop=True)

    falt = out["log_pib_per_capita"].isna().sum()
    print(f"Linhas: {len(out)} | per capita faltante: {falt}")
    print(f"Cobertura: {out['id_municipio'].nunique()} municípios x {out['ano'].nunique()} anos")
    print(f"PIB per capita (R$)  min/mediana/max: "
          f"{out['pib_per_capita'].min():.0f} / {out['pib_per_capita'].median():.0f} / {out['pib_per_capita'].max():.0f}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT, index=False, encoding="utf-8")
    print(f"Salvo: {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
