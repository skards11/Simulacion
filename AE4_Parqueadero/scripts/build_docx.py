"""Genera el documento Word (.docx) a partir de ``docs/documento_entrega.md``.

Uso (desde la carpeta AE4_Parqueadero):

    python scripts/build_docx.py

El conversor cubre lo que usa el documento:

* títulos (#, ##, ###, ####);
* párrafos con **negrita**, *cursiva* y `código`;
* listas con viñetas y numeradas;
* tablas Markdown con encabezado;
* bloques de código y citas;
* imágenes relativas a la carpeta ``docs/``;
* matemáticas simples ($...$ y $$...$$) convertidas a texto legible.

No requiere pandoc ni conexión a internet.  Las fórmulas se simplifican a
notación de texto porque Word no interpreta LaTeX sin complementos.
"""

from __future__ import annotations

from datetime import datetime
import re
from pathlib import Path
import sys

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Inches, Pt, RGBColor

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs" / "documento_entrega.md"
TARGET = ROOT / "docs" / "documento_entrega.docx"

BLUE = RGBColor(0x0F, 0x34, 0x60)
GRAY = RGBColor(0x59, 0x59, 0x59)

# ----------------------------------------------------------------------
# Matemáticas -> texto plano
# ----------------------------------------------------------------------
MATH_REPLACEMENTS: tuple[tuple[str, str], ...] = (
    (r"\\text\{([^{}]*)\}", r"\1"),
    (r"\\mathrm\{([^{}]*)\}", r"\1"),
    (r"\\operatorname\{([^{}]*)\}", r"\1"),
    (r"\\bar\{([^{}]*)\}", r"\1"),
    (r"\\hat\{([^{}]*)\}", r"\1"),
    (r"\\lceil", "⌈"),
    (r"\\rceil", "⌉"),
    (r"\\lfloor", "⌊"),
    (r"\\rfloor", "⌋"),
    (r"\\lambda", "λ"),
    (r"\\mu", "μ"),
    (r"\\rho", "ρ"),
    (r"\\sigma", "σ"),
    (r"\\chi", "χ"),
    (r"\\tau", "τ"),
    (r"\\theta", "θ"),
    (r"\\gamma", "γ"),
    (r"\\pi", "π"),
    (r"\\times", "×"),
    (r"\\cdot", "·"),
    (r"\\leq?", "≤"),
    (r"\\geq?", "≥"),
    (r"\\approx", "≈"),
    (r"\\infty", "∞"),
    (r"\\pm", "±"),
    (r"\\sqrt", "√"),
    (r"\\qquad", "    "),
    (r"\\quad", "  "),
    (r"\\,", " "),
    (r"\\;", " "),
    (r"\\!", ""),
    (r"\\left", ""),
    (r"\\right", ""),
    (r"\\%", "%"),
    (r"\\_", "_"),
)


def _replace_fraction(match: re.Match[str]) -> str:
    numerator = match.group(1).strip()
    denominator = match.group(2).strip()
    if any(operator in denominator for operator in "+- "):
        denominator = f"({denominator})"
    return f"{numerator}/{denominator}"


def math_to_text(expression: str) -> str:
    text = expression.strip()
    # Primero se resuelven los envoltorios de texto para que las fracciones
    # con llaves internas (por ejemplo ``E[\text{tiempo}]``) se reconozcan.
    for pattern, replacement in (
        (r"\\text\{([^{}]*)\}", r"\1"),
        (r"\\mathrm\{([^{}]*)\}", r"\1"),
        (r"\\operatorname\{([^{}]*)\}", r"\1"),
    ):
        text = re.sub(pattern, replacement, text)
    for _ in range(3):  # resuelve fracciones anidadas
        new = re.sub(r"\\frac\{([^{}]+)\}\{([^{}]+)\}", _replace_fraction, text)
        if new == text:
            break
        text = new
    for pattern, replacement in MATH_REPLACEMENTS:
        text = re.sub(pattern, replacement, text)
    text = text.replace("^2", "²").replace("^3", "³")
    text = re.sub(r"_\{([^{}]*)\}", r"\1", text)
    text = re.sub(r"\^\{([^{}]*)\}", r"^\1", text)
    text = re.sub(r"\\[a-zA-Z]+", "", text)
    text = text.replace("{", "").replace("}", "")
    text = re.sub(r"_([A-Za-z0-9])", r"\1", text)
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip()


# ----------------------------------------------------------------------
# Formato en línea
# ----------------------------------------------------------------------
INLINE_PATTERN = re.compile(
    r"(\*\*.+?\*\*|__.+?__|\*[^*\n]+?\*|`[^`]+?`|\[[^\]]+\]\([^)]+\)|\$[^$]+\$)"
)


def add_inline(paragraph, text: str) -> None:
    """Agrega texto con negrita, cursiva, código y enlaces."""
    position = 0
    for match in INLINE_PATTERN.finditer(text):
        if match.start() > position:
            paragraph.add_run(text[position : match.start()])
        token = match.group(0)
        if token.startswith("**") or token.startswith("__"):
            run = paragraph.add_run(token[2:-2])
            run.bold = True
        elif token.startswith("`"):
            run = paragraph.add_run(token[1:-1])
            run.font.name = "Consolas"
            run.font.size = Pt(9.5)
            run.font.color.rgb = RGBColor(0xB0, 0x30, 0x60)
        elif token.startswith("$"):
            run = paragraph.add_run(math_to_text(token[1:-1]))
            run.italic = True
        elif token.startswith("["):
            label = token[1 : token.index("]")]
            run = paragraph.add_run(label)
            run.underline = True
            run.font.color.rgb = BLUE
        elif token.startswith("*"):
            run = paragraph.add_run(token[1:-1])
            run.italic = True
        position = match.end()
    if position < len(text):
        paragraph.add_run(text[position:])


# ----------------------------------------------------------------------
# Utilidades de Word
# ----------------------------------------------------------------------
def set_cell_background(cell, hex_color: str) -> None:
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), hex_color)
    shd.set(qn("w:val"), "clear")
    cell._tc.get_or_add_tcPr().append(shd)


def set_cell_margins(cell, top: int = 40, bottom: int = 40, left: int = 80, right: int = 80) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    mar = OxmlElement("w:tcMar")
    for tag, value in (("top", top), ("bottom", bottom), ("start", left), ("end", right)):
        node = OxmlElement(f"w:{tag}")
        node.set(qn("w:w"), str(value))
        node.set(qn("w:type"), "dxa")
        mar.append(node)
    tc_pr.append(mar)


def add_page_number_footer(section) -> None:
    footer = section.footer
    paragraph = footer.paragraphs[0]
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = paragraph.add_run("Página ")
    run.font.size = Pt(8.5)
    run.font.color.rgb = GRAY

    def field(instruction: str):
        fld_begin = OxmlElement("w:fldChar")
        fld_begin.set(qn("w:fldCharType"), "begin")
        instr = OxmlElement("w:instrText")
        instr.set(qn("xml:space"), "preserve")
        instr.text = instruction
        fld_sep = OxmlElement("w:fldChar")
        fld_sep.set(qn("w:fldCharType"), "separate")
        number = OxmlElement("w:t")
        number.text = "1"
        fld_end = OxmlElement("w:fldChar")
        fld_end.set(qn("w:fldCharType"), "end")
        return [fld_begin, instr, fld_sep, number, fld_end]

    for element in field("PAGE"):
        paragraph._p.append(element)
    run = paragraph.add_run(" de ")
    run.font.size = Pt(8.5)
    run.font.color.rgb = GRAY
    for element in field("NUMPAGES"):
        paragraph._p.append(element)


def add_toc(document: Document) -> None:
    heading = document.add_paragraph()
    heading.paragraph_format.space_before = Pt(0)
    run = heading.add_run("Índice")
    run.bold = True
    run.font.size = Pt(20)
    run.font.color.rgb = BLUE

    paragraph = document.add_paragraph()
    fld_begin = OxmlElement("w:fldChar")
    fld_begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = r'TOC \o "1-3" \h \z \u'
    fld_sep = OxmlElement("w:fldChar")
    fld_sep.set(qn("w:fldCharType"), "separate")
    placeholder = OxmlElement("w:t")
    placeholder.text = (
        "Actualice el índice en Word con clic derecho > Actualizar campo, "
        "o con F9."
    )
    fld_end = OxmlElement("w:fldChar")
    fld_end.set(qn("w:fldCharType"), "end")
    for element in (fld_begin, instr, fld_sep, placeholder, fld_end):
        paragraph._p.append(element)


def style_document(document: Document) -> None:
    styles = document.styles
    normal = styles["Normal"]
    normal.font.name = "Calibri"
    normal.font.size = Pt(11)
    normal.paragraph_format.space_after = Pt(6)
    normal.paragraph_format.line_spacing = 1.15
    normal.element.rPr.rFonts.set(qn("w:eastAsia"), "Calibri")

    for level, size, color in (
        (1, 22, BLUE),
        (2, 16, BLUE),
        (3, 13, RGBColor(0x1A, 0x1A, 0x2E)),
        (4, 11.5, RGBColor(0x1A, 0x1A, 0x2E)),
    ):
        style = styles[f"Heading {level}"]
        style.font.name = "Calibri"
        style.font.size = Pt(size)
        style.font.bold = True
        style.font.color.rgb = color
        style.element.rPr.rFonts.set(qn("w:eastAsia"), "Calibri")
        style.paragraph_format.space_before = Pt(14 if level <= 2 else 10)
        style.paragraph_format.space_after = Pt(6)

    section = document.sections[0]
    section.page_width = Cm(21.0)
    section.page_height = Cm(29.7)
    section.left_margin = Cm(2.5)
    section.right_margin = Cm(2.5)
    section.top_margin = Cm(2.5)
    section.bottom_margin = Cm(2.3)
    add_page_number_footer(section)


# ----------------------------------------------------------------------
# Bloques
# ----------------------------------------------------------------------
def add_table(document: Document, rows: list[list[str]]) -> None:
    if not rows:
        return
    width = max(len(row) for row in rows)
    rows = [row + [""] * (width - len(row)) for row in rows]
    table = document.add_table(rows=len(rows), cols=width)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = "Table Grid"
    table.autofit = True
    font_size = Pt(9) if width <= 7 else Pt(7.8)

    for row_index, row in enumerate(rows):
        for column_index, value in enumerate(row):
            cell = table.cell(row_index, column_index)
            set_cell_margins(cell)
            paragraph = cell.paragraphs[0]
            paragraph.paragraph_format.space_after = Pt(0)
            paragraph.paragraph_format.line_spacing = 1.0
            add_inline(paragraph, value.strip())
            for run in paragraph.runs:
                run.font.size = font_size
                if row_index == 0:
                    run.bold = True
            if row_index == 0:
                set_cell_background(cell, "E8EEF7")

    # Repite el encabezado si la tabla cruza de página.
    header = table.rows[0]._tr
    tr_pr = header.get_or_add_trPr()
    repeat = OxmlElement("w:tblHeader")
    repeat.set(qn("w:val"), "true")
    tr_pr.append(repeat)

    document.add_paragraph().paragraph_format.space_after = Pt(2)


def add_image(document: Document, alt: str, path: Path) -> None:
    if not path.exists():
        paragraph = document.add_paragraph()
        run = paragraph.add_run(f"[Falta la imagen: {path}]")
        run.italic = True
        run.font.color.rgb = RGBColor(0xC0, 0x30, 0x30)
        return
    paragraph = document.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = paragraph.add_run()
    run.add_picture(str(path), width=Inches(6.2))


def add_caption(document: Document, text: str) -> None:
    paragraph = document.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.paragraph_format.space_after = Pt(10)
    add_inline(paragraph, text)
    for run in paragraph.runs:
        run.font.size = Pt(9)
        run.font.color.rgb = GRAY


def add_code_block(document: Document, lines: list[str]) -> None:
    paragraph = document.add_paragraph()
    paragraph.paragraph_format.left_indent = Cm(0.4)
    paragraph.paragraph_format.space_after = Pt(8)
    paragraph.paragraph_format.line_spacing = 1.0
    run = paragraph.add_run("\n".join(lines))
    run.font.name = "Consolas"
    run.font.size = Pt(8.5)
    shading = OxmlElement("w:shd")
    shading.set(qn("w:fill"), "F4F6F8")
    paragraph._p.get_or_add_pPr().append(shading)


def add_quote(document: Document, text: str) -> None:
    paragraph = document.add_paragraph()
    paragraph.paragraph_format.left_indent = Cm(0.8)
    paragraph.paragraph_format.space_before = Pt(4)
    paragraph.paragraph_format.space_after = Pt(8)
    add_inline(paragraph, text)
    for run in paragraph.runs:
        run.font.color.rgb = RGBColor(0x33, 0x33, 0x33)
        run.italic = True


# ----------------------------------------------------------------------
# Conversión
# ----------------------------------------------------------------------
def convert(markdown: str, document: Document) -> None:
    # Ecuaciones en bloque: se convierten a párrafos centrados.
    markdown = re.sub(
        r"\$\$(.+?)\$\$",
        lambda m: "\n\n@@MATH@@" + " ".join(m.group(1).split()) + "\n\n",
        markdown,
        flags=re.S,
    )

    lines = markdown.splitlines()
    index = 0
    first_section = True

    while index < len(lines):
        line = lines[index]
        stripped = line.strip()

        if not stripped:
            index += 1
            continue

        if stripped.startswith("```"):
            block: list[str] = []
            index += 1
            while index < len(lines) and not lines[index].strip().startswith("```"):
                block.append(lines[index])
                index += 1
            add_code_block(document, block)
            index += 1
            continue

        if stripped.startswith("@@MATH@@"):
            paragraph = document.add_paragraph()
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = paragraph.add_run(math_to_text(stripped.replace("@@MATH@@", "")))
            run.italic = True
            run.font.name = "Cambria Math"
            run.font.size = Pt(11)
            paragraph.paragraph_format.space_before = Pt(6)
            paragraph.paragraph_format.space_after = Pt(8)
            index += 1
            continue

        heading = re.match(r"^(#{1,6})\s+(.*)$", stripped)
        if heading:
            level = len(heading.group(1))
            text = heading.group(2).strip()
            if text == "Resumen ejecutivo" and first_section:
                first_section = False
                document.add_page_break()
                add_toc(document)
                document.add_page_break()
            elif re.match(r"^[1-5]\.\s", text) or text in ("Referencias", "Anexos"):
                document.add_page_break()
            document.add_heading(text, level=min(level, 4) if level > 1 else 1)
            index += 1
            continue

        if stripped == "---":
            index += 1
            continue

        if stripped.startswith("|"):
            rows: list[list[str]] = []
            while index < len(lines) and lines[index].strip().startswith("|"):
                row_text = lines[index].strip()
                if not re.match(r"^\|[\s:\-|]+\|$", row_text):
                    cells = [cell.strip() for cell in row_text.strip("|").split("|")]
                    rows.append(cells)
                index += 1
            add_table(document, rows)
            continue

        image = re.match(r"^!\[(.*?)\]\((.*?)\)\s*$", stripped)
        if image:
            alt, relative = image.groups()
            add_image(document, alt, (SOURCE.parent / relative).resolve())
            index += 1
            continue

        if stripped.startswith("> "):
            quoted: list[str] = []
            while index < len(lines) and lines[index].strip().startswith(">"):
                quoted.append(lines[index].strip().lstrip(">").strip())
                index += 1
            add_quote(document, " ".join(quoted))
            continue

        bullet = re.match(r"^[-*]\s+(.*)$", stripped)
        if bullet:
            parts = [bullet.group(1).strip()]
            index += 1
            while (
                index < len(lines)
                and lines[index].strip()
                and lines[index][:1] in (" ", "\t")
                and not re.match(r"^\s*[-*]\s+", lines[index])
            ):
                parts.append(lines[index].strip())
                index += 1
            paragraph = document.add_paragraph(style="List Bullet")
            add_inline(paragraph, " ".join(parts))
            continue

        numbered = re.match(r"^\d+\.\s+(.*)$", stripped)
        if numbered:
            parts = [numbered.group(1).strip()]
            index += 1
            while (
                index < len(lines)
                and lines[index].strip()
                and lines[index][:1] in (" ", "\t")
                and not re.match(r"^\s*(\d+\.|[-*])\s+", lines[index])
            ):
                parts.append(lines[index].strip())
                index += 1
            paragraph = document.add_paragraph(style="List Number")
            add_inline(paragraph, " ".join(parts))
            continue

        # Párrafo normal: une líneas consecutivas.
        paragraph_lines = [stripped]
        index += 1
        while index < len(lines):
            candidate = lines[index].strip()
            if (
                not candidate
                or candidate.startswith(("#", "|", ">", "```", "!["))
                or candidate == "---"
                or re.match(r"^[-*]\s+", candidate)
                or re.match(r"^\d+\.\s+", candidate)
                or re.match(r"^[A-ZÁÉÍÓÚÑ][^.]{0,60}:$", candidate)
            ):
                break
            paragraph_lines.append(candidate)
            index += 1

        text = " ".join(paragraph_lines)
        if text.startswith("*") and text.endswith("*") and len(text) > 2:
            add_caption(document, text)
        else:
            paragraph = document.add_paragraph()
            paragraph.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            add_inline(paragraph, text)


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    if not SOURCE.exists():
        raise SystemExit(f"No se encontró {SOURCE}")

    markdown = SOURCE.read_text(encoding="utf-8")

    document = Document()
    style_document(document)

    core = document.core_properties
    core.title = "Solución de un problema de parqueaderos (AE4)"
    core.subject = "Simulación de eventos discretos - Centro Comercial Supercentro"
    core.author = (
        "Oscar Alonso De la Pava Suarez; Anderson Jesus Ospina Cardona; "
        "Kevin Andrés Valencia Daza"
    )
    core.keywords = "simulación, teoría de colas, M/M/1, parqueadero, AE4"
    core.comments = "Documento generado desde docs/documento_entrega.md"
    core.created = datetime(2026, 11, 24, 12, 0, 0)

    convert(markdown, document)
    document.save(TARGET)

    print(f"Documento generado: {TARGET}")
    print(f"Tamaño: {TARGET.stat().st_size / 1024:.1f} KB")
    print("Abra el archivo en Word y actualice el índice (F9) si es necesario.")


if __name__ == "__main__":
    main()
