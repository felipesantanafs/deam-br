# Guia de Produção: Relatório Acadêmico em LaTeX
## Modelo baseado em "Avaliação de Impacto Causal — DEAMs 24h Brasil"

---

## 1. Visão Geral do Fluxo

```
Código Python          →      Figuras PNG        →      LaTeX .tex      →      PDF Compilado
(diagnostico_*.py)             (figuras_causal/)         (relatorios_finais/)     (10 páginas)
```

**Tempo estimado:** 30–60 min (excluindo instalação do LaTeX).  
**Pré-requisitos:** Python com `diff-diff`, `matplotlib`, `seaborn`; MiKTeX ou TeX Live.

---

## 2. Passo a Passo

### Passo 1 — Instalar LaTeX (uma vez)

```powershell
# Windows — via winget
winget install MiKTeX.MiKTeX --silent --accept-package-agreements

# Linux
sudo apt install texlive-full

# Mac
brew install --cask mactex
```

### Passo 2 — Gerar as Figuras com Python

```bash
python codes/inferencia_causal/diagnostico_callaway_santanna.py
```

Produz em `relatorios/figuras_causal/`:
- `00_adocao_escalonada.png` — desenho de adoção escalonada
- `00b_coortes.png` — tamanho das coortes
- `{desfecho}_01_raw_trends.png` — tendências brutas
- `{desfecho}_02_event_study.png` — ATT dinâmico ← usado no relatório
- `{desfecho}_03_heatmap_gt.png` — ATT(g,t)
- `{desfecho}_04_efeitos_coorte.png` — efeitos por coorte
- `05_forest_att.png` — forest plot ← usado no relatório

### Passo 3 — Criar a pasta de saída

```bash
mkdir relatorios/relatorios_finais
```

### Passo 4 — Escrever e compilar o LaTeX

```bash
cd relatorios/relatorios_finais

# Compilar DUAS vezes (2ª passada resolve cross-references e figuras figure*)
pdflatex -interaction=nonstopmode nome_do_relatorio.tex
pdflatex -interaction=nonstopmode nome_do_relatorio.tex
```

**Por que duas passadas?**  
LaTeX resolve referências cruzadas (`\ref`, `\label`) e bookmarks PDF apenas na 2ª compilação.

---

## 3. Estrutura Visual do Template (The Journal of Investing Style)

### 3.1 Classe e Layout

```latex
\documentclass[twocolumn, 10pt]{article}

\usepackage[
  top=2.0cm, bottom=2.2cm,
  left=1.6cm, right=1.6cm,
  columnsep=0.7cm
]{geometry}

\usepackage{microtype}   % kerning e hifenização otimizados
\usepackage{setspace}
\setstretch{1.08}        % espaçamento entre linhas levemente arejado
\emergencystretch=3em    % evita overfull hbox em duas colunas
```

### 3.2 Fontes

```latex
\usepackage{lmodern}   % corpo serif (Latin Modern)
\usepackage{helvet}    % títulos sans-serif (Helvetica/URW)
```

### 3.3 Seções com titlerule

```latex
\usepackage{titlesec}

\titleformat{\section}
  {\sffamily\bfseries\large}{\thesection}{0.6em}{}[\titlerule]   % linha sob o título
\titleformat{\subsection}
  {\sffamily\bfseries\normalsize}{\thesubsection}{0.5em}{}
\titleformat{\subsubsection}
  {\sffamily\itshape\normalsize}{\thesubsubsection}{0.5em}{}

\titlespacing*{\section}{0pt}{16pt plus 2pt minus 2pt}{8pt}
\titlespacing*{\subsection}{0pt}{11pt plus 1pt minus 1pt}{5pt}
\titlespacing*{\subsubsection}{0pt}{8pt plus 1pt}{3pt}
```

### 3.4 Cabeçalho e rodapé

```latex
\usepackage{fancyhdr}
\pagestyle{fancy}
\fancyhf{}
\renewcommand{\headrulewidth}{0.4pt}
\fancyhead[L]{\footnotesize\sffamily TÍTULO CURTO — TEMA}
\fancyhead[R]{\footnotesize\sffamily\thepage}
\fancyfoot[C]{\footnotesize\sffamily Nome do Projeto \textbar{} Referência metodológica}
```

### 3.5 Tabelas acadêmicas (booktabs)

```latex
\usepackage{booktabs}
\usepackage{tabularx}
\renewcommand{\arraystretch}{1.15}

% Exemplo de tabela padrão:
\begin{table}[H]
\centering
\caption{Título da Tabela}
\label{tab:nome}
\small
\begin{tabularx}{\columnwidth}{@{}Xrr@{}}
\toprule
\textbf{Variável} & \textbf{Grupo A} & \textbf{Grupo B} \\
\midrule
Linha 1 & 100 & 200 \\
Linha 2 & 300 & 400 \\
\bottomrule
\end{tabularx}
\smallskip\par
{\footnotesize\sffamily\itshape Nota: texto explicativo da tabela.}
\end{table}
```

**Regras:** nunca use linhas verticais; use apenas `\toprule`, `\midrule`, `\bottomrule`.

### 3.6 Figuras — IMPORTANTE: largura total vs. coluna

```latex
% Figura dentro de UMA coluna (pequena):
\begin{figure}[H]
  \centering
  \includegraphics[width=\columnwidth]{caminho/figura.png}
  \caption{Legenda.}
  \label{fig:nome}
\end{figure}

% Figura ocupando LARGURA TOTAL da página (legível, recomendado para event studies):
\begin{figure*}[tbp]
  \centering
  \includegraphics[width=0.86\textwidth]{caminho/figura.png}
  \caption{Legenda detalhada.}
  \label{fig:nome}
\end{figure*}
```

> **Atenção:** `figure*` em documentos `twocolumn` só funciona em posições flutuantes
> (`[tbp]`), nunca com `[H]`. O `[H]` é exclusivo do ambiente `figure`.

### 3.7 Caixas de resultado destacadas

```latex
\usepackage{tcolorbox}
\tcbset{
  resultbox/.style={
    colback=gray!8, colframe=gray!40,
    fonttitle=\sffamily\bfseries\small,
    boxrule=0.4pt, arc=2pt,
    left=4pt, right=4pt, top=3pt, bottom=3pt
  }
}

% Uso:
\begin{tcolorbox}[resultbox, title={Resultado Central}]
\small
$\text{ATT} = -20{,}513$ \hfill $p = 0{,}001$ \\
\textit{Interpretação do resultado.}
\end{tcolorbox}
```

### 3.8 Capa (uma coluna em documento duas colunas)

```latex
\twocolumn[{%
\begin{@twocolumnfalse}

  \vspace*{0.3cm}
  \hrule height 2pt
  \vspace{0.5cm}

  {\sffamily\bfseries\LARGE Título Principal:\\[4pt] Subtítulo}

  \vspace{0.5cm}
  \hrule height 0.4pt
  \vspace{0.4cm}

  {\sffamily\large
    Autor 1\textsuperscript{1} \quad Autor 2\textsuperscript{2}}

  \vspace{0.15cm}
  {\sffamily\small\color{gray}
    \textsuperscript{1}E-mail: \href{mailto:email@dominio.br}{email@dominio.br} — Nº USP: XXXXXXXX\\
    \textsuperscript{2}E-mail: \href{mailto:email2@dominio.br}{email2@dominio.br} — Nº USP: YYYYYYYY}

  \vspace{0.6cm}
  \hrule height 0.4pt
  \vspace{0.5cm}

  % Abstract + Informações lado a lado
  \begin{minipage}[t]{0.48\textwidth}
    {\sffamily\bfseries\small Abstract}
    \vspace{4pt}
    \small Texto do abstract...
    \vspace{4pt}
    {\sffamily\bfseries\small Palavras-chave:} \small lista.
    \vspace{4pt}
    {\sffamily\bfseries\small JEL:} \small C23, I18.
  \end{minipage}%
  \hfill
  \begin{minipage}[t]{0.48\textwidth}
    {\sffamily\bfseries\small Informações do Artigo}
    \vspace{4pt}
    \small
    \begin{tabular}{@{}ll}
      \textbf{Período:}   & 2009--2019 \\
      \textbf{N tratados:}& 38 municípios \\
      \textbf{Estimador:} & Callaway \& Sant'Anna \\
    \end{tabular}
  \end{minipage}

  \vspace{0.8cm}
  \hrule height 0.4pt
  \vspace{0.6cm}

\end{@twocolumnfalse}
}]
```

### 3.9 Equações em duas colunas

Equações longas transbordam facilmente em duas colunas. Solução:

```latex
% Quebrar equações longas com \begin{split}
\begin{equation}
\begin{split}
\mathbb{E}[Y_t(0) - Y_{g-1}(0) \mid G = g] \\
= \mathbb{E}[Y_t(0) - Y_{g-1}(0) \mid G = \infty],\; t < g
\end{split}
\label{eq:nome}
\end{equation}

% Simplificar símbolos em display math
\[
  \text{Tratamento} \to \uparrow\text{Acesso} \to \downarrow\text{Desfecho}
\]
% (evitar \;\to\; com muitos espaços: causa overfull)
```

### 3.10 Referências manuais (sem bibtex)

```latex
\section*{Referências}
\addcontentsline{toc}{section}{Referências}
\begingroup
\setlength{\parindent}{-0.4cm}
\setlength{\leftskip}{0.4cm}
\setlength{\parskip}{2pt}    % compacto para caber na última página
\small

\textbf{Bases de Dados}

Base dos Dados. \textit{Nome do Sistema}. Disponível em:
\href{https://link-completo.org}{texto-curto-do-link}.
Acesso em: mês. ano.

\smallskip
\textbf{Referências Metodológicas}

Autor, A., \& Autor, B. (ano). Título do artigo.
\textit{Journal Name}, vol(num), pp--pp.
\href{https://doi.org/...}{https://doi.org/...}.

\endgroup
```

---

## 4. Pacotes Obrigatórios — Lista Completa

| Pacote | Função |
|--------|--------|
| `inputenc` + `fontenc` + `babel` | Codificação UTF-8 e língua portuguesa |
| `lmodern` + `helvet` | Fontes corpo (serif) e títulos (sans-serif) |
| `geometry` | Margens e layout de página |
| `microtype` | Kerning e hifenização tipográfica fina |
| `setspace` | Espaçamento entre linhas (`\setstretch`) |
| `fancyhdr` | Cabeçalho e rodapé personalizados |
| `titlesec` | Formatação de seções com `\titlerule` |
| `booktabs` | Tabelas acadêmicas sem linhas verticais |
| `tabularx` | Tabelas com coluna expansível (`X`) |
| `graphicx` | Inserção de figuras |
| `float` | Posicionamento `[H]` forçado |
| `caption` | Legendas em sans-serif |
| `amsmath` + `amssymb` | Equações e símbolos matemáticos |
| `hyperref` | Hiperlinks e metadados do PDF |
| `url` (com `hyphens`) | Quebra de URLs longas |
| `xcolor` | Cores (usado em `\color{gray}`) |
| `enumitem` | Listas compactas |
| `footmisc` | Notas de rodapé formatadas |
| `tcolorbox` | Caixas de resultado destacadas |

---

## 5. Controle de Páginas

Para ajustar o número de páginas finais, use estas alavancas:

| Objetivo | Ação |
|----------|------|
| Comprimir referências | Reduzir `\parskip` de 5pt → 2pt; trocar `\medskip` por nada |
| Separar refs em nova página | Adicionar `\newpage` antes de `\section*{Referências}` |
| Reduzir espaço entre seções | Diminuir `\titlespacing*` |
| Aumentar espaçamento geral | `\setstretch{1.12}` em vez de `1.08` |
| Compactar listas | `\setlist{noitemsep, topsep=0pt}` |
| Remover `\bigskip`/`\medskip` | Substitua por `\smallskip` ou nada |

---

## 6. Problemas Frequentes e Soluções

| Problema | Causa | Solução |
|----------|-------|---------|
| `figure*` não funciona com `[H]` | Incompatibilidade LaTeX | Usar `[tbp]` em vez de `[H]` |
| Overfull hbox em equação | Fórmula muito longa | Usar `\begin{split}` ou simplificar símbolos |
| Referência `undefined` | Compilação única | Compilar **duas vezes** |
| PDF com `\lipsum` no texto | Esqueceu de remover | Buscar e apagar todos os `\lipsum[...]` |
| Acentos corrompidos | Encoding errado | Garantir `\usepackage[utf8]{inputenc}` e salvar em UTF-8 |
| URLs ultrapassam margem | URL sem quebra | `\usepackage[hyphens]{url}` + `\emergencystretch=3em` |

---

## 7. Prompt Reutilizável para Futuros Relatórios

Copie e adapte o bloco abaixo ao solicitar a criação de um novo relatório:

---

```
Atue como pesquisador sênior em econometria e redator acadêmico.
Escreva o código LaTeX completo e compilável para um relatório de avaliação
de impacto intitulado "[TÍTULO]".

DESIGN VISUAL (obrigatório):
- \documentclass[twocolumn, 10pt]{article}
- Margens: geometry (top=2cm, bottom=2.2cm, left=1.6cm, right=1.6cm, columnsep=0.7cm)
- Fonte corpo: lmodern (serif); títulos: helvet (sans-serif) via titlesec
- Seções: \titleformat com \titlerule abaixo; titlespacing amplo
- Tabelas: booktabs sem linhas verticais (\toprule/\midrule/\bottomrule)
- Figuras grandes (event studies, forest plots): ambiente figure* com width=0.86\textwidth
- Caixas de resultado: tcolorbox com colback=gray!8
- Hiperlinks discretos: hyperref com urlcolor=blue!60!black, linkcolor=black
- Pacotes obrigatórios: graphicx, amsmath, amssymb, booktabs, tabularx, titlesec,
  tcolorbox, fancyhdr, footmisc, caption, float, microtype, setspace, xcolor,
  enumitem, url (com hyphens), hyperref
- \setstretch{1.08}; \emergencystretch=3em; \parskip=4pt
- Compilar com: pdflatex -interaction=nonstopmode (duas passadas)

CAPA (uma coluna com \twocolumn[{\begin{@twocolumnfalse}...}]):
- Sem linha de versão/instituição no topo
- Título grande em \sffamily\bfseries\LARGE
- Autores: [NOME 1] (email, Nº USP) e [NOME 2] (email, Nº USP)
- Abstract à esquerda; tabela de informações do artigo à direita
- JEL codes: [CÓDIGOS]

ESTRUTURA (alvo: [N] páginas):
1. Introdução (~2 páginas): contextualização, pergunta de pesquisa, cadeia causal,
   posicionamento na literatura, estrutura do relatório
2. Dados (~2 páginas): fontes primárias com subsubsections, pareamento/curadoria,
   limitações dos dados (erros de medida), normalização, tabelas descritivas
3. Metodologia (~2 páginas): problema do TWFE, estimador adotado com equações
   numeradas, hipótese de identificação, teste de pré-tendências (equação Wald),
   especificação implementada
4. Resultados (~2 páginas): tabela ATT global, caixas de resultado, tabela de
   pré-tendências, tabelas de efeitos por coorte, figuras figure*, discussão
   de viés de seleção / adoção reativa / DR-DiD
5. Conclusão (~2 páginas): síntese, evidência de mecanismo, próximos passos
   (DR-DiD com covariáveis, controle not_yet_treated, antecipação, raça),
   implicações para política pública, limitações
Referências (fluindo após 5.5, sem \newpage, para fechar em [N] páginas)

DADOS REAIS A USAR:
- [INSERIR: N observações, N tratados, N controles, período, estimador]
- [INSERIR: ATTs globais com SE, IC95%, p-valores]
- [INSERIR: resultados do teste de pré-tendências (Wald, p, k)]
- [INSERIR: efeitos por coorte (tabela)]
- [INSERIR: achado de mecanismo se houver]

FIGURAS (já geradas em [CAMINHO_FIGURAS]/):
- [LISTAR arquivos PNG a incluir]
- Usar figure* para as figuras principais (event studies, forest plot)

REFERÊNCIAS (seção não-numerada, parskip=2pt):
- [LISTAR bases de dados com links exatos]
- [LISTAR referências metodológicas com DOI]
- [LISTAR literatura substantiva]
- [LISTAR recursos do projeto: GitHub, Streamlit etc.]

Ao final: compilar com pdflatex duas vezes e confirmar N páginas e 0 erros.
Salvar .tex e .pdf em [PASTA_DESTINO].
```

---

## 8. Estrutura de Diretórios Recomendada

```
projeto/
├── codes/
│   └── inferencia_causal/
│       └── diagnostico_*.py          ← gera as figuras
├── dados/
│   └── consolidado/
│       └── painel_*.csv              ← dados do painel
└── relatorios/
    ├── figuras_causal/               ← PNGs gerados pelo Python
    │   ├── 05_forest_att.png
    │   ├── {desfecho}_02_event_study.png
    │   └── ...
    ├── estatisticas_causal.md        ← resultados em markdown
    └── relatorios_finais/            ← saída LaTeX
        ├── nome_relatorio.tex
        ├── nome_relatorio.pdf
        └── nome_relatorio.log
```

**Caminho relativo das figuras no .tex** (quando o .tex está em `relatorios_finais/`):
```latex
\includegraphics[...]{../figuras_causal/nome_figura.png}
```

---

## 9. Checklist Final Antes de Entregar

- [ ] Remover todos os `\lipsum[...]` do texto
- [ ] Verificar nomes e e-mails dos autores na capa
- [ ] Confirmar que os dados nas tabelas batem com `estatisticas_causal.md`
- [ ] Compilar **duas vezes** e confirmar que não há "Undefined references"
- [ ] Verificar contagem de páginas
- [ ] Abrir o PDF e checar que as figuras aparecem grandes e legíveis
- [ ] Confirmar que os links de referências estão clicáveis no PDF

---

*Documento gerado a partir da produção do relatório "Avaliação de Impacto Causal: DEAMs 24h Brasil" — Projeto DEAM-BR, jun. 2026.*
