"""
🔥 Página 5 — Mapa de Calor Espacial das DDMs
Visualização espacial real sobre a cidade de SP e análise de cobertura das DDMs.
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from utils.data_loader import load_sinan_cnes
from utils.charts import apply_theme, COLORS, metric_card_css, render_metric, section_header

st.set_page_config(page_title="Mapa de Calor DDMs | DDM", page_icon="🔥", layout="wide")
st.markdown(metric_card_css(), unsafe_allow_html=True)

st.markdown("# 🔥 Mapa de Calor Espacial & Cobertura das DDMs")
st.markdown("*Análise de densidade de ocorrências e distribuição geográfica das 9 Delegacias de Defesa da Mulher (DDMs)*")
st.markdown("---")

# --- Coordenadas das 9 DDMs (Capital) ---
DDMS = {
    "1ª DDM Centro": {"lat": -23.5574, "lon": -46.6226, "end": "Rua Vieira Ravasco, 26, Cambuci - CMB", "func": "24 Horas"},
    "2ª DDM Sul": {"lat": -23.5989, "lon": -46.6344, "end": "Av. Onze de Julho, 89 - Saúde", "func": "Horário Comercial (09h-18h)"},
    "3ª DDM Oeste": {"lat": -23.5567, "lon": -46.7444, "end": "Av. Corifeu de Azevedo Marques, 4300 - Jaguaré", "func": "Horário Comercial (09h-18h)"},
    "4ª DDM Norte": {"lat": -23.4811, "lon": -46.6827, "end": "Av. Itaberaba, 731 - Freguesia do Ó", "func": "Horário Comercial (09h-18h)"},
    "5ª DDM Leste": {"lat": -23.5381, "lon": -46.5744, "end": "Rua Dr. Corinto Baldoíno Costa, 400 - Tatuapé", "func": "Horário Comercial (09h-18h)"},
    "6ª DDM Campo Grande": {"lat": -23.6642, "lon": -46.7568, "end": "R. Sarg. Manoel B. Silva, 115 - Campo Grande", "func": "Horário Comercial (09h-18h)"},
    "7ª DDM Leste (Itaquera)": {"lat": -23.5403, "lon": -46.4526, "end": "Rua Sabbado D'Angelo, 46 - Itaquera", "func": "24 Horas"},
    "8ª DDM Leste": {"lat": -23.5894, "lon": -46.4789, "end": "Av. Osvaldo do Valle Cordeiro, 190 - Jd. Marília", "func": "24 Horas"},
    "9ª DDM Oeste (Pirituba)": {"lat": -23.4769, "lon": -46.7314, "end": "Av. Menotti Laudísio, 286 - Pirituba", "func": "Horário Comercial (09h-18h)"}
}

df_sinan = load_sinan_cnes()

# --- Filtros ---
col1, col2 = st.columns(2)
with col1:
    ano_range = st.slider("Período SINAN", 2015, 2019, (2015, 2019), key="heatmap_ano")
with col2:
    tipo_violencia = st.selectbox(
        "Filtrar por Tipo de Violência (Opcional)",
        ["Todas", "Violência Física", "Violência Psicológica", "Violência Sexual"],
        key="heatmap_tipo"
    )

# --- Processar dados ---
# 1. Filtrar período e coordenadas válidas dentro dos limites aproximados da cidade de São Paulo
df_filt = df_sinan[
    (df_sinan['ano'] >= ano_range[0]) & 
    (df_sinan['ano'] <= ano_range[1]) &
    (df_sinan['latitude'].notna()) & 
    (df_sinan['longitude'].notna()) &
    (df_sinan['latitude'] < -23.3) & (df_sinan['latitude'] > -24.1) &
    (df_sinan['longitude'] > -46.9) & (df_sinan['longitude'] < -46.3)
].copy()

if tipo_violencia == "Violência Física":
    df_filt = df_filt[df_filt['ocorreu_violencia_fisica'] == 1]
elif tipo_violencia == "Violência Psicológica":
    df_filt = df_filt[df_filt['ocorreu_violencia_psicologica'] == 1]
elif tipo_violencia == "Violência Sexual":
    df_filt = df_filt[df_filt['ocorreu_violencia_sexual'] == 1]

# Total de notificações no período (com ou sem geolocalização)
total_notif_periodo = len(df_sinan[
    (df_sinan['ano'] >= ano_range[0]) & 
    (df_sinan['ano'] <= ano_range[1])
])

total_geoloc = len(df_filt)
pct_geoloc = (total_geoloc / total_notif_periodo * 100) if total_notif_periodo > 0 else 0

# --- Cálculo de Distâncias com Haversine ---
def haversine_dist(lon1, lat1, lon2, lat2):
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = np.sin(dlat/2.0)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2.0)**2
    c = 2 * np.arcsin(np.sqrt(a))
    km = 6367 * c
    return km

# Calcular distância de cada ocorrência para cada DDM e encontrar a menor distância
if total_geoloc > 0:
    distances_matrix = {}
    for name, coords in DDMS.items():
        distances_matrix[name] = haversine_dist(df_filt['longitude'], df_filt['latitude'], coords['lon'], coords['lat'])
    
    df_dist = pd.DataFrame(distances_matrix)
    df_filt['dist_min_ddm'] = df_dist.min(axis=1)
    df_filt['ddm_proxima'] = df_dist.idxmin(axis=1)
    
    dist_media = df_filt['dist_min_ddm'].mean()
    # Cobertura considerada num raio de 5km
    cobertura_5km = (df_filt['dist_min_ddm'] <= 5.0).sum()
    pct_cobertura_5km = (cobertura_5km / total_geoloc * 100)
else:
    dist_media = 0
    pct_cobertura_5km = 0

# --- KPIs ---
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(render_metric(
        "Casos Geolocalizados", f"{total_geoloc:,.0f}".replace(",", "."),
        f"{pct_geoloc:.1f}% das notificações", "neutral"
    ), unsafe_allow_html=True)
with c2:
    st.markdown(render_metric(
        "Distância Média à DDM", f"{dist_media:.2f} km",
        "Até a DDM mais próxima", "down" if dist_media < 7 else "up"
    ), unsafe_allow_html=True)
with c3:
    st.markdown(render_metric(
        "Cobertura Raio 5km", f"{pct_cobertura_5km:.1f}%",
        f"Casos a ≤ 5km de uma DDM", "up" if pct_cobertura_5km > 50 else "neutral"
    ), unsafe_allow_html=True)
with c4:
    st.markdown(render_metric(
        "Total de DDMs", "9",
        "Na capital paulista", "neutral"
    ), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Layout do mapa e tabelas
col_map, col_info = st.columns([3, 1])

with col_map:
    st.markdown(section_header("🗺️ Mapa de Densidade Espacial & Localização das DDMs"), unsafe_allow_html=True)
    
    # Criar o mapa de calor usando Densitymapbox
    fig = px.density_mapbox(
        df_filt,
        lat="latitude",
        lon="longitude",
        radius=15,
        zoom=10.0,
        center={"lat": -23.5505, "lon": -46.6333},
        mapbox_style="carto-darkmatter",
        color_continuous_scale="Turbo",
        opacity=0.7,
        range_color=[0, 25] if len(df_filt) > 5000 else None
    )
    
    # Adicionar cada DDM como trace individual para garantir que TODOS os labels apareçam
    # (Plotly oculta labels sobrepostos em traces agrupados)
    text_positions = {
        "1ª DDM Centro": "bottom center",
        "2ª DDM Sul": "top right",
        "3ª DDM Oeste": "bottom right",
        "4ª DDM Norte": "top right",
        "5ª DDM Leste": "top right",
        "6ª DDM Campo Grande": "top right",
        "7ª DDM Leste (Itaquera)": "top left",
        "8ª DDM Leste": "bottom right",
        "9ª DDM Oeste (Pirituba)": "top left",
    }
    for nome, info in DDMS.items():
        fig.add_trace(go.Scattermapbox(
            lat=[info['lat']],
            lon=[info['lon']],
            mode='markers+text',
            marker=go.scattermapbox.Marker(
                size=16,
                color='#FF0000',
                symbol='circle',
                opacity=1.0
            ),
            text=[nome.upper()], # Texto em maiúsculas (Mapbox não suporta <b>)
            textfont=dict(size=14, color='white', family='Arial Black'),
            textposition=text_positions.get(nome, "top right"),
            hovertemplate=f"<b>{nome}</b><br>📍 {info['end']}<br>🕒 {info['func']}<extra></extra>",
            showlegend=False,
            name=nome
        ))
    
    fig.update_layout(
        margin={"r":0,"t":0,"l":0,"b":0},
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True, height=650)
    
    st.markdown("""
    <div class="insight-box" style="margin-top: 15px;">
    💡 <strong>Interpretação do Mapa</strong>:<br>
    O mapa de calor destaca a densidade de ocorrências notificadas. As DDMs estão assinaladas com marcadores vermelhos.
    <br><br>
    <strong>Por que faltam registros na Zona Oeste e bairros nobres?</strong><br>
    O SINAN reflete majoritariamente os atendimentos na rede pública (SUS). Mulheres de classes sociais mais altas (que habitam bairros ricos e parte da Zona Oeste) tendem a usar hospitais e clínicas particulares, onde há grande <strong>subnotificação</strong> da violência no sistema governamental. Isso gera uma 'mancha' concentrada nas regiões periféricas, refletindo tanto a dependência do SUS quanto a desigualdade social.
    </div>
    """, unsafe_allow_html=True)

with col_info:
    st.markdown("#### 🏢 Lista de DDMs na Capital")
    st.markdown("As 9 Delegacias de Defesa da Mulher atualmente em operação:")
    
    for nome, info in DDMS.items():
        func_badge = "🟢 24h" if "24 Horas" in info['func'] else "🕒 Comercial"
        st.markdown(f"**{nome}** — {func_badge}")
        st.caption(f"📍 {info['end']} | 🕒 {info['func']}")

st.markdown("<br>", unsafe_allow_html=True)

# Seção de distância
st.markdown(section_header("📊 Análise de Proximidade e Barreiras de Acesso"), unsafe_allow_html=True)

col_chart, col_dist_table = st.columns([2, 1])

with col_chart:
    if total_geoloc > 0:
        # Histograma de distância à DDM mais próxima
        fig_hist = px.histogram(
            df_filt,
            x="dist_min_ddm",
            nbins=30,
            color_discrete_sequence=[COLORS['secondary']],
            labels={"dist_min_ddm": "Distância à DDM mais próxima (km)", "count": "Nº de Ocorrências"},
            title="Distribuição da Distância das Ocorrências até a DDM mais Próxima"
        )
        
        # Adicionar linha vertical na distância média
        fig_hist.add_vline(x=dist_media, line_dash="dash", line_color=COLORS['danger'], 
                           annotation_text=f"Média: {dist_media:.2f}km", annotation_position="top right")
        
        fig_hist.update_layout(
            xaxis_title="Distância (km)",
            yaxis_title="Nº de Ocorrências",
        )
        apply_theme(fig_hist, height=400, show_legend=False)
        st.plotly_chart(fig_hist, use_container_width=True)
    else:
        st.info("Dados de geolocalização indisponíveis para gerar gráfico de proximidade.")

with col_dist_table:
    if total_geoloc > 0:
        st.markdown("##### Casos por DDM de Referência (mais próxima)")
        ddm_counts = df_filt['ddm_proxima'].value_counts().reset_index()
        ddm_counts.columns = ['DDM Referência', 'Ocorrências']
        ddm_counts['%'] = (ddm_counts['Ocorrências'] / total_geoloc * 100).round(1)
        st.dataframe(ddm_counts, hide_index=True, use_container_width=True)
    else:
        st.info("Nenhuma ocorrência geolocalizada no filtro selecionado.")

st.markdown("---")
st.markdown("""
<div class="insight-box">
    💡 <strong>Diagnóstico de Cobertura Geográfica</strong>: A análise revela que uma grande parcela das 
    notificações de violência ocorre a mais de 5km de distância de qualquer DDM (conforme visto na taxa de cobertura).
    A distância física funciona como uma barreira de acesso à justiça para mulheres residentes nas periferias (extremo leste e sul),
    onde o tempo de deslocamento até a DDM mais próxima é elevado. Expandir o horário de funcionamento das delegacias periféricas para 24h
    (ou criar novos postos) é crucial para viabilizar o acesso institucional contínuo.
</div>
""", unsafe_allow_html=True)
