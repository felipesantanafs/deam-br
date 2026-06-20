# Estatísticas — Callaway & Sant'Anna (DEAMs 24h, Brasil)

Desfechos em **taxa por 100 mil habitantes**. Estimador CS DiD, controle = nunca-tratados (DEAMs comerciais), 999 réplicas bootstrap, estimação **duplamente robusta (DR)** com covariáveis (taxa_homicidios_masc, log_populacao, log_pib_per_capita, delta_homicidios_masc).

## 1. Estatísticas descritivas

| Grupo                |   n_municipios |   n_obs |   taxa_notificacoes |   taxa_feminicidios |   feminicidios |   notificacoes |   populacao |
|:---------------------|---------------:|--------:|--------------------:|--------------------:|---------------:|---------------:|------------:|
| Controle (comercial) |            247 |    2717 |              79.283 |               2.652 |          5.845 |        182.308 |      236689 |
| Tratado (24h)        |             38 |     418 |              59.738 |               2.952 |         20.033 |        448.62  |      608975 |

## 2. Coortes de tratamento (adoção escalonada)

| Ano de adoção | Nº municípios |
|---|---|
| 2009 | 1 |
| 2011 | 2 |
| 2012 | 4 |
| 2013 | 2 |
| 2014 | 12 |
| 2015 | 3 |
| 2016 | 3 |
| 2017 | 2 |
| 2018 | 4 |
| 2019 | 5 |

## 3. ATT global por desfecho

| Desfecho | ATT | SE | IC95% | p-valor | N trat/ctrl |
|---|---|---|---|---|---|
| Notificações /100k (Acesso) | -18.044 | 7.107 | [-31.779, -4.683] | 0.0080 | 38/247 |
| Feminicídios /100k (Letalidade) | +0.482 | 0.271 | [-0.027, 0.986] | 0.0641 | 38/247 |

## 4. Teste conjunto de pré-tendências

H0: todos os coeficientes pré-tratamento do event study = 0.

| Desfecho | Estatística Wald | p-valor | nº coefs pré | indiv. signif. |
|---|---|---|---|---|
| Notificações /100k (Acesso) | 12.98 | 0.1635 | 9 | 0 |
| Feminicídios /100k (Letalidade) | 12.115 | 0.2069 | 9 | 0 |

_Método: Wald diagonal (z² somados ~ χ²). p<0,05 indica violação das tendências paralelas._

## 5. Efeitos por coorte


### Notificações /100k (Acesso)

|   coorte |   efeito |      se |
|---------:|---------:|--------:|
|     2011 |  -2.1485 | 25.4634 |
|     2012 | -17.1593 | 12.5186 |
|     2013 | -34.8074 | 31.1717 |
|     2014 | -20.6624 | 10.0436 |
|     2015 | -13.0154 | 20.9378 |
|     2016 | -25.764  | 15.2364 |
|     2017 | -12.1219 | 19.7172 |
|     2018 | -13.0086 | 23.2938 |
|     2019 |  -7.9936 | 11.6702 |


### Feminicídios /100k (Letalidade)

|   coorte |   efeito |     se |
|---------:|---------:|-------:|
|     2011 |   0.2436 | 0.1685 |
|     2012 |   1.3526 | 0.6573 |
|     2013 |   1.5216 | 0.4531 |
|     2014 |   0.7352 | 0.3232 |
|     2015 |   0.2418 | 0.5384 |
|     2016 |  -2.5306 | 1.1218 |
|     2017 |  -1.5256 | 0.2851 |
|     2018 |   0.4355 | 0.4977 |
|     2019 |  -0.3562 | 0.4616 |

## 6. Figuras geradas (relatorios/figuras_causal/)

- `00_adocao_escalonada.png` — desenho de adoção escalonada
- `00b_coortes.png` — tamanho das coortes
- `{notificacoes,feminicidios}_01_raw_trends.png` — tendências brutas
- `{...}_02_event_study.png` — ATT dinâmico com IC
- `{...}_03_heatmap_gt.png` — ATT(g,t)
- `{...}_04_efeitos_coorte.png` — efeitos por coorte
- `05_forest_att.png` — comparação dos ATT globais
