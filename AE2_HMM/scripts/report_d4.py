"""Genera tablas y una figura a partir del JSON del protocolo D4.

Uso:
    python scripts/report_d4.py
    python scripts/report_d4.py --input outputs/protocolo_d4_resumen.json

El JSON es la fuente de verdad de la ejecución. Este script no recalcula el
experimento ni modifica M1 o la B alterada.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

MODEL_NAMES = ("M0", "M1", "M2")
METRIC_NAMES = ("macro_f1", "recall_s3", "accuracy")
METRIC_LABELS = {
    "macro_f1": "Macro-F1",
    "recall_s3": "Recall s3",
    "accuracy": "Exactitud",
}


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _rows(payload: dict) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for scenario, result in payload.items():
        for model in MODEL_NAMES:
            for metric in METRIC_NAMES:
                stats = result["summary"][model][metric]
                rows.append(
                    {
                        "escenario": scenario,
                        "modelo": model,
                        "metrica": metric,
                        "media": stats["mean"],
                        "sd": stats["sd"],
                        "ic_inferior": stats["ci_low"],
                        "ic_superior": stats["ci_high"],
                        "T": result["T"],
                        "N": result["N"],
                        "semilla_maestra": result["master_seed"],
                    }
                )
    return rows


def _write_csv(rows: list[dict[str, object]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _markdown_table(result: dict) -> str:
    lines = [
        "| Modelo | Macro-F1 (media [IC 95 %]) | Recall s3 | Exactitud |",
        "|---|---:|---:|---:|",
    ]
    for model in MODEL_NAMES:
        cells = []
        for metric in METRIC_NAMES:
            stats = result["summary"][model][metric]
            mean = stats["mean"]
            low, high = stats["ci_low"], stats["ci_high"]
            if low is None or high is None:
                cells.append(f"{mean:.4f}")
            else:
                cells.append(f"{mean:.4f} [{low:.4f}, {high:.4f}]")
        lines.append(f"| {model} | {cells[0]} | {cells[1]} | {cells[2]} |")
    return "\n".join(lines)


def _write_markdown(payload: dict, path: Path) -> None:
    blocks = [
        "# Resultados simulados — protocolo D4",
        "",
        "Cifras simuladas; no son evidencia de validez ecológica.",
        "",
    ]
    for scenario, result in payload.items():
        blocks.append(f"## Escenario: {scenario}")
        blocks.append("")
        blocks.append(
            f"T = {result['T']}, N = {result['N']}, "
            f"semilla maestra = {result['master_seed']}."
        )
        blocks.append("")
        blocks.append(_markdown_table(result))
        blocks.append("")
    path.write_text("\n".join(blocks), encoding="utf-8")


def _plot(payload: dict, path: Path) -> None:
    scenarios = list(payload.keys())
    x = np.arange(len(MODEL_NAMES))
    width = 0.8 / max(len(scenarios), 1)

    fig, axes = plt.subplots(1, 3, figsize=(15, 4.8), sharey=True)
    for scenario_index, scenario in enumerate(scenarios):
        result = payload[scenario]
        offset = (scenario_index - (len(scenarios) - 1) / 2) * width
        for axis, metric in zip(axes, METRIC_NAMES):
            means = np.array(
                [result["summary"][model][metric]["mean"] for model in MODEL_NAMES]
            )
            lows = np.array(
                [result["summary"][model][metric]["ci_low"] for model in MODEL_NAMES],
                dtype=float,
            )
            highs = np.array(
                [result["summary"][model][metric]["ci_high"] for model in MODEL_NAMES],
                dtype=float,
            )
            yerr = np.vstack([means - lows, highs - means])
            axis.bar(
                x + offset,
                means,
                width,
                yerr=yerr,
                capsize=4,
                label=scenario,
                alpha=0.85,
            )
            axis.set_title(METRIC_LABELS[metric])
            axis.set_xticks(x, labels=MODEL_NAMES)
            axis.set_ylim(0.0, 1.0)
            axis.grid(axis="y", alpha=0.25)

    axes[0].set_ylabel("Valor")
    axes[0].legend(loc="lower right")
    fig.suptitle(
        "Protocolo D4 — cifras simuladas (media e IC 95 % por bootstrap de secuencias)",
        fontsize=12,
        fontweight="bold",
    )
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("outputs/protocolo_d4_resumen.json"),
    )
    parser.add_argument("--outdir", type=Path, default=Path("outputs"))
    args = parser.parse_args()

    payload = _load(args.input)
    rows = _rows(payload)
    _write_csv(rows, args.outdir / "protocolo_d4_resumen.csv")
    _write_markdown(payload, args.outdir / "protocolo_d4_resumen.md")
    _plot(payload, args.outdir / "protocolo_d4_metricas.png")
    print(f"Tablas y figura generadas en: {args.outdir.resolve()}")


if __name__ == "__main__":
    main()
