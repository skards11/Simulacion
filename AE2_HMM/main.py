"""Punto de entrada del protocolo D4.

Uso:
    python main.py --quick     # humo: T=50, N=20, bootstrap=200
    python main.py             # protocolo completo: T=500, N=2000

El protocolo completo puede tardar varios minutos. Las cifras son simuladas.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from src.simulation import (
    DEFAULT_BOOTSTRAP_SAMPLES,
    DEFAULT_MASTER_SEED,
    DEFAULT_N,
    DEFAULT_T,
    PROVISIONAL_ALTERED_MIXING,
    format_summary,
    run_d4_experiment,
)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Protocolo D4: comparación M0/M1/M2 sobre secuencias HMM."
    )
    parser.add_argument("--T", type=int, default=DEFAULT_T, help="Pasos por secuencia.")
    parser.add_argument("--N", type=int, default=DEFAULT_N, help="Número de secuencias.")
    parser.add_argument(
        "--seed",
        type=int,
        default=DEFAULT_MASTER_SEED,
        help="Semilla maestra; cada secuencia recibe una semilla derivada.",
    )
    parser.add_argument(
        "--bootstrap",
        type=int,
        default=DEFAULT_BOOTSTRAP_SAMPLES,
        help="Réplicas de bootstrap para el IC de secuencias.",
    )
    parser.add_argument(
        "--decoder",
        choices=("posterior", "viterbi"),
        default="posterior",
        help="Regla de decodificación para M2.",
    )
    parser.add_argument(
        "--altered-mixing",
        type=float,
        default=PROVISIONAL_ALTERED_MIXING,
        help="Mezcla provisional con uniforme para el escenario B alterada.",
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Atajo de humo: T=50, N=20, bootstrap=200.",
    )
    parser.add_argument(
        "--save",
        type=Path,
        default=None,
        help="Ruta opcional para guardar el resumen en JSON.",
    )
    return parser.parse_args()


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    args = _parse_args()
    T, N, bootstrap = args.T, args.N, args.bootstrap
    if args.quick:
        T, N, bootstrap = 50, 20, 200

    results = run_d4_experiment(
        T=T,
        N=N,
        seed=args.seed,
        bootstrap_samples=bootstrap,
        decoder=args.decoder,
        altered_mixing=args.altered_mixing,
    )

    for scenario_name, result in results.items():
        print("=" * 72)
        print(f"Escenario: {scenario_name}")
        print(format_summary(result))

    if args.save is not None:
        payload = {
            scenario_name: result.to_dict()
            for scenario_name, result in results.items()
        }
        args.save.parent.mkdir(parents=True, exist_ok=True)
        args.save.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        print(f"\nResumen guardado en: {args.save.resolve()}")


if __name__ == "__main__":
    main()
