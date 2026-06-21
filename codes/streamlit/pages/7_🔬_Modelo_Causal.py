"""
🔬 Página 7 — Modelo Causal (Callaway & Sant'Anna 2021)
Estimação de impacto da conversão das DEAMs para o regime 24h sobre notificações
e feminicídios, com adoção escalonada — escopo nacional (2009–2019).
"""
import os
import sys

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from utils.data_loader import load_causal_results, load_causal_panel, GRUPO_COLORS
from utils.charts import apply_theme, COLORS, metric_card_css, render_metric, section_header

st.set_page_config(page_title="Modelo Causal | DEAM 24h", page_icon="🔬", layout="wide")
st.markdown(metric_card_css(), unsafe_allow_html=True)

st.markdown("# 🔬 Avaliação de Impacto Causal (CS DiD)")
st.markdown("*Estimador de Callaway & Sant'Anna (2021) para a conversão das DEAMs ao regime 24h — municípios brasileiros, 2009–2019.*")
st.markdown("---")

res = load_causal_results()
if not res:
    st.error("Resultados causais não encontrados (dados/consolidado/causal_results.json). "
             "Execute o modelo causal primeiro.")
    st.stop()

meta = res.get('metadata', {})
notif = res['cs_did_24h']['notificacoes']
fem = res['cs_did_24h']['feminicidios']


def pretrend_sig(stats: dict) -> int:
    """Conta coeficientes pré-tratamento individualmente significativos (|t|>1.96)."""
    es = stats.get('event_study', {})
    return sum(1 for k, v in es.items() if int(k) < 0 and v['se'] and abs(v['effect'] / v['se']) > 1.96)


# ─── Introdução ──────────────────────────────────────────────────────
cov_list = meta.get('covariaveis', [])
COV_LABELS = {
    'taxa_homicidios_masc': 'homicídios masculinos /100k',
    'log_populacao': 'log da população',
    'log_pib_per_capita': 'log do PIB per capita',
    'delta_homicidios_masc': 'variação recente de homicídios masculinos',
}
cov_txt = ', '.join(COV_LABELS.get(c, c) for c in cov_list) if cov_list else 'nenhuma'
est = meta.get('estimation_method', 'reg')
est_nome = 'duplamente robusta (DR)' if est == 'dr' else 'por regressão'

st.markdown(f"""
<div class="insight-box" style="margin-bottom:22px;">
    💡 <strong>Desenho de identificação</strong>: a conversão para o plantão 24h ocorreu de forma
    <strong>escalonada</strong> entre {meta.get('periodo','2009-2019')} ({meta.get('n_municipios_tratados','38')}
    municípios tratados). O DiD clássico (TWFE) seria viesado nesse cenário (Goodman-Bacon, 2021),
    então usa-se o estimador de <strong>Callaway & Sant'Anna (2021)</strong> com grupo de controle
    <em>{meta.get('control_group','never_treated')}</em> — as DEAMs de horário comercial.<br>
    A estimação é <strong>{est_nome}</strong>, condicionando em covariáveis ({cov_txt}) para sustentar
    as tendências paralelas e corrigir a <strong>adoção reativa</strong> (municípios convertem a DEAM
    após uma piora recente da violência).<br>
    Avaliam-se <strong>duas variáveis-resultado</strong>: notificações (acesso, esperado ↑) e
    feminicídios (letalidade, esperado ↓).
</div>
""", unsafe_allow_html=True)

# ─── KPIs ─────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(render_metric("ATT Notificações", f"{notif['cs_att']:+.2f}",
                              f"p = {notif['cs_p_value']:.3f}", "down" if notif['cs_att'] < 0 else "up"),
                unsafe_allow_html=True)
with c2:
    st.markdown(render_metric("ATT Feminicídios", f"{fem['cs_att']:+.3f}",
                              f"p = {fem['cs_p_value']:.3f}", "down" if fem['cs_att'] < 0 else "up"),
                unsafe_allow_html=True)
with c3:
    st.markdown(render_metric("Municípios tratados", str(meta.get('n_municipios_tratados', 38)),
                              "DEAMs 24h"), unsafe_allow_html=True)
with c4:
    st.markdown(render_metric("Controles", str(meta.get('n_municipios_controle', 247)),
                              "DEAMs comerciais"), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

tab_trends, tab_es, tab_att, tab_disc = st.tabs([
    "📈 1. Tendências Paralelas",
    "🎯 2. Event Study",
    "📊 3. ATT & Robustez",
    "🎓 4. Discussão",
])

# ─── TAB 1: Raw trends ───────────────────────────────────────────────
with tab_trends:
    st.markdown(section_header("📈 Tendências Brutas — Tratados vs Controle"), unsafe_allow_html=True)
    st.write("Comportamento médio (por 100 mil hab.) das DEAMs 24h e das DEAMs comerciais ao longo do tempo. "
             "A leitura visual antecede os testes formais de tendências paralelas.")
    panel = load_causal_panel()

    def taxa(df, evento):
        g = df.groupby('ano').agg(ev=(evento, 'sum'), pop=('populacao', 'sum')).reset_index()
        g['t'] = g['ev'] / g['pop'] * 100_000
        return g

    cc1, cc2 = st.columns(2)
    for cc, evento, titulo in [(cc1, 'notificacoes', '🏥 Notificações /100k'),
                               (cc2, 'feminicidios', '⚰️ Feminicídios /100k')]:
        with cc:
            f = go.Figure()
            for g in ['24h', 'comercial']:
                key = 'first_treat' if 'first_treat' in panel.columns else 'tratado'
                sub = panel[panel['grupo'] == g] if 'grupo' in panel.columns else \
                    panel[panel[key] > 0 if g == '24h' else panel[key] == 0]
                s = taxa(sub, evento)
                nome = 'DEAM 24h' if g == '24h' else 'DEAM comercial'
                f.add_trace(go.Scatter(x=s['ano'], y=s['t'], name=nome, mode='lines+markers',
                                       line=dict(color=GRUPO_COLORS[g], width=3), marker=dict(size=7)))
            f.update_layout(title=f"{titulo} — tratados vs controle",
                            xaxis_title="Ano", yaxis_title=titulo.split(' ', 1)[1],
                            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1))
            apply_theme(f, height=380)
            st.plotly_chart(f, use_container_width=True)

# ─── TAB 2: Event study ──────────────────────────────────────────────
with tab_es:
    st.markdown(section_header("🎯 Estudo de Evento (efeitos dinâmicos)"), unsafe_allow_html=True)
    st.write("Coeficientes por ano relativo à adoção. Os períodos **negativos** testam pré-tendências "
             "(devem ficar próximos de zero); os **positivos** medem o efeito dinâmico do tratamento.")

    for stats, titulo, cor in [(notif, '🏥 Notificações /100k', COLORS['accent']),
                               (fem, '⚰️ Feminicídios /100k', COLORS['danger'])]:
        es = stats.get('event_study', {})
        if not es:
            continue
        xs = sorted(int(k) for k in es)
        eff = [es[str(x)]['effect'] for x in xs]
        se = [es[str(x)]['se'] for x in xs]
        hi = [e + 1.96 * s for e, s in zip(eff, se)]
        lo = [e - 1.96 * s for e, s in zip(eff, se)]
        f = go.Figure()
        f.add_trace(go.Scatter(x=xs + xs[::-1], y=hi + lo[::-1], fill='toself',
                               fillcolor='rgba(93,173,226,0.12)', line=dict(width=0),
                               hoverinfo='skip', showlegend=False))
        f.add_trace(go.Scatter(x=xs, y=eff, mode='lines+markers',
                               line=dict(color=cor, width=3), marker=dict(size=7),
                               name='Efeito', hovertemplate='t=%{x}<br>%{y:.2f}<extra></extra>'))
        f.add_vline(x=-0.5, line_dash="dash", line_color=COLORS['warning'])
        f.add_hline(y=0, line_color=COLORS['text_dim'])
        f.update_layout(title=titulo, xaxis_title="Ano relativo à adoção (0 = conversão 24h)",
                        yaxis_title="Efeito estimado /100k")
        apply_theme(f, height=380, show_legend=False)
        st.plotly_chart(f, use_container_width=True)

# ─── TAB 3: ATT & robustez ───────────────────────────────────────────
with tab_att:
    st.markdown(section_header("📊 ATT Global e Estimadores de Robustez"), unsafe_allow_html=True)
    rows = []
    for nome, stats in [('Notificações /100k', notif), ('Feminicídios /100k', fem)]:
        ci_inclui_zero = stats['cs_ci_lower'] <= 0 <= stats['cs_ci_upper']
        rows.append({
            'Desfecho': nome,
            'ATT (CS-DR)': f"{stats['cs_att']:+.3f}",
            'EP': f"{stats['cs_se']:.3f}",
            'IC 95%': f"[{stats['cs_ci_lower']:+.2f}; {stats['cs_ci_upper']:+.2f}]",
            'p-valor': f"{stats['cs_p_value']:.3f}",
            'Significativo (5%)': "Não" if ci_inclui_zero else "Sim",
        })
    st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)

    if notif.get('sa_att') is None and notif.get('bjs_att') is None:
        st.caption("ℹ️ Os estimadores alternativos Sun & Abraham e Borusyak et al. (BJS) não "
                   "convergem sob a especificação DR (posto deficiente com a covariável "
                   "de variação `delta_homicidios_masc`, ausente em 2009–2010). A identificação "
                   "se apoia no CS-DR e no teste de pré-tendências (aba 1/2).")

    coortes = meta.get('coortes', {})
    if coortes:
        cf = pd.DataFrame([{'Ano de adoção': k, 'Nº de municípios': v} for k, v in coortes.items()])
        fb = go.Figure(go.Bar(x=cf['Ano de adoção'], y=cf['Nº de municípios'],
                              marker_color=COLORS['secondary'],
                              hovertemplate='<b>%{x}</b><br>%{y} municípios<extra></extra>'))
        fb.update_layout(title="Coortes de tratamento (nº de municípios por ano de adoção)",
                         xaxis_title="Coorte (ano de adoção)", yaxis_title="Nº de municípios")
        apply_theme(fb, height=320, show_legend=False)
        st.plotly_chart(fb, use_container_width=True)

    st.info(f"Método de estimação: **{est}** ({est_nome}) · "
            f"Covariáveis: {cov_txt} · "
            f"Contrafactual: {meta.get('contrafactual','DEAMs de horário comercial')}.")

# ─── TAB 4: Discussão ────────────────────────────────────────────────
with tab_disc:
    st.markdown(section_header("🎓 Discussão e Leitura Honesta dos Resultados"), unsafe_allow_html=True)

    pt_notif = pretrend_sig(notif)
    pt_fem = pretrend_sig(fem)
    fem_inclui_zero = fem['cs_ci_lower'] <= 0 <= fem['cs_ci_upper']
    notif_inclui_zero = notif['cs_ci_lower'] <= 0 <= notif['cs_ci_upper']

    st.markdown(f"""
    ### I. O que os números dizem

    - **Acesso (notificações)**: ATT = **{notif['cs_att']:+.2f}/100k**
      (IC95% [{notif['cs_ci_lower']:+.1f}; {notif['cs_ci_upper']:+.1f}], p = {notif['cs_p_value']:.3f}).
    - **Letalidade (feminicídios)**: ATT = **{fem['cs_att']:+.3f}/100k**
      (IC95% [{fem['cs_ci_lower']:+.2f}; {fem['cs_ci_upper']:+.2f}], p = {fem['cs_p_value']:.3f}).

    ### II. Validade das tendências paralelas

    Sob a estimação **duplamente robusta com covariáveis**, o estudo de evento não exibe
    coeficientes pré-tratamento individualmente significativos ({pt_notif} para notificações,
    {pt_fem} para feminicídios) e o teste conjunto de pré-tendências **não é rejeitado** para
    nenhum dos dois desfechos. A covariável decisiva é a **variação recente de homicídios
    masculinos** (`delta_homicidios_masc`): ela pareia municípios que tiveram um surto de
    violência letal e abriram a DEAM 24h com municípios de surto semelhante que não abriram,
    corrigindo a **adoção reativa** que antes contaminava as tendências.

    ### III. O achado central — a causalidade reversa do feminicídio

    Sob especificação só com covariáveis de **nível**, o efeito sobre feminicídios aparecia
    **positivo e significativo** (≈ +0,63/100k, p ≈ 0,02), o que, lido ingenuamente, sugeriria
    que "a DEAM 24h aumenta feminicídios" — conclusão falsa, produzida pelo **pico pré-tratamento
    mal atribuído à política**. Ao corrigir as tendências paralelas (via `delta`), o efeito
    **encolhe e perde significância** (ATT = {fem['cs_att']:+.3f}, p = {fem['cs_p_value']:.3f},
    {'IC inclui zero' if fem_inclui_zero else 'IC exclui zero'}).

    > **Conclusão honesta:** não há evidência robusta de efeito da DEAM 24h sobre a
    > **letalidade**. O efeito "positivo" anterior era artefato de causalidade reversa, não da política.

    ### IV. O sinal do acesso

    Para **notificações**, o ATT é **{'significativo' if not notif_inclui_zero else 'não-significativo'}**
    porém **negativo** ({notif['cs_att']:+.1f}/100k) — contrário ao aumento de acesso previsto pela
    cadeia causal. Não deve ser lido como "menos acesso": é compatível com **heterogeneidade entre
    coortes**, deslocamento/consolidação de registro e com o fato de que a hora do SINAN é a do
    *fato*, não a do atendimento (ver página *Sazonalidade & Horário*). É um ponto a investigar,
    não uma evidência de que o plantão reduz o acesso.

    ### V. Princípio metodológico

    **Tendências paralelas é a hipótese de identificação e precisa valer independentemente de o
    efeito ser significativo.** A significância calculada sobre um estimador com pré-tendências
    violadas não tem valor causal. O contraste correto é *enviesado × não-enviesado* — e não
    *significativo × não-significativo*. Com {meta.get('n_municipios_tratados','38')} municípios
    tratados em coortes pequenas, o poder é limitado e os ICs são largos; a leitura responsável
    combina **magnitude**, **mecanismo** e **validação das hipóteses de identificação**.
    """)

st.markdown("---")
st.caption("🔬 Estimação Callaway & Sant'Anna (2021). Painel municipal balanceado 2009–2019 · FEA-USP | Avaliação de Políticas Sociais.")
