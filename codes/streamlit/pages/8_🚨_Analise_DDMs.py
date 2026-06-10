"""
🚨 Página 8 — Análise de Encaminhamentos DDM
Painel focado na hipótese causal: o acesso à Delegacia da Mulher (DDM).
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from utils.data_loader import load_sinan_cnes
from utils.charts import apply_theme, COLORS, PALETTE, metric_card_css, render_metric, section_header

st.set_page_config(page_title="Análise DDMs | DDM", page_icon="🚨", layout="wide")
st.markdown(metric_card_css(), unsafe_allow_html=True)

st.markdown("# 🚨 Acesso e Encaminhamento às DDMs")
st.markdown("*Análise focada na atuação das Delegacias de Defesa da Mulher (DDM) e evidências para a hipótese causal das DDMs 24h.*")
st.markdown("---")

df_sinan = load_sinan_cnes()

# Filtros
ano_range = st.slider("Período (Base 🏥 SINAN)", 2015, 2019, (2015, 2019), key="ddm_ano")
df_filt = df_sinan[
    (df_sinan['ano'] >= ano_range[0]) & 
    (df_sinan['ano'] <= ano_range[1])
].copy()

# ─── Cálculos Globais ──────────────────────────────────────────────────
total_casos = len(df_filt)
casos_ddm = df_filt['encaminhamento_delegacia_mulher'].sum()
taxa_ddm = (casos_ddm / total_casos) * 100 if total_casos > 0 else 0

casos_dp_comum = df_filt['encaminhamento_delegacia'].sum()
taxa_dp_comum = (casos_dp_comum / total_casos) * 100 if total_casos > 0 else 0

# ─── KPIs ─────────────────────────────────────────────────────────────
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(render_metric("Total Ocorrências (SINAN)", f"{total_casos:,.0f}".replace(',','.')), unsafe_allow_html=True)
with c2:
    st.markdown(render_metric("Encaminhadas à DDM", f"{casos_ddm:,.0f}".replace(',','.'), f"{taxa_ddm:.1f}% (Base SINAN)"), unsafe_allow_html=True)
with c3:
    st.markdown(render_metric("Encaminhadas à DP Comum", f"{casos_dp_comum:,.0f}".replace(',','.'), f"{taxa_dp_comum:.1f}% (Base SINAN)", "down"), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─── Evidências Causalidade e Contexto ───────────────────────────────
st.markdown("""
<div class="insight-box">
    🚨 <strong>O que é uma DDM?</strong><br>
    Diferente de uma Delegacia de Polícia (DP) comum, as <strong>Delegacias de Defesa da Mulher (DDMs)</strong> 
    são especializadas em registrar ocorrências, investigar e apurar crimes de violência contra a mulher. 
    Elas oferecem atendimento humanizado, encaminhamento jurídico e para exames de corpo de delito no IML.
    <br><br>
    🎯 <strong>O Desafio do Acesso (Hipótese Causal)</strong>: O município de São Paulo possui <strong>apenas 9 DDMs territoriais</strong> 
    para cobrir toda a cidade. Antes de funcionarem 24 horas, a restrição de horário destas poucas unidades somada 
    à distância representava uma barreira institucional. A taxa geral de encaminhamento para a DDM a partir do sistema de saúde é 
    abaixo de 20%, o que indica que a restrição de acesso pode desestimular a denúncia formal.
</div>
""", unsafe_allow_html=True)

with st.expander("📍 Ver endereços e horários das 9 DDMs na capital"):
    st.markdown("""
    **• Centro**
    - **1ª DDM - Centro**: Rua Vieira Ravasco, 26, Cambuci - Dentro da Casa da Mulher Brasileira | 📞 (11) 3275-8000 | 🟢 **Atendimento 24h**
    
    **• Zona Leste**
    - **5ª DDM - Leste**: Rua Dr. Corinto Baldoíno Costa, 400 - 2º andar - Tatuapé | 📞 (11) 2293-3816 | 🕒 **Horário Comercial (09h às 18h)**
    - **7ª DDM - Leste**: Rua Sabbado D'Angelo, 46 - Itaquera | 📞 (11) 2071-3488 / 2071-4707 | 🟢 **Atendimento 24h**
    - **8ª DDM - Leste**: Avenida Osvaldo do Valle Cordeiro, 190 - 2º andar – Jd. Marília | 📞 (11) 2742-1701 | 🟢 **Atendimento 24h**
    
    **• Zona Oeste**
    - **3ª DDM - Oeste**: Avenida Corifeu de Azevedo Marques, 4300 - 2º andar – Jaguaré | 📞 (11) 3768-4664 | 🕒 **Horário Comercial (09h às 18h)**
    - **9ª DDM - Oeste**: Avenida Menotti Laudisio, 286 – 2º andar - Pirituba | 📞 (11) 3974-8890 | 🕒 **Horário Comercial (09h às 18h)**
    
    **• Zona Norte**
    - **4ª DDM - Norte**: Avenida Itaberaba, 731 - 1º andar – Freguesia do Ó | 📞 (11) 3976-2908 | 🕒 **Horário Comercial (09h às 18h)**
    
    **• Zona Sul**
    - **2ª DDM - Sul**: Avenida Onze de julho, 89 – Saúde | 📞 (11) 5084-2579 | 🕒 **Horário Comercial (09h às 18h)**
    - **6ª DDM - Sul**: Rua Sargento Manoel Barbosa da Silva, nº 115 - 2º andar – Campo Grande | 📞 (11) 5521-6068 / 5686-8567 | 🕒 **Horário Comercial (09h às 18h)**
    """)

st.markdown("<br>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

# ─── Gráfico 1: Evolução do Encaminhamento DDM ───────────────────────
with col1:
    st.markdown(section_header("📈 Evolução da Taxa de Encaminhamento DDM (Base 🏥 SINAN)"), unsafe_allow_html=True)
    
    evol_ddm = df_filt.groupby('ano').agg(
        total=('encaminhamento_delegacia_mulher', 'count'),
        ddm=('encaminhamento_delegacia_mulher', 'sum')
    ).reset_index()
    evol_ddm['taxa'] = (evol_ddm['ddm'] / evol_ddm['total']) * 100

    fig_evol = go.Figure()
    fig_evol.add_trace(go.Scatter(
        x=evol_ddm['ano'], y=evol_ddm['taxa'],
        mode='lines+markers+text',
        text=evol_ddm['taxa'].apply(lambda x: f"{x:.1f}%"),
        textposition='top center',
        line=dict(color=COLORS['primary'], width=3),
        marker=dict(size=10, color=COLORS['secondary']),
        name='% DDM'
    ))
    fig_evol.update_layout(title="Encaminhamentos para DDM (% do Total)", xaxis_title="Ano", yaxis_title="%")
    apply_theme(fig_evol, height=400, show_legend=False)
    st.plotly_chart(fig_evol, use_container_width=True)

# ─── Gráfico 2: DDM por Horário da Ocorrência ────────────────────────
with col2:
    st.markdown(section_header("⏰ Encaminhamento vs. Horário da Ocorrência (Base 🏥 SINAN)"), unsafe_allow_html=True)
    
    df_hora = df_filt[df_filt['hora'].notna()].copy()
    
    # Classificar horário
    def classifica_horario(h):
        if 8 <= h < 18: return 'Horário Comercial (08h-18h)'
        else: return 'Fora de Expediente (18h-08h)'
        
    df_hora['periodo'] = df_hora['hora'].apply(classifica_horario)
    
    hora_ddm = df_hora.groupby('periodo').agg(
        total=('encaminhamento_delegacia_mulher', 'count'),
        ddm=('encaminhamento_delegacia_mulher', 'sum')
    ).reset_index()
    hora_ddm['taxa'] = (hora_ddm['ddm'] / hora_ddm['total']) * 100
    
    fig_hora = go.Figure(data=[
        go.Bar(
            x=hora_ddm['periodo'], y=hora_ddm['taxa'],
            text=hora_ddm['taxa'].apply(lambda x: f"{x:.1f}%"),
            textposition='auto',
            marker_color=[COLORS['danger'], COLORS['success']]
        )
    ])
    fig_hora.update_layout(title="Taxa de Encaminhamento por Período", yaxis_title="% DDM")
    apply_theme(fig_hora, height=400, show_legend=False)
    st.plotly_chart(fig_hora, use_container_width=True)


