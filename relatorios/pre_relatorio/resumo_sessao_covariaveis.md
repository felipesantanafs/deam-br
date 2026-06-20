# Resumo da Sessão — Covariáveis e Estimação Doubly-Robust (CS DiD)

> **Data:** 2026-06-20
> **Escopo desta sessão:** adição de covariáveis ao modelo causal nacional (Callaway & Sant'Anna 2021), migração de estimação `reg` → `dr` (doubly-robust), e correção da violação de tendências paralelas do feminicídio.
> **Para que serve este documento:** dar contexto a outro chat que vá editar o **relatório final** (`relatorios/relatorios_finais/deam24h_relatorio.tex`).

---

## 1. Ponto de partida

O modelo causal (`codes/inferencia_causal/modelo_causal_brasil.py`) rodava **sem covariáveis**, com `estimation_method='reg'`, ou seja, sob **tendências paralelas incondicionais**. Não havia dupla robustez nem ajuste por confundidores.

Decisão da sessão: anexar covariáveis socioeconômicas e de violência ao painel e ativar a estimação doubly-robust (`dr`), que combina regressão de resultado + escore de propensão (consistente se um dos dois estiver bem especificado).

---

## 2. Covariáveis adicionadas (resultado final = 4 covariáveis)

| Covariável | O que é | Por que entrou | Fonte |
|---|---|---|---|
| `taxa_homicidios_masc` | Taxa de homicídios **masculinos** /100k (CIDs X85–Y09, `sexo=1`) | Proxy de violência estrutural ambiente (crime organizado/tráfico) que motiva a adoção reativa da DEAM. **Masculino, não geral**, para evitar *containment* mecânico (ver §4.1) | SIM/BigQuery |
| `log_populacao` | Log da população municipal | Porte: municípios 24h são ~3,4× maiores que controles; população é fortemente assimétrica (skew ~12 → ~0,5 em log) | SIDRA 6579 (já existia) |
| `log_pib_per_capita` | Log do PIB per capita (R$) | Desenvolvimento econômico; mesma assimetria → log | SIDRA 5938 var 37 |
| `delta_homicidios_masc` | **Variação móvel de 2 anos** da taxa de homicídios masculinos (`taxa_t − taxa_{t−2}`) | Capta **surto recente de violência letal** → corrige a adoção reativa (tendência pré-tratamento) que covariáveis de nível NÃO absorviam (ver §5) | derivada no painel |

---

## 3. Arquivos criados e alterados

### Scripts de extração novos
- **`codes/extracao_filtragem/sim_sinan/extract_sim_homicidios_gerais.py`** — extrai homicídios (X85–Y09) do SIM via BigQuery, agrega por município-ano em duas séries (geral + masculino), faz matching com municípios DEAM, calcula taxas /100k. Saídas: `dados/sim/sim_homicidios_gerais_br_detalhada.csv` (microdados) e `dados/consolidado/homicidios_gerais_anual.csv` (agregado).
- **`codes/extracao_filtragem/ibge/fetch_pib_percapita.py`** — baixa PIB municipal (SIDRA tabela 5938, var 37, Mil Reais) dos municípios DEAM; calcula PIB per capita usando a MESMA população das outras taxas; aplica log. Saída: `dados/ibge/pib_percapita_municipios.csv`.

### Scripts alterados
- **`codes/analise_dados/agregar_painel_anual.py`** — passou a incorporar ao painel mestre: `homicidios_gerais`, `homicidios_masc` (+ taxas), `log_populacao`, `pib_per_capita`/`log_pib_per_capita`, e `delta_homicidios_masc` (variação móvel de 2 anos da taxa masculina).
- **`codes/inferencia_causal/modelo_causal_brasil.py`** — `COVARIATES = ["taxa_homicidios_masc", "log_populacao", "log_pib_per_capita", "delta_homicidios_masc"]`; `EST_METHOD` passa automaticamente para `'dr'`.

### Painel resultante
`dados/consolidado/painel_deam_anual.csv` → **3.135 linhas × 32 colunas** (285 municípios: 38 tratados 24h, 247 controles; 2009–2019).

---

## 4. Decisões metodológicas importantes (para citar/justificar no relatório)

### 4.1 Homicídios MASCULINOS, não gerais (evitar *containment*)
O outcome de letalidade (`taxa_feminicidios`) é o **subconjunto feminino** dos mesmos CIDs X85–Y09. Usar homicídios "gerais" (ambos os sexos) como covariável controlaria parcialmente pelo próprio outcome — atenuação mecânica do ATT, não causal. Confirmado nos dados: dos 298.288 homicídios, **273.574 (92%) são masculinos**, e os ~24,7 mil femininos batem quase exatamente com os 24.256 feminicídios. Por isso a covariável usa apenas o recorte masculino.

### 4.2 Time-varying é válido aqui (não é "bad control")
As covariáveis são anuais, mas o estimador CS da lib `diff_diff` recupera a covariável no **base period de cada coorte (g−1)**, nunca no valor pós-tratamento (verificado em `staggered.py:730`, `base_period="varying"`). Logo a coluna anual funciona como **baseline pré-tratamento cohort-specific**, sem o risco de bad control que existiria num TWFE com X contemporâneo. A coorte 2009 (sem g−1 no painel) é descartada pelo estimador.

### 4.3 Variáveis assimétricas em log
População e PIB per capita são fortemente assimétricos (poucas megacidades/municípios ricos dominariam o escore de propensão). Em log ficam ~simétricos, permitindo pareamento por porte e renda em escala proporcional.

---

## 5. A correção da pré-tendência do feminicídio (peça central da sessão)

### Diagnóstico
Com as 3 covariáveis de nível, o feminicídio tinha **violação limítrofe de tendências paralelas** (teste Wald diagonal p ≈ 0,050). O coeficiente ofensor é **t = −2** (z² ≈ 4,8): uma **tendência ascendente** de feminicídios nos anos imediatamente antes da adoção → assinatura da **adoção reativa** (a cidade abre a DEAM 24h *depois* que feminicídios sobem).

### O que NÃO funcionou (testado empiricamente — não re-testar)
Covariáveis de **nível** não corrigem, porque o problema é uma **tendência diferencial**, não diferença de nível. Corrida de cavalos (dr):
- **urbanização** (Censo 2010): PIORA (p 0,050 → 0,031)
- shares de VA agropecuária/indústria/serviços (SIDRA 5938): todas mantêm p < 0,05
- combinações: idem

Motivo: tratados e controles são quase idênticos nessas dimensões (urbanização 88,8% vs 91,3%), então não há alavancagem. IDH/pobreza/escolaridade tenderiam ao mesmo resultado.

### O que funcionou: covariável de VARIAÇÃO
`delta_homicidios_masc` (variação de 2 anos) pareia "municípios que tiveram surto recente de violência letal e abriram DEAM" com "municípios com surto parecido que não abriram". Resultado:

| Especificação | ATT feminicídio | p(ATT) | p(pré-tend.) | TP |
|---|---|---|---|---|
| 3 covariáveis de nível | +0,625 | 0,018 | 0,050 | **VIOLADA** |
| + `delta_homicidios_masc` | +0,482 | 0,064 | **0,207** | **OK** |

---

## 6. Resultados finais do modelo (4 covariáveis, `dr`)

| Desfecho | ATT (/100k) | IC95% | p | Leitura |
|---|---|---|---|---|
| **Acesso** (notificações SINAN) | **−18,04** | [−31,78, −4,68] | 0,008 | **Robusto**; IC exclui 0; pré-tendências OK |
| **Letalidade** (feminicídios SIM) | +0,48 | **[−0,03, +0,99]** | 0,064 | **Não-significativo**; IC inclui 0; pré-tendências OK |

> Observação sobre o sinal do acesso: o ATT de notificações é **negativo** (−18/100k). Isso precisa de interpretação cuidadosa no relatório — não é o aumento de acesso esperado pela cadeia causal. Verificar se reflete fenômeno real (ex.: heterogeneidade, deslocamento de registro) ou artefato; ponto a desenvolver na redação final.

---

## 7. Achado substantivo central (para a discussão do relatório)

**O efeito "positivo" da DEAM 24h sobre feminicídios era causalidade reversa, não efeito da política.**

Com as covariáveis de nível, o modelo indicava efeito **significativo e positivo** (+0,63, p=0,018) — o que, lido ingenuamente, seria "a DEAM 24h aumenta feminicídios", uma conclusão falsa e perigosa produzida pelo viés da adoção reativa (o pico pré-tratamento sendo atribuído à política).

Ao corrigir as tendências paralelas (via `delta`), o efeito **encolhe e perde significância** (+0,48, p=0,064, IC cruza zero). Conclusão honesta: **não há evidência robusta de efeito da DEAM 24h sobre a letalidade**. Isso foi corroborado por um teste independente (fora do escopo final): com `anticipation=1` o ATT colapsa para ≈ −0,05 (p=0,85).

**Princípio metodológico a deixar explícito no relatório:** tendências paralelas é a hipótese de identificação e precisa valer *independentemente* de o resultado ser significativo. Significância calculada sobre um estimador com PT violada não tem valor. O contraste correto é **enviesado vs. não-enviesado**, não "significativo vs. não-significativo".

---

## 8. Ressalvas / pendências (documentar como limitação)

1. **Janela do delta:** `delta_homicidios_masc` é nulo em 2009–2010 (faltam defasagens; a extração do SIM começou em 2009). As coortes 2009 e 2011 (3 municípios) têm contribuição condicional enfraquecida. Fechamento ideal: reextrair homicídios de 2007–2008 (e população desses anos). **Não feito** — opcional.
2. **Teste de pré-tendência:** usa a aproximação diagonal (soma de z² ~ χ², ignora covariância entre coeficientes) do `diagnostico_callaway_santanna.py`. Os p-valores devem ser lidos como aproximados (p=0,207 é folgado; p=0,050 é fronteira).
3. **Robustez SA/BJS:** Sun & Abraham retorna `nan` (colinearidade/posto deficiente) com as covariáveis; BJS roda. Verificar no relatório qual robustez reportar.
4. **`diagnostico_callaway_santanna.py` ainda roda em `reg` sem covariáveis** — gera as figuras/tabelas oficiais sob TP incondicional. Se o relatório final for usar essas figuras, considerar atualizá-lo para `dr` + covariáveis para coerência com o modelo principal.

---

## 9. Pipeline de execução (ordem)

1. `codes/extracao_filtragem/sim_sinan/extract_sim_homicidios_gerais.py` (BigQuery/auth GCP)
2. `codes/extracao_filtragem/ibge/fetch_pib_percapita.py` (SIDRA, sem auth)
3. `codes/analise_dados/agregar_painel_anual.py` (regenera o painel mestre)
4. `codes/inferencia_causal/modelo_causal_brasil.py` (ATT + event study, `dr`)
