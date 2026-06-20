"""
📊 Página 1 — Funil da Violência (Nacional)
Cascata: Notificações → tipos de violência → Feminicídios, nos municípios com DEAM.
"""
import os
import sys

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

# ─── Funil agregado (cascata) ────────────────────────────────────────
st.markdown(section_header("🔻 Funil Agregado do Período (2009–2019)"), unsafe_allow_html=True)

col_funil, col_txt = st.columns([3, 2])
with col_funil:
    etapas = ["Notificações (todas)", "Violência psicológica", "Violência física",
              "Por parceiro íntimo", "Violência sexual", "Feminicídios"]
    valores = [tot_notif, tot_psico, tot_fisica, tot_parceiro, tot_sexual, tot_fem]
    fig = go.Figure(go.Funnel(
        y=etapas, x=valores,
        textposition="inside",
        textinfo="value+percent initial",
        marker=dict(color=[COLORS['accent'], COLORS['secondary'], COLORS['warning'],
                           COLORS['highlight'], COLORS['primary'], COLORS['danger']]),
        connector=dict(line=dict(color=COLORS['grid'], width=1)),
    ))
    fig.update_layout(title="Da notificação ao desfecho fatal")
    apply_theme(fig, height=460, show_legend=False)
    st.plotly_chart(fig, use_container_width=True)

with col_txt:
    st.markdown("""
    O funil mostra a **estrutura da violência registrada** nos municípios com DEAM.
    As categorias de notificação **não são mutuamente exclusivas** (uma mesma vítima
    pode sofrer violência física e psicológica), por isso somam mais que o total em
    alguns recortes — o objetivo é dimensionar cada tipo, não particioná-los.

    O **feminicídio** (SIM) é o desfecho extremo e raro: para cada óbito há centenas
    de notificações. É justamente nessa distância que opera a hipótese do estudo —
    ampliar o acesso (topo do funil) para interromper a escalada antes do óbito (base).
    """)
    razao = tot_notif / tot_fem if tot_fem else 0
    st.markdown(f"""
    <div class="insight-box">
        📌 Razão <strong>notificações : feminicídios</strong> ≈
        <strong>{razao:,.0f} : 1</strong>.
    </div>
    """.replace(",", "."), unsafe_allow_html=True)

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
