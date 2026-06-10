"""
🔬 DDM — Dashboard de Análise Exploratória
Violência contra Mulheres no Município de São Paulo
FEA-USP | Avaliação de Políticas Sociais

Arquivo principal do Streamlit (multipage).
"""
import streamlit as st
import base64
import os

# ─── Configuração da Página ──────────────────────────────────────────
st.set_page_config(
    page_title="DDM | Análise Exploratória — Violência contra Mulheres em SP",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CSS Global Premium ──────────────────────────────────────────────
st.markdown("""
<style>
    /* ── Import Google Font ── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    .stApp {
        font-family: 'Inter', 'Segoe UI', sans-serif;
    }

    /* ── Sidebar styling ── */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0B1A2E 0%, #112240 50%, #0B1A2E 100%) !important;
        border-right: 1px solid #1E3A5F;
    }

    section[data-testid="stSidebar"] .stMarkdown h1,
    section[data-testid="stSidebar"] .stMarkdown h2,
    section[data-testid="stSidebar"] .stMarkdown h3 {{
        color: #AED6F1 !important;
    }}

    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] .stMarkdown li {{
        color: #85C1E9 !important;
    }}

    /* ── Headers ── */
    h1 {{
        color: #ECF0F1 !important;
        font-weight: 700 !important;
        letter-spacing: -0.5px;
    }}
    h2 {{
        color: #AED6F1 !important;
        font-weight: 600 !important;
    }}
    h3 {{
        color: #85C1E9 !important;
        font-weight: 500 !important;
    }}

    /* ── Tabs premium ── */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 4px;
        background: rgba(17,34,64,0.5);
        border-radius: 10px;
        padding: 4px;
    }}
    .stTabs [data-baseweb="tab"] {{
        border-radius: 8px;
        color: #85C1E9;
        font-weight: 500;
        padding: 8px 20px;
    }}
    .stTabs [aria-selected="true"] {{
        background: linear-gradient(135deg, #1B4F72, #2E86C1) !important;
        color: #ECF0F1 !important;
        border-radius: 8px !important;
    }}

    /* ── Selectbox / Multiselect ── */
    .stSelectbox > div > div,
    .stMultiSelect > div > div {{
        background: rgba(17,34,64,0.7) !important;
        border-color: #1E3A5F !important;
        color: #ECF0F1 !important;
    }}

    /* ── Metric containers ── */
    [data-testid="stMetric"] {{
        background: linear-gradient(135deg, #112240 0%, #1A3150 100%);
        border: 1px solid #1E3A5F;
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }}
    [data-testid="stMetricValue"] {{
        color: #5DADE2 !important;
        font-weight: 700 !important;
    }}
    [data-testid="stMetricLabel"] {{
        color: #95A5A6 !important;
        text-transform: uppercase;
        font-size: 0.8rem !important;
        letter-spacing: 1px;
    }}

    /* ── Dataframe styling ── */
    .stDataFrame {{
        border-radius: 10px;
        overflow: hidden;
    }}

    /* ── Divider ── */
    hr {{
        border-color: #1E3A5F !important;
        margin: 24px 0 !important;
    }}

    /* ── Expander ── */
    .streamlit-expanderHeader {{
        background: rgba(17,34,64,0.5) !important;
        border-radius: 8px !important;
        color: #AED6F1 !important;
    }}

    /* ── Plotly chart containers ── */
    .stPlotlyChart {{
        border-radius: 12px;
        overflow: hidden;
    }}

    /* ── Remove extra padding ── */
    .block-container {{
        padding-top: 2rem !important;
    }}

    /* ── Link styling ── */
    a {{
        color: #5DADE2 !important;
    }}
</style>
""", unsafe_allow_html=True)


# ─── Sidebar ─────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    # 🔬 DDM
    ### Análise Exploratória
    ---
    **Violência contra Mulheres**
    *Município de São Paulo*

    FEA-USP | Avaliação de Políticas Sociais
    """)

    st.markdown("---")

    st.markdown("""
    #### 📑 Navegação
    Use o menu acima para navegar entre as páginas de análise.

    ---

    #### 📊 Bases de Dados
    - 🏥 SINAN + CNES (107.212 reg.)
    - ⚰️ SIM/DataSUS (525 óbitos)
    - 📋 Funil Consolidado

    ---

    #### 🔗 Cadeia Causal
    ```
    DDM 24h → ↑Denúncias → ↓Feminicídios
    ```

    *Hipótese: DDMs 24h ampliam o acesso institucional e reduzem a letalidade.*
    """)

    st.markdown("---")
    st.caption("© 2026 DDM | FEA-USP")


# ─── Conteúdo Principal (Home) ───────────────────────────────────────
st.markdown("""
# 🔬 Diagnóstico Espaço-Temporal da Violência contra Mulheres
### Município de São Paulo — Análise Exploratória de Dados
""")

st.markdown("---")

# KPI Cards
from utils.charts import metric_card_css, render_metric
st.markdown(metric_card_css(), unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(render_metric(
        "Notificações SINAN", "107.212",
        "2015–2019", "neutral"
    ), unsafe_allow_html=True)
with col2:
    st.markdown(render_metric(
        "Feminicídios (SIM)", "525",
        "2015–2019", "neutral"
    ), unsafe_allow_html=True)
with col3:
    st.markdown(render_metric(
        "Bairros Mapeados", "359",
        "Via proxy CNES", "neutral"
    ), unsafe_allow_html=True)
with col4:
    st.markdown(render_metric(
        "Geolocalização", "83,7%",
        "Lat/Long SINAN+CNES", "neutral"
    ), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Resumo do projeto
col_left, col_right = st.columns([3, 2])

with col_left:
    st.markdown("""
    ### 🎯 Sobre esta Análise

    Este dashboard apresenta a **Fase 1 — Diagnóstico e Ciência de Dados** do projeto
    de avaliação de impacto das Delegacias de Defesa da Mulher (DDMs) com funcionamento 24h
    no município de São Paulo.

    **Objetivo**: Construir evidência empírica que fundamente as hipóteses antes
    da estimação do modelo causal (Diferenças-em-Diferenças).

    ---

    #### 📐 Cadeia Causal do Modelo

    O modelo resolve o paradoxo da **causalidade reversa de registro**: uma DDM eficiente
    *aumenta* denúncias (reduzindo a cifra oculta) ao mesmo tempo em que *diminui* a
    letalidade. Por isso, usa duas variáveis dependentes:

    - **↑ Denúncias/Notificações** = sucesso no acesso institucional
    - **↓ Feminicídios** = sucesso na proteção da vida
    """)

with col_right:
    st.markdown("""
    ### 📑 Páginas Disponíveis

    | Página | Conteúdo |
    |--------|----------|
    | 📊 **Funil da Violência** | Cascata: Ameaça → Lesão → Feminicídio |
    | 📈 **Séries Temporais** | Evolução mensal e anual detalhada |
    | 🏢 **Delegacias & Bairros** | Rankings e concentrações de ocorrências |
    | 🗺️ **Mapa de Bairros** | Visualização com bolhas por bairro |
    | 🔥 **Mapa de Calor DDMs** | Calor espacial das notificações & markers das 9 DDMs |
    | 👤 **Perfil das Vítimas** | Sociodemografia e contexto das vítimas |
    | ⏰ **Sazonalidade** | Análise temporal (hora, dia e mês) |
    | 🚨 **Análise DDMs** | Avaliação estatística da cobertura das DDMs |
    | 🔬 **Modelo Causal (DiD)** | Avaliação de impacto causal via PSM + Diferenças-em-Diferenças |

    ---

    > *Navegue pelas páginas usando o menu lateral* ◀️
    """)

st.markdown("---")
st.markdown("""
<div class="insight-box">
    💡 <strong>Insight Preliminar do Funil</strong>: Entre 2015 e 2019, as notificações de violência
    cresceram de 7.301 para 33.357 (+357%), enquanto os feminicídios caíram de 177 para 55 (−69%).
    Este padrão sugere que o aumento de registros reflete maior acesso institucional, não aumento real
    da violência — evidência favorável à hipótese da cadeia causal.
</div>
""", unsafe_allow_html=True)
