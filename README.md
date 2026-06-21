<div align="center">

# 🔬 Delegacias de Defesa da Mulher — Avaliação de Impacto

**Violência contra Mulheres no Brasil:**
*Diagnóstico Espaço-Temporal e Avaliação de Impacto das DEAMs em Escala Nacional*

[![Status](https://img.shields.io/badge/Status-Conclu%C3%ADdo-brightgreen?style=for-the-badge)]()
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
- **Método:** Estimador de **Callaway & Sant'Anna (2021) / CS DiD** para corrigir o viés de Goodman-Bacon em tratamentos escalonados no tempo, com estimação **duplamente robusta** (DR — regressão de resultado + escore de propensão).
- **Covariáveis:** taxa de homicídios masculinos /100k, log da população, log do PIB per capita e variação recente de homicídios masculinos (`delta`) — esta última corrige a **adoção reativa** (municípios que convertem a DEAM após pico de violência), restaurando as tendências paralelas do feminicídio.
- **Achado principal:** após corrigir as tendências paralelas, o efeito sobre a **letalidade não é estatisticamente significativo** (ATT = +0,48/100k, IC inclui zero). O efeito "positivo" anterior era causalidade reversa, não efeito da política.

### Produto Final
- 📄 Relatório técnico completo em **LaTeX/PDF** (`relatorios/relatorios_finais/deam24h_relatorio.pdf`).
- 🖥️ **Dashboard interativo** (Streamlit) — 7 páginas analíticas com dados nacionais 2009–2019.

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
│   │   ├── 📂 sim_sinan/           # Extração dos microdados nacionais
│   │   │   ├── extract_sim_bd_detalhada.py   # Query detalhada de feminicídios no SIM/DataSUS
│   │   │   └── extract_sinan_bd_detalhada.py # Query detalhada de notificações no SINAN/DataSUS
│   │   ├── 📂 deams/               # Processamento da base de DEAMs
│   │   │   ├── limpar_dados_deams.py  # Limpeza e filtragem da base de DEAMs
│   │   │   └── separar_deams.py       # Separação em grupos 24h e Comercial
│   │   └── 📂 ibge/                # Download e pareamento de dados do IBGE
│   │       ├── download_ibge.py       # Download de dados socioeconômicos
│   │       ├── fetch_populacao.py     # Série histórica de população por município
│   │       ├── inspect_data.py        # Inspeção rápida de consistência
│   │       └── parear_municipios_ibge.py # Pareamento de municípios IBGE × DEAMs
│   │
│   ├── 📂 analise_dados/           # Agregações e preparação dos painéis
│   │   ├── agregar_painel_anual.py    # Consolida painel município-ano para o modelo DiD
│   │   └── agregar_sazonalidade.py    # Agrega séries horárias e semanais (SINAN)
│   │
│   ├── 📂 streamlit/               # Dashboard Interativo (FEA-USP)
│   │   ├── Home.py                 # Entrada do painel principal
│   │   ├── 📂 assets/              # Fundo, GeoJSON e imagens do modelo causal
│   │   ├── 📂 utils/               # Carregamento de dados e geradores de gráficos Plotly
│   │   │   ├── data_loader.py
│   │   │   └── charts.py
│   │   └── 📂 pages/               # Sete páginas de navegação
│   │       ├── 1_📊_Funil_da_Violência.py
│   │       ├── 2_📈_Séries_Temporais.py
│   │       ├── 3_🗺️_Panorama_Territorial.py
│   │       ├── 4_🏛️_Adoção_das_DEAMs_24h.py
│   │       ├── 5_⏰_Sazonalidade_e_Horário.py
│   │       ├── 6_⚖️_Tratado_vs_Controle.py
│   │       └── 7_🔬_Modelo_Causal.py
│   │
│   └── 📂 inferencia_causal/       # Estimação do modelo econométrico DiD
│       ├── modelo_causal_brasil.py         # Estimador CS DiD (runner terminal — DR + covariáveis)
│       ├── export_causal_results_json.py   # Exporta causal_results.json p/ o Streamlit (especificação DR final)
│       ├── diagnostico_callaway_santanna.py # Suite de diagnósticos: event study, heatmap, forest, pré-tendências
│       ├── _regen_event_studies.py         # Regenera PNGs do event study com fonte ampliada (relatório)
│       ├── generate_notebook_brasil.py     # Geração do notebook de replicação
│       └── modelo_causal_brasil.ipynb      # Notebook com a execução completa do modelo
│
├── 📂 dados/                       # Armazenamento estruturado de fontes e consolidações
│   ├── 📂 ibge/                    # Dados e arquivos auxiliares do IBGE
│   │   ├── municipios_br.csv       # Municípios brasileiros e códigos de identificação
│   │   └── 📂 scraping/            # Arquivos da raspagem e processamento das DEAMs
│   │       ├── deam_delegacias_mulher_brasil.csv                      # Base bruta de raspagem
│   │       └── deam_delegacias_mulher_brasil_706_enriquecido.csv      # Base enriquecida (pré-filtragem)
│   │
│   ├── 📂 info_delegacias/         # Dados processados das DEAMs
│   │   ├── dados_deams.xlsx        # Base original de DEAMs
│   │   ├── dados_deams_filtrados.xlsx # Base filtrada (apenas Delegacias da Mulher)
│   │   ├── dados_deams_24h.xlsx    # DEAMs com regime 24h (2009–2019)
│   │   └── dados_deams_comercial.xlsx # DEAMs com horário comercial
│   │
│   ├── 📂 sim/                     # Dados provenientes do SIM (Sistema de Mortalidade)
│   │   └── sim_feminicidios_br_detalhada.csv  # Microdados detalhados de óbitos — ignorado pelo git
│   │
│   ├── 📂 sinan/                   # Dados provenientes do SINAN (Notificações)
│   │   └── sinan_violencia_br_detalhada.csv   # Microdados detalhados de violência — ignorado pelo git
│   │
│   └── 📂 consolidado/             # Painel mestre e todos os outputs derivados (rastreados pelo git)
│       ├── painel_deam_anual.csv          # Painel balanceado 285 municípios × 11 anos (32 colunas)
│       ├── causal_results.json            # Resultados CS DiD consumidos pelo Streamlit
│       ├── causal_panel.csv               # Painel com first_treat (usado na aba Tendências)
│       ├── homicidios_gerais_anual.csv    # Homicídios gerais e masculinos (covariável DR)
│       ├── feminicidios_anual.csv         # Série anual de feminicídios por município
│       ├── notificacoes_anual.csv         # Série anual de notificações por município
│       └── saz_{hora,mes,dow,resumo}.csv  # Séries horárias pré-agregadas (sazonalidade)
│
└── 📂 relatorios/                  # Relatórios, apresentações e saídas do modelo
    ├── 📂 pre_relatorio/           # Documentos textuais do projeto de pesquisa
    │   ├── PROJETO DE PESQUISA-VIOLENCIA BR.txt
    │   ├── estatisticas_causal.md
    │   └── resumo_sessao.md
    ├── 📂 relatorios_finais/       # Relatório técnico completo em LaTeX/PDF
    │   ├── deam24h_relatorio.tex
    │   └── deam24h_relatorio.pdf
    ├── 📂 apresentacao/            # Slides da pesquisa (LaTeX Beamer + PPTX)
    │   ├── deam24h_slides.tex
    │   ├── deam24h_slides.pdf
    │   ├── deam24h_slides.pptx
    │   ├── build_pptx.py           # Geração programática do PPTX
    │   └── 📂 render/              # Renderizações PNG dos slides
    ├── 📂 figuras_causal/          # Gráficos gerados pelo modelo causal
    │   ├── 00_adocao_escalonada.png
    │   ├── *_raw_trends.png        # Tendências brutas pré/pós tratamento
    │   ├── *_event_study.png       # Estudos de evento (pré-tendências + ATT)
    │   ├── *_heatmap_gt.png        # Heatmaps dos efeitos por coorte-tempo
    │   ├── *_efeitos_coorte.png    # ATT por coorte de adoção
    │   └── 05_forest_att.png       # Forest plot comparativo (notificações vs feminicídios)
    └── 📂 csv_causal/              # Tabelas de resultados do modelo causal
        ├── descritivas.csv
        ├── notificacoes_event_study.csv
        ├── notificacoes_efeitos_coorte.csv
        ├── feminicidios_event_study.csv
        └── feminicidios_efeitos_coorte.csv
```
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
3. Execute no terminal a partir da raiz do repositório na ordem abaixo:
   ```bash
   # 1. Extração dos microdados nacionais (BigQuery — requer auth GCP)
   python codes/extracao_filtragem/sim_sinan/extract_sim_bd_detalhada.py
   python codes/extracao_filtragem/sim_sinan/extract_sinan_bd_detalhada.py
   python codes/extracao_filtragem/sim_sinan/extract_sim_homicidios_gerais.py  # covariável DR

   # 2. Processamento da base de DEAMs
   python codes/extracao_filtragem/deams/limpar_dados_deams.py
   python codes/extracao_filtragem/deams/separar_deams.py
   python codes/extracao_filtragem/ibge/parear_municipios_ibge.py

   # 3. Download de covariáveis do IBGE (sem auth GCP)
   python codes/extracao_filtragem/ibge/fetch_populacao.py
   python codes/extracao_filtragem/ibge/fetch_pib_percapita.py               # covariável DR

   # 4. Construção do painel mestre e séries temporais
   python codes/analise_dados/agregar_painel_anual.py
   python codes/analise_dados/agregar_sazonalidade.py

   # 5. Estimação causal (CS DiD duplamente robusto) e exportação de resultados
   python codes/inferencia_causal/diagnostico_callaway_santanna.py   # figuras + relatório
   python codes/inferencia_causal/export_causal_results_json.py      # JSON para o Streamlit
   ```
4. Os arquivos processados e consolidados aparecerão automaticamente organizados nas respectivas subpastas da pasta `dados/`.

---

## 🖥️ Dashboard Interativo (Streamlit)

O projeto conta com um painel analítico desenvolvido no Streamlit com identidade visual adaptada às cores da **FEA-USP** (azul marinho e elementos de alto contraste), organizado em **7 páginas**:

| # | Página | Conteúdo |
|---|--------|----------|
| 1 | 📊 Funil da Violência | Evolução nacional de ameaças, lesões e feminicídios |
| 2 | 📈 Séries Temporais | Tendências anuais por UF e grupo de tratamento |
| 3 | 🗺️ Panorama Territorial | Mapa coroplético de incidência por município |
| 4 | 🏛️ Adoção das DEAMs 24h | Adoção escalonada e coortes de tratamento |
| 5 | ⏰ Sazonalidade e Horário | Distribuição horária e semanal das notificações (SINAN) |
| 6 | ⚖️ Tratado vs Controle | Comparativo de tendências pré/pós tratamento |
| 7 | 🔬 Modelo Causal | Resultados CS DiD: event study, heatmaps e forest plot |

**Bases utilizadas:** **SINAN**, **SIM** e **DEAMs** (período 2009–2019, cobertura nacional).

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

## 🗺️ Resultados

- [x] Reestruturação do escopo do projeto (foco nacional — 285 municípios com DEAM, 2009–2019)
- [x] Extração dos microdados SIM e SINAN via Base dos Dados / BigQuery (cobertura nacional)
- [x] Raspagem e enriquecimento da base de DEAMs — 38 tratados (24h) e 247 controles (comercial)
- [x] Download de covariáveis IBGE: população municipal (SIDRA 6579) e PIB per capita (SIDRA 5938)
- [x] Extração de homicídios masculinos (SIM, recorte masculino para evitar containment com feminicídios)
- [x] Construção do painel balanceado município-ano com 32 variáveis (incluindo covariáveis DR)
- [x] Agregação de séries horárias/semanais/mensais para análise de sazonalidade (mecanismo)
- [x] Estimação CS DiD **duplamente robusta** com 4 covariáveis — especificação final validada
- [x] Correção da adoção reativa via `delta_homicidios_masc` (restaurou tendências paralelas do feminicídio)
- [x] Diagnósticos completos: event study, heatmap ATT(g,t), forest plot, teste de pré-tendências
- [x] **Achado principal:** efeito sobre feminicídios não-significativo após correção (ATT +0,48, IC inclui zero); efeito "positivo" anterior era causalidade reversa
- [x] Dashboard Streamlit com 7 páginas — resultados DR atualizados, títulos em todos os gráficos
- [x] Relatório técnico completo em LaTeX/PDF (`relatorios/relatorios_finais/deam24h_relatorio.pdf`)
- [x] Apresentação em LaTeX Beamer exportada para PDF e PPTX (`relatorios/apresentacao/`)
