import pandas as pd
import os

def pipeline_feminicidio(input_path: str, output_path: str):
    """
    Realiza a leitura, limpeza e filtragem da base de Feminicídio (2015-2022).
    Remove colunas pouco úteis para o estudo de impacto (Spatial RDD / DiD)
    conforme diretrizes do Projeto DPG MJSP 07/2026.
    """
    print("Iniciando a leitura da base de dados de Feminicídio. Isso pode levar alguns instantes...")
    
    # 1. Leitura dos dados — O arquivo possui uma aba por ano (Abr2015, 2016, ..., 2022).
    # sheet_name=None retorna um dicionário {nome_aba: DataFrame} com TODAS as abas.
    sheets = pd.read_excel(input_path, sheet_name=None, dtype=str)
    
    frames = []
    for nome_aba, df_aba in sheets.items():
        print(f"  Aba '{nome_aba}': {len(df_aba)} registros")
        frames.append(df_aba)
    
    df = pd.concat(frames, ignore_index=True)
    print(f"Total de registros originais carregados (todas as abas): {len(df)}")
    
    # 2. Padronizando o nome das colunas
    df.columns = [str(c).strip().upper() for c in df.columns]
    
    # Tratando colunas específicas que possuem erros de encoding () na leitura
    novas_colunas = []
    for c in df.columns:
        if 'ESTATISTICA' in c and 'S' in c and 'M' in c:
            novas_colunas.append('MES_ESTATISTICA')
        elif 'V' in c and 'T HD' in c:
            novas_colunas.append('N_VITIMAS_HD')
        else:
            novas_colunas.append(c)
    df.columns = novas_colunas
    
    # 3. Identificação de colunas para exclusão
    # Mapeando os nomes exatos como aparecem na base e também como foram solicitados
    colunas_remover = [
        'DESDOBRAMENTO', 'DEDOBRAMENTO', 
        'NATUREZA_APURADA', 
        'DATA_NASCIMENTO_PESSOA', 'DATA_NASCIMETNTO_PESSOA', 
        'SEXO_PESSOA', 
        'TIPO_PESSOA', 
        'NUMERO_LOGRADOURO', 'NUMERO_LOGADOURO', 
        'LOGRADOURO', 'LOGADOURO'
    ]
    
    # Filtra apenas as colunas que de fato existem no dataframe
    colunas_existentes_remover = [c for c in colunas_remover if c in df.columns]
    
    # Drop das colunas
    df = df.drop(columns=colunas_existentes_remover)
    print(f"Colunas removidas do dataset: {colunas_existentes_remover}")
    
    # 4. Filtro geográfico: apenas Região Metropolitana de São Paulo (cidade de SP)
    if 'MUNICIPIO_CIRCUNSCRICAO' in df.columns:
        df['MUNICIPIO_CIRCUNSCRICAO'] = df['MUNICIPIO_CIRCUNSCRICAO'].str.strip()
        df = df[df['MUNICIPIO_CIRCUNSCRICAO'].str.upper() == 'SÃO PAULO']
        print(f"Registros após filtro da cidade de São Paulo: {len(df)}")
    else:
        print("Aviso: Coluna 'MUNICIPIO_CIRCUNSCRICAO' não encontrada. Filtro geográfico não aplicado.")
    
    # 5. Limpeza de registros em branco
    df = df.dropna(how='all')
    print(f"Registros após remoção de linhas vazias: {len(df)}")
    
    # 5. Salvar o Arquivo
    # Sobrescreve o arquivo no caminho de destino (se existir) sem duplicar.
    print(f"Salvando o arquivo resultante em: {output_path}")
    df.to_excel(output_path, index=False)
    print("Processo concluído com sucesso! A planilha foi gerada/reescrita como dados_feminicidio.xlsx")

if __name__ == '__main__':
    # Define o caminho base e os caminhos de entrada e saída
    # Agora estamos 2 níveis abaixo de codes/ (codes/extracao_filtragem/pipeline_feminicidio.py)
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    ARQUIVO_ENTRADA = os.path.join(BASE_DIR, 'dados', 'ssp', 'Feminicidio_2015_2022.xlsx')
    ARQUIVO_SAIDA = os.path.join(BASE_DIR, 'dados', 'ssp', 'dados_feminicidio.xlsx')
    
    # Garante que a pasta de dados exista (embora já deva existir por conter a base de entrada)
    os.makedirs(os.path.dirname(ARQUIVO_SAIDA), exist_ok=True)
    
    pipeline_feminicidio(ARQUIVO_ENTRADA, ARQUIVO_SAIDA)
