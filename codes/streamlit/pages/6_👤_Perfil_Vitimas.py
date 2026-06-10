"""
👤 Página 5 — Perfil das Vítimas
Caracterização sociodemográfica e contextual.
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from utils.data_loader import load_sinan_cnes, load_sim, RACA_PACIENTE_MAP, LOCAL_OCORRENCIA_MAP
from utils.charts import apply_theme, COLORS, PALETTE, PALETTE_WARM, metric_card_css, render_metric, section_header

st.set_page_config(page_title="Perfil das Vítimas | DDM", page_icon="👤", layout="wide")
st.markdown(metric_card_css(), unsafe_allow_html=True)

st.markdown("# 👤 Perfil das Vítimas")
st.markdown("*Caracterização sociodemográfica e contextual da violência física/sexual/psicológica (🏥 SINAN) e feminicídios (⚰️ SIM/DataSUS)*")
st.markdown("---")

st.markdown("""
<div class="insight-box">
    ℹ️ <strong>Especificação das Fontes de Dados</strong>:
    <ul>
        <li><strong>🏥 Base SINAN (Notificações de Violência)</strong>: Registros de violência contra a mulher notificados no sistema de saúde. Utilizada para idade, raça/cor da vítima, relação com o autor, tipos de violência, meios utilizados e local da ocorrência.</li>
        <li><strong>⚰️ Base SIM/DataSUS (Feminicídios/Óbitos)</strong>: Registros de óbitos por agressão contra mulheres (causa básica de morte). Utilizada na análise comparativa de Raça/Cor das vítimas fatais.</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# ─── Dados ────────────────────────────────────────────────────────────
df_sinan = load_sinan_cnes()
df_sim = load_sim()

# Filtro
ano_range = st.slider("Período SINAN/SIM", 2015, 2019, (2015, 2019), key="perfil_ano")
df_filt = df_sinan[(df_sinan['ano'] >= ano_range[0]) & (df_sinan['ano'] <= ano_range[1])].copy()

# ─── KPIs ─────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
idade_media = df_filt['idade_paciente'].dropna().mean()
with c1:
    st.markdown(render_metric("Idade Média (SINAN)", f"{idade_media:.1f} anos"), unsafe_allow_html=True)
with c2:
    pct_conjugue = (df_filt['autor_conjugue'].sum() + df_filt['autor_ex_conjugue'].sum()) / len(df_filt) * 100
    st.markdown(render_metric("Autor: (Ex)Cônjuge (SINAN)", f"{pct_conjugue:.1f}%", "Violência íntima"), unsafe_allow_html=True)
with c3:
    pct_residencia = (df_filt['local_ocorrencia'] == 1).sum() / len(df_filt) * 100
    st.markdown(render_metric("Ocorrência em Casa (SINAN)", f"{pct_residencia:.1f}%", "Local mais frequente"), unsafe_allow_html=True)
with c4:
    pct_fisica = df_filt['ocorreu_violencia_fisica'].sum() / len(df_filt) * 100
    st.markdown(render_metric("Violência Física (SINAN)", f"{pct_fisica:.1f}%", "Tipo predominante"), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─── Tabs ─────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["📊 Idade & Raça", "💔 Relação com Autor", "🔪 Tipos & Meios", "📍 Local"])

# ─── Tab 1: Idade e Raça ─────────────────────────────────────────────
with tab1:
    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown(section_header("📊 Distribuição Etária (Base 🏥 SINAN)"), unsafe_allow_html=True)
        
        idades = df_filt['idade_paciente'].dropna()
        idades = idades[(idades >= 0) & (idades <= 100)]

        fig_idade = go.Figure()
        fig_idade.add_trace(go.Histogram(
            x=idades,
            nbinsx=40,
            marker_color=COLORS['secondary'],
            opacity=0.8,
            hovertemplate='Idade: %{x}<br>Casos: %{y}<extra></extra>',
        ))
        # Adicionar linha de média
        fig_idade.add_vline(x=idade_media, line_dash="dash", line_color=COLORS['warning'],
                           annotation_text=f"Média: {idade_media:.1f}", annotation_position="top")
        fig_idade.update_layout(title="Distribuição Etária das Vítimas (Base 🏥 SINAN)", xaxis_title="Idade", yaxis_title="Frequência")
        apply_theme(fig_idade, height=400, show_legend=False)
        st.plotly_chart(fig_idade, use_container_width=True)

    with col_r:
        st.markdown(section_header("🎨 Raça/Cor (Base 🏥 SINAN)"), unsafe_allow_html=True)

        df_filt['raca_label'] = df_filt['raca_paciente'].map(RACA_PACIENTE_MAP)
        raca_counts = df_filt['raca_label'].value_counts().reset_index()
        raca_counts.columns = ['Raça/Cor', 'Total']
        raca_counts = raca_counts[raca_counts['Raça/Cor'].notna()]

        raca_colors = [COLORS['accent'], COLORS['warning'], COLORS['danger'], '#F1C40F', COLORS['success']]
        
        fig_raca = go.Figure(data=[go.Pie(
            labels=raca_counts['Raça/Cor'],
            values=raca_counts['Total'],
            hole=0.5,
            marker=dict(colors=raca_colors, line=dict(color=COLORS['bg_dark'], width=2)),
            textfont=dict(size=13, color=COLORS['text']),
            hovertemplate='<b>%{label}</b><br>Total: %{value:,.0f}<br>%{percent}<extra></extra>',
        )])
        fig_raca.update_layout(title="Distribuição por Raça/Cor")
        apply_theme(fig_raca, height=400)
        st.plotly_chart(fig_raca, use_container_width=True)

    # Comparação SIM vs SINAN
    st.markdown(section_header("⚖️ Comparativo Raça/Cor: Feminicídios (⚰️ SIM) vs. Notificações (🏥 SINAN)"), unsafe_allow_html=True)

    sim_filt = df_sim[(df_sim['ano'] >= ano_range[0]) & (df_sim['ano'] <= ano_range[1])]
    sim_raca = sim_filt['raca_cor'].value_counts().reset_index()
    sim_raca.columns = ['Raça/Cor', 'SIM']
    
    sinan_raca = raca_counts.rename(columns={'Total': 'SINAN'})
    comp = pd.merge(sinan_raca, sim_raca, on='Raça/Cor', how='outer').fillna(0)
    comp['SINAN_pct'] = (comp['SINAN'] / comp['SINAN'].sum() * 100).round(1)
    comp['SIM_pct'] = (comp['SIM'] / comp['SIM'].sum() * 100).round(1)

    fig_comp = go.Figure()
    fig_comp.add_trace(go.Bar(
        x=comp['Raça/Cor'], y=comp['SINAN_pct'],
        name='SINAN (Notificações)', marker_color=COLORS['secondary'], opacity=0.85,
    ))
    fig_comp.add_trace(go.Bar(
        x=comp['Raça/Cor'], y=comp['SIM_pct'],
        name='SIM (Feminicídios)', marker_color=COLORS['danger'], opacity=0.85,
    ))
    fig_comp.update_layout(
        title="Comparação Raça/Cor: Notificações vs. Feminicídios (%)",
        xaxis_title="Raça/Cor", yaxis_title="%",
        barmode='group',
    )
    apply_theme(fig_comp, height=380)
    st.plotly_chart(fig_comp, use_container_width=True)

# ─── Tab 2: Relação com Autor ────────────────────────────────────────
with tab2:
    st.markdown(section_header("💔 Relação da Vítima com o Autor (Base 🏥 SINAN)"), unsafe_allow_html=True)

    autor_cols = {
        'autor_conjugue': 'Cônjuge',
        'autor_ex_conjugue': 'Ex-Cônjuge',
        'autor_namorado_a': 'Namorado(a)',
        'autor_ex_namorado_a': 'Ex-Namorado(a)',
        'autor_pai': 'Pai',
        'autor_mae': 'Mãe',
        'autor_padrasto': 'Padrasto',
        'autor_madrasta': 'Madrasta',
        'autor_filho_a': 'Filho(a)',
        'autor_irmao': 'Irmão(ã)',
        'autor_conhecido': 'Conhecido(a)',
        'autor_desconhecido': 'Desconhecido(a)',
        'autor_cuidador': 'Cuidador(a)',
        'autor_patrao_chefe': 'Patrão/Chefe',
        'autor_propria_pessoa': 'Própria Pessoa',
    }

    autor_data = []
    for col, label in autor_cols.items():
        if col in df_filt.columns:
            total = df_filt[col].sum()
            if total > 0:
                autor_data.append({'Relação': label, 'Total': int(total)})

    df_autor = pd.DataFrame(autor_data).sort_values('Total', ascending=True)

    fig_autor = go.Figure()
    fig_autor.add_trace(go.Bar(
        y=df_autor['Relação'],
        x=df_autor['Total'],
        orientation='h',
        marker=dict(
            color=df_autor['Total'],
            colorscale=[[0, COLORS['primary']], [0.5, COLORS['secondary']], [1, COLORS['danger']]],
        ),
        hovertemplate='<b>%{y}</b><br>Casos: %{x:,.0f}<extra></extra>',
    ))
    fig_autor.update_layout(title="Relação da Vítima com o Agressor", xaxis_title="Nº de Casos")
    apply_theme(fig_autor, height=500, show_legend=False)
    st.plotly_chart(fig_autor, use_container_width=True)

    # Álcool
    col_a1, col_a2 = st.columns(2)
    with col_a1:
        st.markdown(section_header("🍺 Uso de Álcool pelo Autor (Base 🏥 SINAN)"), unsafe_allow_html=True)
        alcool = df_filt['autor_usou_alcool'].value_counts().reset_index()
        alcool.columns = ['Usou Álcool', 'Total']
        alcool['Usou Álcool'] = alcool['Usou Álcool'].map({1.0: 'Sim', 0.0: 'Não'})
        alcool = alcool[alcool['Usou Álcool'].notna()]

        fig_alc = go.Figure(data=[go.Pie(
            labels=alcool['Usou Álcool'], values=alcool['Total'],
            hole=0.5,
            marker=dict(colors=[COLORS['danger'], COLORS['success']], line=dict(color=COLORS['bg_dark'], width=2)),
            textfont=dict(color=COLORS['text']),
        )])
        fig_alc.update_layout(title="Autor sob efeito de álcool?")
        apply_theme(fig_alc, height=350)
        st.plotly_chart(fig_alc, use_container_width=True)

    with col_a2:
        st.markdown(section_header("👫 Sexo do Autor (Base 🏥 SINAN)"), unsafe_allow_html=True)
        sexo_autor = df_filt['autor_sexo'].value_counts().reset_index()
        sexo_autor.columns = ['Sexo', 'Total']
        sexo_autor['Sexo'] = sexo_autor['Sexo'].map({1.0: 'Masculino', 2.0: 'Feminino', 3.0: 'Ambos'})
        sexo_autor = sexo_autor[sexo_autor['Sexo'].notna()]

        fig_sexo = go.Figure(data=[go.Pie(
            labels=sexo_autor['Sexo'], values=sexo_autor['Total'],
            hole=0.5,
            marker=dict(colors=[COLORS['secondary'], COLORS['warning'], COLORS['accent']], line=dict(color=COLORS['bg_dark'], width=2)),
            textfont=dict(color=COLORS['text']),
        )])
        fig_sexo.update_layout(title="Sexo do Agressor")
        apply_theme(fig_sexo, height=350)
        st.plotly_chart(fig_sexo, use_container_width=True)
        
    st.markdown("""
    <div class="insight-box">
        ⚠️ <strong>O que é "Própria Pessoa" (Autolesão)?</strong><br>
        O dado "Autor - Própria Pessoa" (indicado em ~20% dos casos de violência no SINAN) refere-se a episódios de 
        <strong>lesão autoprovocada</strong> ou <strong>tentativa de suicídio</strong>. É comum que a notificação de violência 
        doméstica/psicológica grave apareça associada a um evento de autolesão que levou a mulher ao hospital. 
    </div>
    """, unsafe_allow_html=True)

# ─── Tab 3: Tipos e Meios ────────────────────────────────────────────
with tab3:
    col_t1, col_t2 = st.columns(2)

    with col_t1:
        st.markdown(section_header("⚡ Tipos de Violência Sofrida (Base 🏥 SINAN)"), unsafe_allow_html=True)

        tipos = {
            'Violência Física': df_filt['ocorreu_violencia_fisica'].sum(),
            'Violência Psicológica': df_filt['ocorreu_violencia_psicologica'].sum(),
            'Violência Sexual': df_filt['ocorreu_violencia_sexual'].sum(),
            'Negligência/Abandono': df_filt['ocorreu_negligencia_abandono'].sum(),
        }
        df_tipos = pd.DataFrame(list(tipos.items()), columns=['Tipo', 'Total']).sort_values('Total', ascending=True)

        fig_tipos = go.Figure()
        fig_tipos.add_trace(go.Bar(
            y=df_tipos['Tipo'], x=df_tipos['Total'],
            orientation='h',
            marker_color=[COLORS['danger'], COLORS['warning'], COLORS['accent'], COLORS['highlight']],
            hovertemplate='<b>%{y}</b><br>Casos: %{x:,.0f}<extra></extra>',
        ))
        fig_tipos.update_layout(title="Tipos de Violência", xaxis_title="Nº de Casos")
        apply_theme(fig_tipos, height=350, show_legend=False)
        st.plotly_chart(fig_tipos, use_container_width=True)

    with col_t2:
        st.markdown(section_header("🔪 Meios Utilizados (Base 🏥 SINAN)"), unsafe_allow_html=True)

        meios = {
            'Força corporal': df_filt['meio_forca'].sum(),
            'Enforcamento': df_filt['meio_enforcamento'].sum(),
            'Objeto contundente': df_filt['meio_objeto_contundente'].sum(),
            'Objeto perfurante': df_filt['meio_objeto_perfurante'].sum(),
            'Objeto quente': df_filt['meio_objeto_quente'].sum(),
            'Envenenamento': df_filt['meio_envenenamento'].sum(),
            'Arma de fogo': df_filt['meio_arma_fogo'].sum(),
            'Ameaça': df_filt['meio_ameaca'].sum(),
        }
        df_meios = pd.DataFrame(list(meios.items()), columns=['Meio', 'Total']).sort_values('Total', ascending=True)

        fig_meios = go.Figure()
        fig_meios.add_trace(go.Bar(
            y=df_meios['Meio'], x=df_meios['Total'],
            orientation='h',
            marker=dict(
                color=df_meios['Total'],
                colorscale=[[0, COLORS['primary']], [1, COLORS['danger']]],
            ),
            hovertemplate='<b>%{y}</b><br>Casos: %{x:,.0f}<extra></extra>',
        ))
        fig_meios.update_layout(title="Meios de Violência", xaxis_title="Nº de Casos")
        apply_theme(fig_meios, height=350, show_legend=False)
        st.plotly_chart(fig_meios, use_container_width=True)

# ─── Tab 4: Local ────────────────────────────────────────────────────
with tab4:
    st.markdown(section_header("📍 Local da Ocorrência (Base 🏥 SINAN)"), unsafe_allow_html=True)

    df_filt['local_label'] = df_filt['local_ocorrencia'].map(LOCAL_OCORRENCIA_MAP)
    local_counts = df_filt['local_label'].value_counts().reset_index()
    local_counts.columns = ['Local', 'Total']
    local_counts = local_counts[local_counts['Local'].notna()]

    fig_local = go.Figure(data=[go.Pie(
        labels=local_counts['Local'], values=local_counts['Total'],
        hole=0.45,
        marker=dict(colors=PALETTE_WARM, line=dict(color=COLORS['bg_dark'], width=2)),
        textfont=dict(size=12, color=COLORS['text']),
        hovertemplate='<b>%{label}</b><br>Total: %{value:,.0f}<br>%{percent}<extra></extra>',
    )])
    fig_local.update_layout(title="Distribuição por Local da Ocorrência")
    apply_theme(fig_local, height=450)
    st.plotly_chart(fig_local, use_container_width=True)

    st.markdown("""
    <div class="insight-box">
        💡 <strong>Perfil Predominante</strong>: A vítima típica tem cerca de {:.0f} anos,
        sofre violência física ({:.0f}%) dentro de casa ({:.0f}%), praticada pelo cônjuge ou ex-cônjuge ({:.0f}%).
        Este perfil reforça a importância de DDMs com atendimento 24h, já que a violência
        doméstica tende a ocorrer fora do horário comercial.
    </div>
    """.format(idade_media, pct_fisica, pct_residencia, pct_conjugue), unsafe_allow_html=True)
