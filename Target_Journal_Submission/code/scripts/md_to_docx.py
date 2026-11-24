"""Convert the manuscript markdown files to .docx (headings, paragraphs with **bold**/*italic*, numbered lists, pipe tables).
Usage: python scripts/md_to_docx.py IN.md OUT.docx"""
import sys, re
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_LINE_SPACING
src, dst = sys.argv[1], sys.argv[2]
doc = Document(); st = doc.styles["Normal"]; st.font.name = "Times New Roman"; st.font.size = Pt(12)
for sec in doc.sections: sec.left_margin = sec.right_margin = Cm(2.5)
def runs(par, text):
    for part in re.split(r"(\*\*[^*]+\*\*|\*[^*]+\*)", text):
        if not part: continue
        if part.startswith("**"): par.add_run(part[2:-2]).bold = True
        elif part.startswith("*") and len(part) > 2: par.add_run(part[1:-1]).italic = True
        else: par.add_run(part)
lines = open(src, encoding="utf-8").read().split("\n"); i = 0
while i < len(lines):
    l = lines[i]
    if l.startswith("|"):
        rows = []
        while i < len(lines) and lines[i].startswith("|"):
            if not re.match(r"^\|[-|\s]+\|$", lines[i]): rows.append([c.strip() for c in lines[i].strip("|").split("|")])
            i += 1
        t = doc.add_table(rows=len(rows), cols=max(len(r) for r in rows)); t.style = "Table Grid"
        for r, row in enumerate(rows):
            for c, val in enumerate(row):
                cell = t.cell(r, c); cell.text = ""; p = cell.paragraphs[0]; runs(p, val)
                for rn in p.runs:
                    rn.font.size = Pt(8.5)
                    if r == 0: rn.bold = True
        doc.add_paragraph(); continue
    m = re.match(r"^(#{1,4})\s+(.*)", l)
    if m: doc.add_heading(m.group(2).strip(), level=min(len(m.group(1)), 3) if len(m.group(1)) > 1 else 0 if i == 0 else 1)
    elif l.strip().startswith(("* ", "- ")): runs(doc.add_paragraph(style="List Bullet"), l.strip()[2:])
    elif l.strip():
        p = doc.add_paragraph(); runs(p, l.strip()); p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE if "References" not in "".join(lines[max(0,i-200):i]) else WD_LINE_SPACING.SINGLE
    i += 1
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
for sec in doc.sections:  # continuous line numbering (journal requirement)
    ln = OxmlElement("w:lnNumType"); ln.set(qn("w:countBy"), "1"); ln.set(qn("w:restart"), "continuous"); sec._sectPr.append(ln)
    fp = sec.footer.paragraphs[0]; r = fp.add_run(); f1 = OxmlElement("w:fldSimple"); f1.set(qn("w:instr"), "PAGE"); r._r.append(f1)
for img in sys.argv[3:]:
    doc.add_picture(img, width=Cm(16))
doc.save(dst); print("wrote", dst)
