"""
causal_model.py
Executa o pipeline completo de inferência causal:
1. Carga e tratamento de dados (SINAN, SSP, Socioeconômico)
2. Pareamento por Escore de Propensão (PSM) 1:1
3. Geração e exportação dos gráficos de Tendências Paralelas Brutas
4. Estimação do Impacto Causal do Plantão 24h via Callaway & Sant'Anna (2021)
5. Estimações de robustez (Sun & Abraham, BJS Imputation) e sensibilidade (HonestDiD)
6. Exportação dos resultados em JSON para o Streamlit
7. Exportação do painel pareado em CSV para gráficos interativos
"""

import pandas as pd
import numpy as np
import os
import json
import unicodedata
import matplotlib.pyplot as plt
import seaborn as sns

from diff_diff import (
    CallawaySantAnna,
    SunAbraham,
    ImputationDiD,
    compute_honest_did,
    plot_event_study
)
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

# Estilo de visualizações
sns.set_theme(style="whitegrid")
plt.rcParams["figure.figsize"] = (10, 6)
plt.rcParams["font.size"] = 12

# Mudar para o diretório raiz para consistência nos paths
if os.path.exists('../../dados'):
    os.chdir('../..')
elif os.path.exists('dados'):
    pass
else:
    # busca diretório raiz subindo níveis
    for _ in range(3):
        os.chdir('..')
        if os.path.exists('dados'):
            break

print("Diretório de trabalho atual:", os.getcwd())

# 1. Carregar as bases de dados
df_socio = pd.read_csv("dados/consolidado/distritos_socioeconomico.csv")
df_sinan = pd.read_csv("dados/sinan/sinan_cnes_merged.csv", low_memory=False)
df_fem = pd.read_excel("dados/ssp/dados_feminicidio.xlsx")

print(f"Covariáveis Socioeconômicas: {df_socio.shape[0]} distritos carregados.")
print(f"Notificações SINAN: {df_sinan.shape[0]} registros carregados.")
print(f"Feminicídios SSP: {df_fem.shape[0]} B.Os carregados.")

# 2. Mapeamento de Distritos
DP_TO_DISTRITO = {
    "001 DP - Sé":                      "se",
    "002 DP - Bom Retiro":              "bom retiro",
    "003 DP - Campos Elísios":          "santa cecilia",
    "005 DP - Aclimação":               "liberdade",
    "006 DP - Cambuci":                 "cambuci",
    "007 DP - Lapa":                    "lapa",
    "009 DP - Carandiru":               "santana",
    "010 DP - Penha de França":         "penha",
    "012 DP - Pari":                    "bras",
    "013 DP - Casa Verde":              "casa verde",
    "014 DP - Pinheiros":               "pinheiros",
    "016 DP - Vila Clementino":         "saude",
    "017 DP - Ipiranga":                "ipiranga",
    "018 DP - Alto da Moóca":           "mooca",
    "020 DP - Água Fria":               "mandaqui",
    "021 DP - Vila Matilde":            "vila matilde",
    "023 DP - Perdizes":                "barra funda",
    "024 DP - Ponte Rasa":              "ponte rasa",
    "025 DP - Parelheiros":             "parelheiros",
    "028 DP - Freguesia do Ó":          "freguesia do o",
    "029 DP - Vila Diva":               "penha",
    "030 DP - Tatuapé":                 "tatuape",
    "031 DP - Vila Carrão":             "carrao",
    "032 DP - Itaquera":                "itaquera",
    "033 DP - Pirituba":                "pirituba",
    "034 DP - Vila Sonia":              "vila sonia",
    "037 DP - Campo Limpo":             "campo limpo",
    "038 DP - Vila Amélia":             "tremembe",
    "039 DP - Vila Gustavo":            "vila medeiros",
    "040 DP - Vila Santa Maria":        "vila maria",
    "041 DP - Vila Rica":               "sao mateus",
    "042 DP - Parque São Lucas":        "sao lucas",
    "044 DP - Guaianazes":              "guaianases",
    "045 DP - Vila Brasilândia":        "cachoeirinha",
    "046 DP - Perus":                   "anhanguera",
    "047 DP - Capão Redondo":           "capao redondo",
    "048 DP - Cidade Dutra":            "cidade dutra",
    "049 DP - São Mateus":              "sao mateus",
    "050 DP - Itaim Paulista":          "itaim paulista",
    "053 DP - Parque do Carmo":         "parque do carmo",
    "054 DP - Cidade Tiradentes":       "cidade tiradentes",
    "055 DP - Parque São Rafael":       "sao mateus",
    "056 DP - Vila Alpina":             "vila prudente",
    "059 DP - Jardim Noemia":           "cidade ademar",
    "062 DP - Ermelino Matarazzo":      "ermelino matarazzo",
    "063 DP - Vila Jacuí":              "vila jacui",
    "064 DP - Cidade A E Carvalho":     "cidade lider",
    "065 DP - Artur Alvim":             "artur alvim",
    "066 DP - Vale do Aricanduva":      "aricanduva",
    "067 DP - Jardim Robru":            "itaim paulista",
    "068 DP - Lajeado":                 "lajeado",
    "069 DP - Teotônio Vilela":         "sapopemba",
    "070 DP - Vila Ema":                "sapopemba",
    "072 DP - Vila Penteado":           "cachoeirinha",
    "073 DP - Jaçanã":                  "jacana",
    "074 DP - Jaraguá":                 "pirituba",
    "075 DP - Jardim Arpoador":         "sapopemba",
    "077 DP - Santa Cecília":           "santa cecilia",
    "078 DP - Jardins":                 "pinheiros",
    "080 DP - Vila Joaniza":            "cidade ademar",
    "081 DP - Belém":                   "belem",
    "083 DP - Parque Bristol":          "sacoma",
    "085 DP - Jardim Mirna":            "pedreira",
    "087 DP - Vila Pereira Barreto":    "pirituba",
    "089 DP - Portal do Morumbi":       "morumbi",
    "090 DP - Parque Novo Mundo":       "vila maria",
    "092 DP - Parque Santo Antônio":    "campo limpo",
    "093 DP - Jaguaré":                 "jaguare",
    "095 DP - Heliópolis":              "sacoma",
    "097 DP - Americanópolis":          "cidade ademar",
    "098 DP - Jardim Míriam":           "pedreira",
    "099 DP - Campo Grande":            "campo grande",
    "100 DP - Jardim Herculano":        "capao redondo",
    "101 DP - Jardim das Imbuias":      "jardim sao luis",
    "102 DP - Socorro":                 "socorro",
    "103 DP - Cohab Itaquera":          "jose bonifacio",
}

def normalize_name(name):
    if pd.isna(name): return ""
    name = str(name).strip().lower()
    return ''.join(c for c in unicodedata.normalize('NFD', name) if unicodedata.category(c) != 'Mn')

def map_dp_to_district(dp_name, official_districts):
    if pd.isna(dp_name): return None
    dp_norm = normalize_name(str(dp_name).strip())
    for dp_key, distrito in DP_TO_DISTRITO.items():
        if normalize_name(dp_key) == dp_norm: return distrito
    parts = str(dp_name).strip().split(' - ')
    if len(parts) > 1:
        bairro = normalize_name(parts[-1])
        if bairro in official_districts: return bairro
    return None

df_socio['distrito_norm'] = df_socio['distrito'].apply(normalize_name)
official_districts = df_socio['distrito_norm'].tolist()

MANUAL_MAPPING_SINAN = {
    "jardim somara": "itaim paulista", "ermelino matarazo": "ermelino matarazzo",
    "parque america": "grajau", "jardim iva": "sapopemba", "jardim copacabana": "sao mateus",
    "cidade lider": "cidade lider", "jardim angela": "jardim angela", "sao miguel paulista": "sao miguel",
    "jardim helena": "jardim helena", "jardim sao luis": "jardim sao luis", "jd. marilia": "sao mateus",
    "jardim marilia": "sao mateus", "bras": "bras", "se": "se", "bosque da saude (s.p.)": "saude",
    "saude": "saude", "freguesia do o": "freguesia do o", "capao redondo": "capao redondo",
    "tatuape": "tatuape", "itaquera": "itaquera", "pirituba": "pirituba", "jaguare": "jaguare",
    "campo grande": "campo grande", "santo amaro": "santo amaro", "cambuci": "cambuci",
}

def map_sinan_to_district(bairro_name):
    norm = normalize_name(bairro_name)
    if not norm: return None
    if norm in MANUAL_MAPPING_SINAN: return MANUAL_MAPPING_SINAN[norm]
    if norm in official_districts: return norm
    for dist in official_districts:
        if dist in norm or norm in dist: return dist
    return None

# 1. Mapeamento e agregação do SINAN (2015-2019)
df_sinan['distrito_mapped'] = df_sinan['bairro'].apply(map_sinan_to_district)
df_sinan_filt = df_sinan[df_sinan['distrito_mapped'].notna() & (df_sinan['ano'].between(2015, 2019))]
panel_sinan = df_sinan_filt.groupby(['distrito_mapped', 'ano']).size().reset_index(name='notificacoes')

# 2. Mapeamento e agregação do Feminicídio SSP (2015-2019)
df_fem_period = df_fem[df_fem['ANO ESTATISTICA'].between(2015, 2019)].copy()
df_fem_period['distrito_mapped'] = df_fem_period['DP_CIRCUNSCRICAO'].apply(lambda x: map_dp_to_district(x, official_districts))
unmapped_mask = df_fem_period['distrito_mapped'].isna()
if unmapped_mask.sum() > 0:
    df_fem_period.loc[unmapped_mask, 'distrito_mapped'] = df_fem_period.loc[unmapped_mask, 'DP_ELABORACAO'].apply(map_sinan_to_district)

df_fem_filt = df_fem_period[df_fem_period['distrito_mapped'].notna()].copy()
panel_fem = df_fem_filt.groupby(['distrito_mapped', 'ANO ESTATISTICA']).size().reset_index(name='feminicidios')
panel_fem.rename(columns={'ANO ESTATISTICA': 'ano'}, inplace=True)


# 4. Construção do painel (APENAS distritos com DDM)
DDM_24H = ['cambuci', 'itaquera', 'sao mateus']
DDM_COMERCIAL = ['saude', 'jaguare', 'freguesia do o', 'tatuape', 'campo grande', 'pirituba']
ALL_DDM = DDM_24H + DDM_COMERCIAL

panel_base = [{"distrito_norm": d, "ano": y} for d in ALL_DDM for y in range(2015, 2020)]
df_panel = pd.DataFrame(panel_base)
df_panel = df_panel.merge(panel_sinan, left_on=['distrito_norm', 'ano'], right_on=['distrito_mapped', 'ano'], how='left')
df_panel = df_panel.merge(panel_fem, left_on=['distrito_norm', 'ano'], right_on=['distrito_mapped', 'ano'], how='left')
df_panel['notificacoes'] = df_panel['notificacoes'].fillna(0).astype(int)
df_panel['feminicidios'] = df_panel['feminicidios'].fillna(0).astype(int)
df_panel.drop(columns=['distrito_mapped_x', 'distrito_mapped_y'], errors='ignore', inplace=True)
df_panel = df_panel.merge(df_socio, on='distrito_norm', how='inner')
df_panel.drop(columns=['distrito_mapped'], errors='ignore', inplace=True)
df_panel['log_pop'] = np.log(df_panel['populacao'])

# 5. Variável de coorte e ID numérico
def assign_cohort(dist):
    if dist == 'cambuci': return 2016
    elif dist in ['itaquera', 'sao mateus']: return 2018
    return 0

df_panel['first_treat'] = df_panel['distrito_norm'].apply(assign_cohort)
dist_to_id = {d: i + 1 for i, d in enumerate(ALL_DDM)}
df_panel['unit_id'] = df_panel['distrito_norm'].map(dist_to_id)

print(f"Painel pré-pareamento construído: {len(df_panel)} obs ({len(ALL_DDM)} distritos × 5 anos)")

# 3.5 Propensity Score Matching (Vizinho Mais Próximo)
df_cross = df_panel[['distrito_norm', 'first_treat', 'populacao', 'renda_per_capita', 'ipvs', 'idh']].drop_duplicates()
df_cross['is_treated'] = (df_cross['first_treat'] > 0).astype(int)

X = df_cross[['populacao', 'renda_per_capita', 'ipvs', 'idh']]
y = df_cross['is_treated']

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

lr = LogisticRegression(penalty='l2', C=1.0, random_state=42)
lr.fit(X_scaled, y)
df_cross['propensity_score'] = lr.predict_proba(X_scaled)[:, 1]

treated_districts = df_cross[df_cross['is_treated'] == 1].copy()
control_districts = df_cross[df_cross['is_treated'] == 0].copy()

matched_controls = []
matching_pairs = {}

for _, t_row in treated_districts.iterrows():
    t_dist = t_row['distrito_norm']
    t_ps = t_row['propensity_score']
    
    available = control_districts[~control_districts['distrito_norm'].isin(matched_controls)].copy()
    if len(available) == 0: break
    available['ps_distance'] = abs(available['propensity_score'] - t_ps)
    best_match = available.loc[available['ps_distance'].idxmin()]
    
    c_dist = best_match['distrito_norm']
    matched_controls.append(c_dist)
    matching_pairs[t_dist] = {
        'treated_ps': round(float(t_ps), 4),
        'matched_control': c_dist,
        'control_ps': round(float(best_match['propensity_score']), 4),
        'ps_distance': round(float(best_match['ps_distance']), 4)
    }

print("PARES ALOCADOS (1:1 Nearest Neighbor):")
for t, d in matching_pairs.items():
    print(f"Tratado: {t.title():12s} (PS={d['treated_ps']:.4f}) -> Controle: {d['matched_control'].title():15s} (PS={d['control_ps']:.4f}) | Distância={d['ps_distance']:.4f}")

psm_matched_districts = list(matching_pairs.keys()) + matched_controls
df_panel = df_panel[df_panel['distrito_norm'].isin(psm_matched_districts)].copy()
print(f"Novo Painel Pós-PSM construído: {len(df_panel)} obs ({len(psm_matched_districts)} distritos × 5 anos)")

# Exportar painel pós-PSM para CSV
causal_panel_path = "dados/consolidado/causal_panel.csv"
df_panel.to_csv(causal_panel_path, index=False)
print(f"Painel pós-PSM exportado para: {causal_panel_path}")

# Balanço das covariáveis
balance_stats = {}
df_socio_ddm = df_panel[['distrito_norm', 'first_treat', 'populacao', 'renda_per_capita', 'ipvs', 'idh']].drop_duplicates()
df_socio_ddm['is_24h'] = (df_socio_ddm['first_treat'] > 0).astype(int)

covariates = ['populacao', 'renda_per_capita', 'ipvs', 'idh']
for cov in covariates:
    t_mean = float(df_socio_ddm.loc[df_socio_ddm['is_24h'] == 1, cov].mean())
    c_mean = float(df_socio_ddm.loc[df_socio_ddm['is_24h'] == 0, cov].mean())
    t_std = float(df_socio_ddm.loc[df_socio_ddm['is_24h'] == 1, cov].std())
    c_std = float(df_socio_ddm.loc[df_socio_ddm['is_24h'] == 0, cov].std())
    denom = np.sqrt((t_std**2 + c_std**2) / 2) if (t_std + c_std) > 0 else 1
    norm_diff = (t_mean - c_mean) / denom
    balance_stats[cov] = {
        'treated_mean': round(t_mean, 2),
        'control_mean': round(c_mean, 2),
        'norm_diff': round(norm_diff, 3),
    }

# 3.6 Observação Visual das Tendências Paralelas Brutas
def plot_raw_trends(df, outcome, label, filename):
    df_plot = df.copy()
    df_plot['Grupo'] = df_plot['first_treat'].apply(lambda x: 'Tratado (DDM 24h)' if x > 0 else 'Controle (DDM Comercial)')
    
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.lineplot(
        data=df_plot, x='ano', y=outcome, hue='Grupo', 
        estimator='mean', errorbar=None, marker='o', linewidth=3, 
        palette={'Tratado (DDM 24h)': '#008080', 'Controle (DDM Comercial)': '#4169E1'}, ax=ax
    )
    ax.axvline(x=2016, color='gray', linestyle='--', alpha=0.7, label='Intervenção (Coorte 2016)')
    ax.axvline(x=2018, color='gray', linestyle=':', alpha=0.7, label='Intervenção (Coorte 2018)')
    
    ax.set_title(f"Tendências Paralelas: Média de {label} por Ano", fontsize=14, fontweight='bold')
    ax.set_xlabel('Ano', fontsize=12)
    ax.set_ylabel(f'Média de {label}', fontsize=12)
    ax.set_xticks([2015, 2016, 2017, 2018, 2019])
    
    # Destaque visual pré-tratamento
    ax.axvspan(2015, 2016, alpha=0.1, color='green', label='Pré-tratamento Universal')
    
    ax.legend(title='Grupo', loc='best')
    plt.tight_layout()
    
    # Salvar o gráfico nos assets do streamlit
    os.makedirs("codes/streamlit/assets", exist_ok=True)
    out_img_path = f"codes/streamlit/assets/{filename}"
    plt.savefig(out_img_path, dpi=300)
    plt.close()
    print(f"Gráfico de tendências brutas salvo em: {out_img_path}")

plot_raw_trends(df_panel, 'notificacoes', 'Acesso (SINAN)', 'raw_trends_notificacoes.png')
plot_raw_trends(df_panel, 'feminicidios', 'Feminicídios (SSP)', 'raw_trends_feminicidios.png')

# 4. Estimação CS DiD
results_all = {}
for outcome in ['notificacoes', 'feminicidios']:
    label = 'Acesso (SINAN)' if outcome == 'notificacoes' else 'Feminicídios (SSP)'
    print(f"\nEstimando DiD para {label}...")

    # Callaway & Sant'Anna (Global)
    cs = CallawaySantAnna(
        control_group='never_treated',
        estimation_method='reg',
        n_bootstrap=999,
    )
    cs_result_all = cs.fit(
        df_panel, outcome=outcome, unit='unit_id',
        time='ano', first_treat='first_treat', aggregate='all',
        covariates=['log_pop', 'ipvs']
    )
    
    # Callaway & Sant'Anna (Event Study)
    cs_result = cs.fit(
        df_panel, outcome=outcome, unit='unit_id',
        time='ano', first_treat='first_treat', aggregate='event_study',
        covariates=['log_pop', 'ipvs']
    )

    # Sun & Abraham
    try:
        sa = SunAbraham()
        sa_result = sa.fit(df_panel, outcome=outcome, unit='unit_id', time='ano', first_treat='first_treat', covariates=['log_pop', 'ipvs'])
        sa_att = sa_result.overall_att
        sa_se = sa_result.overall_se
    except Exception as e:
        print(f"  SA: {e}")
        sa_att, sa_se = None, None

    # Imputation DiD (BJS)
    try:
        bjs = ImputationDiD()
        bjs_result = bjs.fit(df_panel, outcome=outcome, unit='unit_id', time='ano', first_treat='first_treat', covariates=['log_pop', 'ipvs'])
        bjs_att = bjs_result.overall_att
        bjs_se = bjs_result.overall_se
    except Exception as e:
        print(f"  BJS: {e}")
        bjs_att, bjs_se = None, None

    # Sensibilidade: HonestDiD
    honest_summary = None
    try:
        cs_honest = CallawaySantAnna(
            control_group='never_treated',
            estimation_method='reg',
            base_period='universal',
            n_bootstrap=0,
        )
        cs_honest_result = cs_honest.fit(
            df_panel, outcome=outcome, unit='unit_id',
            time='ano', first_treat='first_treat', aggregate='event_study',
            covariates=['log_pop', 'ipvs']
        )
        honest = compute_honest_did(cs_honest_result, method='relative_magnitude', M=1.0)
        ci_lo = getattr(honest, 'ci_lower', None)
        ci_hi = getattr(honest, 'ci_upper', None)
        honest_summary = {
            'method': 'relative_magnitude',
            'M': 1.0,
            'robust_ci_lower': round(float(ci_lo), 4) if ci_lo is not None and np.isfinite(ci_lo) else None,
            'robust_ci_upper': round(float(ci_hi), 4) if ci_hi is not None and np.isfinite(ci_hi) else None,
        }
    except Exception as e:
        print(f"  HonestDiD: {e}")

    # Event study
    event_study = {}
    if hasattr(cs_result, 'event_study_effects') and cs_result.event_study_effects:
        for rel_t, eff in sorted(cs_result.event_study_effects.items()):
            effect_val = eff['effect'] if isinstance(eff, dict) else float(eff)
            se_val = eff.get('se', None) if isinstance(eff, dict) else None
            if se_val is not None and not np.isfinite(se_val):
                se_val = None
            event_study[int(rel_t)] = {
                'effect': round(float(effect_val), 4),
                'se': round(float(se_val), 4) if se_val is not None else None,
            }

    # Cohort effects
    group_effects = {}
    if hasattr(cs_result, 'group_effects') and cs_result.group_effects:
        for g, eff in cs_result.group_effects.items():
            effect_val = eff['effect'] if isinstance(eff, dict) else float(eff)
            se_val = eff.get('se', None) if isinstance(eff, dict) else None
            group_effects[int(g)] = {
                'effect': round(float(effect_val), 4),
                'se': round(float(se_val), 4) if se_val is not None else None,
            }

    results_all[outcome] = {
        'cs_att': round(float(cs_result.overall_att), 4),
        'cs_se': round(float(cs_result.overall_se), 4),
        'sa_att': round(float(sa_att), 4) if sa_att is not None else None,
        'sa_se': round(float(sa_se), 4) if sa_se is not None else None,
        'bjs_att': round(float(bjs_att), 4) if bjs_att is not None else None,
        'bjs_se': round(float(bjs_se), 4) if bjs_se is not None else None,
        'honest_did': honest_summary,
        'event_study': event_study,
        'group_effects': group_effects,
    }

# 7. Salvar Resultados em JSON
causal_results = {
    "metadata": {
        "periodo": "2015-2019",
        "hipotese": "Impacto causal do plantão 24h nas DDMs",
        "metodo_principal": "Callaway & Sant'Anna (2021) via diff-diff",
        "contrafactual": "DDMs de horário comercial (nunca tratadas para 24h)",
        "coortes": {"2016": ["cambuci"], "2018": ["itaquera", "sao mateus"]},
        "controles": DDM_COMERCIAL,
        "robustez": "Sun & Abraham (2021), Borusyak et al. (2024)",
        "sensibilidade": "HonestDiD (Rambachan & Roth, 2023)",
    },
    "balanco_socioeconomico": {
        "descricao": "DDM 24h vs DDM Horário Comercial",
        "covariates": balance_stats,
    },
    "cs_did_24h": results_all,
    "psm_matching": {
        "descricao": "Pareamento 1:1 Nearest Neighbor via Logistic Regression",
        "pares": matching_pairs,
    },
}

output_json_path = "dados/consolidado/causal_results.json"
with open(output_json_path, 'w', encoding='utf-8') as f:
    json.dump(causal_results, f, ensure_ascii=False, indent=4)

print(f"\nResultados salvos com sucesso em: {output_json_path}")
print("Fim do pipeline.")
