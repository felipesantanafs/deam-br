import basedosdados as bd
import pandas as pd
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'extracao_filtragem')))
try:
    from bd_config import BILLING_ID
except ImportError:
    BILLING_ID = None

billing_id = BILLING_ID

output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "dados", "ibge"))
os.makedirs(output_dir, exist_ok=True)
output_file = os.path.join(output_dir, "municipios_br.csv")

query = """
SELECT 
    id_municipio,
    nome,
    sigla_uf,
    id_uf,
    nome_regiao AS regiao
FROM `basedosdados.br_bd_diretorios_brasil.municipio`
"""

print("Baixando diretório de municípios do Brasil...")
try:
    if billing_id:
        df = bd.read_sql(query=query, billing_project_id=billing_id)
        df.to_csv(output_file, index=False, encoding="utf-8")
        print(f"Dados salvos com sucesso em {output_file}")
    else:
        print("Erro: BILLING_ID não encontrado. Configure bd_config.py.")
except Exception as e:
    print(f"Erro ao baixar municípios: {e}")
