"""Genera tablas y figuras del manuscrito a partir de outputs/ (300 dpi).

Uso: python scripts/build_paper_assets.py
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
METHODS = ("M0", "M1", "M2")
LABELS = {
    "M0": "M0: Viterbi nominal",
    "M1": "M1: baseline sin memoria",
    "M2": "M2: Viterbi con $B(m{=}0.5)$",
}
COLORS = {"M0": "#1f4e79", "M1": "#2e75b6", "M2": "#c55a11"}


def load() -> dict:
    return json.loads((OUT / "experimento_hmm_resumen.json").read_text(encoding="utf-8"))


def main() -> None:
    d = load()
    rows = []
    for m in METHODS:
        for metric in ("macro_f1", "accuracy", "recall_s3"):
            s = d["models"][m][metric]
            rows.append(
                {
                    "modelo": m,
                    "metrica": metric,
                    "media": s["mean"],
                    "sd": s["sd"],
                    "min": s["min"],
                    "max": s["max"],
                    "p2_5": s["ci_low"],
                    "p97_5": s["ci_high"],
                }
            )
    with (OUT / "tabla_resumen_manuscrito.csv").open("w", encoding="utf-8", newline="") as fh:
        fh.write("modelo,metrica,media,sd,min,max,ic95_inf,ic95_sup\n")
        for r in rows:
            fh.write(
                f"{r['modelo']},{r['metrica']},{r['media']:.6f},{r['sd']:.6f},"
                f"{r['min']:.6f},{r['max']:.6f},{r['p2_5']:.6f},{r['p97_5']:.6f}\n"
            )

    # Figura 1: macro-F1 por modelo con IC 95 %
    fig, ax = plt.subplots(figsize=(6.6, 3.9))
    x = np.arange(len(METHODS))
    means = [d["models"][m]["macro_f1"]["mean"] for m in METHODS]
    lo = [d["models"][m]["macro_f1"]["ci_low"] for m in METHODS]
    hi = [d["models"][m]["macro_f1"]["ci_high"] for m in METHODS]
    err = [means[i] - lo[i] for i in range(3)], [hi[i] - means[i] for i in range(3)]
    bars = ax.bar(x, means, yerr=err, capsize=5, width=0.58,
                  color=[COLORS[m] for m in METHODS], edgecolor="black", linewidth=0.6)
    ax.axhline(1 / 3, color="gray", linestyle="--", linewidth=0.9)
    ax.set_xticks(x)
    ax.set_xticklabels([LABELS[m] for m in METHODS], fontsize=9)
    ax.set_ylabel("Macro-F1 (media, IC 95 %)", fontsize=9)
    ax.set_ylim(0.25, 0.75)
    ax.grid(axis="y", alpha=0.3, linewidth=0.5)
    for i, b in enumerate(bars):
        ax.text(b.get_x() + b.get_width() / 2, hi[i] + 0.012, f"{means[i]:.4f}",
                ha="center", va="bottom", fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "fig_metricas_300dpi.png", dpi=300)
    plt.close(fig)

    # Figura 2: matrices de confusión normalizadas (3 paneles + barra horizontal)
    fig = plt.figure(figsize=(9.0, 3.5))
    grid = fig.add_gridspec(2, 3, height_ratios=[1.0, 0.05], hspace=0.55,
                            left=0.06, right=0.985, top=0.90, bottom=0.10)
    axes = [fig.add_subplot(grid[0, k]) for k in range(3)]
    for ax, m in zip(axes, METHODS):
        mat = np.asarray(d["models"][m]["confusion_matrix_normalized"], dtype=float)
        im = ax.imshow(mat, cmap="Blues", vmin=0, vmax=1)
        ax.set_title(LABELS[m], fontsize=8)
        ax.set_xticks(range(3), ["RB", "RM", "RE"], fontsize=8)
        ax.set_yticks(range(3), ["RB", "RM", "RE"], fontsize=8)
        ax.set_xlabel("Predicho", fontsize=8)
        if m == "M0":
            ax.set_ylabel("Real", fontsize=8)
        for i in range(3):
            for j in range(3):
                val = mat[i, j]
                ax.text(j, i, f"{val:.3f}", ha="center", va="center", fontsize=7,
                        color="white" if val > 0.55 else "black")
    cax = fig.add_subplot(grid[1, :])
    fig.colorbar(im, cax=cax, orientation="horizontal")
    cax.tick_params(labelsize=7)
    fig.savefig(OUT / "fig_confusion_300dpi.png", dpi=300)
    plt.close(fig)

    # Auditoría: hashes SHA-256 de todos los artefactos
    manifest = []
    for p in sorted(OUT.iterdir()):
        if p.is_file() and p.name != "MANIFEST.txt":
            manifest.append(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}")
    (OUT / "MANIFEST.txt").write_text(
        "# MANIFEST SHA-256 - AE2_HMM/outputs\n"
        "# Generado por scripts/build_paper_assets.py\n"
        "# Algoritmo: SHA-256; formato: <hash>  <archivo>\n\n" + "\n".join(manifest) + "\n",
        encoding="utf-8",
    )

    print(json.dumps({"rows": rows, "comparisons": d["comparisons"],
                      "criteria": d["criteria"], "metadata": d["metadata"]},
                     indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
