"""Reproduce el experimento D7 de punta a punta y regenera ``outputs/``.

Uso:
    python scripts/reproduce.py

Ejecuta, en este orden:
1. Las pruebas unitarias.
2. El experimento completo (T = 500, N = 2000, SeedSequence(42)).
3. Las tablas CSV/Markdown y la figura comparativa.
4. El manifiesto SHA-256 de los artefactos generados.

El script no fija semillas distintas ni modifica parámetros: usa los valores
por defecto del protocolo vigente.
"""

from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUTS = ROOT / "outputs"
EXCLUDED = {"MANIFEST.txt", ".gitkeep"}


def _run(*args: str) -> None:
    subprocess.run([sys.executable, *args], cwd=ROOT, check=True)


def write_manifest() -> Path:
    """Genera ``outputs/MANIFEST.txt`` con SHA-256 de los artefactos."""
    files = sorted(
        path
        for path in OUTPUTS.iterdir()
        if path.is_file() and path.name not in EXCLUDED
    )
    lines = [
        "# MANIFEST SHA-256 - AE2_HMM/outputs",
        "# Generado por scripts/reproduce.py",
        "# Algoritmo: SHA-256; formato: <hash>  <archivo>",
        "",
    ]
    for path in files:
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        lines.append(f"{digest}  {path.name}")

    manifest = OUTPUTS / "MANIFEST.txt"
    manifest.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return manifest


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    _run("-m", "pytest", "-q")
    _run("main.py", "--save", "outputs/experimento_hmm_resumen.json")
    _run(
        "scripts/report_d4.py",
        "--input",
        "outputs/experimento_hmm_resumen.json",
        "--outdir",
        "outputs",
    )
    manifest = write_manifest()
    print(f"\nManifiesto SHA-256 generado en: {manifest.resolve()}")


if __name__ == "__main__":
    main()
