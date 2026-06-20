"""
🏛️ Página 4 — Adoção das DEAMs 24h (Nacional)
A implantação escalonada (staggered adoption) das coortes de tratamento — base
do desenho de identificação Callaway & Sant'Anna.
"""
import os
import sys

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from utils.data_loader import load_painel_deam, referencia_municipios, REGIAO_COLORS
from utils.charts import apply_theme, COLORS, metric_card_css, render_metric, section_header

st.set_page_config(page_title="Adoção DEAMs 24h | DEAM 24h", page_icon="🏛️", layout="wide")
st.markdown(metric_card_css(), unsafe_allow_html=True)

st.markdown("# 🏛️ Adoção das DEAMs 24h")
st.markdown("*Implantação escalonada do regime de plantão 24h — coortes de tratamento, 2009–2019*")
st.markdown("---")

painel = load_painel_deam()
ref = referencia_municipios()
tratados = ref[ref['grupo'] == '24h'].copy()
tratados['coorte'] = tratados['coorte'].astype(int)


def br(n: float) -> str:
    return f"{n:,.0f}".replace(",", ".")


st.markdown("""
<div class="insight-box" style="margin-bottom:20px;">
    💡 <strong>Por que a adoção escalonada importa</strong>: as DEAMs não foram convertidas para
    24h todas no mesmo ano. Esse desenho de <em>staggered adoption</em> inviabiliza o DiD
    clássico (TWFE), que gera pesos negativos e viés (Goodman-Bacon, 2021). É exatamente por
    isso que o estudo adota o estimador de <strong>Callaway & Sant'Anna (2021)</strong>, que
    compara cada coorte ao grupo de controle adequado.
</div>
""", unsafe_allow_html=True)

# ─── KPIs ─────────────────────────────────────────────────────────────
coortes = tratados.groupby('coorte').size().reset_index(name='n')
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(render_metric("DEAMs 24h", br(len(tratados)), "municípios tratados"), unsafe_allow_html=True)
with c2:
    st.markdown(render_metric("Coortes", br(coortes['coorte'].nunique()), "anos de adoção"), unsafe_allow_html=True)
with c3:
    pico = coortes.sort_values('n', ascending=False).iloc[0]
    st.markdown(render_metric("Maior coorte", f"{int(pico['n'])}", f"em {int(pico['coorte'])}"), unsafe_allow_html=True)
with c4:
    st.markdown(render_metric("Período de adoção", f"{int(coortes['coorte'].min())}–{int(coortes['coorte'].max())}"), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─── Adoções por ano + acumulado ─────────────────────────────────────
st.markdown(section_header("📅 Linha do Tempo da Adoção"), unsafe_allow_html=True)
anos_full = pd.DataFrame({'coorte': range(2009, 2020)})
ca = anos_full.merge(coortes, on='coorte', how='left').fillna({'n': 0})
ca['acumulado'] = ca['n'].cumsum()

fig = go.Figure()
fig.add_trace(go.Bar(x=ca['coorte'], y=ca['n'], name='Novas DEAMs 24h',
                     marker_color=COLORS['secondary'],
                     hovertemplate='<b>%{x}</b><br>Novas: %{y}<extra></extra>'))
fig.add_trace(go.Scatter(x=ca['coorte'], y=ca['acumulado'], name='Acumulado',
                         mode='lines+markers', yaxis='y2',
                         line=dict(color=COLORS['warning'], width=3), marker=dict(size=8),
                         hovertemplate='<b>%{x}</b><br>Acumulado: %{y}<extra></extra>'))
fig.update_layout(
    title="Conversões para o regime 24h por ano",
    xaxis_title="Ano de adoção (coorte)", yaxis_title="Novas conversões",
    yaxis2=dict(title="Acumulado", overlaying='y', side='right', showgrid=False),
    legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
)
apply_theme(fig, height=420)
st.plotly_chart(fig, use_container_width=True)

# ─── Coortes por região + tabela ─────────────────────────────────────
col_a, col_b = st.columns([3, 2])
with col_a:
    st.markdown(section_header("🧭 Coortes por Região"), unsafe_allow_html=True)
    cr = tratados.groupby(['coorte', 'regiao']).size().reset_index(name='n')
    figr = px.bar(cr, x='coorte', y='n', color='regiao',
                  color_discrete_map=REGIAO_COLORS)
    figr.update_layout(title="Adoções por ano e região", xaxis_title="Ano de adoção",
                       yaxis_title="Nº de municípios", barmode='stack',
                       xaxis=dict(dtick=1))
    apply_theme(figr, height=400)
    st.plotly_chart(figr, use_container_width=True)

with col_b:
    st.markdown(section_header("📋 Municípios por Coorte"), unsafe_allow_html=True)
    tab = tratados.sort_values(['coorte', 'uf', 'municipio'])[['coorte', 'municipio', 'uf', 'regiao']].copy()
    tab.columns = ['Coorte', 'Município', 'UF', 'Região']
    tab['Coorte'] = tab['Coorte'].astype(int)
    st.dataframe(tab, hide_index=True, use_container_width=True, height=400)

# ─── Diagrama de exposição (swimmer) ─────────────────────────────────
st.markdown(section_header("🏊 Exposição ao Tratamento por Município"), unsafe_allow_html=True)
st.caption("Cada linha é um município tratado; o trecho destacado marca os anos sob regime 24h (ano ≥ coorte).")

sw = tratados.sort_values('coorte').reset_index(drop=True)
sw['rotulo'] = sw['municipio'] + ' (' + sw['uf'] + ')'
figs = go.Figure()
for i, row in sw.iterrows():
    figs.add_trace(go.Scatter(x=[2009, 2019], y=[i, i], mode='lines',
                              line=dict(color=COLORS['grid'], width=2), showlegend=False,
                              hoverinfo='skip'))
    figs.add_trace(go.Scatter(x=[row['coorte'], 2019], y=[i, i], mode='lines',
                              line=dict(color=REGIAO_COLORS.get(row['regiao'], COLORS['secondary']), width=5),
                              showlegend=False,
                              hovertemplate=f"<b>{row['rotulo']}</b><br>Adoção: {int(row['coorte'])}<extra></extra>"))
    figs.add_trace(go.Scatter(x=[row['coorte']], y=[i], mode='markers',
                              marker=dict(color=COLORS['text'], size=7, symbol='diamond'),
                              showlegend=False, hoverinfo='skip'))
figs.update_layout(
    title="Janela de exposição ao plantão 24h",
    xaxis=dict(title="Ano", dtick=1, range=[2008.5, 2019.5]),
    yaxis=dict(title="", tickmode='array', tickvals=list(range(len(sw))),
               ticktext=sw['rotulo'], tickfont=dict(size=9)),
)
apply_theme(figs, height=max(500, len(sw) * 16), show_legend=False)
st.plotly_chart(figs, use_container_width=True)
