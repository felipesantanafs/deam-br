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
print("INSPEÇÃO COMPLETA DAS BASES DE DADOS (BRASIL - AGREGADO MUNICIPAL)")
print("=" * 80)

# ---- 1. SIM — Feminicídios ----
sim_path = os.path.join(ROOT, 'dados', 'sim', 'sim_feminicidios_br.csv')
print("\n\n[1] SIM — Feminicídios Agregados (Brasil)")
print("-" * 60)
if os.path.exists(sim_path):
    df_sim = pd.read_csv(sim_path)
    print(f"   Shape: {df_sim.shape}")
    print(f"   Colunas: {list(df_sim.columns)}")
    print(f"\n   Distribuição de anos na base SIM:")
    if 'ano' in df_sim.columns:
        print(df_sim['ano'].value_counts().sort_index().to_string())
    print(f"\n   Total de Feminicídios Registrados: {df_sim['total_feminicidios'].sum()}")
else:
    print(f"Arquivo não encontrado: {sim_path}")

# ---- 2. SINAN ----
sinan_path = os.path.join(ROOT, 'dados', 'sinan', 'sinan_violencia_br.csv')
print("\n\n[2] SINAN — Notificações de Violência Agregadas (Brasil)")
print("-" * 60)
if os.path.exists(sinan_path):
    df_sinan = pd.read_csv(sinan_path, low_memory=False)
    print(f"   Shape: {df_sinan.shape}")
    print(f"   Colunas: {list(df_sinan.columns)}")
    print(f"\n   Distribuição de anos na base SINAN:")
    if 'ano' in df_sinan.columns:
        print(df_sinan['ano'].value_counts().sort_index().to_string())
    print(f"\n   Total de Notificações: {df_sinan['total_notificacoes'].sum()}")
    print(f"   Total de Lesões Físicas: {df_sinan['total_lesoes'].sum()}")
    print(f"   Total de Ameaças: {df_sinan['total_ameacas'].sum()}")
    print(f"   Total de Encaminhamentos DDM: {df_sinan['total_encaminhamentos_ddm'].sum()}")
else:
    print(f"Arquivo não encontrado: {sinan_path}")

# ---- 3. IBGE Municípios ----
ibge_path = os.path.join(ROOT, 'dados', 'ibge', 'municipios_br.csv')
print("\n\n[3] IBGE — Diretório de Municípios")
print("-" * 60)
if os.path.exists(ibge_path):
    df_ibge = pd.read_csv(ibge_path)
    print(f"   Shape: {df_ibge.shape}")
    print(f"   Colunas: {list(df_ibge.columns)}")
    print(f"\n   Total de Municípios na base: {df_ibge['id_municipio'].nunique()}")
else:
    print(f"Arquivo não encontrado: {ibge_path}")

# ---- 4. Funil consolidado ----
print("\n\n[4] Funil da Violencia Consolidado (Brasil)")
print("-" * 60)
funil_path = os.path.join(ROOT, 'dados', 'consolidado', 'funil_violencia_ano.csv')
if os.path.exists(funil_path):
    df_funil = pd.read_csv(funil_path)
    print(df_funil.to_string())
else:
    print(f"Arquivo não encontrado: {funil_path}")

print("\n\n" + "=" * 80)
print("INSPEÇÃO FINALIZADA")
print("=" * 80)
