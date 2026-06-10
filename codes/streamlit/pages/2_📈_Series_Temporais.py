"""
📈 Página 2 — Séries Temporais Detalhadas
Evolução mensal e anual das notificações e feminicídios.
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from utils.data_loader import load_sinan_cnes, load_sim
from utils.charts import apply_theme, COLORS, PALETTE, PALETTE_WARM, metric_card_css, render_metric, section_header

st.set_page_config(page_title="Séries Temporais | DDM", page_icon="📈", layout="wide")
st.markdown(metric_card_css(), unsafe_allow_html=True)

st.markdown("# 📈 Séries Temporais Detalhadas")
st.markdown("*Evolução mensal e anual de notificações de violência e feminicídios*")
st.markdown("---")

# ─── Dados ────────────────────────────────────────────────────────────
df_sinan = load_sinan_cnes()
df_sim = load_sim()

# ─── Filtros ──────────────────────────────────────────────────────────
col_f1, col_f2 = st.columns(2)
with col_f1:
    anos_disp = sorted(df_sinan['ano'].dropna().unique())
    ano_range = st.slider("Período SINAN", min_value=int(min(anos_disp)), max_value=int(max(anos_disp)),
                          value=(2015, 2019), key="ts_ano")
with col_f2:
    tipo_violencia = st.multiselect("Tipo de Violência (Base 🏥 SINAN)", 
        ["Violência Física", "Ameaça", "Violência Psicológica", "Violência Sexual"],
        default=["Violência Física", "Ameaça", "Violência Psicológica", "Violência Sexual"])

df_filt = df_sinan[(df_sinan['ano'] >= ano_range[0]) & (df_sinan['ano'] <= ano_range[1])].copy()

# ─── KPIs ─────────────────────────────────────────────────────────────
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(render_metric("Total no Período", f"{len(df_filt):,.0f}".replace(",", "."), 
                              f"{ano_range[0]}–{ano_range[1]}"), unsafe_allow_html=True)
with c2:
    vf = df_filt['ocorreu_violencia_fisica'].sum()
    st.markdown(render_metric("Violência Física", f"{int(vf):,.0f}".replace(",", ".")), unsafe_allow_html=True)
with c3:
    am = df_filt['meio_ameaca'].sum()
    st.markdown(render_metric("Ameaças", f"{int(am):,.0f}".replace(",", ".")), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─── Gráfico: Série Mensal SINAN ─────────────────────────────────────
st.markdown(section_header("📅 Série Mensal de Notificações (SINAN)"), unsafe_allow_html=True)

# Agregar por mês (restringido estritamente ao período do filtro para evitar distorções de digitação de datas)
df_filt_valid = df_filt[
    df_filt['data_ocorrencia'].notna() &
    (df_filt['data_ocorrencia'] >= f"{ano_range[0]}-01-01") &
    (df_filt['data_ocorrencia'] <= f"{ano_range[1]}-12-31")
].copy()

monthly = df_filt_valid.set_index('data_ocorrencia').resample('ME').agg(
    total=('ano', 'count'),
    violencia_fisica=('ocorreu_violencia_fisica', 'sum'),
    ameaca=('meio_ameaca', 'sum'),
    violencia_psicologica=('ocorreu_violencia_psicologica', 'sum'),
    violencia_sexual=('ocorreu_violencia_sexual', 'sum'),
).reset_index()

fig1 = go.Figure()

mapping = {
    "Violência Física": ('violencia_fisica', COLORS['warning'], 'Violência Física'),
    "Ameaça": ('ameaca', COLORS['highlight'], 'Ameaça'),
    "Violência Psicológica": ('violencia_psicologica', COLORS['secondary'], 'Violência Psicológica'),
    "Violência Sexual": ('violencia_sexual', COLORS['danger'], 'Violência Sexual'),
}

# Sempre mostrar total
fig1.add_trace(go.Scatter(
    x=monthly['data_ocorrencia'], y=monthly['total'],
    name='Total Notificações (SINAN)',
    mode='lines',
    line=dict(color=COLORS['accent'], width=2.5),
    fill='tozeroy',
    fillcolor='rgba(93,173,226,0.15)',
    hovertemplate='<b>%{x|%b %Y}</b><br>Total: %{y:,.0f}<extra></extra>',
))

for tipo in tipo_violencia:
    if tipo in mapping:
        col, color, label = mapping[tipo]
        fig1.add_trace(go.Scatter(
            x=monthly['data_ocorrencia'], y=monthly[col],
            name=f"{label} (SINAN)",
            mode='lines',
            line=dict(color=color, width=2),
            hovertemplate=f'<b>%{{x|%b %Y}}</b><br>{label}: %{{y:,.0f}}<extra></extra>',
        ))

fig1.update_layout(title="Evolução Mensal das Notificações de Violência (Base 🏥 SINAN)", xaxis_title="Mês", yaxis_title="Nº de Registros")
apply_theme(fig1, height=450)
st.plotly_chart(fig1, use_container_width=True)

# ─── Gráfico: Feminicídios SIM (anual, com raça) ─────────────────────
st.markdown(section_header("⚰️ Feminicídios por Ano e Raça/Cor (SIM/DataSUS)"), unsafe_allow_html=True)

col_sim_l, col_sim_r = st.columns([3, 1])

with col_sim_l:
    sim_ano_raca = df_sim.groupby(['ano', 'raca_cor']).size().reset_index(name='total')
    sim_ano_raca = sim_ano_raca[sim_ano_raca['raca_cor'].notna()]
    
    raca_colors = {
        'Branca': COLORS['accent'],
        'Parda': COLORS['warning'],
        'Preta': COLORS['danger'],
        'Amarela': '#F1C40F',
        'Indígena': COLORS['success'],
    }
    
    fig2 = go.Figure()
    for raca in ['Branca', 'Parda', 'Preta', 'Amarela', 'Indígena']:
        subset = sim_ano_raca[sim_ano_raca['raca_cor'] == raca]
        if len(subset) > 0:
            fig2.add_trace(go.Bar(
                x=subset['ano'], y=subset['total'],
                name=raca,
                marker_color=raca_colors.get(raca, COLORS['text_dim']),
                hovertemplate=f'<b>{raca}</b><br>Ano: %{{x}}<br>Óbitos: %{{y}}<extra></extra>',
            ))
    
    fig2.update_layout(
        title="Feminicídios — Óbitos por Agressão contra Mulheres (SP Capital)",
        xaxis_title="Ano", yaxis_title="Nº de Óbitos",
        barmode='stack',
    )
    apply_theme(fig2, height=450)
    st.plotly_chart(fig2, use_container_width=True)

with col_sim_r:
    st.markdown("#### Resumo de Óbitos (⚰️ SIM)")
    sim_total = df_sim.groupby('ano').size().reset_index(name='Óbitos')
    sim_total.columns = ['Ano', 'Óbitos']
    st.dataframe(sim_total, hide_index=True, use_container_width=True)

# ─── Gráfico: Taxa de letalidade implícita ────────────────────────────
st.markdown(section_header("📉 Taxa de Letalidade Implícita"), unsafe_allow_html=True)

st.markdown("""
> A **taxa de letalidade implícita** é calculada como a razão entre feminicídios (SIM) e 
> notificações de violência física (SINAN) no mesmo ano. Uma queda indica que, proporcionalmente,
> menos casos de violência resultam em morte.
""")

# Calcular taxa
sinan_ano = df_sinan[df_sinan['ano'].between(2015, 2019)].groupby('ano').agg(
    vf=('ocorreu_violencia_fisica', 'sum')
).reset_index()
sim_ano = df_sim[df_sim['ano'].between(2015, 2019)].groupby('ano').size().reset_index(name='fem')

taxa = sinan_ano.merge(sim_ano, on='ano', how='inner')
taxa['taxa_letalidade'] = (taxa['fem'] / taxa['vf']) * 1000  # por mil

fig3 = go.Figure()
fig3.add_trace(go.Scatter(
    x=taxa['ano'], y=taxa['taxa_letalidade'],
    mode='lines+markers+text',
    text=[f"{v:.1f}‰" for v in taxa['taxa_letalidade']],
    textposition='top center',
    textfont=dict(color=COLORS['text'], size=13, family='Inter'),
    line=dict(color=COLORS['danger'], width=3),
    marker=dict(size=12, color=COLORS['danger'], line=dict(width=2, color=COLORS['text'])),
    hovertemplate='<b>%{x}</b><br>Taxa: %{y:.2f} por mil<extra></extra>',
    name='Taxa de Letalidade',
))

fig3.update_layout(
    title="Taxa de Letalidade (Feminicídios / Violência Física × 1.000)",
    xaxis_title="Ano", yaxis_title="Por mil notificações",
)
apply_theme(fig3, height=380, show_legend=False)
st.plotly_chart(fig3, use_container_width=True)

st.markdown("""
<div class="insight-box">
    💡 <strong>Interpretação</strong>: A taxa caiu de {:.1f}‰ em 2015 para {:.1f}‰ em 2019.
    Isso indica que a chance de um episódio de violência física resultar em feminicídio
    diminuiu consideravelmente no período, reforçando a hipótese de que a ampliação do acesso
    à rede de proteção (incluindo DDMs) contribui para salvar vidas.
</div>
""".format(taxa.iloc[0]['taxa_letalidade'], taxa.iloc[-1]['taxa_letalidade']), unsafe_allow_html=True)
