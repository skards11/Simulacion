"""Punto de entrada del experimento HMM M0/M1/M2.

Uso:
    python main.py                 # protocolo completo: T=500, N=2000
    python main.py --quick         # humo: T=50, N=50
    python main.py --save outputs/experimento_hmm_resumen.json

Las cifras son simuladas.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from src.simulation import (
    ALTERED_MIXING,
    DEFAULT_MASTER_SEED,
    DEFAULT_N,
    DEFAULT_T,
    format_summary,
    run_experiment,
)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Experimento HMM: comparación M0/M1/M2 sobre secuencias discretas."
    )
    parser.add_argument("--T", type=int, default=DEFAULT_T, help="Pasos por secuencia.")
    parser.add_argument("--N", type=int, default=DEFAULT_N, help="Número de réplicas.")
    parser.add_argument(
        "--seed",
        type=int,
        default=DEFAULT_MASTER_SEED,
        help="Semilla maestra para SeedSequence.spawn.",
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Atajo de humo: T=50, N=50.",
    )
    parser.add_argument(
        "--save",
        type=Path,
        default=Path("outputs/experimento_hmm_resumen.json"),
        help="Ruta del JSON de resultados.",
    )
    return parser.parse_args()


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    args = _parse_args()
    T, N = args.T, args.N
    if args.quick:
        T, N = 50, 50

    result = run_experiment(T=T, N=N, master_seed=args.seed, mixing=ALTERED_MIXING)
    print(format_summary(result))

    args.save.parent.mkdir(parents=True, exist_ok=True)
    args.save.write_text(
        json.dumps(result.to_dict(), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"\nResumen guardado en: {args.save.resolve()}")


if __name__ == "__main__":
    main()
