# Resumo da Sessão — Projeto DEAM 24h Brasil

## Contexto do Projeto

**Objetivo:** Avaliação de impacto causal da conversão de DEAMs (Delegacias Especializadas de Atendimento à Mulher) do horário comercial para **plantão 24 horas** em municípios brasileiros.

**Pergunta de pesquisa:** A ampliação do horário reduz a letalidade (feminicídios) e aumenta o acesso institucional (notificações)?

**Cadeia causal (cifra oculta):**
> Conversão para 24h → ↑ acesso (mais notificações fora do horário comercial) → proteção ativa / medidas protetivas → ↓ letalidade (feminicídios)

**Período:** 2009–2019 | **Unidade:** municípios brasileiros | **Metodologia:** Callaway & Sant'Anna (2021) DiD com adoção escalonada

---

## Estrutura de Dados

### Fontes Primárias
- **SIM** (Sistema de Informações sobre Mortalidade): feminicídios — `sexo==2` é feminino
- **SINAN** (Sistema de Informação de Agravos de Notificação): notificações de violência contra a mulher — `sexo_paciente==0` é feminino (codificação diverge do SIM; confirmado via cross-tab com `gestante_paciente`)
- **SIDRA IBGE** (tabela 6579, variável 9324): população municipal estimada por ano
- **Planilhas DEAMs**: `dados_deams_24h.xlsx` (38 municípios tratados) e `dados_deams_comercial.xlsx` (247 controles)

### Variáveis do Painel Final (`dados/consolidado/painel_deam_anual.csv`)
| Coluna | Descrição |
|--------|-----------|
| `id_municipio` | IBGE 7 dígitos (chave de junção) |
| `ano` | 2009–2019 |
| `grupo` | "24h" ou "comercial" |
| `coorte` | Ano de adoção (0 = nunca tratado) |
| `feminicidios` | Contagem absoluta (SIM) |
| `notificacoes` | Contagem absoluta (SINAN) |
| `populacao` | Estimativa IBGE |
| `taxa_feminicidios` | Por 100k hab |
| `taxa_notificacoes` | Por 100k hab |
| `tratado` | 1 se grupo==24h |
| `pos_tratamento` | 1 se ano >= coorte |
| `tratamento_ativo` | 1 se tratado & pos_tratamento |

**Dimensões:** 285 municípios × 11 anos = 3.135 linhas (painel balanceado)

---

## Arquivos Criados / Modificados

### `codes/extracao_filtragem/parear_municipios_ibge.py`
- Pareamento fuzzy (difflib) dos nomes de cidades das planilhas DEAMs com `municipios_br.csv` (IBGE)
- Dicionário `CORRECOES` com 12 correções manuais (erros de digitação, UF errada, nomes truncados, municípios renomeados)
- Exemplos: `("Embu","SP") → ("Embu das Artes","SP")`, `("Ariquemes","TO") → ("Ariquemes","RO")`
- Outputs: `dados_deams_24h_com_id.xlsx`, `dados_deams_comercial_com_id.xlsx`

### `codes/extracao_filtragem/ibge/fetch_populacao.py`
- Consulta SIDRA API (tabela 6579) em lotes de 50 municípios
- Interpolação linear para 2010 (ano censitário ausente na SIDRA)
- Output: `dados/ibge/populacao_municipios.csv` (3.135 linhas, 0 missings)

### `codes/analise_dados/agregar_painel_anual.py`
- `construir_referencia_municipios()`: merge 24h + comercial, precedência ao 24h nos 3 municípios sobrepostos
- `agregar_sim()`: feminicídios por município-ano (sexo==2)
- `agregar_sinan()`: leitura em chunks de 300k linhas, filtra sexo_paciente==0, conta notificações + subtypes (física/sexual/psicológica/parceiro)
- `montar_painel()`: painel balanceado, merge de população, cálculo das 6 colunas taxa_*
- Outputs: `painel_deam_anual.csv`, `feminicidios_anual.csv`, `notificacoes_anual.csv`

### `codes/inferencia_causal/diagnostico_callaway_santanna.py`
- Suite completa CS DiD: 999 bootstrap, cluster por id_municipio
- Funções: `descritivas()`, `fig_adocao()`, `fig_raw_trends()`, `teste_pretrends()` (Wald), `processar_desfecho()` (event study + heatmap + cohort effects), `fig_forest()`, `escrever_relatorio()`
- Gera 11 PNGs em `relatorios/figuras_causal/` + relatório markdown + CSVs
- Copia event study PNGs para `codes/streamlit/assets/`

### `codes/inferencia_causal/modelo_causal_brasil.py`
- Runner limpo: lê painel, roda CS DiD para os 2 outcomes, imprime resultados no terminal
- **Não gera imagens locais nem salva arquivos** (por decisão do usuário — gráficos ficam em `diagnostico_callaway_santanna.py`)
- `OUTCOMES` dict com chave `"col"` apontando para as colunas `taxa_*`

### `codes/inferencia_causal/generate_notebook_brasil.py`
- Gera `modelo_causal_brasil.ipynb` programaticamente via `json.dumps` (convenção do projeto para evitar erros de escape LaTeX/acentos)
- 21 células: 12 markdown + 9 código, cobrindo toda a metodologia
- Notebook executado via `jupyter nbconvert --execute --inplace`: 0 erros, 8 imagens embutidas

### `codes/streamlit/utils/data_loader.py`
- Adicionados: `load_painel_deam()`, `load_feminicidios_anual()`, `load_notificacoes_anual()`

### `requirements.txt`
- Adicionados: `tabulate>=0.9`, `scipy>=1.10`, `jupyter>=1.0`

---

## Resultados do Modelo Causal

### ATT Global (Callaway & Sant'Anna, taxa /100k)

| Desfecho | ATT | SE | IC 95% | p-valor | Esperado | Obtido |
|----------|-----|-----|--------|---------|---------|--------|
| Notificações /100k | −20,513 | 7,418 | [−35,312; −6,578] | 0,0010 | ↑ | ↓ significativo |
| Feminicídios /100k | +0,438 | 0,255 | [−0,054; +0,913] | 0,0821 | ↓ | ↑ marginal |

### Teste de Pré-Tendências (Wald diagonal)

| Desfecho | Wald | p-valor | Nº coefs pré | Indiv. signif. | Resultado |
|----------|------|---------|--------------|----------------|-----------|
| Notificações /100k | 24,141 | 0,0041 | 9 | 2 | **VIOLAÇÃO** |
| Feminicídios /100k | 12,948 | 0,165 | 9 | 1 | OK |

### Interpretação Honesta
1. **Feminicídios**: pré-tendências passam; ATT=+0,44 (p=0,082) — sinal contrário ao esperado, mas marginalmente não-significativo. Possível endogeneidade: municípios adotam 24h em resposta a piora na violência.
2. **Notificações**: pré-tendências **falham** (p=0,004) — o ATT=−20,5 captura tendência preexistente, não efeito causal puro. Resultado não confiável sem covariáveis.
3. **Próximo passo**: `estimation_method='dr'` (doubly-robust) com covariáveis socioeconômicas (IDH, renda, urbanização) + `control_group='not_yet_treated'` + `anticipation=1`.

---

## Decisões Técnicas Relevantes

| Problema | Solução adotada |
|----------|----------------|
| Heterogeneidade de porte municipal (tratados 3,4× maiores) | Normalizar por população → taxas /100k |
| Ano censitário 2010 ausente na SIDRA | Interpolação linear entre 2009 e 2011 |
| Codificação divergente de sexo SIM/SINAN | SIM sexo==2=feminino; SINAN sexo_paciente==0=feminino (confirmado por gestante_paciente) |
| Adoção escalonada invalida TWFE clássico | CS DiD com never_treated como controle |
| Escapes LaTeX/acentos em JSON do notebook | Geração programática via json.dumps |
| Coluna `coorte=0` para controles | Mapeada para `first_treat=0` na estimação CS |

---

## Pendências / Próximos Passos Sugeridos

- [ ] Reestimar com `estimation_method='dr'` e covariáveis socioeconômicas
- [ ] Testar `control_group='not_yet_treated'` e `anticipation=1`
- [ ] Integrar visualizações causais no dashboard Streamlit
- [ ] Investigar pré-tendência de notificações: covariável de tendência municipal?
- [ ] Avaliar se `modelo_causal_brasil.py` precisa das remoções finais de imagem/export (pendente da última sessão)

---

## Estrutura de Diretórios Relevante

```
deam-br/
├── codes/
│   ├── extracao_filtragem/
│   │   ├── parear_municipios_ibge.py       ← pareamento DEAM↔IBGE
│   │   └── ibge/fetch_populacao.py         ← população SIDRA
│   ├── analise_dados/
│   │   └── agregar_painel_anual.py         ← construção do painel
│   ├── inferencia_causal/
│   │   ├── modelo_causal_brasil.py         ← runner terminal
│   │   ├── diagnostico_callaway_santanna.py← gráficos + relatório
│   │   ├── generate_notebook_brasil.py     ← gerador do notebook
│   │   └── modelo_causal_brasil.ipynb      ← notebook executado
│   └── streamlit/
│       ├── utils/data_loader.py
│       └── assets/                         ← PNGs copiados para o app
├── dados/
│   ├── consolidado/
│   │   ├── painel_deam_anual.csv           ← painel principal (3135 linhas)
│   │   ├── feminicidios_anual.csv
│   │   └── notificacoes_anual.csv
│   └── ibge/populacao_municipios.csv
└── relatorios/
    ├── figuras_causal/                     ← 11 PNGs da metodologia CS
    └── estatisticas_causal.md              ← relatório automático
```
