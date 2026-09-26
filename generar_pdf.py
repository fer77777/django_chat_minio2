"""
Script para generar informe.pdf desde informe.md usando reportlab.
Uso: python generar_pdf.py
"""
import re
import sys
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    HRFlowable,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.platypus.flowables import KeepTogether

# ─── Rutas ────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
MD_PATH  = BASE_DIR / "informe.md"
PDF_PATH = BASE_DIR / "informe.pdf"

# ─── Paleta de colores ────────────────────────────────────────────────────────
DARK_BROWN   = colors.HexColor("#3B1F0A")
AMBER        = colors.HexColor("#D97706")
AMBER_LIGHT  = colors.HexColor("#FEF3C7")
AMBER_BORDER = colors.HexColor("#F59E0B")
GRAY_CODE    = colors.HexColor("#1E1E1E")
GRAY_LIGHT   = colors.HexColor("#F5F5F4")
WHITE        = colors.white
TEXT_DARK    = colors.HexColor("#1C1917")
TEXT_MID     = colors.HexColor("#57534E")
HR_COLOR     = colors.HexColor("#D6D3D1")

# ─── Estilos ──────────────────────────────────────────────────────────────────
base = getSampleStyleSheet()

def S(name, **kw):
    return ParagraphStyle(name, **kw)

styles = {
    "h1": S("H1",
        fontName="Helvetica-Bold", fontSize=20, leading=26,
        textColor=DARK_BROWN, spaceAfter=10, spaceBefore=16,
        alignment=TA_CENTER,
    ),
    "meta": S("Meta",
        fontName="Helvetica", fontSize=10, leading=14,
        textColor=TEXT_MID, spaceAfter=4,
        alignment=TA_CENTER,
    ),
    "h2": S("H2",
        fontName="Helvetica-Bold", fontSize=15, leading=20,
        textColor=DARK_BROWN, spaceBefore=18, spaceAfter=8,
        borderPad=4,
    ),
    "h3": S("H3",
        fontName="Helvetica-Bold", fontSize=12, leading=16,
        textColor=colors.HexColor("#78350F"), spaceBefore=12, spaceAfter=6,
    ),
    "body": S("Body",
        fontName="Helvetica", fontSize=10, leading=15,
        textColor=TEXT_DARK, spaceAfter=6, alignment=TA_JUSTIFY,
    ),
    "bullet": S("Bullet",
        fontName="Helvetica", fontSize=10, leading=14,
        textColor=TEXT_DARK, spaceAfter=3,
        leftIndent=16, bulletIndent=4,
        bulletFontName="Helvetica-Bold",
        bulletFontSize=10,
    ),
    "code": S("Code",
        fontName="Courier", fontSize=8.5, leading=13,
        textColor=colors.HexColor("#E5E7EB"),
        backColor=GRAY_CODE,
        borderColor=colors.HexColor("#374151"),
        borderWidth=1,
        borderPad=8,
        spaceBefore=6, spaceAfter=6,
        leftIndent=6, rightIndent=6,
    ),
    "code_label": S("CodeLabel",
        fontName="Courier-Bold", fontSize=8,
        textColor=AMBER, spaceBefore=2, spaceAfter=0,
        leftIndent=6,
    ),
    "conclusion": S("Conclusion",
        fontName="Helvetica", fontSize=10, leading=15,
        textColor=TEXT_DARK, spaceAfter=6, alignment=TA_JUSTIFY,
        leftIndent=10, rightIndent=10,
    ),
    "ref": S("Ref",
        fontName="Courier", fontSize=8.5, leading=13,
        textColor=colors.HexColor("#3B82F6"), spaceAfter=4,
    ),
}


# ─── Parser línea a línea ─────────────────────────────────────────────────────
def escape(text: str) -> str:
    """Escapa caracteres especiales de ReportLab."""
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")
    # restaurar ** → <b>
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    # restaurar `code` inline
    text = re.sub(r"`([^`]+)`", r'<font name="Courier" color="#D97706">\1</font>', text)
    return text


def parse_md(md_text: str):
    """Convierte el markdown a una lista de flowables de ReportLab."""
    story = []
    lines = md_text.splitlines()
    i = 0
    in_code = False
    code_lines = []
    code_lang = ""

    while i < len(lines):
        line = lines[i]

        # ── Bloque de código ──────────────────────────────────────
        if line.strip().startswith("```"):
            if not in_code:
                in_code = True
                code_lang = line.strip()[3:].strip()
                code_lines = []
            else:
                # cierra bloque
                in_code = False
                code_text = "\n".join(code_lines)
                if code_lang:
                    story.append(Paragraph(code_lang.upper(), styles["code_label"]))
                # Renderizar como Paragraph con estilo code
                safe = code_text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                story.append(Paragraph(safe.replace("\n", "<br/>"), styles["code"]))
                story.append(Spacer(1, 4))
            i += 1
            continue

        if in_code:
            code_lines.append(line)
            i += 1
            continue

        # ── Línea horizontal ---
        if re.match(r"^-{3,}$", line.strip()):
            story.append(Spacer(1, 6))
            story.append(HRFlowable(width="100%", thickness=1, color=HR_COLOR))
            story.append(Spacer(1, 6))
            i += 1
            continue

        # ── H1
        if line.startswith("# ") and not line.startswith("## "):
            story.append(Paragraph(escape(line[2:].strip()), styles["h1"]))
            story.append(HRFlowable(width="60%", thickness=2, color=AMBER, hAlign="CENTER"))
            story.append(Spacer(1, 8))
            i += 1
            continue

        # ── H2
        if line.startswith("## "):
            text = escape(line[3:].strip())
            p = Paragraph(text, styles["h2"])
            hr = HRFlowable(width="100%", thickness=1.5, color=AMBER)
            story.append(KeepTogether([Spacer(1, 4), p, hr, Spacer(1, 4)]))
            i += 1
            continue

        # ── H3
        if line.startswith("### "):
            story.append(Paragraph(escape(line[4:].strip()), styles["h3"]))
            i += 1
            continue

        # ── Negrita de metadata al inicio (**key:** value)
        if line.startswith("**") and ":**" in line:
            story.append(Paragraph(escape(line.strip()), styles["meta"]))
            i += 1
            continue

        # ── Bullet list
        if line.strip().startswith("- "):
            text = escape(line.strip()[2:])
            story.append(Paragraph(f"• &nbsp;{text}", styles["bullet"]))
            i += 1
            continue

        # ── Lista numerada
        m = re.match(r"^\d+\.\s+(.*)", line.strip())
        if m:
            text = escape(m.group(1))
            story.append(Paragraph(f"<b>•</b> &nbsp;{text}", styles["bullet"]))
            i += 1
            continue

        # ── Línea vacía
        if not line.strip():
            story.append(Spacer(1, 4))
            i += 1
            continue

        # ── Párrafo normal
        story.append(Paragraph(escape(line.strip()), styles["body"]))
        i += 1

    return story


# ─── Encabezado / pie de página ───────────────────────────────────────────────
def header_footer(canvas, doc):
    canvas.saveState()
    w, h = A4

    # Encabezado
    canvas.setFillColor(DARK_BROWN)
    canvas.rect(0, h - 1.2 * cm, w, 1.2 * cm, fill=True, stroke=False)
    canvas.setFillColor(WHITE)
    canvas.setFont("Helvetica-Bold", 9)
    canvas.drawString(1.5 * cm, h - 0.85 * cm, "🍫  Chocolatería Artesanal & Gourmet — Programación IV")
    canvas.setFont("Helvetica", 8)
    canvas.drawRightString(w - 1.5 * cm, h - 0.85 * cm, "Actividad 5 — Django + Ollama IA")

    # Pie
    canvas.setFillColor(AMBER_LIGHT)
    canvas.rect(0, 0, w, 0.9 * cm, fill=True, stroke=False)
    canvas.setFillColor(DARK_BROWN)
    canvas.setFont("Helvetica", 8)
    canvas.drawString(1.5 * cm, 0.3 * cm, "Informe Técnico — Fernando (FER)")
    canvas.drawRightString(w - 1.5 * cm, 0.3 * cm, f"Página {doc.page}")

    canvas.restoreState()


# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    print(f"[INFO] Leyendo {MD_PATH} ...")
    md_text = MD_PATH.read_text(encoding="utf-8")

    print("[INFO] Construyendo PDF ...")
    doc = SimpleDocTemplate(
        str(PDF_PATH),
        pagesize=A4,
        topMargin=1.8 * cm,
        bottomMargin=1.4 * cm,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        title="Informe Actividad 5 — Django + Ollama",
        author="Fernando (FER)",
        subject="Programación IV",
    )

    story = parse_md(md_text)
    doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)

    size_kb = PDF_PATH.stat().st_size // 1024
    print(f"[OK] PDF generado: {PDF_PATH}  ({size_kb} KB)")


if __name__ == "__main__":
    main()
