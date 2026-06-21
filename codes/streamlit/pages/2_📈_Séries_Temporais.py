"""
📈 Página 2 — Séries Temporais (Nacional)
Evolução anual de feminicídios e notificações em taxas por 100 mil habitantes,
com filtros por grupo, região e UF.
"""
import os
import sys

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from utils.data_loader import load_painel_deam, GRUPO_COLORS, REGIAO_COLORS
from utils.charts import apply_theme, COLORS, metric_card_css, render_metric, section_header

st.set_page_config(page_title="Séries Temporais | DEAM 24h", page_icon="📈", layout="wide")
st.markdown(metric_card_css(), unsafe_allow_html=True)

st.markdown("# 📈 Séries Temporais")
st.markdown("*Evolução anual das taxas de feminicídios e notificações por 100 mil habitantes — municípios com DEAM, 2009–2019*")
st.markdown("---")

painel = load_painel_deam()


def taxa_anual(df: pd.DataFrame, evento: str) -> pd.DataFrame:
    """Taxa /100k correta: soma de eventos / soma de população × 100k, por ano."""
    g = df.groupby('ano').agg(ev=(evento, 'sum'), pop=('populacao', 'sum')).reset_index()
    g['taxa'] = (g['ev'] / g['pop'] * 100_000).round(3)
    return g


# ─── Filtros ─────────────────────────────────────────────────────────
f1, f2, f3 = st.columns([2, 2, 3])
with f1:
    grupos_sel = st.multiselect("Grupo", ['24h', 'comercial'], default=['24h', 'comercial'],
                                format_func=lambda x: 'DEAM 24h (tratado)' if x == '24h' else 'DEAM comercial (controle)')
with f2:
    regioes = sorted(painel['regiao'].dropna().unique())
    reg_sel = st.multiselect("Região", regioes, default=regioes)
with f3:
    ufs_disp = sorted(painel[painel['regiao'].isin(reg_sel)]['uf'].dropna().unique())
    uf_sel = st.multiselect("UF (opcional)", ufs_disp, default=[])

df = painel[painel['grupo'].isin(grupos_sel) & painel['regiao'].isin(reg_sel)]
if uf_sel:
    df = df[df['uf'].isin(uf_sel)]

if df.empty:
    st.warning("Nenhum município corresponde aos filtros selecionados.")
    st.stop()


def br(n: float) -> str:
    return f"{n:,.0f}".replace(",", ".")


# ─── KPIs ─────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(render_metric("Municípios no recorte", br(df['id_municipio'].nunique())), unsafe_allow_html=True)
with c2:
    st.markdown(render_metric("Feminicídios", br(df['feminicidios'].sum()), "soma do período", "down"), unsafe_allow_html=True)
with c3:
    st.markdown(render_metric("Notificações", br(df['notificacoes'].sum()), "soma do período"), unsafe_allow_html=True)
tx_fem = df['feminicidios'].sum() / df['populacao'].sum() * 100_000 / 11
with c4:
    st.markdown(render_metric("Taxa fem. média", f"{tx_fem:.2f}", "/100k ao ano"), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─── Série por grupo: notificações e feminicídios ────────────────────
st.markdown(section_header("📊 Taxas por 100 mil — DEAM 24h vs Comercial"), unsafe_allow_html=True)
col_n, col_f = st.columns(2)

with col_n:
    fign = go.Figure()
    for g in grupos_sel:
        s = taxa_anual(df[df['grupo'] == g], 'notificacoes')
        nome = 'DEAM 24h' if g == '24h' else 'DEAM comercial'
        fign.add_trace(go.Scatter(x=s['ano'], y=s['taxa'], name=nome, mode='lines+markers',
                                  line=dict(color=GRUPO_COLORS[g], width=3), marker=dict(size=8),
                                  hovertemplate=f'<b>%{{x}}</b><br>{nome}: %{{y:.1f}}/100k<extra></extra>'))
    fign.update_layout(title="🏥 Notificações /100k — 24h vs comercial",
                       xaxis_title="Ano", yaxis_title="Notificações /100k")
    apply_theme(fign, height=400)
    st.plotly_chart(fign, use_container_width=True)

with col_f:
    figf = go.Figure()
    for g in grupos_sel:
        s = taxa_anual(df[df['grupo'] == g], 'feminicidios')
        nome = 'DEAM 24h' if g == '24h' else 'DEAM comercial'
        figf.add_trace(go.Scatter(x=s['ano'], y=s['taxa'], name=nome, mode='lines+markers',
                                  line=dict(color=GRUPO_COLORS[g], width=3), marker=dict(size=8),
                                  hovertemplate=f'<b>%{{x}}</b><br>{nome}: %{{y:.2f}}/100k<extra></extra>'))
    figf.update_layout(title="⚰️ Feminicídios /100k — 24h vs comercial",
                       xaxis_title="Ano", yaxis_title="Feminicídios /100k")
    apply_theme(figf, height=400)
    st.plotly_chart(figf, use_container_width=True)

# ─── Comparação por região ───────────────────────────────────────────
st.markdown(section_header("🗺️ Taxas por Região"), unsafe_allow_html=True)
metrica = st.radio("Indicador", ['notificacoes', 'feminicidios'], horizontal=True,
                   format_func=lambda x: 'Notificações /100k' if x == 'notificacoes' else 'Feminicídios /100k')

figr = go.Figure()
for reg in reg_sel:
    sub = df[df['regiao'] == reg]
    if sub.empty:
        continue
    s = taxa_anual(sub, metrica)
    figr.add_trace(go.Scatter(x=s['ano'], y=s['taxa'], name=reg, mode='lines+markers',
                              line=dict(color=REGIAO_COLORS.get(reg, COLORS['accent']), width=2.5),
                              marker=dict(size=7),
                              hovertemplate=f'<b>{reg}</b><br>%{{x}}: %{{y:.2f}}/100k<extra></extra>'))
unid = 'Notificações /100k' if metrica == 'notificacoes' else 'Feminicídios /100k'
figr.update_layout(title=f"{unid} por região", xaxis_title="Ano", yaxis_title=unid)
apply_theme(figr, height=440)
st.plotly_chart(figr, use_container_width=True)

st.caption("Taxas calculadas como total de eventos ÷ população total do recorte × 100.000 — média ponderada, não média simples das taxas municipais.")
