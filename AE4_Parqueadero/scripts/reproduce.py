"""Reproduce el laboratorio AE4 completo y genera un manifiesto SHA-256.

Uso (desde la carpeta AE4_Parqueadero):

    python scripts/reproduce.py
    python scripts/reproduce.py --replicas 40
    python scripts/reproduce.py --skip-tests

Pasos:

1. Pruebas unitarias (pytest).
2. Simulación completa (main.py).
3. Tablas, figuras y resumen (build_report_assets.py).
4. Documento Word (build_docx.py).
5. Manifiesto ``outputs/MANIFEST.txt`` con el hash SHA-256 de cada artefacto.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def _run(command: list[str]) -> None:
    print("")
    print("> " + " ".join(command), flush=True)
    subprocess.run(command, cwd=ROOT, check=True)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_manifest(outputs_dir: Path) -> Path:
    """Escribe los hashes de todos los artefactos generados."""
    manifest = outputs_dir / "MANIFEST.txt"
    files = sorted(
        path
        for path in outputs_dir.rglob("*")
        if path.is_file() and path.name != "MANIFEST.txt"
    )
    lines = [
        "# Manifiesto SHA-256 de los artefactos generados",
        "# Ejecutar: python scripts/reproduce.py",
        "",
    ]
    for path in files:
        relative = path.relative_to(outputs_dir).as_posix()
        lines.append(f"{_sha256(path)}  {relative}")
    manifest.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Reproduce el laboratorio de parqueaderos y genera el manifiesto."
    )
    parser.add_argument(
        "--replicas",
        type=int,
        default=30,
        help="Réplicas base; main.py puede aumentarlas para cumplir la precisión.",
    )
    parser.add_argument("--duration", type=float, default=720.0)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="Omite pytest (no recomendado para la entrega final).",
    )
    args = parser.parse_args()

    if not args.skip_tests:
        _run([sys.executable, "-m", "pytest", "-q"])

    _run(
        [
            sys.executable,
            "main.py",
            "--replicas",
            str(args.replicas),
            "--duration",
            str(args.duration),
            "--seed",
            str(args.seed),
        ]
    )
    _run([sys.executable, "scripts/build_report_assets.py"])
    _run([sys.executable, "scripts/build_docx.py"])

    manifest = write_manifest(ROOT / "outputs")
    print("")
    print("Manifiesto generado:", manifest.resolve())


if __name__ == "__main__":
    main()
