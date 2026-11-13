"""Audita las cifras del manuscrito contra outputs/ y verifica rubric.

Uso: python scripts/audit_manuscript.py
Genera: outputs/auditoria_manuscrito.json y docs/auditoria_final.md
"""
from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path

from PIL import Image
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
TEX = ROOT / "manuscrito_final.tex"
PDF = ROOT / "manuscrito_final.pdf"
DOCS = ROOT / "docs"

METRICS = ("macro_f1", "accuracy", "recall_s3")
FIELDS = ("mean", "sd", "min", "max", "ci_low", "ci_high")


def load_data() -> dict:
    return json.loads((OUT / "experimento_hmm_resumen.json").read_text(encoding="utf-8"))


def pdf_text() -> str:
    reader = PdfReader(PDF)
    return "\n".join((page.extract_text() or "") for page in reader.pages)


def count_abstract_words(text: str) -> int:
    start = text.find("El riesgo de incendio forestal suele")
    end = text.find("Palabras clave")
    abstract = text[start:end]
    return len(re.findall(r"\S+", abstract))


def main() -> None:
    data = load_data()
    text = pdf_text()
    flat = re.sub(r"\s+", " ", text).replace("−", "-")

    rows = []
    def check(label: str, value: float, source: str) -> None:
        formatted = f"{value:.4f}"
        candidates = {f"{value:.3f}", f"{value:.4f}", f"{value:.6f}"}
        present = any(candidate in flat for candidate in candidates)
        if "p_value_holm" in source and value == 0.0:
            present = "< 0.001" in flat
        rows.append(
            {
                "afirmacion": label,
                "valor": value,
                "redondeado": formatted,
                "fuente": source,
                "presente_en_texto": present,
            }
        )

    for model in ("M0", "M1", "M2"):
        for metric in METRICS:
            for field in FIELDS:
                check(
                    f"{model}.{metric}.{field}",
                    data["models"][model][metric][field],
                    f"models.{model}.{metric}.{field}",
                )

    for contrast in ("M0_vs_M1", "M0_vs_M2"):
        comp = data["comparisons"][contrast]
        check(f"{contrast}.mean_difference", comp["mean_difference"],
              f"comparisons.{contrast}.mean_difference")
        check(f"{contrast}.p_value_holm", comp["p_value_holm"],
              f"comparisons.{contrast}.p_value_holm")
        check(f"{contrast}.cliff_delta", comp["cliff_delta"],
              f"comparisons.{contrast}.cliff_delta")

    # Solo se auditan las diagonales citadas en el texto (M0 y M2).
    for model in ("M0", "M2"):
        matrix = data["models"][model]["confusion_matrix_normalized"]
        for index in range(3):
            check(f"{model}.confusion.diag{index + 1}", matrix[index][index],
                  f"models.{model}.confusion_matrix_normalized[{index}][{index}]")

    reader = PdfReader(PDF)
    total_pages = len(reader.pages)
    ref_page = None
    annex_page = None
    for index, page in enumerate(reader.pages, start=1):
        page_text = unicodedata.normalize("NFKC", page.extract_text() or "")
        if ref_page is None and "Referencias" in page_text:
            ref_page = index
        if annex_page is None and "Tabla de verificación numérica" in page_text:
            annex_page = index

    abstract_words = count_abstract_words(text)
    forbidden = {
        word: len(re.findall(rf"\b{word}\b", text, flags=re.IGNORECASE))
        for word in ("anteproyecto", "provisional", "pendiente")
    }
    hashes = {}
    for name in (
        "experimento_hmm_resumen.json",
        "tabla_resumen_manuscrito.csv",
        "fig_metricas_300dpi.png",
        "fig_confusion_300dpi.png",
    ):
        import hashlib
        hashes[name] = hashlib.sha256((OUT / name).read_bytes()).hexdigest()

    dpi = {}
    for name in ("fig_metricas_300dpi.png", "fig_confusion_300dpi.png"):
        dpi[name] = Image.open(OUT / name).info.get("dpi")

    all_present = all(row["presente_en_texto"] for row in rows)
    report = {
        "paginas_totales": total_pages,
        "pagina_inicio_referencias": ref_page,
        "paginas_cuerpo": ref_page,
        "paginas_cuerpo_rango": "10-15",
        "pagina_inicio_anexo": annex_page,
        "resumen_palabras": abstract_words,
        "resumen_rango": "150-250",
        "terminos_prohibidos": forbidden,
        "figuras_dpi": dpi,
        "hashes_sha256": hashes,
        "cifras_verificadas": len(rows),
        "todas_las_cifras_presentes": all_present,
        "filas": rows,
    }
    (OUT / "auditoria_manuscrito.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    DOCS.mkdir(exist_ok=True)
    lines = [
        "# Auditoría final del manuscrito",
        "",
        f"- PDF: `manuscrito_final.pdf` ({total_pages} páginas totales).",
        f"- Cuerpo principal: páginas 1-{ref_page} (Referencias inician en la p. {ref_page}); "
        f"Anexo inicia en la p. {annex_page}.",
        f"- Resumen: {abstract_words} palabras (rango 150-250).",
        f"- Términos prohibidos: {forbidden}.",
        f"- Figuras a 300 dpi: {dpi}.",
        f"- Cifras contrastadas: {len(rows)}; todas presentes: {all_present}.",
        "",
        "## Cifras del manuscrito contra `outputs/`",
        "",
        "| Afirmación | Valor | Redondeado | Fuente | Coincide |",
        "|---|---:|---:|---|---|",
    ]
    for row in rows:
        status = "Sí" if row["presente_en_texto"] else "NO"
        lines.append(
            f"| {row['afirmacion']} | {row['valor']:.6f} | {row['redondeado']} | "
            f"`{row['fuente']}` | {status} |"
        )
    lines += [
        "",
        "## Hashes SHA-256",
        "",
        "| Archivo | SHA-256 |",
        "|---|---|",
    ]
    for name, digest in hashes.items():
        lines.append(f"| `{name}` | `{digest}` |")
    (DOCS / "auditoria_final.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "filas"}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
