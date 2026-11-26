"""Punto de entrada del laboratorio AE4 - Problema de parqueaderos.

Uso:
    python main.py                       # 30 réplicas base, 720 min, semilla 42
    python main.py --quick               # humo: 3 réplicas, 180 min
    python main.py --replicas 40
    python main.py --duration 720
    python main.py --seed 7

El programa:
1. corre una simulación piloto larga para detectar el calentamiento;
2. estima cuántas réplicas se necesitan para un error relativo del 10 %;
3. corre el experimento definitivo con números aleatorios comunes;
4. guarda los datos crudos en ``outputs/``.

Las cifras son simuladas.  No provienen de datos reales del centro comercial.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import numpy as np

from src.analysis import result_to_dataframes
from src.parking_simulation import (
    DEFAULT_DURATION_MIN,
    DEFAULT_MASTER_SEED,
    DEFAULT_PILOT_DURATION_MIN,
    DEFAULT_REPLICAS,
    DEFAULT_SCENARIO_KEYS,
    MAIN_SCENARIO,
    estimar_replicas_requeridas,
    format_summary,
    run_experiment,
    run_pilot,
)


def _json_default(value: object):
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, (np.bool_,)):
        return bool(value)
    raise TypeError(f"Tipo no serializable: {type(value)!r}")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Simulación del sistema de pago de parqueaderos (AE4)."
    )
    parser.add_argument(
        "--replicas",
        type=int,
        default=DEFAULT_REPLICAS,
        help="Réplicas base; el programa puede aumentarlas para cumplir la precisión.",
    )
    parser.add_argument(
        "--duration",
        type=float,
        default=DEFAULT_DURATION_MIN,
        help="Duración de una jornada en minutos (por defecto 720 = 12 h).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=DEFAULT_MASTER_SEED,
        help="Semilla maestra para SeedSequence.spawn.",
    )
    parser.add_argument(
        "--pilot-duration",
        type=float,
        default=DEFAULT_PILOT_DURATION_MIN,
        help="Duración de la corrida piloto para detectar el calentamiento.",
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
        help="Atajo de humo: 3 réplicas, 180 minutos y piloto de 800 minutos.",
    )
    return parser.parse_args()


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    args = _parse_args()
    replicas_base = 3 if args.quick else args.replicas
    duration = 180.0 if args.quick else args.duration
    pilot_duration = 800.0 if args.quick else args.pilot_duration

    print("1/3  Corrida piloto para detectar el estado estable...")
    pilot = run_pilot(
        duration_min=pilot_duration,
        master_seed=args.seed,
        scenario_key=MAIN_SCENARIO,
    )
    warmup = float(pilot["cut_min"])
    # Protección: nunca descartar más de la cuarta parte de la jornada.
    warmup = min(warmup, 0.25 * duration)
    print(
        f"     Calentamiento detectado: {warmup:.0f} min "
        f"(ventana del promedio móvil: {pilot['window']} min)."
    )

    print("2/3  Estimación del número de réplicas necesarias...")
    preliminary = run_experiment(
        replicas=replicas_base,
        duration_min=duration,
        warmup_min=warmup,
        master_seed=args.seed,
        scenario_keys=DEFAULT_SCENARIO_KEYS,
    )
    base_waits = [
        row["mean_wait"]
        for row in preliminary.replica_rows
        if row["scenario"] == MAIN_SCENARIO
    ]
    replication = estimar_replicas_requeridas(
        base_waits,
        target_relative_error=0.10,
        min_replicas=replicas_base,
    )
    replicas_final = int(replication["n_requerido"])
    print(
        f"     Réplicas base: {replicas_base} | requeridas: {replicas_final} | "
        f"error relativo actual: {replication['error_relativo_actual']:.1%}"
    )

    print("3/3  Experimento definitivo...")
    if replicas_final != replicas_base:
        result = run_experiment(
            replicas=replicas_final,
            duration_min=duration,
            warmup_min=warmup,
            master_seed=args.seed,
            scenario_keys=DEFAULT_SCENARIO_KEYS,
        )
    else:
        result = preliminary

    result.metadata.update(
        {
            "replicas_base": replicas_base,
            "replicas_requeridas_estimadas": replicas_final,
            "replicas_finales": replicas_final,
            "target_relative_error": 0.10,
            "error_relativo_actual": replication["error_relativo_actual"],
            "pilot_duration_min": pilot_duration,
            "pilot_cut_min": pilot["cut_min"],
            "pilot_window_min": pilot["window"],
            "pilot_reference_mean": pilot["reference_mean"],
            "pilot_tolerance": pilot["tolerance"],
            "pilot_mean_before": pilot["mean_before"],
            "pilot_mean_after": pilot["mean_after"],
        }
    )

    print(format_summary(result))

    save_dir: Path = args.save_dir
    save_dir.mkdir(parents=True, exist_ok=True)

    frames = result_to_dataframes(result)
    frames["replicas"].to_csv(
        save_dir / "replicas.csv", index=False, encoding="utf-8-sig"
    )
    frames["cajeros"].to_csv(
        save_dir / "cajeros.csv", index=False, encoding="utf-8-sig"
    )
    frames["clientes"].to_csv(
        save_dir / "clientes.csv", index=False, encoding="utf-8-sig"
    )

    payload = result.to_dict(include_customers=False)
    (save_dir / "resultados.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False, default=_json_default),
        encoding="utf-8",
    )

    # Serie del piloto para las figuras del punto E.
    pilot_df = {
        "minuto": pilot["times"],
        "n_en_sistema": pilot["series"],
        "media_movil": np.concatenate(
            [
                np.full(int(pilot["window"]), np.nan),
                np.asarray(pilot["moving_average"], dtype=float),
            ]
        )[: len(pilot["times"])],
        "media_acumulada": pilot["cumulative"],
    }
    max_len = len(pilot["times"])
    for key in pilot_df:
        pilot_df[key] = np.asarray(pilot_df[key])[:max_len]
    import pandas as pd

    pd.DataFrame(pilot_df).to_csv(
        save_dir / "pilot_serie.csv", index=False, encoding="utf-8-sig"
    )
    pilot_summary = {
        "duracion_min": pilot["duration_min"],
        "escenario": pilot["scenario"],
        "calentamiento_min": pilot["cut_min"],
        "ventana_promedio_movil_min": pilot["window"],
        "referencia_n": pilot["reference_mean"],
        "tolerancia": pilot["tolerance"],
        "media_antes": pilot["mean_before"],
        "media_despues": pilot["mean_after"],
        "primer_bloque_n": float(np.mean(np.asarray(pilot["series"])[: int(pilot["cut_min"])])),
        "serie_n": int(max_len),
    }
    (save_dir / "pilot_resumen.json").write_text(
        json.dumps(pilot_summary, indent=2, ensure_ascii=False, default=_json_default),
        encoding="utf-8",
    )

    print("")
    print(f"Archivos crudos guardados en: {save_dir.resolve()}")
    print("  - replicas.csv")
    print("  - cajeros.csv")
    print("  - clientes.csv")
    print("  - resultados.json")
    print("  - pilot_serie.csv")
    print("  - pilot_resumen.json")
    print("")
    print("Siguiente paso: python scripts/build_report_assets.py")


if __name__ == "__main__":
    main()
