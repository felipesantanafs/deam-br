import basedosdados as bd
import os
import sys

sys.path.append(os.path.dirname(__file__))
from bd_config import BILLING_ID

def get_deams():
    # First, let's see what columns exist in MUNIC seguranca_publica
    query_schema = """
    SELECT column_name
    FROM `basedosdados.br_ibge_munic.INFORMATION_SCHEMA.COLUMNS`
    WHERE table_name = 'seguranca_publica'
    """
    df_cols = bd.read_sql(query_schema, billing_project_id=BILLING_ID)
    
    # Check if there is anything related to delegacia da mulher
    cols = df_cols['column_name'].tolist()
    deam_cols = [c for c in cols if 'mulher' in c.lower() or 'delegacia' in c.lower() or 'deam' in c.lower()]
    print("Colunas relacionadas a mulher/delegacia no MUNIC Segurança Pública:", deam_cols)

    query_direitos = """
    SELECT column_name
    FROM `basedosdados.br_ibge_munic.INFORMATION_SCHEMA.COLUMNS`
    WHERE table_name = 'direitos_humanos'
    """
    try:
        df_dir = bd.read_sql(query_direitos, billing_project_id=BILLING_ID)
        cols_dir = df_dir['column_name'].tolist()
        deam_cols_dir = [c for c in cols_dir if 'mulher' in c.lower() or 'delegacia' in c.lower() or 'deam' in c.lower()]
        print("Colunas relacionadas a mulher/delegacia no MUNIC Direitos Humanos:", deam_cols_dir)
    except:
        pass

if __name__ == "__main__":
    get_deams()
