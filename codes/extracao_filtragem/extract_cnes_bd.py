import os
import sys
import pandas as pd

# pyrefly: ignore [missing-import]
import basedosdados as bd

sys.path.append(os.path.dirname(__file__))
# O arquivo 'bd_config.py' é uma configuração local contendo o ID de faturamento (Billing ID) do Google Cloud.
# Este arquivo é mantido localmente e está no .gitignore para evitar vazamento de credenciais.
from bd_config import BILLING_ID

output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "dados", "cnes"))
os.makedirs(output_dir, exist_ok=True)
output_file = os.path.join(output_dir, "cnes_sp_geolocalizado.csv")

# Query para buscar os estabelecimentos do CNES em SP e cruzar com o diretório de CEPs
# para obter o bairro, latitude e longitude. Usamos DISTINCT para pegar apenas 1 registro por CNES.
query = """
SELECT DISTINCT
    cnes.id_estabelecimento_cnes,
    cnes.cep,
    cep.logradouro,
    cep.localidade as bairro,
    ST_Y(cep.centroide) as latitude,
    ST_X(cep.centroide) as longitude
FROM `basedosdados.br_ms_cnes.estabelecimento` AS cnes
LEFT JOIN `basedosdados.br_bd_diretorios_brasil.cep` AS cep
    ON cnes.cep = cep.cep
WHERE cnes.id_municipio = '3550308'
"""

print("Baixando dicionário geolocalizado do CNES para São Paulo...")
try:
    df = bd.read_sql(query=query, billing_project_id=BILLING_ID)
    print(f"Download concluído! Total de unidades (CNES) únicas: {len(df)}")

    # É possível que alguns estabelecimentos tenham mudado de CEP ao longo do tempo,
    # gerando duplicatas. Vamos remover duplicatas pelo CNES mantendo o primeiro.
    df = df.drop_duplicates(subset=["id_estabelecimento_cnes"], keep="first")

    # --- PATCH MANUAL PARA HOSPITAIS COM CEP FALTANTE/INVÁLIDO ---
    # Os 5 hospitais abaixo representam quase 50% de todas as falhas de geolocalização no SINAN.
    patch_data = {
        "2080346": {"bairro": "Tatuapé", "lat": -23.5367, "lon": -46.5684},
        "5718368": {"bairro": "Jardim Copacabana", "lat": -23.6828, "lon": -46.7562},
        "2080583": {"bairro": "São Miguel Paulista", "lat": -23.4939, "lon": -46.4385},
        "2082837": {"bairro": "Vila Hamburguesa", "lat": -23.5350, "lon": -46.7265},
        "2078015": {"bairro": "Cerqueira César", "lat": -23.5576, "lon": -46.6669},
    }

    for cnes_id, info in patch_data.items():
        idx = df[df["id_estabelecimento_cnes"] == cnes_id].index
        if len(idx) > 0:
            df.loc[idx, "bairro"] = info["bairro"]
            df.loc[idx, "latitude"] = info["lat"]
            df.loc[idx, "longitude"] = info["lon"]
    # -------------------------------------------------------------

    df.to_csv(output_file, index=False, encoding="utf-8")
    print(f"Dados salvos em: {output_file}")
except Exception as e:
    print(f"Erro ao extrair CNES: {e}")
