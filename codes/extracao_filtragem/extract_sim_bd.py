import basedosdados as bd
import pandas as pd
import os
import sys

sys.path.append(os.path.dirname(__file__))
# O arquivo 'bd_config.py' é uma configuração local contendo o ID de faturamento (Billing ID) do Google Cloud.
# Este arquivo é mantido localmente e está no .gitignore para evitar vazamento de credenciais.
from bd_config import BILLING_ID

# Substitua pelo seu ID de projeto do Google Cloud
billing_id = BILLING_ID

# Definir caminho para salvar os dados dinamicamente (raiz do projeto -> dados)
output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "dados", "sim"))
os.makedirs(output_dir, exist_ok = True)
output_file = os.path.join(output_dir, "sim_feminicidios_sp.csv")

# A query foi otimizada para filtrar APENAS mulheres, vítimas de agressão, na cidade de São Paulo
query = """ 
WITH 
dicionario_tipo_obito AS (
    SELECT chave AS chave_tipo_obito, valor AS descricao_tipo_obito
    FROM `basedosdados.br_ms_sim.dicionario`
    WHERE nome_coluna = 'tipo_obito' AND id_tabela = 'microdados'
),
dicionario_sexo AS (
    SELECT chave AS chave_sexo, valor AS descricao_sexo
    FROM `basedosdados.br_ms_sim.dicionario`
    WHERE nome_coluna = 'sexo' AND id_tabela = 'microdados'
),
dicionario_raca_cor AS (
    SELECT chave AS chave_raca_cor, valor AS descricao_raca_cor
    FROM `basedosdados.br_ms_sim.dicionario`
    WHERE nome_coluna = 'raca_cor' AND id_tabela = 'microdados'
)
SELECT
    dados.ano as ano,
    dados.data_obito as data_obito,
    dados.hora_obito as hora_obito,
    dados.id_municipio_ocorrencia AS id_municipio_ocorrencia,
    dados.codigo_bairro_ocorrencia AS codigo_bairro_ocorrencia,
    dados.causa_basica AS causa_basica,
    diretorio_causa_basica.descricao_subcategoria AS causa_basica_descricao,
    descricao_sexo AS sexo,
    dados.idade as idade,
    descricao_raca_cor AS raca_cor,
    dados.id_municipio_residencia AS id_municipio_residencia
FROM `basedosdados.br_ms_sim.microdados` AS dados
LEFT JOIN `dicionario_tipo_obito` ON dados.tipo_obito = chave_tipo_obito
LEFT JOIN `dicionario_sexo` ON dados.sexo = chave_sexo
LEFT JOIN `dicionario_raca_cor` ON dados.raca_cor = chave_raca_cor
LEFT JOIN (
    SELECT DISTINCT subcategoria, descricao_subcategoria 
    FROM `basedosdados.br_bd_diretorios_brasil.cid_10`
) AS diretorio_causa_basica ON dados.causa_basica = diretorio_causa_basica.subcategoria
WHERE 
    -- Filtro 1: Apenas Município de São Paulo
    dados.id_municipio_ocorrencia = '3550308' 
    -- Filtro 2: Apenas Mulheres (Código 2 no SIM geralmente é Feminino)
    AND dados.sexo = '2'
    -- Filtro 3: CIDs de agressão (X85 a Y09) - Usamos LIKE para pegar os subgrupos
    AND (
        dados.causa_basica LIKE 'X8%' OR 
        dados.causa_basica LIKE 'X9%' OR 
        dados.causa_basica LIKE 'Y0%'
    )
"""

print("Iniciando o download dos dados via Base dos Dados (BigQuery)...")
try:
    df = bd.read_sql(query = query, billing_project_id = billing_id)
    print(f"Download concluído! Total de registros encontrados: {len(df)}")

    # Salvar em CSV na pasta dados
    df.to_csv(output_file, index = False, encoding = "utf-8")
    print(f"Dados salvos com sucesso em: {output_file}")
except Exception as e:
    print(f"Erro ao executar a query: {e}")
    print("Verifique se você configurou o 'billing_id' corretamente e se está autenticado no GCP.")
