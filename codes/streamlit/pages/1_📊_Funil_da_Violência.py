"""
📊 Página 1 — Funil da Violência (Nacional)
Cascata: Notificações → tipos de violência → Feminicídios, nos municípios com DEAM.
"""
import os
import sys

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from utils.data_loader import load_painel_deam, serie_nacional_anual
from utils.charts import apply_theme, COLORS, metric_card_css, render_metric, section_header

st.set_page_config(page_title="Funil da Violência | DEAM 24h", page_icon="📊", layout="wide")
st.markdown(metric_card_css(), unsafe_allow_html=True)

st.markdown("# 📊 Funil da Violência contra a Mulher")
st.markdown("*Cascata da violência nos municípios com DEAM — Notificações (🏥 SINAN) ➔ tipos ➔ Feminicídios (⚰️ SIM) · Brasil, 2009–2019*")
st.markdown("---")

painel = load_painel_deam()
serie = serie_nacional_anual()


def br(n: float) -> str:
    return f"{n:,.0f}".replace(",", ".")


# ─── KPIs agregados do período ───────────────────────────────────────
tot_notif = int(painel['notificacoes'].sum())
tot_fisica = int(painel['viol_fisica'].sum())
tot_psico = int(painel['viol_psicologica'].sum())
tot_sexual = int(painel['viol_sexual'].sum())
tot_parceiro = int(painel['viol_parceiro'].sum())
tot_fem = int(painel['feminicidios'].sum())

c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    st.markdown(render_metric("Notificações", br(tot_notif), "Total SINAN"), unsafe_allow_html=True)
with c2:
    st.markdown(render_metric("Violência Física", br(tot_fisica), f"{tot_fisica/tot_notif*100:.0f}% das notif."), unsafe_allow_html=True)
with c3:
    st.markdown(render_metric("Por Parceiro Íntimo", br(tot_parceiro), f"{tot_parceiro/tot_notif*100:.0f}% das notif."), unsafe_allow_html=True)
with c4:
    st.markdown(render_metric("Violência Sexual", br(tot_sexual), f"{tot_sexual/tot_notif*100:.0f}% das notif."), unsafe_allow_html=True)
with c5:
    st.markdown(render_metric("Feminicídios", br(tot_fem), "SIM/DataSUS", "down"), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─── Funil agregado (barras horizontais legíveis) ────────────────────
st.markdown(section_header("🔻 Estrutura da Violência no Período (2009–2019)"), unsafe_allow_html=True)

etapas = ["Notificações (todas)", "Violência psicológica", "Violência física",
          "Por parceiro íntimo", "Violência sexual", "Feminicídios"]
valores = [tot_notif, tot_psico, tot_fisica, tot_parceiro, tot_sexual, tot_fem]
cores = [COLORS['accent'], COLORS['secondary'], COLORS['warning'],
         COLORS['highlight'], COLORS['primary'], COLORS['danger']]
pcts = [v / tot_notif * 100 for v in valores]
rotulos = [f"  {br(v)} ({p:.1f}%)" for v, p in zip(valores, pcts)]
razao = tot_notif / tot_fem if tot_fem else 0

col_bar, col_txt = st.columns([3, 2])
with col_bar:
    figb = go.Figure(go.Bar(
        x=valores[::-1], y=etapas[::-1], orientation='h',
        marker=dict(color=cores[::-1], line=dict(color=COLORS['bg_dark'], width=1)),
        text=rotulos[::-1], textposition='outside',
        textfont=dict(size=13, color=COLORS['text']),
        cliponaxis=False,
        hovertemplate='<b>%{y}</b><br>%{x:,.0f} registros<extra></extra>',
    ))
    figb.update_layout(title="Da notificação ao desfecho fatal (contagem 2009–2019)",
                       xaxis_title="Nº de registros", yaxis_title="")
    figb.update_xaxes(range=[0, tot_notif * 1.20])
    apply_theme(figb, height=460, show_legend=False)
    st.plotly_chart(figb, use_container_width=True)

with col_txt:
    st.markdown("##### 🧾 Resumo do Funil")
    resumo_df = pd.DataFrame({
        "Etapa": etapas,
        "Registros": [br(v) for v in valores],
        "% das notif.": [f"{p:.1f}%" for p in pcts],
    })
    st.dataframe(resumo_df, hide_index=True, use_container_width=True)

    st.markdown(f"""
    <div class="insight-box">
        📌 <strong>Interpretação imediata</strong>: para cada
        <strong>feminicídio</strong> há cerca de <strong>{razao:,.0f} notificações</strong>
        de violência registradas. Essa enorme distância entre o topo (acesso) e a base
        (letalidade) é o espaço em que a política atua: ampliar o registro tempestivo para
        interromper a escalada antes do óbito.
    </div>
    """.replace(",", "."), unsafe_allow_html=True)

    st.caption("As categorias de notificação não são mutuamente exclusivas (uma vítima pode "
               "sofrer mais de um tipo), por isso o objetivo é dimensionar cada tipo, não particioná-los.")

# ─── Evolução temporal do funil ──────────────────────────────────────
st.markdown(section_header("📈 Evolução Temporal do Funil"), unsafe_allow_html=True)

col_chart, col_table = st.columns([3, 1])
with col_chart:
    fig2 = go.Figure()
    confs = [
        ('notificacoes', 'Notificações', COLORS['accent'], 'circle'),
        ('viol_fisica', 'Violência Física', COLORS['warning'], 'diamond'),
        ('viol_parceiro', 'Por Parceiro', COLORS['highlight'], 'square'),
        ('feminicidios', 'Feminicídios', COLORS['danger'], 'x'),
    ]
    for col, name, color, sym in confs:
        fig2.add_trace(go.Scatter(
            x=serie['ano'], y=serie[col], name=name, mode='lines+markers',
            line=dict(color=color, width=3, dash='dash' if col == 'feminicidios' else None),
            marker=dict(size=9, symbol=sym),
            hovertemplate=f'<b>%{{x}}</b><br>{name}: %{{y:,.0f}}<extra></extra>',
        ))
    fig2.update_layout(title="Evolução do funil (escala logarítmica)",
                       xaxis_title="Ano", yaxis_title="Nº de registros (log)", yaxis_type="log")
    apply_theme(fig2, height=460)
    st.plotly_chart(fig2, use_container_width=True)

with col_table:
    st.markdown("#### Dados anuais")
    disp = serie[['ano', 'notificacoes', 'viol_fisica', 'feminicidios']].copy()
    disp.columns = ['Ano', 'Notif.', 'V. Física', 'Femin.']
    disp['Ano'] = disp['Ano'].astype(int)
    st.dataframe(disp, hide_index=True, use_container_width=True, height=430)

# ─── Composição por tipo (área empilhada) ────────────────────────────
st.markdown(section_header("🧩 Composição das Notificações por Tipo"), unsafe_allow_html=True)
tipos = [
    ('viol_fisica', 'Física', COLORS['warning']),
    ('viol_psicologica', 'Psicológica', COLORS['secondary']),
    ('viol_sexual', 'Sexual', COLORS['danger']),
    ('viol_parceiro', 'Por parceiro íntimo', COLORS['highlight']),
]
fig3 = go.Figure()
for col, name, color in tipos:
    fig3.add_trace(go.Scatter(
        x=serie['ano'], y=serie[col], name=name, mode='lines',
        stackgroup='one', line=dict(width=0.5, color=color),
        hovertemplate=f'<b>%{{x}}</b><br>{name}: %{{y:,.0f}}<extra></extra>',
    ))
fig3.update_layout(title="Tipos de violência notificada ao longo do tempo (contagens)",
                   xaxis_title="Ano", yaxis_title="Nº de notificações")
apply_theme(fig3, height=420)
st.plotly_chart(fig3, use_container_width=True)

st.markdown("""
<div class="insight-box">
    💡 <strong>Leitura do funil</strong>: o crescimento sustentado das notificações, com o
    feminicídio mantendo-se em patamar muito inferior, é consistente com a hipótese de que
    o aumento de registros reflete <strong>redução da subnotificação</strong> (cifra oculta),
    não aumento real da violência. As páginas <em>Tratado vs Controle</em> e
    <em>Modelo Causal</em> testam se a conversão para o plantão 24h acelera esse acesso e
    protege a vida.
</div>
""", unsafe_allow_html=True)
