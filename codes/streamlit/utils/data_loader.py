"""
Módulo centralizado de carregamento e cache dos dados — escopo NACIONAL.

Estudo DEAM 24h (Brasil, 2009-2019): avaliação de impacto da conversão de
Delegacias Especializadas de Atendimento à Mulher para o regime de plantão 24h.

Fonte mestre: painel municipal anual balanceado (285 municípios × 11 anos),
integrando feminicídios (SIM) e notificações de violência (SINAN), mais os
agregados temporais (hora/mês/dia) pré-processados para a análise de sazonalidade.
"""
import json
import os

import pandas as pd
import streamlit as st

# dados/ na raiz do repositório (utils -> streamlit -> codes -> raiz)
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'dados'))
CONS_DIR = os.path.join(DATA_DIR, 'consolidado')
ASSETS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'assets'))


# ─── Painel mestre e séries tidy ─────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner="Carregando painel municipal DEAM (2009-2019)...")
def load_painel_deam() -> pd.DataFrame:
    """
    Painel municipal balanceado (município × ano) das 285 cidades com DEAM,
    integrando feminicídios (SIM) e notificações (SINAN) anualmente.

    Pronto para inferência causal (staggered DiD / Callaway & Sant'Anna):
      - grupo:            '24h' (tratado) ou 'comercial' (controle)
      - coorte:           ano de adoção do regime 24h (0 = nunca tratado)
      - tratamento_ativo: 1 a partir do ano de adoção nas cidades tratadas
    Métricas anuais por município (contagem e taxa /100k): feminicidios,
    notificacoes, viol_fisica, viol_sexual, viol_psicologica, viol_parceiro.
    """
    return pd.read_csv(os.path.join(CONS_DIR, 'painel_deam_anual.csv'))


@st.cache_data(ttl=3600, show_spinner="Carregando feminicídios anuais...")
def load_feminicidios_anual() -> pd.DataFrame:
    """Série anual de feminicídios (SIM) por município com DEAM."""
    return pd.read_csv(os.path.join(CONS_DIR, 'feminicidios_anual.csv'))


@st.cache_data(ttl=3600, show_spinner="Carregando notificações anuais...")
def load_notificacoes_anual() -> pd.DataFrame:
    """Série anual de notificações (SINAN) por município com DEAM."""
    return pd.read_csv(os.path.join(CONS_DIR, 'notificacoes_anual.csv'))


# ─── Agregados temporais (sazonalidade / horário) ────────────────────
@st.cache_data(ttl=3600, show_spinner="Carregando distribuição horária...")
def load_saz_hora() -> pd.DataFrame:
    """Contagem de notificações por (grupo, periodo, hora 0-23)."""
    return pd.read_csv(os.path.join(CONS_DIR, 'saz_hora.csv'))


@st.cache_data(ttl=3600)
def load_saz_mes() -> pd.DataFrame:
    """Contagem de notificações por (grupo, periodo, mes 1-12)."""
    return pd.read_csv(os.path.join(CONS_DIR, 'saz_mes.csv'))


@st.cache_data(ttl=3600)
def load_saz_dow() -> pd.DataFrame:
    """Contagem de notificações por (grupo, periodo, dia da semana 0=Seg..6=Dom)."""
    return pd.read_csv(os.path.join(CONS_DIR, 'saz_dow.csv'))


@st.cache_data(ttl=3600)
def load_saz_resumo() -> pd.DataFrame:
    """Notificações dentro x fora do horário comercial por grupo/periodo."""
    return pd.read_csv(os.path.join(CONS_DIR, 'saz_resumo.csv'))


# ─── Inferência causal ───────────────────────────────────────────────
@st.cache_data(ttl=3600)
def load_causal_results() -> dict:
    """Resultados do modelo CS DiD (ATT, event study, robustez)."""
    path = os.path.join(CONS_DIR, 'causal_results.json')
    if not os.path.exists(path):
        return {}
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


@st.cache_data(ttl=3600)
def load_causal_panel() -> pd.DataFrame:
    """Painel usado na estimação causal (inclui first_treat)."""
    path = os.path.join(CONS_DIR, 'causal_panel.csv')
    if os.path.exists(path):
        return pd.read_csv(path)
    return load_painel_deam().rename(columns={'coorte': 'first_treat'})


@st.cache_data(ttl=3600)
def load_geojson_uf() -> dict | None:
    """GeoJSON das UFs do Brasil (chave de junção: properties.sigla)."""
    path = os.path.join(ASSETS_DIR, 'brasil_uf.geojson')
    if not os.path.exists(path):
        return None
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


# ─── Agregações reutilizáveis ────────────────────────────────────────
@st.cache_data(ttl=3600)
def serie_nacional_anual(grupo: str | None = None) -> pd.DataFrame:
    """
    Série nacional por ano: somatórios de eventos e taxas /100k corretas
    (total de eventos / população total × 100k). `grupo` filtra '24h'/'comercial'.
    """
    df = load_painel_deam()
    if grupo:
        df = df[df['grupo'] == grupo]
    agg = df.groupby('ano').agg(
        feminicidios=('feminicidios', 'sum'),
        notificacoes=('notificacoes', 'sum'),
        viol_fisica=('viol_fisica', 'sum'),
        viol_sexual=('viol_sexual', 'sum'),
        viol_psicologica=('viol_psicologica', 'sum'),
        viol_parceiro=('viol_parceiro', 'sum'),
        populacao=('populacao', 'sum'),
        municipios=('id_municipio', 'nunique'),
    ).reset_index()
    for m in ['feminicidios', 'notificacoes', 'viol_fisica',
              'viol_sexual', 'viol_psicologica', 'viol_parceiro']:
        agg[f'taxa_{m}'] = (agg[m] / agg['populacao'] * 100_000).round(3)
    return agg


@st.cache_data(ttl=3600)
def referencia_municipios() -> pd.DataFrame:
    """1 linha por município: grupo, coorte, uf, regiao, população 2019."""
    df = load_painel_deam()
    pop19 = df[df['ano'] == 2019][['id_municipio', 'populacao']]
    ref = (df[['id_municipio', 'municipio', 'uf', 'regiao', 'grupo', 'coorte']]
           .drop_duplicates('id_municipio')
           .merge(pop19, on='id_municipio', how='left'))
    return ref


# ─── Rótulos e paletas de domínio ────────────────────────────────────
MESES = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun',
         'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']

DIAS_SEMANA = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom']

REGIAO_COLORS = {
    'Norte':        '#27AE60',
    'Nordeste':     '#F39C12',
    'Centro-Oeste': '#8E44AD',
    'Sudeste':      '#2E86C1',
    'Sul':          '#E74C3C',
}

GRUPO_COLORS = {
    '24h':       '#2E86C1',   # tratado
    'comercial': '#95A5A6',   # controle
}

PERIODO_COLORS = {
    'Antes 24h':  '#F39C12',
    'Depois 24h': '#2E86C1',
    'Comercial':  '#95A5A6',
}
