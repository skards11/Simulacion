"""Punto de entrada del laboratorio AE3 - Problema bancario.

Uso:
    python main.py                       # 30 réplicas, 480 min, semilla 42
    python main.py --quick               # humo: 3 réplicas, 120 min
    python main.py --replicas 50
    python main.py --save-dir outputs

Las cifras son simuladas. No provienen de datos reales del banco.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import numpy as np

from src.analysis import enrich_replicas, result_to_dataframes
from src.bank_simulation import (
    DEFAULT_DURATION_MIN,
    DEFAULT_MASTER_SEED,
    DEFAULT_REPLICAS,
    DEFAULT_SCENARIO_KEYS,
    format_summary,
    run_experiment,
)


def _json_default(value: object):
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, np.ndarray):
        return value.tolist()
    raise TypeError(f"Tipo no serializable: {type(value)!r}")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Simulación del problema bancario con cajas M/M/1."
    )
    parser.add_argument(
        "--replicas",
        type=int,
        default=DEFAULT_REPLICAS,
        help="Número de réplicas independientes (mínimo recomendado: 10).",
    )
    parser.add_argument(
        "--duration",
        type=float,
        default=DEFAULT_DURATION_MIN,
        help="Duración de un día de operación en minutos.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=DEFAULT_MASTER_SEED,
        help="Semilla maestra para SeedSequence.spawn.",
    )
    parser.add_argument(
        "--save-dir",
        type=Path,
        default=Path("outputs"),
        help="Carpeta donde se guardan los resultados crudos.",
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Atajo de humo: 3 réplicas y 120 minutos.",
    )
    return parser.parse_args()


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    args = _parse_args()
    replicas = 3 if args.quick else args.replicas
    duration = 120.0 if args.quick else args.duration

    result = run_experiment(
        replicas=replicas,
        duration_min=duration,
        master_seed=args.seed,
        scenario_keys=DEFAULT_SCENARIO_KEYS,
    )
    print(format_summary(result))

    save_dir: Path = args.save_dir
    save_dir.mkdir(parents=True, exist_ok=True)

    frames = result_to_dataframes(result)
    frames["replicas"] = enrich_replicas(frames["replicas"])

    frames["replicas"].to_csv(
        save_dir / "replicas.csv", index=False, encoding="utf-8-sig"
    )
    frames["cajeros"].to_csv(
        save_dir / "cajeros.csv", index=False, encoding="utf-8-sig"
    )
    frames["clientes"].to_csv(
        save_dir / "clientes.csv", index=False, encoding="utf-8-sig"
    )
    frames["conteos"].to_csv(
        save_dir / "conteos_tipo.csv", index=False, encoding="utf-8-sig"
    )

    payload = result.to_dict(include_customers=False)
    (save_dir / "resultados.json").write_text(
        json.dumps(
            payload,
            indent=2,
            ensure_ascii=False,
            default=_json_default,
        ),
        encoding="utf-8",
    )

    print("")
    print(f"Archivos crudos guardados en: {save_dir.resolve()}")
    print("  - replicas.csv")
    print("  - cajeros.csv")
    print("  - clientes.csv")
    print("  - conteos_tipo.csv")
    print("  - resultados.json")
    print("")
    print("Siguiente paso: python scripts/build_report_assets.py")


if __name__ == "__main__":
    main()
