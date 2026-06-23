# Guia de Estilo — Padrão Visual de Slides "DEAM-BR / Academic-Corporate"

> **Para quem lê isto (humano ou IA):** este documento registra o sistema visual
> aprovado na apresentação `Trabalho de avaliacao de politicas sociais (revisado v2).pptx`.
> Ele é a **referência canônica** para montar QUALQUER deck futuro com a mesma estética.
> O guia foi escrito de forma que uma IA consiga **reaplicar o estilo do zero**, com
> especificações exatas + código `python-pptx` pronto para copiar. Siga as medidas à risca:
> a estética depende do alinhamento milimétrico e da paleta restrita.

---

## 0. Resumo da estética (o "look")

Estilo **academic-corporate** derivado de uma capa de deck financeiro, adaptado para
**fundo branco**: tipografia serifada clássica (Times New Roman), paleta sóbria
**azul-marinho + dourado**, muito espaço em branco, filetes finos, rótulos em
versalete com *letter-spacing*, tabelas tipo *booktabs* com cabeçalho escuro, e
acentos dourados discretos. Sensação: artigo científico + apresentação executiva.

Princípios inegociáveis:
1. **Fundo sempre branco**; cor entra só em texto, filetes e pequenos acentos.
2. **Uma única fonte:** Times New Roman em tudo (inclusive tabelas e rótulos).
3. **Paleta restrita:** marinho `0A1A2F`, dourado `B8964A`/`C9A961`, cinza `4A5057`.
4. **Chrome consistente** em todo slide de conteúdo (cabeçalho + rodapé idênticos).
5. **Menos é mais:** poucos bullets, fontes grandes e legíveis, no máximo 1–2 elementos
   visuais (gráfico/tabela) por slide.
6. **Marcadores são "•" dourados**, nunca travessões.

---

## 1. Canvas e unidades

- Proporção **16:9**, tamanho **13.333 × 7.5 in** = **12.192.000 × 6.858.000 EMU**.
- Trabalhe num grid mental de **1280 × 720 px** (px @96dpi).
- Conversão: **1 px = 9525 EMU**. Helper: `def E(px): return Emu(round(px*9525))`.
- Todas as coordenadas neste guia estão em **px** (multiplicar por 9525 ao aplicar).

---

## 2. Paleta de cores (hex)

| Nome    | Hex      | Uso |
|---------|----------|-----|
| NAVY    | `0A1A2F` | texto principal, títulos, cabeçalho de tabela, fórmulas |
| GOLD    | `B8964A` | acentos, marcadores "•", rótulos, bordas de caixa (dourado mais escuro p/ contraste no branco) |
| GOLDL   | `C9A961` | barra vertical direita, preenchimento de barras, dourado "claro" |
| GRAY    | `4A5057` | subtítulos, legendas, notas |
| LINEC   | `D8CEB4` | filetes finos (cabeçalho/rodapé), bordas inferiores de linha de tabela |
| ROWALT  | `F4F1E9` | zebra das linhas pares de tabela |
| BOXBG   | `F3EEDF` | fundo de caixas de destaque/fórmula/cadeia causal |
| TRACK   | `E7E0CD` | trilho (fundo) das barras de progresso |
| WHITE   | `FFFFFF` | fundo do slide e células de tabela |

> Cuidado: o tema do master pode ser Arial — **sempre** force `font.name = "Times New Roman"`
> em cada run; não confie na herança do tema.

---

## 3. Tipografia (Times New Roman em tudo)

| Elemento | Tamanho (pt) | Peso/cor | Obs. |
|---|---|---|---|
| Título da capa | 42 | bold, NAVY | 2 linhas, `line_spacing 1.05` |
| Sobretítulo capa (eyebrow) | 15 | bold, GOLD | versalete, `spc=160` |
| Rótulo topo capa | 11 | bold, GOLD | versalete, `spc=220` |
| Autores (capa) | 19 | regular, NAVY | |
| Linha USP (capa) | 12 | regular, GRAY | |
| Rodapé capa | 9 | bold, GOLD | versalete, `spc=100` |
| Rótulo de seção (chrome) | 11 | bold, GOLD | versalete, `spc=180` |
| Título de conteúdo | 30 | bold, NAVY | |
| Subtítulo de conteúdo | 15 | itálico, GRAY | |
| Bullets | 14.5–21 | NAVY (marcador GOLD) | quanto menos texto, maior a fonte |
| Cabeçalho de tabela | 13–14 | bold, WHITE sobre NAVY | |
| Corpo de tabela | 13–14 | NAVY | |
| Legenda de figura/tabela | 11 | itálico, GRAY | |
| Rodapé/numeração | 9 | bold, GOLD | `"NN / TT"` |

`spc` é o atributo de *tracking* (centésimos de ponto) aplicado via
`run._r.get_or_add_rPr().set("spc", str(int(spc)))`. Use em TODO texto em versalete.

---

## 4. Anatomia da CAPA (slide 0)

Fundo branco + barra dourada vertical à direita. Bloco de texto alinhado à esquerda
(margem 81 px), com hierarquia: rótulo → eyebrow → título grande → filete → autores → rodapé.

| Elemento | L | T | W | H | Estilo |
|---|---|---|---|---|---|
| Retângulo branco (fundo) | 0 | 0 | 1280 | 720 | fill WHITE |
| Barra vertical direita | 1190 | 0 | 5 | 720 | fill GOLDL |
| Ponto (oval) | 57 | 62 | 9 | 9 | fill GOLD |
| Rótulo topo | 81 | 52 | 760 | 30 | 11 bold GOLD `spc=220` |
| Eyebrow | 81 | 232 | 1056 | 40 | 15 bold GOLD `spc=160` |
| Título (2 linhas) | 81 | 280 | 1040 | 200 | 42 bold NAVY |
| Filete dourado | 81 | 502 | 92 | 4 | fill GOLD |
| Autores | 81 | 522 | 1056 | 40 | 19 NAVY |
| Linha USP/subinfo | 81 | 562 | 1056 | 28 | 12 GRAY |
| Rodapé (metadados) | 81 | 678 | 1090 | 28 | 9 bold GOLD `spc=100` |

Separe campos com `·` cercado de espaços largos (ex.: `"Autor A       ·       Autor B"`).

---

## 5. CHROME do slide de conteúdo (igual em todos)

Toda página de conteúdo começa chamando `chrome(slide, section, title, subtitle, page)`.
Ele desenha:

| Elemento | L | T | W | H | Estilo |
|---|---|---|---|---|---|
| Fundo branco | 0 | 0 | 1280 | 720 | WHITE |
| Barra vertical direita | 1190 | 0 | 5 | 720 | GOLDL |
| Ponto de seção | 57 | 49 | 7 | 7 | GOLD (oval) |
| Rótulo de seção (esq.) | 74 | 42 | 820 | 24 | 11 bold GOLD `spc=180` — ex.: `"DADOS · 02"` |
| Rótulo fixo (dir.) | 900 | 42 | 270 | 24 | 11 bold GOLD `spc=100`, **dir.** — ex.: `"DEAMs 24h · CS DiD"` |
| Filete superior | 57 | 74 | 1133 | 1 | LINEC |
| Barra-acento do título | 57 | 110 | 5 | 84 | GOLD |
| Título | 81 | 100 | 1100 | 64 | 30 bold NAVY (vert. centralizado) |
| Subtítulo | 81 | 188 | 1110 | 38 | 15 itálico GRAY |
| Filete inferior | 57 | 676 | 1133 | 1 | LINEC |
| Rótulo de rodapé (esq.) | 74 | 684 | 900 | 22 | 9 bold GOLD `spc=110` |
| Numeração (dir.) | 1060 | 684 | 130 | 22 | 9 bold GOLD, **dir.**, `"%02d / 08"` |

**Região de conteúdo livre:** `L 57 → 1190`, `T ≈ 235 → 660`. Nunca invada cabeçalho/rodapé.

Convenção do rótulo de seção: `"<TEMA> · <NN>"` em versalete (ex.: `PERGUNTA · 01`,
`MÉTODO · 04`, `RESULTADOS · 05`, `SÍNTESE · 07`).

---

## 6. Componentes

### 6.1 Bullets
- Sem marcador nativo (aplicar `buNone`). Cada parágrafo = 2 runs:
  `"•  "` em **GOLD bold** + texto em **NAVY**.
- `space_after` 9–18 pt, `line_spacing ≈ 1.06`.
- Para destacar um bullet, deixe o texto **bold** (NAVY).
- Tamanho: 21 (poucos itens) a 14.5 (duas colunas densas). **Se não couber, corte texto — não diminua demais.**

### 6.2 Tabelas (estilo booktabs + cabeçalho escuro)
- Estilo "No Style, No Grid": setar `tableStyleId = {2D5ABB26-0587-4C30-8999-92F81FD0307C}`,
  `firstRow=0`, `bandRow=0` (remove o azul padrão).
- Cabeçalho: fundo **NAVY**, texto **WHITE bold**.
- Linhas: **zebra** (pares = ROWALT, ímpares = WHITE).
- Borda só inferior, fina (0.5 pt) em LINEC; sem linhas verticais.
- 1ª coluna alinhada à esquerda; numéricas centralizadas.
- Fonte 13–14. Margens de célula pequenas (L/R 8 px, T/B 2 px), `vertical_anchor=MIDDLE`.
- Linhas que devem saltar aos olhos (ex.: especificação principal "DR"): `bold_rows`.
- Sempre acompanhar de **legenda** 11 itálico GRAY logo abaixo.

### 6.3 Caixa de destaque / callout
- `ROUNDED_RECTANGLE`, fill **BOXBG**, borda **GOLD 1.0–1.25 pt**, sombra off.
- Texto centralizado: rótulo curto GOLD bold + frase NAVY bold.
- Usado para: "Cadeia causal", resultados centrais, fórmulas.

### 6.4 Caixa de fórmula
- Igual ao callout, mas com **barra dourada de 6 px na borda esquerda** e rótulo
  versalete `"ESTIMADOR — ..."` (11 GOLD `spc=120`).
- A fórmula em si entra como **imagem PNG** (ver 6.6).

### 6.5 Barras de progresso (bar chart nativo)
Para séries categóricas (ex.: contagem por ano/coorte). Cada linha:
- rótulo (ano) à direita, `MIDDLE`, NAVY bold 13;
- **trilho**: `ROUNDED_RECTANGLE` fill TRACK, largura fixa (ex.: 372 px);
- **preenchimento**: `ROUNDED_RECTANGLE` por cima, largura = `valor/max * trilho`,
  fill **GOLDL** (e **GOLD** no valor máximo, p/ destaque);
- contagem ao final, NAVY bold 13.
- passo vertical ~36 px, altura da barra ~18 px. Fechar com nota-resumo GRAY itálico.

### 6.6 Fórmulas matemáticas (matplotlib → PNG)
- `python-pptx` não faz LaTeX. Renderize com **matplotlib mathtext**, cor NAVY,
  fundo **transparente**, `dpi=300`, `bbox_inches="tight"`, e **embuta como imagem**.
- `math_fontfamily="cm"` (Computer Modern) combina bem com Times.
- Ex.: `r"$ATT(g,t)=E\,[\,Y_{t}(g)-Y_{t}(0)\mid G=g\,]$"`.

### 6.7 Figuras (imagens)
- **Sempre preservar aspect ratio** e **centralizar** dentro de uma caixa-alvo (`fit_pic`).
- Caixas típicas: 1 figura grande à direita de bullets, ou 2 figuras lado a lado
  (caixas ~565×360 px em `L57` e `L640`).
- Legenda 11 itálico GRAY centralizada sob a figura.
- Use figuras de fonte com **título embutido** quando possível (reduz texto no slide).

---

## 7. Arquétipos de slide (receitas)

1. **Capa** — seção 4.
2. **Texto + caixa de ênfase** — bullets grandes no topo + 1 callout (ex.: cadeia causal).
3. **Tabela cheia** — 1 tabela larga (≤7 linhas) ocupando a região, ex.: fontes de dados.
4. **Duas tabelas** — lado a lado (`L57` ~560 px e `L645` ~545 px) + notas.
5. **Bullets + figura** — bullets à esquerda (~545 px) + 1 figura à direita (~450 px).
6. **Fórmula + barras** — bullets + caixa de fórmula à esquerda; barras de progresso à direita.
7. **Duas figuras** — 2 gráficos lado a lado + 2 legendas.
8. **Duas colunas de texto** — ex.: Conclusões | Limitações, cada coluna com mini-cabeçalho
   (filete dourado 60×4 px + título 20 NAVY bold) e bullets 14.5.

---

## 8. Notas de implementação / armadilhas (python-pptx)

- **Forçar a fonte** em cada run (`f.name = "Times New Roman"`); o tema pode ser Arial.
- **Sem marcador nativo:** `p._p.get_or_add_pPr()` (não existe `p.get_or_add_pPr()`),
  remover `buChar/buAutoNum/buNone` e anexar `<a:buNone/>`.
- **Bordas de célula:** inserir `<a:lnT>/<a:lnB>` no `tcPr` **na posição 0** (devem vir
  antes do fill na ordem do schema).
- **Apagar slides do template:** para cada `sldId`, `prs.part.drop_rel(rId)` **e**
  remover do `sldIdLst`. Só remover do `sldIdLst` deixa partes órfãs → "Duplicate name"
  no zip e arquivo corrompido.
- **Criar slide limpo:** `add_slide(layout)` e então remover todos os placeholders clonados,
  desenhando tudo manualmente (controle total).
- **Fonte do arquivo (glob):** ignore arquivos `~$...` (locks do PowerPoint/Office) e
  cuidado com nomes acentuados (normalização NFC/NFD no Windows). Prefira `os.walk` + filtro.
- **Salvar com o arquivo aberto:** Windows trava o `.pptx` aberto no PowerPoint; o
  `os.access(W_OK)` **não** detecta o lock. Faça `try: save(OUT) except PermissionError: save(OUT_v_next)`.
- **`shadow.inherit = False`** em todo shape (evita sombra padrão feia).
- **Renderização/preview:** o usuário **não usa LibreOffice**; valide o `.pptx`
  estruturalmente (reabrindo com python-pptx e checando overflow), sem converter para PDF.

---

## 9. Biblioteca de helpers (copiar e usar)

```python
# -*- coding: utf-8 -*-
import os
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pptx import Presentation
from pptx.util import Emu, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn
from lxml import etree
from PIL import Image

PX = 9525
def E(px): return Emu(int(round(px * PX)))
FNAME = "Times New Roman"
NAVY=RGBColor(0x0A,0x1A,0x2F); GOLD=RGBColor(0xB8,0x96,0x4A); GOLDL=RGBColor(0xC9,0xA9,0x61)
GRAY=RGBColor(0x4A,0x50,0x57); LINEC=RGBColor(0xD8,0xCE,0xB4); HEADBG=NAVY
ROWALT=RGBColor(0xF4,0xF1,0xE9); BOXBG=RGBColor(0xF3,0xEE,0xDF); TRACK=RGBColor(0xE7,0xE0,0xCD)
WHITE=RGBColor(0xFF,0xFF,0xFF); NAVY_HEX="#0A1A2F"

def set_run(r, text, size, color=NAVY, bold=False, italic=False, name=FNAME, spc=None):
    r.text=text; f=r.font; f.name=name; f.size=Pt(size); f.bold=bold; f.italic=italic
    f.color.rgb=color
    if spc is not None: r._r.get_or_add_rPr().set("spc", str(int(spc)))

def add_box(slide,l,t,w,h,anchor=MSO_ANCHOR.TOP,align=None):
    tb=slide.shapes.add_textbox(E(l),E(t),E(w),E(h)); tf=tb.text_frame
    tf.word_wrap=True; tf.vertical_anchor=anchor
    tf.margin_left=tf.margin_right=tf.margin_top=tf.margin_bottom=0
    if align is not None: tf.paragraphs[0].alignment=align
    return tb,tf
def p0(tf): return tf.paragraphs[0]

def add_rect(slide,l,t,w,h,color,shape=MSO_SHAPE.RECTANGLE,line=None,lw=1.0):
    sp=slide.shapes.add_shape(shape,E(l),E(t),E(w),E(h))
    sp.fill.solid(); sp.fill.fore_color.rgb=color
    if line is None: sp.line.fill.background()
    else: sp.line.color.rgb=line; sp.line.width=Pt(lw)
    sp.shadow.inherit=False; return sp

def no_bullet(p):
    pPr=p._p.get_or_add_pPr()
    for tag in ("a:buChar","a:buAutoNum","a:buNone"):
        for e in pPr.findall(qn(tag)): pPr.remove(e)
    etree.SubElement(pPr, qn("a:buNone"))

def fit_pic(slide,path,bl,bt,bw,bh):
    iw,ih=Image.open(path).size; ar=iw/ih
    if bw/bh>ar: h=bh; w=bh*ar
    else: w=bw; h=bw/ar
    return slide.shapes.add_picture(path,E(bl+(bw-w)/2),E(bt+(bh-h)/2),E(w),E(h))

def caption(slide,text,l,t,w):
    _,tf=add_box(slide,l,t,w,20,align=PP_ALIGN.CENTER)
    set_run(p0(tf).add_run(),text,11,color=GRAY,italic=True)

def bullets(slide,items,l,t,w,h,size=18,gap=10,ls=1.06):
    _,tf=add_box(slide,l,t,w,h)
    for i,it in enumerate(items):
        bold=False
        if isinstance(it,tuple): it,bold=it
        p=p0(tf) if i==0 else tf.add_paragraph()
        no_bullet(p); p.space_after=Pt(gap); p.space_before=Pt(0); p.line_spacing=ls
        set_run(p.add_run(),"•  ",size,color=GOLD,bold=True)
        set_run(p.add_run(),it,size,color=NAVY,bold=bold)
    return tf

NOSTYLE="{2D5ABB26-0587-4C30-8999-92F81FD0307C}"
def _bd(cell,edge,color,pt):
    tag="a:ln"+edge; tcPr=cell._tc.get_or_add_tcPr()
    for e in tcPr.findall(qn(tag)): tcPr.remove(e)
    ln=etree.Element(qn(tag)); ln.set("w",str(int(pt*12700))); ln.set("cap","flat")
    sf=etree.SubElement(ln,qn("a:solidFill"))
    c=etree.SubElement(sf,qn("a:srgbClr")); c.set("val","%02X%02X%02X"%(color[0],color[1],color[2]))
    tcPr.insert(0,ln)

def table(slide,data,l,t,w,h,col_w,fs=13,bold_rows=(),aligns=None,dark_header=True,zebra=True):
    rows=len(data); cols=len(data[0])
    gf=slide.shapes.add_table(rows,cols,E(l),E(t),E(w),E(h)); tbl=gf.table
    tblPr=tbl._tbl.find(qn("a:tblPr")); tblPr.set("firstRow","0"); tblPr.set("bandRow","0")
    sid=tblPr.find(qn("a:tableStyleId"))
    if sid is None: sid=etree.SubElement(tblPr,qn("a:tableStyleId"))
    sid.text=NOSTYLE
    tot=sum(col_w)
    for i,cw in enumerate(col_w): tbl.columns[i].width=E(w*cw/tot)
    for ri in range(rows): tbl.rows[ri].height=E(h/rows)
    for ri,row in enumerate(data):
        for ci,val in enumerate(row):
            cell=tbl.cell(ri,ci); cell.vertical_anchor=MSO_ANCHOR.MIDDLE
            cell.margin_left=E(8); cell.margin_right=E(8); cell.margin_top=E(2); cell.margin_bottom=E(2)
            head=dark_header and ri==0; cell.fill.solid()
            cell.fill.fore_color.rgb=HEADBG if head else (ROWALT if (zebra and ri%2==0) else WHITE)
            p=cell.text_frame.paragraphs[0]
            p.alignment=(aligns[ci] if aligns else (PP_ALIGN.LEFT if ci==0 else PP_ALIGN.CENTER))
            set_run(p.add_run(),str(val),fs,color=(WHITE if head else NAVY),bold=head or (ri in bold_rows))
            if not head: _bd(cell,"B",LINEC,0.5)
    return gf

def chrome(slide,section,title,subtitle,page,total=8):
    add_rect(slide,0,0,1280,720,WHITE); add_rect(slide,1190,0,5,720,GOLDL)
    add_rect(slide,57,49,7,7,GOLD,shape=MSO_SHAPE.OVAL)
    _,tf=add_box(slide,74,42,820,24); set_run(p0(tf).add_run(),section,11,color=GOLD,bold=True,spc=180)
    _,tf=add_box(slide,900,42,270,24,align=PP_ALIGN.RIGHT); set_run(p0(tf).add_run(),"DEAMs 24h  ·  CS DiD",11,color=GOLD,bold=True,spc=100)
    add_rect(slide,57,74,1133,1,LINEC); add_rect(slide,57,110,5,84,GOLD)
    _,tf=add_box(slide,81,100,1100,64,anchor=MSO_ANCHOR.MIDDLE); set_run(p0(tf).add_run(),title,30,color=NAVY,bold=True)
    if subtitle:
        _,tf=add_box(slide,81,188,1110,38); set_run(p0(tf).add_run(),subtitle,15,color=GRAY,italic=True)
    add_rect(slide,57,676,1133,1,LINEC)
    _,tf=add_box(slide,74,684,900,22); set_run(p0(tf).add_run(),"AVALIAÇÃO DE IMPACTO CAUSAL  ·  DEAMs 24h NO BRASIL",9,color=GOLD,bold=True,spc=110)
    _,tf=add_box(slide,1060,684,130,22,align=PP_ALIGN.RIGHT); set_run(p0(tf).add_run(),"%02d / %02d"%(page,total),9,color=GOLD,bold=True)

def render_formula(tex,path,fontsize=26):
    fig=plt.figure(figsize=(6,1.1))
    fig.text(0.01,0.5,tex,fontsize=fontsize,color=NAVY_HEX,ha="left",va="center",math_fontfamily="cm")
    fig.savefig(path,dpi=300,transparent=True,bbox_inches="tight",pad_inches=0.05); plt.close(fig)

def progress_bars(slide, rows, l_label, l_bar, bar_w, top, step=36, barh=18):
    # rows = [(label, value), ...]
    maxv=max(v for _,v in rows)
    for i,(lab,v) in enumerate(rows):
        cy=top+i*step
        _,tf=add_box(slide,l_label,cy-4,66,barh+8,anchor=MSO_ANCHOR.MIDDLE,align=PP_ALIGN.RIGHT)
        set_run(p0(tf).add_run(),str(lab),13,color=NAVY,bold=True)
        add_rect(slide,l_bar,cy,bar_w,barh,TRACK,shape=MSO_SHAPE.ROUNDED_RECTANGLE)
        add_rect(slide,l_bar,cy,max(10,v/maxv*bar_w),barh,(GOLD if v==maxv else GOLDL),shape=MSO_SHAPE.ROUNDED_RECTANGLE)
        _,tf=add_box(slide,l_bar+bar_w+8,cy-4,40,barh+8,anchor=MSO_ANCHOR.MIDDLE)
        set_run(p0(tf).add_run(),str(v),13,color=NAVY,bold=True)

def wipe_slides(prs):
    lst=prs.slides._sldIdLst
    for sid in list(lst):
        prs.part.drop_rel(sid.get(qn("r:id"))); lst.remove(sid)

def new_slide(prs,layout):
    s=prs.slides.add_slide(layout)
    for sh in list(s.shapes): sh._element.getparent().remove(sh._element)
    return s

def safe_save(prs, out):
    try: prs.save(out); return out
    except PermissionError:
        base,ext=os.path.splitext(out); out=base+" (novo)"+ext; prs.save(out); return out
```

### Esqueleto de uso
```python
prs = Presentation(SRC_OU_TEMPLATE)       # qualquer pptx 16:9 com 1 layout utilizável
LAY = prs.slides[0].slide_layout
wipe_slides(prs)
s = new_slide(prs, LAY)                    # capa: desenhar à mão (seção 4)
s = new_slide(prs, LAY); chrome(s,"DADOS · 02","Dados e Fontes","subtítulo",2)
# ... add tables / bullets / fit_pic / progress_bars ...
out = safe_save(prs, OUT)
```

---

## 10. Checklist de QA antes de entregar

- [ ] Fundo branco em todos os slides; barra dourada à direita presente.
- [ ] Toda fonte é Times New Roman (inclusive tabelas e fórmulas-imagem em tom NAVY).
- [ ] Marcadores são "•" dourados; nenhum travessão como marcador.
- [ ] Chrome idêntico (rótulos, filetes, numeração `NN / TT`) em todo conteúdo.
- [ ] Nenhum shape ultrapassa `1280×720` (validar reabrindo com python-pptx).
- [ ] Tabelas com cabeçalho NAVY, zebra e bordas finas; legenda abaixo.
- [ ] Máx. 1–2 elementos visuais por slide; fontes legíveis (corpo ≥ 14.5).
- [ ] Salvou ignorando locks `~$`; não tentou converter via LibreOffice.

---

## 11. Referência viva

- **Deck de referência:** `Trabalho de avaliacao de politicas sociais (revisado v2).pptx` (8 slides).
- **Origem do estilo:** capa de `Volatility_Trading_Profissional.pptx` (marinho+dourado),
  adaptada para fundo branco + Times New Roman.
- **Conteúdo/dados:** relatório `relatorios/relatorios_finais/deam24h_relatorio.tex` (tabelas e números)
  e figuras em `relatorios/figuras_causal/`.
- Estrutura aprovada (8 slides): Capa · Pergunta · Dados · Estatísticas (Tratados×Controle) ·
  Metodologia (fórmula CS + barras de progresso por coorte) · Resultados (ATT + pré-tendências) ·
  Event Studies · Conclusões & Limitações.
