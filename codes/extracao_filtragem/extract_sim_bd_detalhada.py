import basedosdados as bd
import pandas as pd
import os
import sys

sys.path.append(os.path.dirname(__file__))
from bd_config import BILLING_ID

billing_id = BILLING_ID

output_dir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "dados", "sim")
)
os.makedirs(output_dir, exist_ok=True)
output_file = os.path.join(output_dir, "sim_feminicidios_br_detalhada.csv")

query = """ 
SELECT
    dados.ano,
    dados.data_obito,
    dados.hora_obito,
    dados.id_municipio_ocorrencia,
    dados.causa_basica,
    cid.descricao_subcategoria AS causa_basica_descricao,
    dados.sexo,
    dados.idade,
    dados.raca_cor,
    dados.id_municipio_residencia
FROM `basedosdados.br_ms_sim.microdados` AS dados
LEFT JOIN `basedosdados.br_bd_diretorios_brasil.cid_10` AS cid
    ON dados.causa_basica = cid.subcategoria
WHERE 
    -- Apenas Mulheres (Código 2 no SIM geralmente é Feminino)
    dados.sexo = '2'
    -- CIDs de agressão (X85 a Y09) - Usamos LIKE para pegar os subgrupos
    AND (
        dados.causa_basica LIKE 'X8%' OR 
        dados.causa_basica LIKE 'X9%' OR 
        dados.causa_basica LIKE 'Y0%'
    )
    AND dados.id_municipio_ocorrencia IS NOT NULL
    AND dados.ano BETWEEN 2009 AND 2019
"""

print("Iniciando a extração detalhada do SIM via Base dos Dados (BigQuery)...")
try:
    df = bd.read_sql(query=query, billing_project_id=billing_id)
    print(f"Download concluído! Total de registros detalhados (SIM): {len(df)}")

    # Salvar em CSV na pasta dados
    df.to_csv(output_file, index=False, encoding="utf-8")
    print(f"Dados detalhados salvos com sucesso em: {output_file}")
except Exception as e:
    print(f"Erro ao executar a query: {e}")
    print(
        "Verifique se você configurou o 'billing_id' corretamente e se está autenticado no GCP."
    )
