"""
Script para limpeza e filtragem da base de dados das DEAMs.

Seleciona apenas as colunas: categoria, municipio, uf, 24horas e ano de implementação.
Exclui todas as observações que não sejam "Delegacia da Mulher".
Salva o resultado em dados_deams_filtrados.xlsx.
"""

import pandas as pd
from pathlib import Path

# Caminhos
CAMINHO_ENTRADA = Path(__file__).resolve().parents[2] / "dados" / "info_delegacias" / "dados_deams.xlsx"
CAMINHO_SAIDA = Path(__file__).resolve().parents[2] / "dados" / "info_delegacias" / "dados_deams_filtrados.xlsx"

def limpar_dados():
    # Leitura do arquivo original
    df = pd.read_excel(CAMINHO_ENTRADA)

    print(f"Base original: {df.shape[0]} observações, {df.shape[1]} colunas")
    print(f"Categorias encontradas: {df['categoria'].unique()}")

    # Identificar a coluna de ano de implementação (pode ter encoding diferente)
    col_ano = [c for c in df.columns if "implement" in c.lower() or "ano" in c.lower()]
    if not col_ano:
        raise ValueError("Coluna de ano de implementação não encontrada!")
    col_ano = col_ano[0]
    print(f"Coluna de ano identificada: '{col_ano}'")

    # Selecionar apenas as colunas desejadas
    colunas_selecionadas = ["categoria", "municipio", "uf", "24horas", col_ano]
    df_filtrado = df[colunas_selecionadas].copy()

    # Renomear a coluna de ano para um nome padronizado
    df_filtrado = df_filtrado.rename(columns={col_ano: "ano_implementacao"})

    # Filtrar apenas "Delegacia da Mulher"
    df_filtrado = df_filtrado[df_filtrado["categoria"] == "Delegacia da Mulher"].reset_index(drop=True)

    # Preencher NaN em ano_implementacao com informações da coluna 24horas
    mask_na = df_filtrado["ano_implementacao"].isna()
    df_filtrado.loc[mask_na, "ano_implementacao"] = df_filtrado.loc[mask_na, "24horas"]
    print(f"\nNaN preenchidos com coluna 24horas: {mask_na.sum()} observações")

    print(f"\nBase filtrada: {df_filtrado.shape[0]} observações, {df_filtrado.shape[1]} colunas")
    print(f"\nPrimeiras linhas:")
    print(df_filtrado.head(10))

    # Salvar arquivo filtrado
    df_filtrado.to_excel(CAMINHO_SAIDA, index=False)
    print(f"\nArquivo salvo em: {CAMINHO_SAIDA}")

if __name__ == "__main__":
    limpar_dados()
