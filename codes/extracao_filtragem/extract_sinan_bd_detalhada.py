import basedosdados as bd
import pandas as pd
import os
import sys

sys.path.append(os.path.dirname(__file__))
from bd_config import BILLING_ID

billing_id = BILLING_ID

output_dir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "dados", "sinan")
)
os.makedirs(output_dir, exist_ok=True)
output_file = os.path.join(output_dir, "sinan_violencia_br_detalhada.csv")

# A consulta inclui os campos solicitados para análise detalhada no SINAN.
query = """ 
SELECT
    dados.ano,
    dados.data_ocorrencia,
    dados.hora_ocorrencia,
    dados.id_uf_ocorrencia,
    dados.id_municipio_ocorrencia,
    diretorio.nome AS id_municipio_ocorrencia_nome,
    dados.id_municipio_6_ocorrencia,
    dados.idade_paciente,
    dados.sexo_paciente,
    dados.gestante_paciente,
    dados.raca_paciente,
    dados.escolaridade_paciente,
    dados.ocupacao_paciente,
    dados.estado_civil_paciente,
    dados.orientacao_sexual_paciente,
    dados.identidade_genero_paciente,
    dados.motivacao_violencia,
    dados.lesao_autoprovocada,
    dados.ocorreu_violencia_fisica,
    dados.ocorreu_violencia_psicologica,
    dados.ocorreu_violencia_sexual,
    dados.ocorreu_negligencia_abandono,
    dados.meio_forca,
    dados.meio_enforcamento,
    dados.meio_objeto_contundente,
    dados.meio_objeto_perfurante,
    dados.meio_objeto_quente,
    dados.meio_envenenamento,
    dados.meio_arma_fogo,
    dados.meio_ameaca,
    dados.meio_outros,
    dados.meio_qual_outro,
    dados.houve_assedio,
    dados.houve_estupro,
    dados.autor_pai,
    dados.autor_mae,
    dados.autor_padrasto,
    dados.autor_madrasta,
    dados.autor_conjugue,
    dados.autor_ex_conjugue,
    dados.autor_namorado_a,
    dados.autor_ex_namorado_a,
    dados.autor_filho_a,
    dados.autor_irmao,
    dados.autor_conhecido,
    dados.autor_desconhecido,
    dados.autor_cuidador,
    dados.autor_patrao_chefe,
    dados.autor_institucional,
    dados.autor_policial,
    dados.autor_propria_pessoa,
    dados.autor_outros
FROM `basedosdados.br_ms_sinan.microdados_violencia` AS dados
LEFT JOIN `basedosdados.br_bd_diretorios_brasil.municipio` AS diretorio
    ON dados.id_municipio_ocorrencia = diretorio.id_municipio
WHERE 
    dados.ano BETWEEN 2009 AND 2019
"""

print("Iniciando a extração detalhada do SINAN via Base dos Dados (BigQuery)...")
try:
    df = bd.read_sql(query=query, billing_project_id=billing_id)
    print(f"Download concluído! Total de registros detalhados (SINAN): {len(df)}")

    # Salvar em CSV na pasta dados
    df.to_csv(output_file, index=False, encoding="utf-8")
    print(f"Dados detalhados salvos com sucesso em: {output_file}")
except Exception as e:
    print(f"Erro ao executar a query: {e}")
    print(
        "Verifique se você configurou o 'billing_id' corretamente e se está autenticado no GCP."
    )
