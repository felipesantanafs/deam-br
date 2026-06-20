"""
⏰ Página 5 — Sazonalidade & Horário (Nacional)
Distribuição temporal das notificações (hora do dia, dia da semana, mês),
testando o mecanismo central: o plantão 24h capta violência fora do horário comercial?
"""
import os
import sys

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from utils.data_loader import (
    load_saz_hora, load_saz_mes, load_saz_dow, load_saz_resumo,
    MESES, DIAS_SEMANA, PERIODO_COLORS,
)
from utils.charts import apply_theme, COLORS, metric_card_css, render_metric, section_header

st.set_page_config(page_title="Sazonalidade & Horário | DEAM 24h", page_icon="⏰", layout="wide")
st.markdown(metric_card_css(), unsafe_allow_html=True)

st.markdown("# ⏰ Sazonalidade & Horário")
st.markdown("*Quando ocorre a violência notificada? Hora do dia, dia da semana e mês — o mecanismo do plantão 24h*")
st.markdown("---")

hora = load_saz_hora()
mes = load_saz_mes()
dow = load_saz_dow()
resumo = load_saz_resumo()

ORDEM = ['Antes 24h', 'Depois 24h', 'Comercial']
ROTULO = {'Antes 24h': 'DEAM 24h — antes da conversão',
          'Depois 24h': 'DEAM 24h — depois da conversão',
          'Comercial': 'DEAM comercial (controle)'}


def br(n: float) -> str:
    return f"{n:,.0f}".replace(",", ".")


st.markdown("""
<div class="insight-box" style="margin-bottom:20px;">
    💡 <strong>A hipótese do mecanismo</strong>: se o regime 24h amplia o acesso, a delegacia
    passa a registrar episódios que ocorrem <em>fora do horário comercial</em> (noite, madrugada,
    fins de semana) — janelas em que uma delegacia comum estaria fechada. Comparamos a
    distribuição horária das notificações <strong>antes</strong> e <strong>depois</strong> da
    conversão, e contra as DEAMs de horário comercial. <br>
    <em>Observação metodológica: usa-se a hora de <strong>ocorrência</strong> do SINAN
    (preenchida em ~53% dos registros). As distribuições são normalizadas (% dentro de cada grupo)
    para permitir comparação apesar dos volumes distintos.</em>
</div>
""", unsafe_allow_html=True)

# ─── KPIs: % fora do horário comercial ───────────────────────────────
st.markdown(section_header("🌙 Notificações Fora do Horário Comercial (08–17h)"), unsafe_allow_html=True)
piv = resumo.pivot_table(index='periodo', columns='faixa', values='n', aggfunc='sum').fillna(0)
piv['total'] = piv.sum(axis=1)
piv['pct_fora'] = piv['Fora do comercial'] / piv['total'] * 100

cols = st.columns(3)
for col, per in zip(cols, ORDEM):
    if per in piv.index:
        pct = piv.loc[per, 'pct_fora']
        with col:
            st.markdown(render_metric(ROTULO[per], f"{pct:.1f}%", "fora do horário comercial",
                                      "neutral"), unsafe_allow_html=True)

delta = piv.loc['Depois 24h', 'pct_fora'] - piv.loc['Antes 24h', 'pct_fora'] if {'Antes 24h', 'Depois 24h'} <= set(piv.index) else None
if delta is not None:
    sinal = "aumentou" if delta > 0 else "reduziu"
    st.caption(f"Após a conversão, a fração de notificações fora do horário comercial {sinal} "
               f"{abs(delta):.1f} ponto(s) percentual(is) nas DEAMs 24h (de "
               f"{piv.loc['Antes 24h','pct_fora']:.1f}% para {piv.loc['Depois 24h','pct_fora']:.1f}%).")

st.markdown("<br>", unsafe_allow_html=True)

# ─── Distribuição horária consolidada (contagens) ────────────────────
st.markdown(section_header("🕐 Distribuição Horária das Ocorrências (SINAN)"), unsafe_allow_html=True)

FILTRO_HORA = {
    'Todos os grupos': None,
    'DEAM 24h — após conversão': 'Depois 24h',
    'DEAM 24h — antes da conversão': 'Antes 24h',
    'DEAM comercial (controle)': 'Comercial',
}
sel = st.selectbox("Recorte", list(FILTRO_HORA.keys()), index=0, key="hora_consolidada")
per_sel = FILTRO_HORA[sel]

base = hora if per_sel is None else hora[hora['periodo'] == per_sel]
por_hora = (base.groupby('hora')['n'].sum()
            .reindex(range(24), fill_value=0).reset_index(name='n'))
total_h = por_hora['n'].sum()

col_bar, col_resumo = st.columns([3, 1])
with col_bar:
    COR_FORA = PERIODO_COLORS['Antes 24h']   # laranja da paleta da página
    COR_DENTRO = PERIODO_COLORS['Depois 24h']  # azul da paleta da página
    cores_h = [COR_DENTRO if 8 <= h < 18 else COR_FORA for h in por_hora['hora']]
    figc = go.Figure(go.Bar(
        x=por_hora['hora'], y=por_hora['n'], marker_color=cores_h,
        hovertemplate='<b>%{x}h</b><br>%{y:,.0f} ocorrências<extra></extra>',
    ))
    figc.add_vrect(x0=-0.5, x1=7.5, fillcolor=COR_FORA, opacity=0.06, line_width=0)
    figc.add_vrect(x0=7.5, x1=17.5, fillcolor=COR_DENTRO, opacity=0.08, line_width=0,
                   annotation_text="Horário comercial", annotation_position="top",
                   annotation_font_color=COLORS['text_dim'])
    figc.add_vrect(x0=17.5, x1=23.5, fillcolor=COR_FORA, opacity=0.06, line_width=0)
    figc.update_layout(title="Nº de ocorrências por hora do dia",
                       xaxis=dict(title="Hora do dia", dtick=1, range=[-0.5, 23.5]),
                       yaxis_title="Nº de ocorrências")
    apply_theme(figc, height=440, show_legend=False)
    st.plotly_chart(figc, use_container_width=True)

with col_resumo:
    st.markdown("##### 🧾 Resumo Horário")
    faixas = [
        ('🌙 Madrugada (0h–6h)', range(0, 6)),
        ('🌅 Manhã (6h–12h)', range(6, 12)),
        ('☀️ Tarde (12h–18h)', range(12, 18)),
        ('🌆 Noite (18h–0h)', range(18, 24)),
    ]
    linhas = []
    for nome, rng in faixas:
        n = int(por_hora[por_hora['hora'].isin(rng)]['n'].sum())
        linhas.append({'Faixa': nome, '%': f"{n / total_h * 100:.1f}%" if total_h else "—"})
    st.dataframe(pd.DataFrame(linhas), hide_index=True, use_container_width=True)

    n_fora = int(por_hora[~por_hora['hora'].between(8, 17)]['n'].sum())
    pct_fora = n_fora / total_h * 100 if total_h else 0
    st.markdown(f"""
    <div class="insight-box" style="border-left-color:{PERIODO_COLORS['Antes 24h']};">
        🟠 <strong>Fora do horário comercial</strong> (antes das 8h e a partir das 18h):
        <strong>{pct_fora:.1f}%</strong> das ocorrências.
    </div>
    <div class="insight-box" style="border-left-color:{PERIODO_COLORS['Depois 24h']};">
        🔵 <strong>Dentro do horário comercial</strong> (08–17h): <strong>{100 - pct_fora:.1f}%</strong>.
    </div>
    """, unsafe_allow_html=True)

st.caption("Barras em laranja = fora do expediente comercial; em azul = horário comercial (08–17h). "
           "Use o recorte acima para comparar antes/depois da conversão e o grupo de controle.")

st.markdown("<br>", unsafe_allow_html=True)

# ─── Distribuição por hora do dia ────────────────────────────────────
st.markdown(section_header("🕐 Distribuição por Hora do Dia"), unsafe_allow_html=True)

# normaliza: % dentro de cada periodo
hora_tot = hora.groupby('periodo')['n'].transform('sum')
hora = hora.assign(pct=hora['n'] / hora_tot * 100)

figh = go.Figure()
# faixa de horário comercial
figh.add_vrect(x0=7.5, x1=17.5, fillcolor=COLORS['warning'], opacity=0.10,
               line_width=0, annotation_text="Horário comercial", annotation_position="top left",
               annotation_font_color=COLORS['text_dim'])
for per in ORDEM:
    sub = hora[hora['periodo'] == per].sort_values('hora')
    if sub.empty:
        continue
    figh.add_trace(go.Scatter(x=sub['hora'], y=sub['pct'], name=ROTULO[per],
                              mode='lines+markers',
                              line=dict(color=PERIODO_COLORS[per], width=3,
                                        dash='dot' if per == 'Comercial' else None),
                              marker=dict(size=6),
                              hovertemplate=f'<b>%{{x}}h</b><br>{per}: %{{y:.1f}}%<extra></extra>'))
figh.update_layout(title="Notificações por hora de ocorrência (% dentro do grupo)",
                   xaxis=dict(title="Hora do dia", dtick=2, range=[-0.5, 23.5]),
                   yaxis_title="% das notificações do grupo",
                   legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1))
apply_theme(figh, height=460)
st.plotly_chart(figh, use_container_width=True)

# ─── Relógio polar + dia da semana ───────────────────────────────────
col_clock, col_dow = st.columns(2)
with col_clock:
    st.markdown("##### 🕛 Relógio de 24h")
    figp = go.Figure()
    for per in ORDEM:
        sub = hora[hora['periodo'] == per].sort_values('hora')
        if sub.empty:
            continue
        figp.add_trace(go.Scatterpolar(
            r=sub['pct'], theta=sub['hora'] * 15,  # 360/24
            mode='lines', name=ROTULO[per], fill='toself',
            line=dict(color=PERIODO_COLORS[per], width=2),
            opacity=0.55,
            hovertemplate=f'%{{customdata}}h<br>{per}: %{{r:.1f}}%<extra></extra>',
            customdata=sub['hora'],
        ))
    figp.update_layout(
        polar=dict(
            bgcolor="rgba(11,26,46,0.6)",
            radialaxis=dict(visible=True, gridcolor=COLORS['grid'], tickfont=dict(size=9)),
            angularaxis=dict(direction='clockwise', rotation=90,
                             tickmode='array', tickvals=list(range(0, 360, 45)),
                             ticktext=['0h', '3h', '6h', '9h', '12h', '15h', '18h', '21h'],
                             gridcolor=COLORS['grid']),
        ),
        paper_bgcolor="rgba(0,0,0,0)", font=dict(color=COLORS['text'], size=11),
        height=440, margin=dict(l=40, r=40, t=30, b=30),
        legend=dict(orientation='h', yanchor='bottom', y=-0.15, xanchor='center', x=0.5,
                    font=dict(size=9)),
    )
    st.plotly_chart(figp, use_container_width=True)

with col_dow:
    st.markdown("##### 📆 Dia da Semana")
    dow_tot = dow.groupby('periodo')['n'].transform('sum')
    dow = dow.assign(pct=dow['n'] / dow_tot * 100)
    figd = go.Figure()
    for per in ORDEM:
        sub = dow[dow['periodo'] == per].sort_values('dow')
        if sub.empty:
            continue
        figd.add_trace(go.Bar(x=[DIAS_SEMANA[d] for d in sub['dow']], y=sub['pct'],
                              name=ROTULO[per], marker_color=PERIODO_COLORS[per],
                              hovertemplate=f'<b>%{{x}}</b><br>{per}: %{{y:.1f}}%<extra></extra>'))
    figd.update_layout(title="", xaxis_title="", yaxis_title="% das notificações",
                       barmode='group',
                       legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1,
                                   font=dict(size=9)))
    apply_theme(figd, height=440)
    st.plotly_chart(figd, use_container_width=True)

# ─── Sazonalidade mensal ─────────────────────────────────────────────
st.markdown(section_header("📅 Sazonalidade Mensal"), unsafe_allow_html=True)
mes_tot = mes.groupby('periodo')['n'].transform('sum')
mes = mes.assign(pct=mes['n'] / mes_tot * 100)
figm = go.Figure()
for per in ORDEM:
    sub = mes[mes['periodo'] == per].sort_values('mes')
    if sub.empty:
        continue
    figm.add_trace(go.Scatter(x=[MESES[m - 1] for m in sub['mes']], y=sub['pct'],
                              name=ROTULO[per], mode='lines+markers',
                              line=dict(color=PERIODO_COLORS[per], width=3,
                                        dash='dot' if per == 'Comercial' else None),
                              marker=dict(size=7),
                              hovertemplate=f'<b>%{{x}}</b><br>{per}: %{{y:.1f}}%<extra></extra>'))
figm.update_layout(title="Notificações por mês de ocorrência (% dentro do grupo)",
                   xaxis_title="Mês", yaxis_title="% das notificações",
                   legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1))
apply_theme(figm, height=420)
st.plotly_chart(figm, use_container_width=True)

st.markdown("""
<div class="insight-box">
    🔎 <strong>Como ler estes gráficos</strong>: a concentração de notificações na noite e
    madrugada e nos fins de semana evidencia a demanda por atendimento <em>fora do horário
    comercial</em> — exatamente a lacuna que o plantão 24h se propõe a cobrir. A comparação
    <em>antes × depois</em> nas DEAMs 24h indica se a conversão deslocou o perfil temporal dos
    registros. Como a hora de ocorrência está preenchida em parte dos casos e reflete o
    <em>momento do fato</em> (não o do registro), os padrões devem ser lidos como evidência
    de mecanismo, complementar à estimação causal.
</div>
""", unsafe_allow_html=True)
