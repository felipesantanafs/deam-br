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
output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "dados", "sinan"))
os.makedirs(output_dir, exist_ok = True)
output_file = os.path.join(output_dir, "sinan_violencia_sp.csv")

# A query extrai microdados de violência para o município de São Paulo,
# incluindo o código CNES da unidade notificadora (proxy geográfico intra-municipal).
query = """
SELECT
    dados.ano as ano,
    dados.data_ocorrencia as data_ocorrencia,
    dados.hora_ocorrencia as hora_ocorrencia,
    dados.id_uf_ocorrencia as id_uf_ocorrencia,
    dados.id_municipio_ocorrencia AS id_municipio_ocorrencia,
    diretorio_id_municipio_ocorrencia.nome AS id_municipio_ocorrencia_nome,
    dados.id_municipio_6_ocorrencia as id_municipio_6_ocorrencia,
    dados.local_ocorrencia as local_ocorrencia,
    -- Proxy geográfico: código CNES da unidade de saúde que notificou o caso.
    -- Pode ser cruzado com o diretório CNES para obter lat/long e bairro.
    dados.id_unidade_notificacao as id_unidade_notificacao,
    dados.id_municipio_residencia as id_municipio_residencia,
    dados.id_municipio_6_residencia as id_municipio_6_residencia,
    dados.idade_paciente as idade_paciente,
    dados.sexo_paciente as sexo_paciente,
    dados.gestante_paciente as gestante_paciente,
    dados.raca_paciente as raca_paciente,
    dados.escolaridade_paciente as escolaridade_paciente,
    dados.ocupacao_paciente as ocupacao_paciente,
    dados.estado_civil_paciente as estado_civil_paciente,
    dados.orientacao_sexual_paciente as orientacao_sexual_paciente,
    dados.identidade_genero_paciente as identidade_genero_paciente,
    dados.motivacao_violencia as motivacao_violencia,
    dados.lesao_autoprovocada as lesao_autoprovocada,
    dados.ocorreu_violencia_fisica as ocorreu_violencia_fisica,
    dados.ocorreu_violencia_psicologica as ocorreu_violencia_psicologica,
    dados.ocorreu_violencia_sexual as ocorreu_violencia_sexual,
    dados.ocorreu_negligencia_abandono as ocorreu_negligencia_abandono,
    dados.meio_forca as meio_forca,
    dados.meio_enforcamento as meio_enforcamento,
    dados.meio_objeto_contundente as meio_objeto_contundente,
    dados.meio_objeto_perfurante as meio_objeto_perfurante,
    dados.meio_objeto_quente as meio_objeto_quente,
    dados.meio_envenenamento as meio_envenenamento,
    dados.meio_arma_fogo as meio_arma_fogo,
    dados.meio_ameaca as meio_ameaca,
    dados.meio_outros as meio_outros,
    dados.meio_qual_outro as meio_qual_outro,
    dados.houve_assedio as houve_assedio,
    dados.houve_estupro as houve_estupro,
    dados.autor_pai as autor_pai,
    dados.autor_mae as autor_mae,
    dados.autor_padrasto as autor_padrasto,
    dados.autor_madrasta as autor_madrasta,
    dados.autor_conjugue as autor_conjugue,
    dados.autor_ex_conjugue as autor_ex_conjugue,
    dados.autor_namorado_a as autor_namorado_a,
    dados.autor_ex_namorado_a as autor_ex_namorado_a,
    dados.autor_filho_a as autor_filho_a,
    dados.autor_desconhecido as autor_desconhecido,
    dados.autor_irmao as autor_irmao,
    dados.autor_conhecido as autor_conhecido,
    dados.autor_cuidador as autor_cuidador,
    dados.autor_patrao_chefe as autor_patrao_chefe,
    dados.autor_propria_pessoa as autor_propria_pessoa,
    dados.autor_sexo as autor_sexo,
    dados.autor_usou_alcool as autor_usou_alcool,
    dados.encaminhamento_delegacia_mulher as encaminhamento_delegacia_mulher,
    dados.encaminhamento_delegacia as encaminhamento_delegacia
FROM `basedosdados.br_ms_sinan.microdados_violencia` AS dados
LEFT JOIN (SELECT DISTINCT id_municipio, nome FROM `basedosdados.br_bd_diretorios_brasil.municipio`) AS diretorio_id_municipio_ocorrencia
    ON dados.id_municipio_ocorrencia = diretorio_id_municipio_ocorrencia.id_municipio
WHERE 
    -- Filtro 1: Apenas Município de São Paulo
    dados.id_municipio_ocorrencia = '3550308' 
"""

print("Iniciando o download dos dados do SINAN via Base dos Dados (BigQuery)...")
try:
    df = bd.read_sql(query = query, billing_project_id = billing_id)
    print(f"Download concluído! Total de registros encontrados: {len(df)}")

    # Salvar em CSV na pasta dados
    df.to_csv(output_file, index = False, encoding = "utf-8")
    print(f"Dados salvos com sucesso em: {output_file}")
except Exception as e:
    print(f"Erro ao executar a query: {e}")
    print("Verifique se você configurou o 'billing_id' corretamente e se está autenticado no GCP.")
