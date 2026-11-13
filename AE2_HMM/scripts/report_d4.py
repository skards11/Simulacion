"""Genera tablas y figura a partir del JSON del experimento HMM.

Uso:
    python scripts/report_d4.py
    python scripts/report_d4.py --input outputs/experimento_hmm_resumen.json

El JSON es la fuente de verdad. Este script no recalcula el experimento.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

MODEL_NAMES = ("M0", "M1", "M2")
METRIC_NAMES = ("macro_f1", "accuracy", "recall_s3")
METRIC_LABELS = {
    "macro_f1": "Macro-F1",
    "accuracy": "Exactitud",
    "recall_s3": "Recall Riesgo Extremo",
}
STATE_LABELS = ("Riesgo Bajo", "Riesgo Moderado", "Riesgo Extremo")
STATE_SHORT = ("RB", "RM", "RE")


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _metric_rows(payload: dict) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for model_name in MODEL_NAMES:
        for metric_name in METRIC_NAMES:
            stats = payload["models"][model_name][metric_name]
            rows.append(
                {
                    "modelo": model_name,
                    "metrica": metric_name,
                    "media": stats["mean"],
                    "sd": stats["sd"],
                    "minimo": stats["min"],
                    "maximo": stats["max"],
                    "mediana": stats["median"],
                    "q1": stats["q1"],
                    "q3": stats["q3"],
                    "ric": stats["iqr"],
                    "ic_inferior": stats["ci_low"],
                    "ic_superior": stats["ci_high"],
                    "n": stats["n"],
                }
            )
    return rows


def _confusion_rows(payload: dict) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for model_name in MODEL_NAMES:
        counts = np.asarray(
            payload["models"][model_name]["confusion_matrix_counts"],
            dtype=int,
        )
        normalized = np.asarray(
            payload["models"][model_name]["confusion_matrix_normalized"],
            dtype=float,
        )
        for true_index, true_label in enumerate(STATE_LABELS):
            for predicted_index, predicted_label in enumerate(STATE_LABELS):
                rows.append(
                    {
                        "modelo": model_name,
                        "estado_real": true_label,
                        "estado_predicho": predicted_label,
                        "conteo": int(counts[true_index, predicted_index]),
                        "proporcion_fila": float(
                            normalized[true_index, predicted_index]
                        ),
                    }
                )
    return rows


def _comparison_rows(payload: dict) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for comparison_name, comparison in payload["comparisons"].items():
        rows.append(
            {
                "comparacion": comparison_name,
                "diferencia_media": comparison["mean_difference"],
                "diferencia_mediana": comparison["median_difference"],
                "estadistico_wilcoxon": comparison["wilcoxon_statistic"],
                "p_valor": comparison["p_value_raw"],
                "p_valor_holm": comparison["p_value_holm"],
                "delta_cliff": comparison["cliff_delta"],
                "n_pares": comparison["n_pairs"],
            }
        )
    return rows


def _write_csv(rows: list[dict[str, object]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _markdown(payload: dict) -> str:
    metadata = payload["metadata"]
    lines = [
        "# Resultados simulados — experimento HMM M0/M1/M2",
        "",
        "Cifras simuladas; no son evidencia de validez ecológica.",
        "",
        f"- T = {metadata['T']}",
        f"- N = {metadata['N']}",
        f"- Semilla maestra = {metadata['master_seed']}",
        f"- Secuencias de semilla: `{metadata['seed_sequence']}`",
        f"- Mezcla de B alterada: m = {metadata['mixing']}",
        f"- Corrección: {metadata['holm_correction']}",
        "",
        "## Métricas por modelo",
        "",
        "| Modelo | Media | Desviación Estándar | Mínimo | Máximo | Mediana | RIC | IC 95 % [P2.5, P97.5] |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for model_name in MODEL_NAMES:
        stats = payload["models"][model_name]["macro_f1"]
        lines.append(
            f"| {model_name} | {stats['mean']:.4f} | {stats['sd']:.4f} | "
            f"{stats['min']:.4f} | {stats['max']:.4f} | "
            f"{stats['median']:.4f} | {stats['iqr']:.4f} | "
            f"[{stats['ci_low']:.4f}, {stats['ci_high']:.4f}] |"
        )

    lines.extend(
        [
            "",
            "## Contrastes pareados",
            "",
            "| Contraste | Diferencia media | p crudo | p Holm | Delta de Cliff |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for comparison_name in ("M0_vs_M1", "M0_vs_M2"):
        comparison = payload["comparisons"][comparison_name]
        lines.append(
            f"| {comparison_name} | {comparison['mean_difference']:.4f} | "
            f"{comparison['p_value_raw']:.3e} | "
            f"{comparison['p_value_holm']:.3e} | "
            f"{comparison['cliff_delta']:.4f} |"
        )

    lines.extend(["", "## Criterios de éxito", ""])
    for criterion_name, criterion in payload["criteria"].items():
        status = "CUMPLE" if criterion["met"] else "NO CUMPLE"
        lines.append(f"- **{criterion_name}:** {status}")

    lines.extend(["", "## Matriz de confusión normalizada por fila", ""])
    for model_name in MODEL_NAMES:
        matrix = np.asarray(
            payload["models"][model_name]["confusion_matrix_normalized"],
            dtype=float,
        )
        lines.append(f"### {model_name}")
        lines.append("")
        lines.append("| Real \\ Predicho | RB | RM | RE |")
        lines.append("|---|---:|---:|---:|")
        for index, label in enumerate(STATE_LABELS):
            cells = " | ".join(f"{value:.4f}" for value in matrix[index])
            lines.append(f"| {label} | {cells} |")
        lines.append("")

    return "\n".join(lines)


def _plot(payload: dict, path: Path) -> None:
    fig = plt.figure(figsize=(15, 9), constrained_layout=True)
    grid = fig.add_gridspec(2, 3, height_ratios=(1.0, 1.15))

    ax_bar = fig.add_subplot(grid[0, :2])
    ax_box = fig.add_subplot(grid[0, 2])
    axes_confusion = [fig.add_subplot(grid[1, index]) for index in range(3)]

    means = np.array(
        [payload["models"][model]["macro_f1"]["mean"] for model in MODEL_NAMES]
    )
    lows = np.array(
        [payload["models"][model]["macro_f1"]["ci_low"] for model in MODEL_NAMES]
    )
    highs = np.array(
        [payload["models"][model]["macro_f1"]["ci_high"] for model in MODEL_NAMES]
    )
    x = np.arange(len(MODEL_NAMES))
    ax_bar.bar(
        x,
        means,
        yerr=np.vstack([means - lows, highs - means]),
        capsize=5,
        color=("#4c72b0", "#dd8452", "#55a868"),
        alpha=0.9,
    )
    ax_bar.set_xticks(x, labels=MODEL_NAMES)
    ax_bar.set_ylim(0.0, 1.0)
    ax_bar.set_ylabel("Macro-F1")
    ax_bar.set_title("Macro-F1 por modelo (media e IC 95 % percentil)")
    ax_bar.grid(axis="y", alpha=0.25)

    sequences = [
        np.asarray(payload["per_sequence"][model]["macro_f1"], dtype=float)
        for model in MODEL_NAMES
    ]
    ax_box.boxplot(sequences, tick_labels=MODEL_NAMES, showfliers=False)
    ax_box.set_ylim(0.0, 1.0)
    ax_box.set_title("Distribución por secuencia")
    ax_box.grid(axis="y", alpha=0.25)

    for axis, model_name in zip(axes_confusion, MODEL_NAMES):
        matrix = np.asarray(
            payload["models"][model_name]["confusion_matrix_normalized"],
            dtype=float,
        )
        image = axis.imshow(matrix, vmin=0.0, vmax=1.0, cmap="Blues")
        axis.set_xticks(range(3), labels=STATE_SHORT)
        axis.set_yticks(range(3), labels=STATE_SHORT)
        axis.set_xlabel("Predicho")
        axis.set_ylabel("Real")
        axis.set_title(f"Matriz de confusión — {model_name}")
        for row in range(3):
            for column in range(3):
                value = matrix[row, column]
                axis.text(
                    column,
                    row,
                    f"{value:.2f}",
                    ha="center",
                    va="center",
                    color="white" if value > 0.55 else "black",
                    fontsize=9,
                )

    fig.colorbar(image, ax=axes_confusion, fraction=0.025, pad=0.02)
    fig.suptitle(
        "Experimento HMM — cifras simuladas (T = "
        f"{payload['metadata']['T']}, N = {payload['metadata']['N']})",
        fontsize=13,
        fontweight="bold",
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("outputs/experimento_hmm_resumen.json"),
    )
    parser.add_argument("--outdir", type=Path, default=Path("outputs"))
    args = parser.parse_args()

    payload = _load(args.input)
    _write_csv(_metric_rows(payload), args.outdir / "experimento_hmm_metricas.csv")
    _write_csv(
        _confusion_rows(payload),
        args.outdir / "experimento_hmm_confusion.csv",
    )
    _write_csv(
        _comparison_rows(payload),
        args.outdir / "experimento_hmm_comparaciones.csv",
    )
    (args.outdir / "experimento_hmm_resumen.md").write_text(
        _markdown(payload),
        encoding="utf-8",
    )
    _plot(payload, args.outdir / "experimento_hmm_comparativa.png")
    print(f"Tablas y figura generadas en: {args.outdir.resolve()}")


if __name__ == "__main__":
    main()
