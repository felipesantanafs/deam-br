import pandas as pd
import os


def processar_base_sipcv(input_path: str, output_path: str):
    """
    Realiza a leitura, limpeza e filtragem da base SIPCV com foco na análise da violência contra a mulher e a infraestrutura das DDMs.
    """
    print("Iniciando a leitura da base de dados. Isso pode levar alguns instantes...")

    # 1. Leitura dos dados
    # Forçamos todas as colunas a serem lidas como texto (str) para evitar avisos de mixed types
    df = pd.read_excel(input_path, dtype=str)
    print(f"Total de registros originais carregados: {len(df)}")

    # Padronizando o nome das colunas para facilitar a manipulação
    df.columns = [str(c).strip().upper() for c in df.columns]

    # 2. Filtragem 1: Apenas Vítimas do Sexo Feminino
    if "SEXO_PESSOA" in df.columns:
        mask_feminino = df["SEXO_PESSOA"].str.upper().isin(["F", "FEMININO", "MULHER"])
        df = df[mask_feminino]
        print(f"Registros após filtro de vítimas mulheres: {len(df)}")

    # 3. Filtragem 2: Foco em Lesão Corporal e Ameaça (Alta Elasticidade de Denúncia)
    # Utilizamos expressões regulares (ex: LES.O, AMEA.A) para ignorar problemas de enconding (acentos quebrados na base)
    termos_crime = ["LES.O CORPORAL", "AMEA.A", "ART\. 129", "ART\. 147"]
    mask_crime = pd.Series(False, index=df.index)

    if "RUBRICA" in df.columns:
        mask_crime = mask_crime | df["RUBRICA"].fillna("").str.upper().str.contains(
            "|".join(termos_crime), regex=True
        )
    if "NATUREZA APURADA" in df.columns:
        mask_crime = mask_crime | df["NATUREZA APURADA"].fillna(
            ""
        ).str.upper().str.contains("|".join(termos_crime), regex=True)

    df = df[mask_crime]
    print(f"Registros após filtro de Lesão/Ameaça: {len(df)}")

    # 4. Filtragem 3: Contexto de Violência Doméstica (Maria da Penha)
    # Buscamos os valores reais observados na base: 'CONFLITO INTERPESSOAL ENTRE CONHECIDOS - RELAÇÃO AFETIVA', 'FAMILIARES', etc.
    termos_violencia = [
        "DOM.STICA",
        "DOMESTICA",
        "MARIA DA PENHA",
        "FAMILIAR",
        "AFETIVA",
    ]
    mask_violencia = pd.Series(False, index=df.index)

    colunas_contexto = ["CONTEXTO", "TIPO_INTOLERANCIA", "FLAG_INTOLERANCIA"]
    for col in colunas_contexto:
        if col in df.columns:
            mask_violencia = mask_violencia | df[col].fillna(
                ""
            ).str.upper().str.contains("|".join(termos_violencia), regex=True)

    # Para não perder toda a base (já que filtramos agressões a mulheres),
    # flexibilizamos o critério caso o filtro de contexto seja restritivo demais devido a mau preenchimento do BO
    if mask_violencia.sum() > 10:
        df = df[mask_violencia]
        print(f"Registros após filtro de Violência Doméstica: {len(df)}")
    else:
        print(
            f"Aviso: Filtro restrito achou apenas {mask_violencia.sum()} casos explícitos. Flexibilizando e mantendo a amostra de agressão contra a mulher ({len(df)} registros)."
        )

    # 5. Seleção das Variáveis (Colunas) de Interesse para o Modelo
    # Separamos as colunas que respondem às necessidades de Y, D, X e Distância.
    colunas_desejadas = [
        # Chaves e Tempo
        "NUM_BO",
        "ANO_BO",
        "DATA_OCORRENCIA_BO",
        "HORA_OCORRENCIA_BO",
        # Tipificação (Variável Dependente - Y)
        "RUBRICA",
        "NATUREZA APURADA",
        "CONTEXTO",
        "FLAG_INTOLERANCIA",
        "TIPO_INTOLERANCIA",
        # Georreferenciamento (Running Variable - Distância)
        "LATITUDE",
        "LONGITUDE",
        "LOGRADOURO",
        "NUMERO_LOGRADOURO",
        "CIDADE",
        # Jurisdição (Tratamento - D)
        "NOME_DELEGACIA_CIRC",
        "NOME_SECCIONAL_CIRC",
        "NOME_DELEGACIA",
        "NOME_DEPARTAMENTO_CIRC",
        # Controles Sociais (Covariáveis - X)
        "SEXO_PESSOA",
        "IDENTIDADE_GENERO",
        "IDADE_DATA_OCORRENCIA",
        "COR_CURTIS",
        "NOME_PROFISSAO",
    ]

    # Mantém apenas as colunas que de fato existem na planilha original
    colunas_finais = [c for c in colunas_desejadas if c in df.columns]
    df = df[colunas_finais]

    # 6. Limpeza e Formatação de Dados Finais
    # Removemos linhas que estejam 100% vazias
    df = df.dropna(how="all")

    # 7. Salvar o Arquivo
    # Utilizando CSV (com separador de ponto e vírgula) para ser leve no processamento do modelo
    # e poder ser aberto naturalmente como "planilha" no Excel sem travar.
    # index=False e mode='w' garante que o arquivo seja sobrescrito se já existir.
    print(f"Salvando o arquivo resultante em: {output_path}")
    df.to_csv(output_path, index=False, sep=";", encoding="utf-8-sig")
    print("Processo concluído com sucesso! O arquivo foi gerado/sobrescrito.")


if __name__ == "__main__":
    # Caminhos dinâmicos a partir da raiz do projeto, sem hardcode de caminho local
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

    ARQUIVO_ENTRADA = os.path.join(BASE_DIR, "dados", "ssp", "SIPCV_2026.xlsx")

    # Salvaremos como CSV para melhor performance em Data Science,
    # mas que abre normalmente no Excel (utf-8-sig + sep=';')
    ARQUIVO_SAIDA = os.path.join(BASE_DIR, "dados", "ssp", "data_sipcv.csv")

    # Garante que o diretório de saída exista
    os.makedirs(os.path.dirname(ARQUIVO_SAIDA), exist_ok=True)

    processar_base_sipcv(ARQUIVO_ENTRADA, ARQUIVO_SAIDA)
