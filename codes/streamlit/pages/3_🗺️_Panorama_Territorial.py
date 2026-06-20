"""
🗺️ Página 3 — Panorama Territorial (Nacional)
Distribuição geográfica da violência e da rede de DEAMs: mapa por UF,
composição por região e ranking de municípios.
"""
import os
import sys

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from utils.data_loader import (
    load_painel_deam, load_geojson_uf, referencia_municipios, REGIAO_COLORS,
)
from utils.charts import apply_theme, COLORS, metric_card_css, render_metric, section_header

st.set_page_config(page_title="Panorama Territorial | DEAM 24h", page_icon="🗺️", layout="wide")
st.markdown(metric_card_css(), unsafe_allow_html=True)

st.markdown("# 🗺️ Panorama Territorial")
st.markdown("*Distribuição geográfica da violência e da rede de DEAMs nos municípios do estudo — Brasil, 2009–2019*")
st.markdown("---")

painel = load_painel_deam()
ref = referencia_municipios()
geo = load_geojson_uf()


def br(n: float) -> str:
    return f"{n:,.0f}".replace(",", ".")


# ─── Agregação por UF ────────────────────────────────────────────────
def agg_uf(df: pd.DataFrame) -> pd.DataFrame:
    g = df.groupby('uf').agg(
        feminicidios=('feminicidios', 'sum'),
        notificacoes=('notificacoes', 'sum'),
        pop=('populacao', 'sum'),
        municipios=('id_municipio', 'nunique'),
    ).reset_index()
    # população é somada ao longo de 11 anos -> taxa anual média
    g['taxa_fem'] = (g['feminicidios'] / g['pop'] * 100_000).round(3)
    g['taxa_notif'] = (g['notificacoes'] / g['pop'] * 100_000).round(2)
    deams = ref.groupby('uf').agg(
        deam_24h=('grupo', lambda s: (s == '24h').sum()),
        deam_com=('grupo', lambda s: (s == 'comercial').sum()),
    ).reset_index()
    return g.merge(deams, on='uf', how='left')


uf_df = agg_uf(painel)

# ─── KPIs ─────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(render_metric("UFs cobertas", br(uf_df['uf'].nunique())), unsafe_allow_html=True)
with c2:
    top_fem = uf_df.sort_values('taxa_fem', ascending=False).iloc[0]
    st.markdown(render_metric("Maior taxa fem.", f"{top_fem['taxa_fem']:.2f}", f"{top_fem['uf']} /100k", "up"), unsafe_allow_html=True)
with c3:
    top_notif = uf_df.sort_values('taxa_notif', ascending=False).iloc[0]
    st.markdown(render_metric("Maior taxa notif.", f"{top_notif['taxa_notif']:.0f}", f"{top_notif['uf']} /100k"), unsafe_allow_html=True)
with c4:
    st.markdown(render_metric("Municípios", br(ref['id_municipio'].nunique()), "no estudo"), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─── Mapa coroplético ────────────────────────────────────────────────
st.markdown(section_header("🗺️ Mapa por Unidade da Federação"), unsafe_allow_html=True)

metrica = st.radio(
    "Indicador no mapa", ['taxa_fem', 'taxa_notif', 'deam_24h'], horizontal=True,
    format_func=lambda x: {'taxa_fem': 'Feminicídios /100k', 'taxa_notif': 'Notificações /100k',
                           'deam_24h': 'Nº de DEAMs 24h'}[x])

if geo is not None:
    labels = {'taxa_fem': 'Feminicídios /100k', 'taxa_notif': 'Notificações /100k', 'deam_24h': 'DEAMs 24h'}
    cscale = 'Reds' if metrica == 'taxa_fem' else ('Blues' if metrica == 'taxa_notif' else 'Teal')
    figm = px.choropleth(
        uf_df, geojson=geo, locations='uf', featureidkey='properties.sigla',
        color=metrica, color_continuous_scale=cscale,
        hover_name='uf',
        hover_data={'taxa_fem': ':.2f', 'taxa_notif': ':.1f', 'deam_24h': True,
                    'municipios': True, metrica: False},
        labels=labels,
    )
    figm.update_geos(fitbounds="locations", visible=False)
    figm.update_layout(
        height=560, margin=dict(l=0, r=0, t=10, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        geo=dict(bgcolor="rgba(0,0,0,0)"),
        coloraxis_colorbar=dict(title=labels[metrica].split(' /')[0]),
        font=dict(color=COLORS['text']),
    )
    st.plotly_chart(figm, use_container_width=True)
else:
    st.info("GeoJSON das UFs não encontrado em assets/brasil_uf.geojson — exibindo apenas o ranking abaixo.")

# ─── Composição por região (treemap) e ranking de UF ─────────────────
col_tree, col_rank = st.columns([3, 2])
with col_tree:
    st.markdown(section_header("🧭 Composição por Região e UF"), unsafe_allow_html=True)
    reg_uf = painel.groupby(['regiao', 'uf']).agg(notificacoes=('notificacoes', 'sum')).reset_index()
    figt = px.treemap(
        reg_uf, path=[px.Constant("Brasil"), 'regiao', 'uf'], values='notificacoes',
        color='regiao', color_discrete_map={**REGIAO_COLORS, '(?)': COLORS['grid']},
    )
    figt.update_traces(root_color="rgba(17,34,64,0.6)",
                       hovertemplate='<b>%{label}</b><br>Notificações: %{value:,.0f}<extra></extra>')
    figt.update_layout(height=440, margin=dict(l=0, r=0, t=10, b=0),
                       paper_bgcolor="rgba(0,0,0,0)", font=dict(color=COLORS['text']))
    st.plotly_chart(figt, use_container_width=True)

with col_rank:
    st.markdown(section_header("📋 Ranking de UFs"), unsafe_allow_html=True)
    rk = uf_df.sort_values(metrica, ascending=False)[
        ['uf', 'taxa_fem', 'taxa_notif', 'deam_24h', 'municipios']].copy()
    rk.columns = ['UF', 'Fem./100k', 'Notif./100k', 'DEAMs 24h', 'Municípios']
    st.dataframe(rk, hide_index=True, use_container_width=True, height=440)

# ─── Ranking de municípios ───────────────────────────────────────────
st.markdown(section_header("🏙️ Ranking de Municípios"), unsafe_allow_html=True)
col_ctrl, col_tab = st.columns([1, 3])
with col_ctrl:
    ind = st.selectbox("Ordenar por", ['taxa_feminicidios', 'taxa_notificacoes'],
                       format_func=lambda x: 'Feminicídios /100k' if 'fem' in x else 'Notificações /100k')
    grupo_f = st.selectbox("Grupo", ['Todos', '24h', 'comercial'])
    topn = st.slider("Top N", 5, 30, 15)

mun = painel.groupby(['municipio', 'uf', 'grupo']).agg(
    fem=('feminicidios', 'sum'), notif=('notificacoes', 'sum'), pop=('populacao', 'sum'),
).reset_index()
mun['taxa_feminicidios'] = (mun['fem'] / mun['pop'] * 100_000).round(2)
mun['taxa_notificacoes'] = (mun['notif'] / mun['pop'] * 100_000).round(1)
if grupo_f != 'Todos':
    mun = mun[mun['grupo'] == grupo_f]
mun = mun.sort_values(ind, ascending=False).head(topn)

with col_tab:
    figb = go.Figure(go.Bar(
        x=mun[ind][::-1], y=(mun['municipio'] + ' (' + mun['uf'] + ')')[::-1],
        orientation='h',
        marker=dict(color=mun[ind][::-1], colorscale='Reds' if 'fem' in ind else 'Blues'),
        hovertemplate='<b>%{y}</b><br>%{x:.2f}/100k<extra></extra>',
    ))
    unid = 'Feminicídios /100k' if 'fem' in ind else 'Notificações /100k'
    figb.update_layout(title=f"Top {topn} municípios — {unid}", xaxis_title=unid)
    apply_theme(figb, height=max(380, topn * 24), show_legend=False)
    st.plotly_chart(figb, use_container_width=True)

st.caption("Taxas /100k = total de eventos no período ÷ população acumulada × 100.000. Municípios pequenos podem exibir taxas voláteis.")
