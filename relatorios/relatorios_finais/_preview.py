"""Renderiza cada página do PDF do relatório em PNG para inspeção visual.
Uso: python _preview.py
Saída: _preview/pagina_NN.png
"""
from pathlib import Path
import fitz

ROOT = Path(__file__).resolve().parent
PDF = ROOT / "deam24h_relatorio.pdf"
OUT = ROOT / "_preview"
OUT.mkdir(exist_ok=True)

doc = fitz.open(PDF)
for i, page in enumerate(doc, start=1):
    pix = page.get_pixmap(dpi=110)
    pix.save(OUT / f"pagina_{i:02d}.png")
print(f"{doc.page_count} páginas renderizadas em {OUT.relative_to(ROOT)}/")
