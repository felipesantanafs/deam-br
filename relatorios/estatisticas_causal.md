# Estatísticas — Callaway & Sant'Anna (DEAMs 24h, Brasil)

Desfechos em **taxa por 100 mil habitantes**. Estimador CS DiD, controle = nunca-tratados (DEAMs comerciais), 999 réplicas bootstrap.

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
| Notificações /100k (Acesso) | -20.513 | 7.418 | [-35.312, -6.578] | 0.0010 | 38/247 |
| Feminicídios /100k (Letalidade) | +0.438 | 0.255 | [-0.054, 0.913] | 0.0821 | 38/247 |

## 4. Teste conjunto de pré-tendências

H0: todos os coeficientes pré-tratamento do event study = 0.

| Desfecho | Estatística Wald | p-valor | nº coefs pré | indiv. signif. |
|---|---|---|---|---|
| Notificações /100k (Acesso) | 24.141 | 0.0041 | 9 | 2 |
| Feminicídios /100k (Letalidade) | 12.948 | 0.165 | 9 | 1 |

_Método: Wald diagonal (z² somados ~ χ²). p<0,05 indica violação das tendências paralelas._

## 5. Efeitos por coorte


### Notificações /100k (Acesso)

|   coorte |   efeito |      se |
|---------:|---------:|--------:|
|     2011 |  -2.1485 | 25.4634 |
|     2012 | -19.1303 | 13.6261 |
|     2013 | -13.0207 | 17.3099 |
|     2014 | -32.3022 | 12.1732 |
|     2015 | -12.1205 | 14.9725 |
|     2016 | -28.8364 | 16.9071 |
|     2017 |  -6.545  | 18.4733 |
|     2018 |   2.0346 | 18.8501 |
|     2019 |  -4.7395 | 10.4717 |


### Feminicídios /100k (Letalidade)

|   coorte |   efeito |     se |
|---------:|---------:|-------:|
|     2011 |   0.2436 | 0.1685 |
|     2012 |   1.2874 | 0.7164 |
|     2013 |   0.7816 | 0.1433 |
|     2014 |   0.7904 | 0.3176 |
|     2015 |   0.2022 | 0.6144 |
|     2016 |  -2.3564 | 0.9546 |
|     2017 |  -1.0751 | 0.1521 |
|     2018 |  -0.044  | 0.2256 |
|     2019 |  -0.345  | 0.4741 |

## 6. Figuras geradas (relatorios/figuras_causal/)

- `00_adocao_escalonada.png` — desenho de adoção escalonada
- `00b_coortes.png` — tamanho das coortes
- `{notificacoes,feminicidios}_01_raw_trends.png` — tendências brutas
- `{...}_02_event_study.png` — ATT dinâmico com IC
- `{...}_03_heatmap_gt.png` — ATT(g,t)
- `{...}_04_efeitos_coorte.png` — efeitos por coorte
- `05_forest_att.png` — comparação dos ATT globais
