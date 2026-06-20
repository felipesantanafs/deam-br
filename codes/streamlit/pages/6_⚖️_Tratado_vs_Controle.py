"""
⚖️ Página 6 — Tratado vs Controle (Nacional)
Comparação descritiva entre DEAMs 24h e DEAMs comerciais: tendências brutas,
alinhamento em tempo-de-evento e o gap entre grupos — leitura visual das
tendências paralelas que fundamentam o DiD.
"""
import os
import sys

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from utils.data_loader import load_painel_deam, GRUPO_COLORS
from utils.charts import apply_theme, COLORS, metric_card_css, render_metric, section_header

st.set_page_config(page_title="Tratado vs Controle | DEAM 24h", page_icon="⚖️", layout="wide")
st.markdown(metric_card_css(), unsafe_allow_html=True)

st.markdown("# ⚖️ Tratado vs Controle")
st.markdown("*Comparação descritiva entre DEAMs 24h (tratadas) e DEAMs comerciais (controle) — antessala da inferência causal*")
st.markdown("---")

painel = load_painel_deam()

OUTCOMES = {
    'taxa_notificacoes': ('Notificações /100k', 'notificacoes'),
    'taxa_feminicidios': ('Feminicídios /100k', 'feminicidios'),
}


def taxa_por(df, by, evento):
    g = df.groupby(by).agg(ev=(evento, 'sum'), pop=('populacao', 'sum')).reset_index()
    g['taxa'] = g['ev'] / g['pop'] * 100_000
    return g


# ─── Controle de outcome ─────────────────────────────────────────────
oc = st.radio("Indicador", list(OUTCOMES.keys()), horizontal=True,
              format_func=lambda x: OUTCOMES[x][0])
label, evento = OUTCOMES[oc]

# ─── KPIs comparativos ───────────────────────────────────────────────
def media_taxa(grupo):
    sub = painel[painel['grupo'] == grupo]
    return sub[evento].sum() / sub['populacao'].sum() * 100_000 / 11

t24, tco = media_taxa('24h'), media_taxa('comercial')
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(render_metric("DEAMs 24h", f"{painel[painel.grupo=='24h'].id_municipio.nunique()}", "tratados"), unsafe_allow_html=True)
with c2:
    st.markdown(render_metric("DEAMs comerciais", f"{painel[painel.grupo=='comercial'].id_municipio.nunique()}", "controle"), unsafe_allow_html=True)
with c3:
    st.markdown(render_metric(f"Taxa 24h", f"{t24:.2f}", f"{label} /ano"), unsafe_allow_html=True)
with c4:
    st.markdown(render_metric(f"Taxa comercial", f"{tco:.2f}", f"{label} /ano"), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─── Tendências brutas (calendário) ──────────────────────────────────
st.markdown(section_header("📈 Tendências Brutas por Ano-Calendário"), unsafe_allow_html=True)
col_g, col_d = st.columns([3, 2])
with col_g:
    fig = go.Figure()
    for g in ['24h', 'comercial']:
        s = taxa_por(painel[painel['grupo'] == g], 'ano', evento)
        nome = 'DEAM 24h (tratado)' if g == '24h' else 'DEAM comercial (controle)'
        fig.add_trace(go.Scatter(x=s['ano'], y=s['taxa'], name=nome, mode='lines+markers',
                                 line=dict(color=GRUPO_COLORS[g], width=3), marker=dict(size=8),
                                 hovertemplate=f'<b>%{{x}}</b><br>{nome}: %{{y:.2f}}<extra></extra>'))
    fig.update_layout(title=f"{label} — média ponderada por grupo",
                      xaxis_title="Ano", yaxis_title=label)
    apply_theme(fig, height=440)
    st.plotly_chart(fig, use_container_width=True)
with col_d:
    st.markdown("""
    A comparação por ano-calendário mistura coortes que adotaram o plantão em momentos
    diferentes. Por isso, o gráfico de **tempo-de-evento** ao lado é mais informativo: ele
    realinha cada município no **ano de sua própria adoção** (ano 0), permitindo observar o
    comportamento **antes** e **depois** da conversão.

    Linhas pré-tratamento aproximadamente paralelas dão suporte visual à hipótese de
    **tendências paralelas** — condição-chave do DiD. A validação formal está na página
    *Modelo Causal*.
    """)

# ─── Tempo de evento ─────────────────────────────────────────────────
st.markdown(section_header("🎯 Alinhamento em Tempo-de-Evento (ano 0 = adoção)"), unsafe_allow_html=True)

tr = painel[painel['grupo'] == '24h'].copy()
tr['rel'] = tr['ano'] - tr['coorte']
ev_tr = taxa_por(tr, 'rel', evento)
ev_tr = ev_tr[ev_tr['rel'].between(-8, 8)]

# controle: sem coorte; usa nível médio como banda de referência
ctrl_lvl = painel[painel['grupo'] == 'comercial'][evento].sum() / \
    painel[painel['grupo'] == 'comercial']['populacao'].sum() * 100_000

fige = go.Figure()
fige.add_vrect(x0=-0.5, x1=8.5, fillcolor=COLORS['secondary'], opacity=0.07, line_width=0,
               annotation_text="Pós-adoção", annotation_position="top right",
               annotation_font_color=COLORS['text_dim'])
fige.add_vline(x=0, line_dash="dash", line_color=COLORS['warning'], line_width=2,
               annotation_text="Adoção 24h", annotation_position="top")
fige.add_hline(y=ctrl_lvl, line_dash="dot", line_color=GRUPO_COLORS['comercial'],
               annotation_text="Nível médio controle", annotation_position="bottom left",
               annotation_font_color=COLORS['text_dim'])
fige.add_trace(go.Scatter(x=ev_tr['rel'], y=ev_tr['taxa'], name='DEAM 24h (tratado)',
                          mode='lines+markers',
                          line=dict(color=GRUPO_COLORS['24h'], width=3), marker=dict(size=9),
                          hovertemplate='Ano relativo %{x}<br>%{y:.2f}<extra></extra>'))
fige.update_layout(title=f"{label} das DEAMs 24h em torno do ano de adoção",
                   xaxis=dict(title="Anos desde a adoção", dtick=2), yaxis_title=label)
apply_theme(fige, height=440)
st.plotly_chart(fige, use_container_width=True)

# ─── Gap entre grupos ────────────────────────────────────────────────
st.markdown(section_header("📐 Diferença entre Grupos (24h − Comercial)"), unsafe_allow_html=True)
s24 = taxa_por(painel[painel['grupo'] == '24h'], 'ano', evento).rename(columns={'taxa': 't24'})
sco = taxa_por(painel[painel['grupo'] == 'comercial'], 'ano', evento).rename(columns={'taxa': 'tco'})
gap = s24[['ano', 't24']].merge(sco[['ano', 'tco']], on='ano')
gap['gap'] = gap['t24'] - gap['tco']
figg = go.Figure(go.Bar(x=gap['ano'], y=gap['gap'],
                        marker_color=[COLORS['secondary'] if v >= 0 else COLORS['danger'] for v in gap['gap']],
                        hovertemplate='<b>%{x}</b><br>Gap: %{y:+.2f}<extra></extra>'))
figg.add_hline(y=0, line_color=COLORS['text_dim'])
figg.update_layout(title=f"Gap de {label}: tratados − controle", xaxis_title="Ano",
                   yaxis_title="Diferença (/100k)")
apply_theme(figg, height=380, show_legend=False)
st.plotly_chart(figg, use_container_width=True)

st.caption("Comparações descritivas (médias ponderadas por população). A estimativa causal "
           "ajustada — que isola o efeito do plantão 24h da dinâmica comum — está na página Modelo Causal.")
