"""
Script de inspeção inicial dos dados disponíveis no projeto.
Gera um relatório rápido com shapes, colunas, values e estatísticas descritivas.
"""
import pandas as pd
import os
import sys
import io

# Forçar UTF-8 no stdout
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

print("=" * 80)
print("INSPEÇÃO COMPLETA DAS BASES DE DADOS")
print("=" * 80)

# ---- 1. SSP / SIPCV ----
print("\n\n[1] SSP / SIPCV — Boletins de Ocorrência")
print("-" * 60)
df_ssp = pd.read_csv(os.path.join(ROOT, 'dados', 'ssp', 'data_sipcv.csv'), sep=';', encoding='latin-1')
# Limpar BOM do nome da primeira coluna
df_ssp.columns = [c.strip('\ufeff').strip() for c in df_ssp.columns]
print(f"   Shape: {df_ssp.shape}")
print(f"   Colunas: {list(df_ssp.columns)}")
print(f"\n   Rubricas (tipos de crime):")
print(df_ssp['RUBRICA'].value_counts().to_string())
print(f"\n   Delegacias unicas: {df_ssp['NOME_DELEGACIA'].nunique()}")
print(f"\n   Top 15 Delegacias com mais BOs:")
print(df_ssp['NOME_DELEGACIA'].value_counts().head(15).to_string())
print(f"\n   Seccionais unicas: {df_ssp['NOME_SECCIONAL_CIRC'].nunique()}")
print(f"\n   Top 10 Seccionais:")
print(df_ssp['NOME_SECCIONAL_CIRC'].value_counts().head(10).to_string())
print(f"\n   Delegacias Circunscricionais unicas: {df_ssp['NOME_DELEGACIA_CIRC'].nunique()}")
print(f"\n   Top 15 Delegacias Circunscricionais:")
print(df_ssp['NOME_DELEGACIA_CIRC'].value_counts().head(15).to_string())

# Filtrar DDMs (Delegacias de Defesa da Mulher)
ddm_mask = df_ssp['NOME_DELEGACIA'].str.contains('MULHER|DDM|DEAM', case=False, na=False)
print(f"\n   BOs em DDMs: {ddm_mask.sum()} ({ddm_mask.mean()*100:.1f}%)")
if ddm_mask.any():
    print(f"   DDMs encontradas:")
    print(df_ssp.loc[ddm_mask, 'NOME_DELEGACIA'].value_counts().to_string())

# ---- 2. SIM — Feminicídios ----
print("\n\n[2] SIM — Feminicídios (DataSUS)")
print("-" * 60)
df_sim = pd.read_csv(os.path.join(ROOT, 'dados', 'sim', 'sim_feminicidios_sp.csv'))
print(f"   Shape: {df_sim.shape}")
print(f"   Colunas: {list(df_sim.columns)}")
print(f"\n   Distribuição por ano:")
print(df_sim['ano'].value_counts().sort_index().to_string())
print(f"\n   Raca/Cor:")
print(df_sim['raca_cor'].value_counts().to_string())
print(f"\n   Causa basica (top 10):")
print(df_sim['causa_basica'].value_counts().head(10).to_string())
print(f"\n   Idade - Estatísticas:")
print(df_sim['idade'].describe().to_string())
print(f"\n   Codigo bairro preenchido: {df_sim['codigo_bairro_ocorrencia'].notna().sum()} / {len(df_sim)} ({df_sim['codigo_bairro_ocorrencia'].notna().mean()*100:.1f}%)")

# ---- 3. SINAN + CNES ----
print("\n\n[3] SINAN + CNES — Notificações de Violência")
print("-" * 60)
df_sinan = pd.read_csv(os.path.join(ROOT, 'dados', 'sinan', 'sinan_cnes_merged.csv'), low_memory=False)
print(f"   Shape: {df_sinan.shape}")
print(f"\n   Distribuição por ano:")
print(df_sinan['ano'].value_counts().sort_index().to_string())
print(f"\n   Bairros unicos (via CNES): {df_sinan['bairro'].nunique()}")
print(f"\n   Top 15 Bairros (local do hospital notificador):")
print(df_sinan['bairro'].value_counts().head(15).to_string())
print(f"\n   Lat/Long preenchidos: {df_sinan['latitude'].notna().sum()} / {len(df_sinan)} ({df_sinan['latitude'].notna().mean()*100:.1f}%)")
print(f"\n   Violencia Física:")
vf = df_sinan['ocorreu_violencia_fisica'].astype(str).str.lower()
print(vf.value_counts().to_string())
print(f"\n   Ameaca (meio_ameaca):")
ma = df_sinan['meio_ameaca'].astype(str).str.lower()
print(ma.value_counts().to_string())
print(f"\n   Local da ocorrencia:")
print(df_sinan['local_ocorrencia'].value_counts().to_string())
print(f"\n   Encaminhamento Delegacia Mulher:")
print(df_sinan['encaminhamento_delegacia_mulher'].value_counts().to_string())
print(f"\n   Autor - Conjuge:")
print(df_sinan['autor_conjugue'].value_counts().to_string())
print(f"\n   Autor - Ex-Conjuge:")
print(df_sinan['autor_ex_conjugue'].value_counts().to_string())
print(f"\n   Hora da ocorrencia - exemplos:")
print(df_sinan['hora_ocorrencia'].head(20).to_string())

# ---- 4. CNES ----
print("\n\n[4] CNES — Estabelecimentos de Saude Geolocalizados")
print("-" * 60)
df_cnes = pd.read_csv(os.path.join(ROOT, 'dados', 'cnes', 'cnes_sp_geolocalizado.csv'))
print(f"   Shape: {df_cnes.shape}")
print(f"   Bairros unicos: {df_cnes['bairro'].nunique()}")
print(f"\n   Top 15 Bairros com mais estabelecimentos:")
print(df_cnes['bairro'].value_counts().head(15).to_string())

# ---- 5. SSP — Feminicídios ----
print("\n\n[5] SSP — Feminicidios (dados_feminicidio.xlsx)")
print("-" * 60)
df_fem = pd.read_excel(os.path.join(ROOT, 'dados', 'ssp', 'dados_feminicidio.xlsx'))
print(f"   Shape: {df_fem.shape}")
print(f"   Colunas: {list(df_fem.columns)}")
print(f"\n   Primeiras linhas:")
print(df_fem.head(5).to_string())

# ---- 6. Funil consolidado ----
print("\n\n[6] Funil da Violencia Consolidado")
print("-" * 60)
df_funil = pd.read_csv(os.path.join(ROOT, 'dados', 'consolidado', 'funil_violencia_ano.csv'))
print(df_funil.to_string())

print("\n\n" + "=" * 80)
print("INSPEÇÃO FINALIZADA")
print("=" * 80)
