"""
⏰ Página 6 — Sazonalidade e Horários
Análise temporal que sustenta a hipótese DDM 24h.
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from utils.data_loader import load_sinan_cnes
from utils.charts import apply_theme, COLORS, PALETTE, metric_card_css, render_metric, section_header

st.set_page_config(page_title="Sazonalidade | DDM", page_icon="⏰", layout="wide")
st.markdown(metric_card_css(), unsafe_allow_html=True)

st.markdown("# ⏰ Sazonalidade e Horários")
st.markdown("*Quando a violência acontece? — Evidência para a hipótese do funcionamento 24h*")
st.markdown("---")

# ─── Dados ────────────────────────────────────────────────────────────
df_sinan = load_sinan_cnes()

ano_range = st.slider("Período SINAN", 2015, 2019, (2015, 2019), key="saz_ano")
df_filt = df_sinan[
    (df_sinan['ano'] >= ano_range[0]) & (df_sinan['ano'] <= ano_range[1]) &
    (df_sinan['hora'].notna())
].copy()

# ─── Cálculos ─────────────────────────────────────────────────────────
total_com_hora = len(df_filt)
fora_horario = df_filt[(df_filt['hora'] < 8) | (df_filt['hora'] >= 18)]
pct_fora = len(fora_horario) / total_com_hora * 100 if total_com_hora > 0 else 0
madrugada = df_filt[(df_filt['hora'] >= 0) & (df_filt['hora'] < 6)]
pct_madrugada = len(madrugada) / total_com_hora * 100 if total_com_hora > 0 else 0
noturno = df_filt[(df_filt['hora'] >= 18) | (df_filt['hora'] < 6)]
pct_noturno = len(noturno) / total_com_hora * 100 if total_com_hora > 0 else 0

# ─── KPIs ─────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(render_metric("Total com Hora", f"{total_com_hora:,.0f}".replace(",", "."),
                              f"de {len(df_sinan[(df_sinan['ano']>=ano_range[0])&(df_sinan['ano']<=ano_range[1])]):,} total"), unsafe_allow_html=True)
with c2:
    st.markdown(render_metric("Fora do Horário Comercial", f"{pct_fora:.1f}%",
                              "18h–8h", "up"), unsafe_allow_html=True)
with c3:
    st.markdown(render_metric("Período Noturno", f"{pct_noturno:.1f}%",
                              "18h–6h"), unsafe_allow_html=True)
with c4:
    st.markdown(render_metric("Madrugada", f"{pct_madrugada:.1f}%",
                              "0h–6h"), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─── Destaque ─────────────────────────────────────────────────────────
st.markdown(f"""
<div class="insight-box">
    🎯 <strong>Evidência Central</strong>: <strong>{pct_fora:.1f}%</strong> das ocorrências com horário registrado
    aconteceram <strong>fora do horário comercial</strong> (18h–8h). Isso significa que uma DDM que funciona
    apenas em horário comercial não está disponível para atender quase metade dos casos de violência.
    Este dado sustenta diretamente a hipótese de impacto diferencial das DDMs 24h.
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─── Gráfico 1: Distribuição Horária SINAN ───────────────────────────
st.markdown(section_header("🕐 Distribuição Horária das Ocorrências (SINAN)"), unsafe_allow_html=True)

col_chart, col_summary = st.columns([3, 1])

with col_chart:
    hora_counts = df_filt.groupby('hora').size().reset_index(name='total')
    hora_counts = hora_counts.sort_values('hora')

    # Criar cores: vermelho para fora do horário comercial, azul para dentro
    bar_colors = []
    for h in hora_counts['hora']:
        if h < 8 or h >= 18:
            bar_colors.append(COLORS['danger'])
        else:
            bar_colors.append(COLORS['secondary'])

    fig1 = go.Figure()
    fig1.add_trace(go.Bar(
        x=hora_counts['hora'],
        y=hora_counts['total'],
        marker_color=bar_colors,
        hovertemplate='<b>%{x}h</b><br>Ocorrências: %{y:,.0f}<extra></extra>',
    ))

    # Faixas de horário comercial
    fig1.add_vrect(x0=-0.5, x1=7.5, fillcolor=COLORS['danger'], opacity=0.08, line_width=0,
                   annotation_text="Fora do expediente", annotation_position="top left",
                   annotation_font=dict(color=COLORS['danger'], size=11))
    fig1.add_vrect(x0=17.5, x1=23.5, fillcolor=COLORS['danger'], opacity=0.08, line_width=0,
                   annotation_text="Fora do expediente", annotation_position="top right",
                   annotation_font=dict(color=COLORS['danger'], size=11))
    fig1.add_vrect(x0=7.5, x1=17.5, fillcolor=COLORS['success'], opacity=0.05, line_width=0,
                   annotation_text="Horário Comercial", annotation_position="top",
                   annotation_font=dict(color=COLORS['success'], size=11))

    fig1.update_layout(
        title="Distribuição Horária — Notificações de Violência",
        xaxis_title="Hora do Dia",
        yaxis_title="Nº de Ocorrências",
        xaxis=dict(tickmode='linear', dtick=1),
    )
    apply_theme(fig1, height=450, show_legend=False)
    st.plotly_chart(fig1, use_container_width=True)

with col_summary:
    st.markdown("#### Resumo Horário")
    st.markdown(f"""
    | Faixa | % |
    |-------|---|
    | 🌙 Madrugada (0h–6h) | **{pct_madrugada:.1f}%** |
    | 🌅 Manhã (6h–12h) | **{(len(df_filt[(df_filt['hora']>=6)&(df_filt['hora']<12)])/total_com_hora*100):.1f}%** |
    | ☀️ Tarde (12h–18h) | **{(len(df_filt[(df_filt['hora']>=12)&(df_filt['hora']<18)])/total_com_hora*100):.1f}%** |
    | 🌃 Noite (18h–0h) | **{(len(df_filt[(df_filt['hora']>=18)])/total_com_hora*100):.1f}%** |

    ---

    🔴 Fora do horário comercial: **{pct_fora:.1f}%**

    🟢 Dentro do horário comercial: **{100-pct_fora:.1f}%**
    """)

# ─── Gráfico 2: Heatmap Hora x Mês ──────────────────────────────────
st.markdown(section_header("📅 Heatmap: Hora × Mês"), unsafe_allow_html=True)

df_hm = df_filt.copy()
df_hm['mes_nome'] = df_hm['data_ocorrencia'].dt.month_name()
df_hm['mes_num'] = df_hm['data_ocorrencia'].dt.month

heat_data = df_hm.groupby(['hora', 'mes_num']).size().reset_index(name='total')
heat_pivot = heat_data.pivot(index='hora', columns='mes_num', values='total').fillna(0)
heat_pivot = heat_pivot.reindex(index=range(0, 24)).fillna(0)

meses_nomes = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
cols_existentes = [c for c in range(1, 13) if c in heat_pivot.columns]
heat_pivot = heat_pivot[cols_existentes]

fig2 = go.Figure(data=go.Heatmap(
    z=heat_pivot.values,
    x=[meses_nomes[c-1] for c in cols_existentes],
    y=[f"{h:02d}h" for h in heat_pivot.index],
    colorscale=[
        [0, COLORS['bg_dark']],
        [0.25, COLORS['primary']],
        [0.5, COLORS['secondary']],
        [0.75, COLORS['warning']],
        [1.0, COLORS['danger']],
    ],
    hovertemplate='<b>%{y}</b> — %{x}<br>Ocorrências: %{z:,.0f}<extra></extra>',
))
fig2.update_layout(
    title="Concentração de Ocorrências por Hora e Mês",
    xaxis_title="Mês", yaxis_title="Hora do Dia",
    yaxis=dict(autorange="reversed"),
)
apply_theme(fig2, height=550, show_legend=False)
st.plotly_chart(fig2, use_container_width=True)
# ─── Gráfico 4: Sazonalidade Mensal ──────────────────────────────────
st.markdown(section_header("📆 Sazonalidade Mensal"), unsafe_allow_html=True)

df_mes = df_sinan[(df_sinan['ano'] >= ano_range[0]) & (df_sinan['ano'] <= ano_range[1])]
mes_counts = df_mes.groupby('mes').size().reset_index(name='total')
mes_counts = mes_counts.sort_values('mes')
mes_counts['mes_nome'] = mes_counts['mes'].map(dict(enumerate(meses_nomes, 1)))

fig4 = go.Figure()
fig4.add_trace(go.Scatter(
    x=mes_counts['mes_nome'], y=mes_counts['total'],
    mode='lines+markers',
    line=dict(color=COLORS['accent'], width=3),
    marker=dict(size=10),
    fill='tozeroy',
    fillcolor='rgba(93,173,226,0.15)',
    hovertemplate='<b>%{x}</b><br>Notificações: %{y:,.0f}<extra></extra>',
))
fig4.update_layout(
    title="Volume de Notificações por Mês (agregado todos os anos)",
    xaxis_title="Mês", yaxis_title="Nº de Notificações",
)
apply_theme(fig4, height=380, show_legend=False)
st.plotly_chart(fig4, use_container_width=True)
