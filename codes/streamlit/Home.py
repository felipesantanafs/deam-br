"""
🛡️ DEAM 24h — Avaliação de Impacto Nacional
Violência contra a Mulher no Brasil (2009–2019)
FEA-USP | Avaliação de Políticas Sociais

Arquivo principal do Streamlit (multipage).
"""
import os
import sys

import streamlit as st

sys.path.insert(0, os.path.dirname(__file__))
from utils.data_loader import (
    load_painel_deam, referencia_municipios, serie_nacional_anual,
)
from utils.charts import metric_card_css, render_metric

# ─── Configuração da Página ──────────────────────────────────────────
st.set_page_config(
    page_title="DEAM 24h | Avaliação de Impacto Nacional",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CSS Global ──────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    .stApp { font-family: 'Inter', 'Segoe UI', sans-serif; }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0B1A2E 0%, #112240 50%, #0B1A2E 100%) !important;
        border-right: 1px solid #1E3A5F;
    }
    section[data-testid="stSidebar"] .stMarkdown h1,
    section[data-testid="stSidebar"] .stMarkdown h2,
    section[data-testid="stSidebar"] .stMarkdown h3 { color: #AED6F1 !important; }
    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] .stMarkdown li { color: #85C1E9 !important; }

    h1 { color: #ECF0F1 !important; font-weight: 700 !important; letter-spacing: -0.5px; }
    h2 { color: #AED6F1 !important; font-weight: 600 !important; }
    h3 { color: #85C1E9 !important; font-weight: 500 !important; }

    .stTabs [data-baseweb="tab-list"] {
        gap: 4px; background: rgba(17,34,64,0.5); border-radius: 10px; padding: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px; color: #85C1E9; font-weight: 500; padding: 8px 20px;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #1B4F72, #2E86C1) !important;
        color: #ECF0F1 !important; border-radius: 8px !important;
    }

    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #112240 0%, #1A3150 100%);
        border: 1px solid #1E3A5F; border-radius: 12px; padding: 16px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    [data-testid="stMetricValue"] { color: #5DADE2 !important; font-weight: 700 !important; }
    [data-testid="stMetricLabel"] {
        color: #95A5A6 !important; text-transform: uppercase;
        font-size: 0.8rem !important; letter-spacing: 1px;
    }

    .stDataFrame { border-radius: 10px; overflow: hidden; }
    hr { border-color: #1E3A5F !important; margin: 24px 0 !important; }
    .stPlotlyChart { border-radius: 12px; overflow: hidden; }
    .block-container { padding-top: 2rem !important; }
    a { color: #5DADE2 !important; }
</style>
""", unsafe_allow_html=True)

# ─── Dados ───────────────────────────────────────────────────────────
painel = load_painel_deam()
ref = referencia_municipios()
serie = serie_nacional_anual()

n_munic = ref['id_municipio'].nunique()
n_24h = int((ref['grupo'] == '24h').sum())
n_com = int((ref['grupo'] == 'comercial').sum())
tot_fem = int(painel['feminicidios'].sum())
tot_notif = int(painel['notificacoes'].sum())
n_uf = ref['uf'].nunique()
ano_min, ano_max = int(painel['ano'].min()), int(painel['ano'].max())


def br(n: int) -> str:
    return f"{n:,.0f}".replace(",", ".")


# ─── Sidebar ─────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    # 🛡️ DEAM 24h
    ### Avaliação de Impacto
    ---
    **Violência contra a Mulher**
    *Municípios brasileiros · 2009–2019*

    FEA-USP | Avaliação de Políticas Sociais
    """)
    st.markdown("---")
    st.markdown(f"""
    #### 📑 Navegação
    Use o menu acima para navegar entre as páginas de análise.

    ---

    #### 📊 Bases de Dados
    - 🏥 SINAN — notificações de violência
    - ⚰️ SIM/DataSUS — feminicídios
    - 🏛️ IBGE/SIDRA — população municipal
    - 📋 Cadastro de DEAMs (24h x comercial)

    ---

    #### 🔗 Cadeia Causal
    ```
    DEAM 24h → ↑Acesso → ↓Feminicídios
    ```
    *Hipótese: o plantão 24h amplia o acesso institucional fora do horário comercial e reduz a letalidade.*
    """)
    st.markdown("---")
    st.caption("© 2026 DEAM 24h | FEA-USP")


# ─── Conteúdo Principal ──────────────────────────────────────────────
st.markdown("""
# 🛡️ Avaliação de Impacto das DEAMs 24h no Brasil
### Violência contra a Mulher — Diagnóstico Nacional e Inferência Causal (2009–2019)
""")
st.markdown("---")

st.markdown(metric_card_css(), unsafe_allow_html=True)

c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    st.markdown(render_metric("Municípios", br(n_munic), f"{n_uf} UFs · 5 regiões", "neutral"), unsafe_allow_html=True)
with c2:
    st.markdown(render_metric("DEAMs 24h (tratados)", br(n_24h), "Adoção escalonada", "neutral"), unsafe_allow_html=True)
with c3:
    st.markdown(render_metric("DEAMs comerciais (controle)", br(n_com), "Nunca convertidas", "neutral"), unsafe_allow_html=True)
with c4:
    st.markdown(render_metric("Feminicídios (SIM)", br(tot_fem), f"{ano_min}–{ano_max}", "neutral"), unsafe_allow_html=True)
with c5:
    st.markdown(render_metric("Notificações (SINAN)", br(tot_notif), f"{ano_min}–{ano_max}", "neutral"), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

col_left, col_right = st.columns([3, 2])
with col_left:
    st.markdown("""
    ### 🎯 Sobre este Estudo

    Este painel avalia o **impacto causal da conversão de Delegacias Especializadas de
    Atendimento à Mulher (DEAMs) para o regime de plantão 24 horas** em municípios
    brasileiros, entre 2009 e 2019.

    **Pergunta de pesquisa:** a ampliação do horário de atendimento reduz a **letalidade**
    (feminicídios) e amplia o **acesso institucional** (notificações), especialmente fora
    do horário comercial?

    ---

    #### 📐 Cadeia Causal (duas variáveis-resultado)

    O desenho resolve o **paradoxo da causalidade reversa de registro**: uma delegacia mais
    acessível *aumenta* o número de notificações (reduzindo a cifra oculta) ao mesmo tempo
    em que *reduz* a letalidade. Por isso, avalia-se:

    - **↑ Notificações (SINAN)** = sucesso no acesso institucional
    - **↓ Feminicídios (SIM)** = sucesso na proteção da vida

    A identificação usa **Diferenças-em-Diferenças com adoção escalonada**
    (Callaway & Sant'Anna, 2021) em estimação **duplamente robusta** com covariáveis,
    tendo como contrafactual as DEAMs de horário comercial.

    > ⚖️ **Achado principal:** após corrigir as tendências paralelas, **não há evidência robusta**
    > de efeito da DEAM 24h sobre a letalidade — o efeito "positivo" aparente era **causalidade
    > reversa** (adoção reativa). Detalhes na página *Modelo Causal*.
    """)

with col_right:
    st.markdown("""
    ### 📑 Páginas Disponíveis

    | Página | Conteúdo |
    |--------|----------|
    | 📊 **Funil da Violência** | Cascata: notificações → tipos → feminicídios |
    | 📈 **Séries Temporais** | Evolução anual de taxas /100k |
    | 🗺️ **Panorama Territorial** | Mapa por UF, regiões e ranking |
    | 🏛️ **Adoção das DEAMs 24h** | Coortes da implantação escalonada |
    | ⏰ **Sazonalidade & Horário** | Hora, dia e mês — o mecanismo do plantão |
    | ⚖️ **Tratado vs Controle** | Comparação descritiva 24h × comercial |
    | 🔬 **Modelo Causal (CS DiD)** | Estimação de impacto (Callaway & Sant'Anna) |

    ---

    > *Navegue pelas páginas usando o menu lateral* ◀️
    """)

st.markdown("---")

# Insight preliminar a partir dos próprios dados
notif_ini, notif_fim = serie.iloc[0]['notificacoes'], serie.iloc[-1]['notificacoes']
var_notif = (notif_fim / notif_ini - 1) * 100
st.markdown(f"""
<div class="insight-box">
    💡 <strong>Panorama preliminar</strong>: nas {br(n_munic)} cidades analisadas, as notificações
    de violência contra a mulher passaram de {br(int(notif_ini))} ({ano_min}) para
    {br(int(notif_fim))} ({ano_max}) — alta de {var_notif:+.0f}%. O crescimento sustentado dos
    registros é compatível com a hipótese de <strong>ampliação do acesso institucional</strong>
    (redução da subnotificação), e não necessariamente com aumento real da violência. As páginas
    a seguir decompõem esse movimento e isolam o efeito causal do plantão 24h.
</div>
""", unsafe_allow_html=True)
