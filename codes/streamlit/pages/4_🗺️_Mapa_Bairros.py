"""
🗺️ Página 4 — Mapa de Bairros
Análise espacial por bairro utilizando mapa de bolhas interpretativo.
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from utils.data_loader import load_sinan_cnes
from utils.charts import apply_theme, COLORS, metric_card_css, section_header

st.set_page_config(page_title="Mapa de Bairros | DDM", page_icon="🗺️", layout="wide")
st.markdown(metric_card_css(), unsafe_allow_html=True)

st.markdown("# 🗺️ Mapa de Incidência por Bairros")
st.markdown("*Concentração espacial de ocorrências agregada por bairro/distrito na cidade de São Paulo (Base 🏥 SINAN).*")
st.markdown("---")

df_sinan = load_sinan_cnes()

# Filtros
col1, col2 = st.columns(2)
with col1:
    ano_range = st.slider("Período (Base 🏥 SINAN)", 2015, 2019, (2015, 2019), key="map_ano")
with col2:
    tipo_violencia = st.selectbox(
        "Filtrar por Tipo de Violência (Opcional)",
        ["Todas", "Violência Física", "Violência Psicológica", "Violência Sexual"]
    )

# Aplicar filtros
df_filt = df_sinan[
    (df_sinan['ano'] >= ano_range[0]) & 
    (df_sinan['ano'] <= ano_range[1]) & 
    (df_sinan['latitude'].notna()) & 
    (df_sinan['longitude'].notna()) &
    (df_sinan['bairro'].notna())
].copy()

if tipo_violencia == "Violência Física":
    df_filt = df_filt[df_filt['ocorreu_violencia_fisica'] == 1]
elif tipo_violencia == "Violência Psicológica":
    df_filt = df_filt[df_filt['ocorreu_violencia_psicologica'] == 1]
elif tipo_violencia == "Violência Sexual":
    df_filt = df_filt[df_filt['ocorreu_violencia_sexual'] == 1]

# Agregação por Bairro
df_bairro = df_filt.groupby('bairro').agg(
    total=('ano', 'count'),
    lat=('latitude', 'median'),
    lon=('longitude', 'median')
).reset_index()

# Filtrar bairros muito com poucas ocorrências (ruído ou erros de geoloc) e limites de SP
df_bairro = df_bairro[
    (df_bairro['total'] > 5) &
    (df_bairro['lat'] < -23.3) & (df_bairro['lat'] > -24.0) &
    (df_bairro['lon'] > -46.9) & (df_bairro['lon'] < -46.3)
]

st.markdown(section_header(f"📍 Mapa de Bolhas: Demandas por Bairro (Base 🏥 SINAN - {ano_range[0]}-{ano_range[1]})"), unsafe_allow_html=True)
st.markdown("Cada círculo representa um bairro. O **tamanho** e a **cor** indicam o volume de notificações.")

# Ajuste escala de cores baseada em percentis para melhor visualização
max_val = df_bairro['total'].quantile(0.95)

fig = px.scatter_mapbox(
    df_bairro, 
    lat="lat", lon="lon",
    size="total", 
    color="total",
    hover_name="bairro",
    hover_data={"lat": False, "lon": False, "total": True},
    color_continuous_scale=[
        (0.0, COLORS['primary']),
        (0.5, COLORS['warning']),
        (1.0, COLORS['danger'])
    ],
    range_color=[0, max_val],
    size_max=40,
    zoom=9.5,
    center={"lat": -23.5505, "lon": -46.6333},
    mapbox_style="carto-darkmatter"
)

fig.update_layout(
    margin={"r":0,"t":0,"l":0,"b":0},
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    mapbox=dict(
        style="carto-darkmatter",
        center={"lat": -23.5505, "lon": -46.6333},
        zoom=9.5,
        layers=[
            dict(
                sourcetype='geojson',
                source='https://raw.githubusercontent.com/codigourbano/distritos-sp/master/distritos-sp.geojson',
                type='line',
                color='rgba(255, 255, 255, 0.3)', # Linhas de delimitação física
                line=dict(width=1)
            )
        ]
    )
)

st.plotly_chart(fig, use_container_width=True, height=600)

st.markdown("""
<div class="insight-box">
    💡 <strong>Interpretação Geográfica</strong>: Este mapa permite identificar claramente as 
    bolsas de alta incidência na periferia da cidade (extremo Sul e Leste), onde a demanda por serviços 
    de proteção 24 horas costuma ser mais crítica e as distâncias até as DDMs centrais são maiores.
</div>
""", unsafe_allow_html=True)
