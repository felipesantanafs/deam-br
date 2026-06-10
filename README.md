<div align="center">

# 🔬 Delegacias de Defesa da Mulher — Avaliação de Impacto

**Violência contra Mulheres no Município de São Paulo:**
*Diagnóstico Espaço-Temporal e Avaliação de Impacto das DDMs*

[![Status](https://img.shields.io/badge/Status-Em%20Desenvolvimento-yellow?style=for-the-badge)]()
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)]()
[![Basedosdados](https://img.shields.io/badge/Base_dos_Dados-BigQuery-150458?style=for-the-badge)]()

---

*Projeto de pesquisa focado na avaliação de políticas sociais no município de São Paulo.*

</div>

---

## 📋 Sumário

- [Sobre o Projeto](#-sobre-o-projeto)
- [Delegacias na Capital (DDMs 24h vs. Comercial)](#-delegacias-de-defesa-da-mulher-ddms-na-capital)
- [Problema de Pesquisa](#-problema-de-pesquisa)
- [Cadeia Causal](#-cadeia-causal)
- [Metodologia](#-metodologia)
- [Estrutura do Repositório](#-estrutura-do-repositório)
- [Dados](#-dados)
- [Como Extrair os Dados](#-como-extrair-os-dados)
- [Roadmap](#-roadmap)

---

## 🎯 Sobre o Projeto

Este repositório contém o código-fonte, dados e relatórios do projeto de pesquisa que investiga a **eficácia das Delegacias de Defesa da Mulher (DDMs) com funcionamento 24 horas no município de São Paulo**.

O estudo combina **ciência de dados descritiva** (mapas de calor territoriais e funil da violência) com **avaliação de impacto causal** (Diferenças-em-Diferenças intra-municipal), produzindo evidências acionáveis para subsidiar a avaliação de políticas sociais e otimizar a rede de proteção à mulher na capital paulista.

**Período de análise padronizado: 2015–2019** (a partir da Lei do Feminicídio até o limite do SINAN disponível).

---

## 🏢 Delegacias de Defesa da Mulher (DDMs) na Capital

O município de São Paulo conta com **9 Delegacias de Defesa da Mulher (DDMs)** de atuação territorial. Destas, **3 unidades operam em regime de plantão 24 horas** e **6 operam exclusivamente em horário comercial (09h às 18h)**.

Abaixo está o detalhamento de funcionamento, telefones e localização de cada unidade:

| DDM | Região | Endereço | Telefone | Funcionamento |
| :--- | :--- | :--- | :--- | :--- |
| **1ª DDM Centro** | Centro | Rua Vieira Ravasco, 26, Cambuci (dentro da Casa da Mulher Brasileira) | (11) 3275-8000 | 🟢 **24 Horas** |
| **2ª DDM Sul** | Zona Sul | Avenida Onze de Julho, 89 - Saúde | (11) 5084-2579 | 🕒 **Horário Comercial (09h-18h)** |
| **3ª DDM Oeste** | Zona Oeste | Avenida Corifeu de Azevedo Marques, 4300 - 2º andar - Jaguaré | (11) 3768-4664 | 🕒 **Horário Comercial (09h-18h)** |
| **4ª DDM Norte** | Zona Norte | Avenida Itaberaba, 731 - 1º andar - Freguesia do Ó | (11) 3976-2908 | 🕒 **Horário Comercial (09h-18h)** |
| **5ª DDM Leste** | Zona Leste | Rua Dr. Corinto Baldoíno Costa, 400 - 2º andar - Tatuapé | (11) 2293-3816 | 🕒 **Horário Comercial (09h-18h)** |
| **6ª DDM Campo Grande** | Zona Sul | Rua Sargento Manoel Barbosa da Silva, nº 115 - 2º andar - Campo Grande | (11) 5521-6068 / 5686-8567 | 🕒 **Horário Comercial (09h-18h)** |
| **7ª DDM Leste (Itaquera)** | Zona Leste | Rua Sabbado D'Angelo, 46 - Itaquera | (11) 2071-3488 / 2071-4707 | 🟢 **24 Horas** |
| **8ª DDM Leste** | Zona Leste | Avenida Osvaldo do Valle Cordeiro, 190 - 2º andar - Jd. Marília | (11) 2742-1701 | 🟢 **24 Horas** |
| **9ª DDM Oeste (Pirituba)** | Zona Oeste | Avenida Menotti Laudisio, 286 - 2º andar - Pirituba | (11) 3974-8890 | 🕒 **Horário Comercial (09h-18h)** |

---

## 🔍 Problema de Pesquisa

A violência contra mulheres exige respostas capilarizadas e com disponibilidade ininterrupta, visto que grande parte das agressões em contexto doméstico ocorre durante madrugadas e finais de semana — períodos nos quais DDMs de horário comercial encontram-se fechadas.

O projeto busca responder à seguinte questão principal:
> **As DDMs que funcionam 24 hrs na cidade de São Paulo possuem maior impacto na ampliação de registros (redução da subnotificação) e na prevenção de feminicídios em seus distritos de abrangência, em comparação àquelas que funcionam apenas em horário comercial?**

---

## 🔗 Cadeia Causal

O projeto resolve o paradoxo econométrico da **causalidade reversa de registro**. Avaliar o sucesso de uma delegacia apenas pelo volume de denúncias é falho, pois a delegacia estimula o relato de crimes que já existiam (cifra oculta). 

Para contornar isso, o modelo possui duas variáveis dependentes:

```mermaid
flowchart LR
    A["🏛️ Inauguração/Conversão\nDDM 24h"] --> B["📈 Aumento de Acesso\n(Denúncias/SINAN)"]
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
- **Análise Descritiva Espacial:** Mapas de densidade (Heatmaps) por Bairro e Subprefeitura.
- **Integração de Bases e Geolocalização (SINAN + CNES):** Como a base do SINAN omite endereços exatos para preservação da privacidade das vítimas, adotamos a **Hipótese de Proxy Espacial (Bairro de Atendimento)**. O SINAN é cruzado com o diretório geocodificado do CNES através da chave do estabelecimento notificador (`id_unidade_notificacao` = `id_estabelecimento_cnes`). *Foi aplicado um patch manual de geolocalização aos 5 principais hospitais públicos do município para corrigir falhas no CEP do diretório CNES, recuperando cerca de 15.000 registros na base final*. Assume-se que a vítima de agressão grave busca socorro imediato no próprio bairro ou em bairros vizinhos. Desse modo, o bairro do estabelecimento de saúde serve como proxy geográfico do local da agressão.
- **Funil da Violência:** Evolução e correlação temporal entre Ameaças (SINAN), Violência Física (SINAN) e Feminicídios (SIM) na capital, no período padronizado de **2015–2019**.
- **Sazonalidade:** Gráficos temporais cruzando horários e dias da semana.

### Etapa 2 — Avaliação de Impacto Causal
- **Método:** Modelo empírico em duas camadas:
  1. **Efeito Global:** Diferenças-em-Diferenças em painel comparando a presença da DDM vs ausência, usando **Propensity Score Matching (PSM)** para parear controles socioeconômicos da Fundação SEADE.
  2. **Efeito 24h:** Estimador de **Callaway & Sant'Anna (2021) / CS DiD** para corrigir o viés de Goodman-Bacon em tratamentos escalonados no tempo, comparando as coortes de conversão (2016 e 2018) com distritos-controle "limpos".
- **Heterogeneidade:** O modelo integra a **Dummy Racial Global** para mensurar impactos assimétricos sobre populações de mulheres negras (Preta+Parda).

### Produto Final
- 📊 Relatório técnico para tomada de decisão (Word).
- 🖥️ Dashboard interativo (Streamlit) com o mapa da capital e simulador de impactos.

---

## 📁 Estrutura do Repositório

```text
deams-pp-aps/
│
├── 📄 README.md                    # Este arquivo
├── 📄 pyproject.toml               # Dependências e metadados do projeto
│
├── 📂 codes/                       # Scripts organizados por fases de desenvolvimento
│   ├── 📂 extracao_filtragem/      # Extração (APIs/BigQuery) e higienização inicial
│   │   ├── bd_config.py            # ⚠️ LOCAL APENAS — credenciais GCP (Não versionado)
│   │   ├── extract_cnes_bd.py      # Query de estabelecimentos geolocalizados do CNES (Com patch manual)
│   │   ├── extract_sim_bd.py       # Query de feminicídios notificados no SIM/DataSUS
│   │   ├── extract_sinan_bd.py     # Query de notificações de agressões no SINAN/DataSUS
│   │   └── merge_sinan_cnes.py     # Cruzamento SINAN + CNES usando a chave do hospital
│   │
│   ├── 📂 analise_dados/           # Análise exploratória e visualizações
│   │   └── eda_funil_violencia.py  # Análise do Funil da Violência e geração de gráficos
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
│   │       ├── 5_👤_Perfil_Vitimas.py
│   │       ├── 6_⏰_Sazonalidade.py
│   │       └── 7_🚨_Analise_DDMs.py
│   │
│   └── 📂 inferencia_causal/       # Estimação do modelo econométrico DiD (Próxima Etapa)
│       └── .gitkeep
│
├── 📂 dados/                       # Armazenamento estruturado de fontes e consolidações
│   ├── 📂 sim/                     # Dados provenientes do SIM (Sistema de Mortalidade)
│   │   └── sim_feminicidios_sp.csv # Óbitos por agressão contra mulheres (DataSUS)
│   │
│   ├── 📂 sinan/                   # Dados provenientes do SINAN (Notificações)
│   │   └── sinan_cnes_merged.csv   # Base integrada espacialmente ao CNES (107k reg.)
│   │
│   └── 📂 consolidado/             # Bases prontas agregadas para visualização/modelagem
│       └── funil_violencia_ano.csv # Tabela agregada anual do Funil da Violência (2015-2019)
│
└── 📂 relatorios/                  # Relatórios gerenciais e imagens geradas
    ├── PROJETO DE PESQUISA-VIOLENCIA SP.docx
    ├── PROJETO DE PESQUISA-VIOLENCIA SP.txt
    └── funil_violencia.png         # Gráfico temporal de evolução do funil
```

> **Nota:** Dados da SSP (Secretaria de Segurança Pública), CNES bruto e SINAN bruto foram movidos para o `.gitignore` por incompatibilidade com a análise padronizada SINAN+SIM (2015–2019). Os scripts de extração SSP (`data_filter_sicpv.py`, `pipeline_feminicidio.py`) também foram ignorados.

---

## 📊 Dados

Os microdados são obtidos diretamente via integração com o data lake público da **Base dos Dados (BigQuery)**, evitando downloads massivos de repositórios legados do DataSUS.

**Período padronizado: 2015–2019** (início da Lei do Feminicídio até o último ano disponível no SINAN).

| Base | Fonte Original | Registros (2015–2019) | Papel no Modelo |
|------|----------------|-----------------------|-----------------|
| **SINAN+CNES** | DataSUS + CNES | **107.212** notificações | Acesso (Ameaça/Lesão) — proxy geográfico via CNES |
| **SSP-SP** | SSP (dados abertos) | **118** BOs | Letalidade (Feminicídios) no modelo DiD (geolocalização via DP territorial) |
| **SIM** | DataSUS | **525** óbitos | Diagnóstico de Óbitos a nível municipal (sem uso no DiD devido à ausência de bairro) |
| **SEADE** | Gov. SP | *96 distritos* | Covariáveis (Controles socioeconômicos para PSM) |

---

## 🚀 Como Extrair os Dados

Os scripts em Python dentro da pasta `codes/extracao_filtragem/` já possuem as *queries* SQL otimizadas para processar os dados em nuvem antes de baixar, trazendo apenas o escopo geográfico e de perfil do nosso estudo.

### Pré-requisitos

1. Ter Python 3.10+ instalado com Pandas, `basedosdados` e bibliotecas de excel:
   ```bash
   pip install pandas basedosdados openpyxl xlrd
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
   python codes/extracao_filtragem/extract_cnes_bd.py
   python codes/extracao_filtragem/extract_sim_bd.py
   python codes/extracao_filtragem/extract_sinan_bd.py
   python codes/extracao_filtragem/merge_sinan_cnes.py
   ```
4. Os arquivos processados e consolidados aparecerão automaticamente organizados nas respectivas subpastas da pasta `dados/`.

---

## 🖥️ Dashboard Interativo (Streamlit)

A Fase 1 está acoplada a um painel analítico dinâmico desenvolvido no Streamlit com uma identidade visual premium adaptada às cores da **FEA-USP** (azul marinho e elementos de alta visibilidade/contraste).

**Bases utilizadas no dashboard:** exclusivamente **SINAN+CNES** e **SIM** (período 2015–2019).

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

- [x] Reestruturação do escopo do projeto (Foco em São Paulo e DiD Intra-municipal)
- [x] Criação das *queries* otimizadas para extração SIM/SINAN via Base dos Dados
- [x] Extração dos microdados SIM (525 registros — 2015-2019) e SINAN+CNES (107.212 registros — 2015-2019)
- [x] Construção do Funil da Violência e EDA Espaço-Temporal
- [x] Construção do Dashboard Interativo Premium no Streamlit (7 abas funcionais com mapas e sazonalidade)
- [x] Padronização do período de análise para 2015–2019 (somente SINAN+SIM)
- [x] Mapa de calor espacial com localização das DDMs e correção de geolocalização do CNES
- [x] Estimação do modelo econométrico causal DiD em duas camadas (Global e Callaway & Sant'Anna) com moderação racial
