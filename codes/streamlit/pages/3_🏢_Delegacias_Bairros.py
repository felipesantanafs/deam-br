"""
🏢 Página 3 — Delegacias e Bairros
Rankings e concentrações territoriais.
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from utils.data_loader import load_sinan_cnes, load_sim, LOCAL_OCORRENCIA_MAP
from utils.charts import apply_theme, COLORS, PALETTE, metric_card_css, render_metric, section_header

st.set_page_config(page_title="Delegacias & Bairros | DDM", page_icon="🏢", layout="wide")
st.markdown(metric_card_css(), unsafe_allow_html=True)

st.markdown("# 🏢 Análise por Delegacias e Bairros")
st.markdown("*Identificando concentrações territoriais da violência — base para o DiD*")
st.markdown("---")

# ─── Dados ────────────────────────────────────────────────────────────
df_sinan = load_sinan_cnes()
df_sim = load_sim()

# ─── Filtros ──────────────────────────────────────────────────────────
ano_range = st.slider("Período", 2015, 2019, (2015, 2019), key="db_ano")
df_filt = df_sinan[(df_sinan['ano'] >= ano_range[0]) & (df_sinan['ano'] <= ano_range[1])]

# ─── KPIs ─────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
bairros_unicos = df_filt['bairro'].dropna().nunique()
with c1:
    st.markdown(render_metric("Bairros Ativos", str(bairros_unicos), "Com notificações"), unsafe_allow_html=True)
with c2:
    top_bairro = df_filt['bairro'].value_counts().index[0] if len(df_filt) > 0 else "N/A"
    top_count = df_filt['bairro'].value_counts().iloc[0] if len(df_filt) > 0 else 0
    st.markdown(render_metric("Bairro Líder", top_bairro, f"{top_count:,.0f} notif."), unsafe_allow_html=True)
with c3:
    encam_ddm = df_filt['encaminhamento_delegacia_mulher'].sum()
    st.markdown(render_metric("Encam. DDM", f"{int(encam_ddm):,.0f}".replace(",", "."),
                              f"{encam_ddm/len(df_filt)*100:.1f}% do total"), unsafe_allow_html=True)
with c4:
    df_sim_filt = df_sim[(df_sim['ano'] >= ano_range[0]) & (df_sim['ano'] <= ano_range[1])]
    fem_count = len(df_sim_filt)
    st.markdown(render_metric("Feminicídios (SIM)", str(fem_count), f"Total SP {ano_range[0]}–{ano_range[1]}", "down"), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─── Tab Layout ───────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["🏘️ Ranking de Bairros", "📋 Cruzamento"])

# ─── Tab 1: Bairros ──────────────────────────────────────────────────
with tab1:
    st.markdown(section_header("Top 25 Bairros por Volume de Notificações (SINAN)"), unsafe_allow_html=True)

    n_bairros = st.slider("Nº de bairros a exibir", 10, 50, 25, key="n_bairros")
    
    bairro_counts = df_filt['bairro'].value_counts().head(n_bairros).reset_index()
    bairro_counts.columns = ['Bairro', 'Notificações']
    bairro_counts = bairro_counts.sort_values('Notificações')

    fig1 = go.Figure()
    fig1.add_trace(go.Bar(
        y=bairro_counts['Bairro'],
        x=bairro_counts['Notificações'],
        orientation='h',
        marker=dict(
            color=bairro_counts['Notificações'],
            colorscale=[[0, COLORS['primary']], [0.5, COLORS['secondary']], [1, COLORS['accent']]],
            line=dict(width=0),
        ),
        hovertemplate='<b>%{y}</b><br>Notificações: %{x:,.0f}<extra></extra>',
    ))
    fig1.update_layout(
        title=f"Top {n_bairros} Bairros — Notificações de Violência (SINAN)",
        xaxis_title="Nº de Notificações",
        yaxis_title="",
    )
    apply_theme(fig1, height=max(400, n_bairros * 22), show_legend=False)
    st.plotly_chart(fig1, use_container_width=True)

    # Encaminhamento a DDM por bairro
    st.markdown(section_header("📬 Taxa de Encaminhamento à DDM por Bairro"), unsafe_allow_html=True)

    bairro_ddm = df_filt.groupby('bairro').agg(
        total=('ano', 'count'),
        encam_ddm=('encaminhamento_delegacia_mulher', 'sum'),
    ).reset_index()
    bairro_ddm['taxa_encam'] = (bairro_ddm['encam_ddm'] / bairro_ddm['total'] * 100).round(1)
    bairro_ddm = bairro_ddm[bairro_ddm['total'] >= 50].sort_values('taxa_encam', ascending=False).head(20)

    fig_ddm = go.Figure()
    fig_ddm.add_trace(go.Bar(
        x=bairro_ddm['bairro'],
        y=bairro_ddm['taxa_encam'],
        marker_color=COLORS['secondary'],
        hovertemplate='<b>%{x}</b><br>Taxa: %{y:.1f}%<br>Total notif.: ' + 
                      bairro_ddm['total'].astype(str) + '<extra></extra>',
    ))
    fig_ddm.update_layout(
        title="Taxa de Encaminhamento à Delegacia da Mulher (%) — Bairros com ≥50 notif.",
        xaxis_title="Bairro", yaxis_title="% Encaminhados à DDM",
    )
    apply_theme(fig_ddm, height=420, show_legend=False)
    st.plotly_chart(fig_ddm, use_container_width=True)

# ─── Tab 2: Cruzamento ───────────────────────────────────────────────
with tab2:
    st.markdown(section_header("📋 Bairros × Tipo de Violência"), unsafe_allow_html=True)

    top_bairros = df_filt['bairro'].value_counts().head(15).index.tolist()
    df_cross = df_filt[df_filt['bairro'].isin(top_bairros)].copy()

    cross_table = df_cross.groupby('bairro').agg(
        total=('ano', 'count'),
        v_fisica=('ocorreu_violencia_fisica', 'sum'),
        ameaca=('meio_ameaca', 'sum'),
        v_sexual=('ocorreu_violencia_sexual', 'sum'),
        v_psicol=('ocorreu_violencia_psicologica', 'sum'),
        encam_ddm=('encaminhamento_delegacia_mulher', 'sum'),
    ).reset_index()
    cross_table.columns = ['Bairro', 'Total', 'V. Física', 'Ameaça', 'V. Sexual', 'V. Psicológica', 'Encam. DDM']
    cross_table = cross_table.sort_values('Total', ascending=False)

    st.dataframe(cross_table, hide_index=True, use_container_width=True)

    # ─── Gráfico 1: Perfil de Violência por Bairro (barras empilhadas normalizadas) ───
    st.markdown(section_header("🔍 Perfil de Violência por Bairro (Composição %)"), unsafe_allow_html=True)
    st.markdown("*Cada bairro tem um perfil diferente de violência. Este gráfico revela quais bairros concentram mais violência sexual ou ameaças proporcionalmente, independente do volume total.*")

    # Calcular percentuais
    tipos_cols = ['V. Física', 'Ameaça', 'V. Sexual', 'V. Psicológica']
    df_pct = cross_table[['Bairro'] + tipos_cols].copy()
    soma_tipos = df_pct[tipos_cols].sum(axis=1)
    for col in tipos_cols:
        df_pct[col] = (df_pct[col] / soma_tipos * 100).round(1)
    df_pct = df_pct.sort_values('V. Sexual', ascending=True)

    tipo_colors = {
        'V. Física': COLORS['danger'],
        'Ameaça': COLORS['warning'],
        'V. Sexual': '#9b59b6',
        'V. Psicológica': COLORS['primary'],
    }

    fig_perfil = go.Figure()
    for tipo in tipos_cols:
        fig_perfil.add_trace(go.Bar(
            y=df_pct['Bairro'],
            x=df_pct[tipo],
            name=tipo,
            orientation='h',
            marker_color=tipo_colors[tipo],
            hovertemplate=f'<b>%{{y}}</b><br>{tipo}: %{{x:.1f}}%<extra></extra>',
        ))
    fig_perfil.update_layout(
        barmode='stack',
        title="Composição (%) por Tipo de Violência — Top 15 Bairros",
        xaxis_title="% do Total de Violências",
        yaxis_title="",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
    )
    apply_theme(fig_perfil, height=500, show_legend=True)
    st.plotly_chart(fig_perfil, use_container_width=True)

    # ─── Gráfico 2: Demanda vs Resposta Institucional (scatter) ───
    st.markdown(section_header("🎯 Demanda vs Resposta Institucional (DDM)"), unsafe_allow_html=True)
    st.markdown("*Identifica bairros com alta demanda e baixa taxa de encaminhamento à DDM — territórios críticos para expansão de atendimento.*")

    df_scatter = df_filt.groupby('bairro').agg(
        total=('ano', 'count'),
        encam_ddm=('encaminhamento_delegacia_mulher', 'sum'),
    ).reset_index()
    df_scatter['taxa_ddm'] = (df_scatter['encam_ddm'] / df_scatter['total'] * 100).round(1)
    df_scatter = df_scatter[df_scatter['total'] >= 50]

    taxa_mediana = df_scatter['taxa_ddm'].median()
    demanda_mediana = df_scatter['total'].median()

    fig_scatter = px.scatter(
        df_scatter, x="total", y="taxa_ddm",
        size="total", color="taxa_ddm",
        hover_name="bairro",
        color_continuous_scale=[[0, COLORS['danger']], [0.5, COLORS['warning']], [1, COLORS['secondary']]],
        labels={"total": "Volume de Notificações (SINAN)", "taxa_ddm": "Taxa Encam. DDM (%)"},
        size_max=25,
    )
    # Quadrantes interpretativos
    fig_scatter.add_hline(y=taxa_mediana, line_dash="dot", line_color="rgba(255,255,255,0.4)",
                          annotation_text=f"Mediana Taxa DDM: {taxa_mediana:.1f}%",
                          annotation_position="top right",
                          annotation_font_color="rgba(255,255,255,0.6)")
    fig_scatter.add_vline(x=demanda_mediana, line_dash="dot", line_color="rgba(255,255,255,0.4)",
                          annotation_text=f"Mediana Demanda: {int(demanda_mediana)}",
                          annotation_position="top right",
                          annotation_font_color="rgba(255,255,255,0.6)")

    # Anotação do quadrante crítico (alta demanda + baixa taxa)
    fig_scatter.add_annotation(
        x=df_scatter['total'].quantile(0.85),
        y=df_scatter['taxa_ddm'].quantile(0.15),
        text="⚠️ Alta demanda,<br>baixo encaminhamento",
        showarrow=False,
        font=dict(size=11, color=COLORS['danger']),
        bgcolor="rgba(0,0,0,0.5)",
        bordercolor=COLORS['danger'],
        borderwidth=1,
    )

    fig_scatter.update_layout(
        title="Bairros: Volume de Casos × Taxa de Encaminhamento à DDM",
    )
    apply_theme(fig_scatter, height=500, show_legend=False)
    st.plotly_chart(fig_scatter, use_container_width=True)

    st.markdown("""
<div class="insight-box">
    💡 <strong>Como interpretar</strong>: Os bairros no quadrante <strong>inferior-direito</strong> (muitas notificações, 
    mas baixa taxa de encaminhamento à DDM) representam <strong>territórios críticos</strong> onde a demanda é alta mas 
    a articulação com a rede policial é fraca. Esses bairros são candidatos prioritários para políticas de ampliação 
    de acesso (DDMs 24h, postos avançados, ou protocolos integrados saúde-segurança).
</div>
""", unsafe_allow_html=True)


