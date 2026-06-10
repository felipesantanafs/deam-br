import pandas as pd
import os

# Definir caminhos
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "dados"))
sinan_file = os.path.join(base_dir, "sinan", "sinan_violencia_sp.csv")
cnes_file = os.path.join(base_dir, "cnes", "cnes_sp_geolocalizado.csv")
output_file = os.path.join(base_dir, "sinan", "sinan_cnes_merged.csv")

print("Carregando base do SINAN...")
# Lendo id_unidade_notificacao como string para evitar perdas de zeros à esquerda
df_sinan = pd.read_csv(sinan_file, dtype={'id_unidade_notificacao': str})
print(f"Total de registros SINAN: {len(df_sinan)}")

print("\nCarregando dicionário CNES...")
df_cnes = pd.read_csv(cnes_file, dtype={'id_estabelecimento_cnes': str, 'cep': str})
print(f"Total de unidades CNES: {len(df_cnes)}")

print("\nRealizando o merge...")
# Merge Left: mantemos todos os registros do SINAN e trazemos as infos do CNES quando houver match
df_merged = pd.merge(
    df_sinan,
    df_cnes,
    left_on='id_unidade_notificacao',
    right_on='id_estabelecimento_cnes',
    how='left'
)

# Estatísticas de Match
matched = df_merged['id_estabelecimento_cnes'].notnull().sum()
missing = df_merged['id_estabelecimento_cnes'].isnull().sum()
print(f"\n=== ESTATÍSTICAS DO MERGE ===")
print(f"Registros SINAN com geolocalização (CNES encontrado): {matched} ({matched/len(df_sinan)*100:.2f}%)")
print(f"Registros SINAN sem localização (CNES não encontrado ou vazio): {missing} ({missing/len(df_sinan)*100:.2f}%)")

# Remover a coluna duplicada (id_estabelecimento_cnes) que veio do right dataset
df_merged = df_merged.drop(columns=['id_estabelecimento_cnes'])

print("\nSalvando base consolidada...")
df_merged.to_csv(output_file, index=False, encoding='utf-8')
print(f"Base salva em: {output_file}")
