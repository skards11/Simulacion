"""Punto de entrada del sistema HMM de riesgo de incendios forestales.

Uso local:
    python main.py

Uso en Google Colab (desde la carpeta del proyecto):
    !python main.py

El programa imprime el reporte operativo y muestra tres figuras:
    1. Humedad diaria con bandas de riesgo y posibles focos.
    2. Índice de peligro y comparación real vs inferido (Viterbi).
    3. Panel resumen: conteos, matriz de confusión y focos por humedad.
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt

from src.hmm_model import HMM
from src.simulation import compute_metrics, run_simulation
from src.utils import (
    format_report,
    plot_danger_index_and_comparison,
    plot_humidity_and_risk,
    plot_summary_dashboard,
    results_dataframe,
)

N_DAYS = 120
SEED = 42
ALERT_THRESHOLD = 75.0
OUTPUT_DIR = Path("outputs")


def main() -> None:
    # Evita errores de codificación al imprimir acentos en consolas Windows.
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    model = HMM(seed=SEED)
    simulation = run_simulation(
        model=model,
        n_days=N_DAYS,
        seed=SEED,
        alert_threshold=ALERT_THRESHOLD,
    )
    metrics = compute_metrics(simulation)

    print(format_report(simulation, metrics))

    # Tabla diaria (útil en Colab para inspeccionar o descargar resultados).
    dataframe = results_dataframe(simulation)
    print("\nPrimeros 8 días de la tabla de resultados:")
    print(dataframe.head(8).to_string(index=False))

    OUTPUT_DIR.mkdir(exist_ok=True)
    plot_humidity_and_risk(
        simulation, save_path=OUTPUT_DIR / "humedad_y_riesgo.png"
    )
    plot_danger_index_and_comparison(
        simulation, save_path=OUTPUT_DIR / "indice_y_comparacion.png"
    )
    plot_summary_dashboard(
        simulation, save_path=OUTPUT_DIR / "resumen_metricas.png"
    )
    dataframe.to_csv(OUTPUT_DIR / "resultados_diarios.csv", index=False)

    print(f"\nFiguras y CSV guardados en: {OUTPUT_DIR.resolve()}")
    plt.show()


if __name__ == "__main__":
    main()
