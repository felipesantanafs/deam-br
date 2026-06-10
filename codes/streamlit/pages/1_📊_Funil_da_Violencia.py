"""
📊 Página 1 — Funil da Violência
Cascata da violência: Ameaça → Lesão → Notificações → Feminicídios
"""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from utils.data_loader import load_funil, load_sinan_cnes, load_sim
from utils.charts import apply_theme, COLORS, PALETTE, metric_card_css, render_metric, section_header

st.set_page_config(page_title="Funil da Violência | DDM", page_icon="📊", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
</style>
""", unsafe_allow_html=True)
st.markdown(metric_card_css(), unsafe_allow_html=True)

st.markdown("# 📊 Funil da Violência")
st.markdown("*Análise consolidada da cascata: Ameaças e Violência Física (Base 🏥 SINAN) ➔ Feminicídios (Base ⚰️ SIM/DataSUS) — São Paulo, 2015–2019*")
st.markdown("---")

# ─── Carregar dados ──────────────────────────────────────────────────
funil = load_funil()

# ─── KPIs ─────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
with c1:
    total_notif = int(funil['total_notificacoes'].sum())
    st.markdown(render_metric("Total Notificações", f"{total_notif:,.0f}".replace(",", "."), "2015–2019"), unsafe_allow_html=True)
with c2:
    total_lesoes = int(funil['total_lesoes'].sum())
    st.markdown(render_metric("Violência Física", f"{total_lesoes:,.0f}".replace(",", "."), f"{total_lesoes/total_notif*100:.0f}% do total"), unsafe_allow_html=True)
with c3:
    total_ameacas = int(funil['total_ameacas'].sum())
    st.markdown(render_metric("Ameaças", f"{total_ameacas:,.0f}".replace(",", "."), f"{total_ameacas/total_notif*100:.0f}% do total"), unsafe_allow_html=True)
with c4:
    total_fem = int(funil['total_feminicidios'].sum())
    st.markdown(render_metric("Feminicídios", f"{total_fem}", "SIM/DataSUS", "down"), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─── Gráfico 1: Funil Temporal (Escala Log) ──────────────────────────
st.markdown(section_header("📈 Evolução Temporal do Funil"), unsafe_allow_html=True)

col_chart, col_table = st.columns([3, 1])

with col_chart:
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=funil['ano'], y=funil['total_notificacoes'],
        name='Notificações SINAN',
        mode='lines+markers',
        line=dict(color=COLORS['accent'], width=3),
        marker=dict(size=10, symbol='circle'),
        fill='tonexty' if False else None,
        hovertemplate='<b>%{x}</b><br>Notificações: %{y:,.0f}<extra></extra>',
    ))
    fig.add_trace(go.Scatter(
        x=funil['ano'], y=funil['total_lesoes'],
        name='Violência Física',
        mode='lines+markers',
        line=dict(color=COLORS['warning'], width=3),
        marker=dict(size=10, symbol='diamond'),
        hovertemplate='<b>%{x}</b><br>Violência Física: %{y:,.0f}<extra></extra>',
    ))
    fig.add_trace(go.Scatter(
        x=funil['ano'], y=funil['total_ameacas'],
        name='Ameaças',
        mode='lines+markers',
        line=dict(color=COLORS['highlight'], width=3),
        marker=dict(size=10, symbol='square'),
        hovertemplate='<b>%{x}</b><br>Ameaças: %{y:,.0f}<extra></extra>',
    ))
    fig.add_trace(go.Scatter(
        x=funil['ano'], y=funil['total_feminicidios'],
        name='Feminicídios (SIM)',
        mode='lines+markers',
        line=dict(color=COLORS['danger'], width=3, dash='dash'),
        marker=dict(size=12, symbol='x', line=dict(width=2)),
        hovertemplate='<b>%{x}</b><br>Feminicídios: %{y:,.0f}<extra></extra>',
    ))

    fig.update_layout(yaxis_type="log")
    fig.update_layout(
        title="Evolução do Funil da Violência (escala logarítmica)",
        xaxis_title="Ano",
        yaxis_title="Nº de Registros (log)",
    )
    apply_theme(fig, height=480)
    st.plotly_chart(fig, use_container_width=True)

with col_table:
    st.markdown("#### Dados")
    display_df = funil.copy()
    display_df.columns = ['Ano', 'Ameaças (SINAN)', 'V. Física (SINAN)', 'Notificações (SINAN)', 'Feminicídios (SIM)']
    display_df['Ano'] = display_df['Ano'].astype(int)
    for col in ['Ameaças (SINAN)', 'V. Física (SINAN)', 'Notificações (SINAN)']:
        display_df[col] = display_df[col].astype(int)
    st.dataframe(display_df, hide_index=True, use_container_width=True)

# ─── Gráfico 2: Variação Percentual YoY ──────────────────────────────
st.markdown(section_header("📊 Variação Percentual Ano-a-Ano"), unsafe_allow_html=True)

funil_pct = funil.copy()
for col in ['total_ameacas', 'total_lesoes', 'total_notificacoes', 'total_feminicidios']:
    funil_pct[f'{col}_pct'] = funil_pct[col].pct_change() * 100

funil_pct = funil_pct.dropna(subset=['total_ameacas_pct'])

fig2 = go.Figure()
configs = [
    ('total_notificacoes_pct', 'Notificações', COLORS['accent']),
    ('total_lesoes_pct', 'Violência Física', COLORS['warning']),
    ('total_ameacas_pct', 'Ameaças', COLORS['highlight']),
    ('total_feminicidios_pct', 'Feminicídios', COLORS['danger']),
]
for col, name, color in configs:
    fig2.add_trace(go.Bar(
        x=funil_pct['ano'].astype(int).astype(str),
        y=funil_pct[col],
        name=name,
        marker_color=color,
        hovertemplate=f'<b>{name}</b><br>Ano: %{{x}}<br>Variação: %{{y:+.1f}}%<extra></extra>',
        opacity=0.85,
    ))

fig2.update_layout(
    title="Variação Percentual Anual (%)",
    xaxis_title="Ano",
    yaxis_title="Variação (%)",
    barmode='group',
)
fig2.add_hline(y=0, line_dash="dash", line_color=COLORS['text_dim'], line_width=1)
apply_theme(fig2, height=420)
st.plotly_chart(fig2, use_container_width=True)

# ─── Insight ──────────────────────────────────────────────────────────
st.markdown("""
<div class="insight-box">
    💡 <strong>Leitura do Funil</strong>: O crescimento contínuo das notificações (+357% de 2015 a 2019)
    combinado com a queda dos feminicídios (−69%) é consistente com a hipótese de que
    o aumento de registros reflete <strong>redução da subnotificação</strong> (cifra oculta),
    não aumento real da violência. A ampliação do acesso institucional parece estar associada
    a uma maior proteção efetiva das vítimas.
    <br><br>
    ⚠️ <strong>Nota sobre a Variação YoY de 2016</strong>: O pico de variação percentual observado em 2016 
    (ex. +129% em notificações) decorre principalmente do <strong>acoplamento da geolocalização via CNES</strong> 
    e de uma expressiva melhora no fluxo de registro das notificações integradas a partir daquele ano. Trata-se, portanto, 
    de uma variação administrativa de aprimoramento dos cadastros (redução da subnotificação), e não de um aumento epidemiológico real na ocorrência de violências na cidade.
</div>
""", unsafe_allow_html=True)
