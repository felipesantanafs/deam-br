"""
Módulo centralizado de carregamento e cache dos dados.
Usa @st.cache_data para evitar recarregar a cada interação.
"""
import pandas as pd
import streamlit as st
import os

# Caminho base dos dados (relativo ao diretório do streamlit)
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'dados'))


@st.cache_data(ttl=3600, show_spinner="Carregando dados do SINAN + CNES (2015-2019)...")
def load_sinan_cnes() -> pd.DataFrame:
    """Carrega a base integrada SINAN + CNES filtrada para o período de 2015 a 2019 (107.212 registros)."""
    path = os.path.join(DATA_DIR, 'sinan', 'sinan_cnes_merged.csv')
    df = pd.read_csv(path, low_memory=False)

    # Filtrar para o período de 2015 a 2019
    if 'ano' in df.columns:
        df = df[(df['ano'] >= 2015) & (df['ano'] <= 2019)]

    # Converter colunas binárias para numérico
    binary_cols = [
        'ocorreu_violencia_fisica', 'ocorreu_violencia_psicologica',
        'ocorreu_violencia_sexual', 'ocorreu_negligencia_abandono',
        'meio_forca', 'meio_enforcamento', 'meio_objeto_contundente',
        'meio_objeto_perfurante', 'meio_objeto_quente', 'meio_envenenamento',
        'meio_arma_fogo', 'meio_ameaca', 'meio_outros',
        'autor_pai', 'autor_mae', 'autor_padrasto', 'autor_madrasta',
        'autor_conjugue', 'autor_ex_conjugue', 'autor_namorado_a',
        'autor_ex_namorado_a', 'autor_filho_a', 'autor_desconhecido',
        'autor_irmao', 'autor_conhecido', 'autor_cuidador',
        'autor_patrao_chefe', 'autor_propria_pessoa',
        'encaminhamento_delegacia_mulher', 'encaminhamento_delegacia',
        'lesao_autoprovocada', 'autor_sexo'
    ]
    for col in binary_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # Extrair hora como inteiro
    if 'hora_ocorrencia' in df.columns:
        df['hora'] = pd.to_datetime(df['hora_ocorrencia'], format='%H:%M:%S', errors='coerce').dt.hour

    # Converter data_ocorrencia para datetime
    if 'data_ocorrencia' in df.columns:
        df['data_ocorrencia'] = pd.to_datetime(df['data_ocorrencia'], errors='coerce')
        df['mes'] = df['data_ocorrencia'].dt.month
        df['ano_mes'] = df['data_ocorrencia'].dt.to_period('M').astype(str)

    return df


@st.cache_data(ttl=3600, show_spinner="Carregando dados do SIM (2015-2019)...")
def load_sim() -> pd.DataFrame:
    """Carrega a base de feminicídios do SIM/DataSUS filtrada para 2015-2019 (525 registros)."""
    path = os.path.join(DATA_DIR, 'sim', 'sim_feminicidios_sp.csv')
    df = pd.read_csv(path)
    
    # Filtrar para o período de 2015 a 2019
    if 'ano' in df.columns:
        df = df[(df['ano'] >= 2015) & (df['ano'] <= 2019)]

    df['data_obito'] = pd.to_datetime(df['data_obito'], errors='coerce')
    df['idade'] = pd.to_numeric(df['idade'], errors='coerce')
    return df



@st.cache_data(ttl=3600, show_spinner="Carregando funil consolidado...")
def load_funil() -> pd.DataFrame:
    """Carrega a tabela consolidada do funil da violência."""
    path = os.path.join(DATA_DIR, 'consolidado', 'funil_violencia_ano.csv')
    return pd.read_csv(path)


# ─── Mapeamentos de códigos ──────────────────────────────────────────
LOCAL_OCORRENCIA_MAP = {
    1: "Residência",
    2: "Habitação coletiva",
    3: "Escola",
    4: "Local de prática esportiva",
    5: "Bar ou similar",
    6: "Via pública",
    7: "Comércio/Serviços",
    8: "Indústrias/Construção",
    9: "Outros",
}

RACA_PACIENTE_MAP = {
    1: "Branca",
    2: "Preta",
    3: "Amarela",
    4: "Parda",
    5: "Indígena",
}

ESCOLARIDADE_MAP = {
    0: "Sem escolaridade",
    1: "1ª a 4ª série",
    2: "5ª a 8ª série",
    3: "Ensino médio",
    4: "Superior incompleto",
    5: "Superior completo",
    6: "Não se aplica",
    9: "Ignorado",
}
