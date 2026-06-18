"""
Script para separar as DEAMs filtradas em dois arquivos:
  - Comerciais: delegacias com horário comercial
  - 24 horas: delegacias com ano de implementação numérico (funcionam 24h)

Para entradas com "/desativada" ou "/desativado", ignora-se essa parte
e considera-se apenas se é "Comercial" ou o ano.
"""

import pandas as pd
from pathlib import Path

# Caminhos
DIR_DADOS = Path(__file__).resolve().parents[2] / "dados" / "info_delegacias"
CAMINHO_ENTRADA = DIR_DADOS / "dados_deams_filtrados.xlsx"
CAMINHO_COMERCIAL = DIR_DADOS / "dados_deams_comercial.xlsx"
CAMINHO_24H = DIR_DADOS / "dados_deams_24h.xlsx"

def separar_dados():
    df = pd.read_excel(CAMINHO_ENTRADA)
    print(f"Base filtrada: {df.shape[0]} observações")

    # Remover observações sem informação de ano/implementação
    df = df.dropna(subset=["ano_implementacao"])
    print(f"Após remover NaN em ano_implementacao: {df.shape[0]} observações")

    # Limpar a coluna: remover "/desativada", "/desativado"
    df["ano_implementacao"] = (
        df["ano_implementacao"]
        .astype(str)
        .str.replace(r"/desativad[ao]", "", regex=True)
        .str.strip()
    )

    # Separar: comerciais vs 24 horas
    # Comercial: "Comercial" ou "Não" (não funciona 24h)
    # 24 horas: valores numéricos (ano) ou "Sim" (funciona 24h)
    valores_comercial = df["ano_implementacao"].str.lower().isin(["comercial", "não", "nao"])
    mask_comercial = valores_comercial

    # Criar DataFrame Comercial (sem a coluna ano_implementacao)
    df_comercial = df[mask_comercial][["municipio", "uf"]].reset_index(drop=True)

    # Criar DataFrame 24 Horas
    df_24h_all = df[~mask_comercial].copy()
    
    # Converter ano_implementacao para numérico para podermos filtrar por intervalo de anos
    df_24h_all["ano_num"] = pd.to_numeric(df_24h_all["ano_implementacao"], errors="coerce")
    
    # Filtrar apenas delegacias com ano de implementação entre 2009 e 2019
    df_24h = df_24h_all[(df_24h_all["ano_num"] >= 2009) & (df_24h_all["ano_num"] <= 2019)].copy()
    
    # Manter apenas as colunas desejadas e remover a coluna auxiliar de ano numérico
    df_24h = df_24h[["municipio", "uf", "ano_implementacao"]].reset_index(drop=True)

    # Remover cidades que aparecem mais de uma vez (municipio e uf)
    # keep=False marca todas as ocorrências de duplicadas para exclusão
    duplicados = df_24h.duplicated(subset=["municipio", "uf"], keep=False)
    print(f"\nRemovendo cidades duplicadas: {df_24h[duplicados]['municipio'].unique()}")
    df_24h = df_24h[~duplicados].reset_index(drop=True)

    # Exibir resultados
    print(f"\n--- Comerciais: {df_comercial.shape[0]} observações ---")
    print(df_comercial.head(10).to_string())

    print(f"\n--- 24 Horas (2009-2019): {df_24h.shape[0]} observações ---")
    print(df_24h.to_string())

    # Salvar arquivos
    df_comercial.to_excel(CAMINHO_COMERCIAL, index=False)
    print(f"\nArquivo comercial salvo em: {CAMINHO_COMERCIAL}")

    df_24h.to_excel(CAMINHO_24H, index=False)
    print(f"Arquivo 24h salvo em: {CAMINHO_24H}")

if __name__ == "__main__":
    separar_dados()
