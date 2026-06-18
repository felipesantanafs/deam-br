<div align="center">

# 🔬 Delegacias de Defesa da Mulher — Avaliação de Impacto

**Violência contra Mulheres no Brasil:**
*Diagnóstico Espaço-Temporal e Avaliação de Impacto das DEAMs em Escala Nacional*

[![Status](https://img.shields.io/badge/Status-Em%20Desenvolvimento-yellow?style=for-the-badge)]()
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)]()
[![Basedosdados](https://img.shields.io/badge/Base_dos_Dados-BigQuery-150458?style=for-the-badge)]()

---

*Projeto de pesquisa focado na avaliação de políticas públicas de enfrentamento à violência contra mulheres em todo o território brasileiro.*

</div>

---

## 📋 Sumário

- [Sobre o Projeto](#-sobre-o-projeto)
- [DEAMs no Brasil](#-delegacias-especializadas-de-atendimento-à-mulher-deams-no-brasil)
- [Problema de Pesquisa](#-problema-de-pesquisa)
- [Cadeia Causal](#-cadeia-causal)
- [Metodologia](#-metodologia)
- [Estrutura do Repositório](#-estrutura-do-repositório)
- [Dados](#-dados)
- [Como Extrair os Dados](#-como-extrair-os-dados)
- [Roadmap](#-roadmap)

---

## 🎯 Sobre o Projeto

Este repositório contém o código-fonte, dados e relatórios do projeto de pesquisa que investiga a **eficácia das Delegacias Especializadas de Atendimento à Mulher (DEAMs) com funcionamento 24 horas em todo o território brasileiro**.

O estudo combina **ciência de dados descritiva** (mapas de calor territoriais e funil da violência) com **avaliação de impacto causal** (Diferenças-em-Diferenças com tratamento escalonado), produzindo evidências acionáveis para subsidiar a avaliação de políticas públicas e otimizar a rede de proteção à mulher em escala nacional.

**Período de análise padronizado: 2009–2019** (abrangendo a Lei Maria da Penha consolidada até o limite do SINAN disponível).

---

## 🏢 Delegacias Especializadas de Atendimento à Mulher (DEAMs) no Brasil

O Brasil conta com **339 Delegacias Especializadas de Atendimento à Mulher (DEAMs)** distribuídas pelos 26 estados e o Distrito Federal. Destas, um subconjunto opera em **regime de plantão 24 horas**, enquanto a maioria funciona exclusivamente em **horário comercial**.

A base de dados de DEAMs utilizada neste projeto foi construída a partir da raspagem e enriquecimento de dados públicos, resultando em um cadastro com informações de município, UF, regime de funcionamento (comercial ou 24h) e ano de implementação do regime 24h (quando aplicável).

> [!NOTE]
> A classificação das DEAMs em "24 horas" e "Comercial" é fundamental para a estratégia de identificação causal do projeto. DEAMs que foram convertidas para o regime 24h entre 2009 e 2019 constituem o **grupo de tratamento**, enquanto as DEAMs em horário comercial servem como **grupo de controle**.

---

## 🔍 Problema de Pesquisa

A violência contra mulheres exige respostas capilarizadas e com disponibilidade ininterrupta, visto que grande parte das agressões em contexto doméstico ocorre durante madrugadas e finais de semana — períodos nos quais DEAMs de horário comercial encontram-se fechadas.

O projeto busca responder à seguinte questão principal:
> **As DEAMs que funcionam 24 horas no Brasil possuem maior impacto na ampliação de registros (redução da subnotificação) e na prevenção de feminicídios nos seus municípios de abrangência, em comparação àquelas que funcionam apenas em horário comercial?**

---

## 🔗 Cadeia Causal

O projeto resolve o paradoxo econométrico da **causalidade reversa de registro**. Avaliar o sucesso de uma delegacia apenas pelo volume de denúncias é falho, pois a delegacia estimula o relato de crimes que já existiam (cifra oculta). 

Para contornar isso, o modelo possui duas variáveis dependentes:

```mermaid
flowchart LR
    A["🏛️ Inauguração/Conversão\nDEAM 24h"] --> B["📈 Aumento de Acesso\n(Denúncias/SINAN)"]
    B --> C["🛡️ Proteção Ativa"]
    C --> D["📉 Redução de Letalidade\n(Feminicídios/SIM)"]

    style A fill:#4a90d9,color:#fff,stroke:#2c5f8a
    style B fill:#f5a623,color:#fff,stroke:#c48418
    style C fill:#7b68ee,color:#fff,stroke:#5b48ce
    style D fill:#50c878,color:#fff,stroke:#3a9a5a
```

> [!NOTE]
> Um coeficiente positivo na variável de denúncias (Ameaça/Lesão) indica **sucesso no acesso institucional**, e um coeficiente negativo na variável de óbitos indica **sucesso na eficácia protetiva da vida**.

---

## 📐 Metodologia

### Etapa 1 — Diagnóstico e Ciência de Dados
- **Análise Descritiva Espacial:** Mapas de densidade (Heatmaps) por município e UF em todo o Brasil.
- **Integração de Bases (SINAN + CNES):** Cruzamento dos microdados do SINAN com o diretório geocodificado do CNES através da chave do estabelecimento notificador (`id_unidade_notificacao` = `id_estabelecimento_cnes`), utilizando a **Hipótese de Proxy Espacial (Município de Atendimento)**. Assume-se que a vítima de agressão grave busca socorro imediato no próprio município ou em municípios vizinhos. Desse modo, o município do estabelecimento de saúde serve como proxy geográfico do local da agressão.
- **Funil da Violência:** Evolução e correlação temporal entre Ameaças (SINAN), Violência Física (SINAN) e Feminicídios (SIM) em escala nacional, no período padronizado de **2009–2019**.
- **Sazonalidade:** Gráficos temporais cruzando horários e dias da semana.

### Etapa 2 — Avaliação de Impacto Causal
- **Método:** Modelo empírico em duas camadas:
  1. **Efeito Global:** Diferenças-em-Diferenças em painel comparando municípios com presença de DEAM vs. municípios sem DEAM, usando **Propensity Score Matching (PSM)** para parear controles socioeconômicos.
  2. **Efeito 24h:** Estimador de **Callaway & Sant'Anna (2021) / CS DiD** para corrigir o viés de Goodman-Bacon em tratamentos escalonados no tempo, comparando os municípios cujas DEAMs foram convertidas para 24h com municípios-controle "limpos".
- **Heterogeneidade:** O modelo integra a **Dummy Racial Global** para mensurar impactos assimétricos sobre populações de mulheres negras (Preta+Parda).

### Produto Final
- 📊 Relatório técnico para tomada de decisão (Word).
- 🖥️ Dashboard interativo (Streamlit) com mapa do Brasil e simulador de impactos.

---

## 📁 Estrutura do Repositório

```text
deam-br/
│
├── 📄 README.md                    # Este arquivo
├── 📄 requirements.txt            # Dependências do projeto
│
├── 📂 codes/                       # Scripts organizados por fases de desenvolvimento
│   ├── 📂 extracao_filtragem/      # Extração (APIs/BigQuery) e higienização inicial
│   │   ├── bd_config.py            # ⚠️ LOCAL APENAS — credenciais GCP (Não versionado)
│   │   ├── extract_sim_bd_detalhada.py  # Query detalhada de feminicídios no SIM/DataSUS (Brasil)
│   │   ├── extract_sinan_bd_detalhada.py # Query detalhada de notificações no SINAN/DataSUS (Brasil)
│   │   ├── limpar_dados_deams.py   # Limpeza e filtragem da base de DEAMs
│   │   └── separar_deams.py        # Separação das DEAMs em 24h e Comercial
│   │
│   ├── 📂 analise_dados/           # Análise exploratória e visualizações
│   │   ├── download_ibge.py        # Download de dados do IBGE
│   │   └── inspect_data.py         # Inspeção rápida de consistência dos dados
│   │
│   ├── 📂 streamlit/               # Dashboard Interativo Premium (FEA-USP)
│   │   ├── Home.py                 # Arquivo de entrada do painel principal
│   │   ├── 📂 assets/              # Plano de fundo minimalista e bases espaciais (GeoJSON)
│   │   ├── 📂 utils/               # Funções de carregamento rápido e geradores de gráficos Plotly
│   │   └── 📂 pages/               # Páginas estruturadas para navegação
│   │       ├── 1_📊_Funil_da_Violencia.py
│   │       ├── 2_📈_Series_Temporais.py
│   │       ├── 3_🏢_Delegacias_Bairros.py
│   │       ├── 4_🗺️_Mapa_Bairros.py
│   │       ├── 5_🔥_Mapa_Calor_DDMs.py
│   │       ├── 6_👤_Perfil_Vitimas.py
│   │       ├── 7_⏰_Sazonalidade.py
│   │       ├── 8_🚨_Analise_DDMs.py
│   │       └── 9_🔬_Modelo_Causal.py
│   │
│   └── 📂 inferencia_causal/       # Estimação do modelo econométrico DiD
│       ├── causal_model.py         # Estimação do modelo DiD e pareamento por PSM
│       ├── generate_notebook.py    # Geração de notebook explicativo
│       └── modelo_causal.ipynb     # Notebook com a execução do modelo
│
├── 📂 dados/                       # Armazenamento estruturado de fontes e consolidações
│   ├── 📂 ibge/                    # Dados e arquivos auxiliares do IBGE
│   │   ├── municipios_br.csv       # Municípios brasileiros e códigos de identificação
│   │   └── 📂 scraping/            # Arquivos da raspagem e processamento das DEAMs
│   │       ├── deam_delegacias_mulher_brasil.csv           # Base bruta de raspagem
│   │       └── deam_delegacias_mulher_brasil_706_enriquecido.csv  # Base enriquecida (pré-filtragem)
│   │
│   ├── 📂 info_delegacias/         # Dados processados das DEAMs
│   │   ├── dados_deams.xlsx        # Base original de DEAMs
│   │   ├── dados_deams_filtrados.xlsx # Base filtrada (apenas Delegacias da Mulher)
│   │   ├── dados_deams_24h.xlsx    # DEAMs com regime 24h (2009–2019)
│   │   └── dados_deams_comercial.xlsx # DEAMs com horário comercial
│   │
│   ├── 📂 sim/                     # Dados provenientes do SIM (Sistema de Mortalidade)
│   │   └── sim_feminicidios_br_detalhada.csv # Microdados detalhados de óbitos (Brasil)
│   │
│   └── 📂 sinan/                   # Dados provenientes do SINAN (Notificações)
│       └── sinan_violencia_br_detalhada.csv # Microdados detalhados de violência (Brasil)
│
└── 📂 relatorios/                  # Relatórios gerenciais e documentos do projeto
    ├── PROJETO DE PESQUISA-VIOLENCIA BR.docx
    └── PROJETO DE PESQUISA-VIOLENCIA BR.txt
```

> **Nota:** Dados da SSP (Secretaria de Segurança Pública de SP), CNES bruto e SINAN bruto filtrado por SP foram removidos/ignorados por incompatibilidade com o escopo nacional. Os scripts de extração legados específicos de SP (`data_filter_sicpv.py`, `pipeline_feminicidio.py`, scripts antigos com sufixo `_sp`) também foram ignorados.

---

## 📊 Dados

Os microdados são obtidos diretamente via integração com o data lake público da **Base dos Dados (BigQuery)**, evitando downloads massivos de repositórios legados do DataSUS.

**Período padronizado: 2009–2019** (abrangendo dados consolidados até o último ano disponível no SINAN).

| Base | Fonte Original | Cobertura Geográfica | Papel no Modelo |
|------|----------------|----------------------|-----------------|
| **SINAN** | DataSUS | **Brasil** — todos os municípios notificadores | Acesso (Ameaça/Lesão) — variável dependente de denúncias |
| **SIM** | DataSUS | **Brasil** — todos os municípios de ocorrência | Letalidade (Feminicídios) — variável dependente de óbitos |
| **DEAMs** | IBGE / Raspagem | **339 DEAMs** em todo o Brasil | Variável de tratamento (regime 24h vs. comercial) |
| **IBGE** | IBGE | **5.570 municípios** | Covariáveis socioeconômicas para PSM |

---

## 🚀 Como Extrair os Dados

Os scripts em Python dentro da pasta `codes/extracao_filtragem/` já possuem as *queries* SQL otimizadas para processar os dados em nuvem antes de baixar, trazendo o escopo nacional.

### Pré-requisitos

1. Ter Python 3.10+ instalado com as dependências listadas no `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```
2. Ter um projeto no **Google Cloud Platform (GCP)**.
3. Estar autenticado no GCP no seu terminal local:
   ```bash
   gcloud auth application-default login
   ```

### Extração e Processamento

1. Entre na pasta dos scripts de extração.
2. Crie o arquivo `codes/extracao_filtragem/bd_config.py` localmente com o seguinte conteúdo:
   ```python
   BILLING_ID = "seu-projeto-id-aqui"
   ```
   > **Atenção:** este arquivo está no `.gitignore` e não é enviado ao GitHub.
3. Execute no terminal a partir da raiz do repositório:
   ```bash
   # Extração dos microdados nacionais
   python codes/extracao_filtragem/extract_sim_bd_detalhada.py
   python codes/extracao_filtragem/extract_sinan_bd_detalhada.py
   
   # Processamento da base de DEAMs
   python codes/extracao_filtragem/limpar_dados_deams.py
   python codes/extracao_filtragem/separar_deams.py
   ```
4. Os arquivos processados e consolidados aparecerão automaticamente organizados nas respectivas subpastas da pasta `dados/`.

---

## 🖥️ Dashboard Interativo (Streamlit)

A Fase 1 está acoplada a um painel analítico dinâmico desenvolvido no Streamlit com uma identidade visual premium adaptada às cores da **FEA-USP** (azul marinho e elementos de alta visibilidade/contraste).

**Bases utilizadas no dashboard:** **SINAN**, **SIM** e **DEAMs** (período 2009–2019, cobertura nacional).

### Como executar localmente:

1. Instale as dependências listadas no `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```
2. Inicialize o dashboard a partir da raiz do repositório:
   ```bash
   streamlit run codes/streamlit/Home.py
   ```
3. O painel abrirá automaticamente em `http://localhost:8501`.

---

## 🗺️ Roadmap

- [x] Reestruturação do escopo do projeto (Foco nacional — Brasil inteiro com 339 DEAMs)
- [x] Criação das *queries* otimizadas para extração SIM/SINAN via Base dos Dados (escopo nacional)
- [x] Extração dos microdados SIM e SINAN detalhados (cobertura 2009–2019, Brasil)
- [x] Raspagem e enriquecimento da base de DEAMs — 339 delegacias filtradas (município, UF, regime, ano 24h)
- [x] Separação das DEAMs em grupos de tratamento (24h) e controle (comercial)
- [x] Construção do Funil da Violência e EDA Espaço-Temporal
- [x] Construção do Dashboard Interativo Premium no Streamlit (9 abas funcionais com mapas e sazonalidade)
- [x] Padronização do período de análise para 2009–2019 (SINAN + SIM)
- [x] Estimação do modelo econométrico causal DiD em duas camadas (Global e Callaway & Sant'Anna) com moderação racial
