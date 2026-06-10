import basedosdados as bd
import pandas as pd
import os
import sys

sys.path.append(os.path.dirname(__file__))
# O arquivo 'bd_config.py' é uma configuração local contendo o ID de faturamento (Billing ID) do Google Cloud.
# Este arquivo é mantido localmente e está no .gitignore para evitar vazamento de credenciais.
from bd_config import BILLING_ID

billing_id = BILLING_ID

# Definir caminho para salvar os dados dinamicamente (raiz do projeto -> dados)
output_dir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "dados", "sinan")
)
os.makedirs(output_dir, exist_ok=True)
output_file = os.path.join(output_dir, "sinan_violencia_br.csv")

# A query extrai e AGREGA dados de violência para todos os municípios do Brasil
query = """
SELECT
    dados.ano as ano,
    dados.id_municipio_ocorrencia AS id_municipio_ocorrencia,
    diretorio_id_municipio_ocorrencia.nome AS id_municipio_ocorrencia_nome,
    diretorio_id_municipio_ocorrencia.sigla_uf AS uf,
    COUNT(*) as total_notificacoes,
    SUM(CASE WHEN LOWER(CAST(dados.ocorreu_violencia_fisica AS STRING)) IN ('sim', '1', '1.0', 'true') THEN 1 ELSE 0 END) as total_lesoes,
    SUM(CASE WHEN LOWER(CAST(dados.meio_ameaca AS STRING)) IN ('sim', '1', '1.0', 'true') THEN 1 ELSE 0 END) as total_ameacas,
    SUM(CASE WHEN LOWER(CAST(dados.encaminhamento_delegacia_mulher AS STRING)) IN ('sim', '1', '1.0', 'true') THEN 1 ELSE 0 END) as total_encaminhamentos_ddm
FROM `basedosdados.br_ms_sinan.microdados_violencia` AS dados
LEFT JOIN `basedosdados.br_bd_diretorios_brasil.municipio` AS diretorio_id_municipio_ocorrencia
    ON dados.id_municipio_ocorrencia = diretorio_id_municipio_ocorrencia.id_municipio
WHERE 
    dados.id_municipio_ocorrencia IS NOT NULL
    AND dados.ano BETWEEN 2009 AND 2019
GROUP BY
    dados.ano,
    dados.id_municipio_ocorrencia,
    diretorio_id_municipio_ocorrencia.nome,
    diretorio_id_municipio_ocorrencia.sigla_uf
ORDER BY 
    dados.id_municipio_ocorrencia ASC,
    dados.ano ASC
"""

print("Iniciando a extração agregada do SINAN via Base dos Dados (BigQuery)...")
try:
    df = bd.read_sql(query=query, billing_project_id=billing_id)
    print(f"Download concluído! Total de registros agregados: {len(df)}")

    # Salvar em CSV na pasta dados
    df.to_csv(output_file, index=False, encoding="utf-8")
    print(f"Dados agregados salvos com sucesso em: {output_file}")
except Exception as e:
    print(f"Erro ao executar a query: {e}")
    print(
        "Verifique se você configurou o 'billing_id' corretamente e se está autenticado no GCP."
    )
