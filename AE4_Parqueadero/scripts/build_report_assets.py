"""Construye tablas derivadas, figuras y resumen del laboratorio AE4.

Uso (desde la carpeta AE4_Parqueadero, después de ejecutar ``main.py``):

    python scripts/build_report_assets.py

Entradas:
    outputs/replicas.csv, cajeros.csv, clientes.csv, resultados.json,
    pilot_serie.csv, pilot_resumen.json

Salidas:
    outputs/punto1_cajeros.csv ... outputs/punto5_antes_despues.csv
    outputs/decisiones.json
    outputs/resumen_ejecucion.md
    outputs/figuras/*.png (300 dpi)
"""

from __future__ import annotations

import json
from pathlib import Path
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.analysis import (  # noqa: E402
    build_calibration_tables,
    build_core_summaries,
    build_point1_table,
    build_point2_table,
    build_point3_tables,
    build_point5_table,
    build_validation_tables,
    build_verification_table,
)
from src.parking_simulation import (  # noqa: E402
    DEFAULT_MASTER_SEED,
    MAIN_SCENARIO,
    SERVICE_MEAN_MIN,
    TYPE_PROB,
    USER_TYPES,
    USER_TYPE_LABELS,
    mean_interarrival_min,
    mean_service_min,
    offered_load_erlangs,
    run_experiment,
    run_single_type_experiment,
    theoretical_mm1,
)

FIG_DIR = ROOT / "outputs" / "figuras"
OUT_DIR = ROOT / "outputs"

COLORS = {
    "rapido": "#27ae60",
    "normal": "#3498db",
    "lento": "#f39c12",
    "muy_lento": "#e74c3c",
    "ok": "#27ae60",
    "fail": "#e74c3c",
    "blue": "#0f3460",
    "gray": "#7f8c8d",
}


# ----------------------------------------------------------------------
# Utilidades
# ----------------------------------------------------------------------
def save_csv(df: pd.DataFrame, name: str) -> None:
    df.to_csv(OUT_DIR / name, index=False, encoding="utf-8-sig")


def save_json(payload: object, name: str) -> None:
    (OUT_DIR / name).write_text(
        json.dumps(payload, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )


def _fmt(value: float, decimals: int = 2) -> str:
    if value is None or (isinstance(value, float) and not np.isfinite(value)):
        return "—"
    return f"{value:.{decimals}f}"


def _md_table(df: pd.DataFrame, columns: list[tuple[str, str]], decimals: int = 2) -> str:
    header = "| " + " | ".join(label for _, label in columns) + " |"
    separator = "|" + "|".join(["---"] * len(columns)) + "|"
    lines = [header, separator]
    for _, row in df.iterrows():
        cells: list[str] = []
        for column, _ in columns:
            value = row[column]
            if isinstance(value, (bool, np.bool_)):
                cells.append("Sí" if value else "No")
            elif isinstance(value, (int, np.integer)):
                cells.append(str(int(value)))
            elif isinstance(value, (float, np.floating)):
                cells.append(_fmt(float(value), decimals))
            else:
                cells.append(str(value))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def _style_ax(ax: plt.Axes) -> None:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(True, axis="y", alpha=0.25)


# ----------------------------------------------------------------------
# Figuras
# ----------------------------------------------------------------------
def plot_sistema(path: Path) -> None:
    """Esquema conceptual: tres cajeros con filas independientes."""
    fig, ax = plt.subplots(figsize=(12, 5.6))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 6)
    ax.axis("off")

    ax.add_patch(
        FancyBboxPatch(
            (0.2, 2.2),
            2.2,
            1.6,
            boxstyle="round,pad=0.12",
            facecolor="#e3f2fd",
            edgecolor=COLORS["blue"],
            linewidth=1.5,
        )
    )
    ax.text(
        1.3,
        3.0,
        "Llegadas\nλ = 0.215 usu/min\n25% / 20% / 27.5% / 27.5%",
        ha="center",
        va="center",
        fontsize=9.5,
        weight="bold",
    )

    ys = [4.6, 3.0, 1.4]
    for index, y in enumerate(ys, start=1):
        ax.add_patch(
            FancyBboxPatch(
                (3.6, y - 0.28),
                2.1,
                0.56,
                boxstyle="round,pad=0.05",
                facecolor="#f8f9fa",
                edgecolor="#95a5a6",
                linewidth=1.1,
            )
        )
        ax.text(
            4.65,
            y,
            "Fila FIFO",
            ha="center",
            va="center",
            fontsize=9,
            color="#34495e",
        )
        ax.add_patch(
            FancyBboxPatch(
                (7.1, y - 0.34),
                1.7,
                0.68,
                boxstyle="round,pad=0.05",
                facecolor="#fff3e0",
                edgecolor="#e67e22",
                linewidth=1.4,
            )
        )
        ax.text(
            7.95,
            y,
            f"Cajero {index}\nM/M/1",
            ha="center",
            va="center",
            fontsize=9,
            weight="bold",
        )
        ax.annotate(
            "",
            xy=(3.55, y),
            xytext=(2.5, 3.0),
            arrowprops=dict(
                arrowstyle="->", color=COLORS["gray"], lw=1.0, connectionstyle="arc3"
            ),
        )
        ax.annotate(
            "",
            xy=(7.0, y),
            xytext=(5.8, y),
            arrowprops=dict(arrowstyle="->", color=COLORS["gray"], lw=1.2),
        )
        ax.annotate(
            "",
            xy=(10.0, y),
            xytext=(8.9, y),
            arrowprops=dict(arrowstyle="->", color=COLORS["gray"], lw=1.2),
        )
        ax.text(
            10.25,
            y,
            "Salida",
            ha="left",
            va="center",
            fontsize=9,
            color="#34495e",
        )

    ax.text(
        6.0,
        5.55,
        "Tres servidores independientes, sin cambio de fila ni deserción",
        ha="center",
        va="center",
        fontsize=12,
        weight="bold",
        color=COLORS["blue"],
    )
    ax.text(
        6.0,
        0.55,
        "Cada usuario elige un cajero al azar.  Servicio exponencial: 1, 3, 4 y 6 min.",
        ha="center",
        va="center",
        fontsize=9.5,
        color="#555555",
    )
    fig.tight_layout()
    fig.savefig(path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_transitorio(
    pilot: pd.DataFrame,
    meta: dict[str, object],
    path: Path,
) -> None:
    """N(t), promedio móvil, corte y media acumulada antes/después."""
    series = pilot["n_en_sistema"].to_numpy(dtype=float)
    times = pilot["minuto"].to_numpy(dtype=float)
    moving = pilot["media_movil"].to_numpy(dtype=float)
    cut = float(meta["calentamiento_min"])
    ref = float(meta["referencia_n"])
    tol = float(meta["tolerancia"])

    fig, axes = plt.subplots(2, 1, figsize=(12, 8.2), sharex=True)
    ax = axes[0]
    ax.plot(times, series, color="#bdc3c7", linewidth=0.7, label="N(t) observado")
    ax.plot(times, moving, color=COLORS["blue"], linewidth=2.0, label="Promedio móvil (60 min)")
    ax.axhline(ref, color=COLORS["ok"], linestyle="--", linewidth=1.4, label=f"Referencia = {ref:.2f}")
    ax.fill_between(
        times,
        ref - tol,
        ref + tol,
        color=COLORS["ok"],
        alpha=0.15,
        label=f"Banda ± {tol:.2f}",
    )
    ax.axvline(cut, color=COLORS["fail"], linestyle="--", linewidth=1.8)
    ax.text(
        cut + 80,
        ax.get_ylim()[1] * 0.88,
        f"Corte = {cut:.0f} min",
        color=COLORS["fail"],
        fontsize=10,
        weight="bold",
    )
    ax.set_ylabel("Usuarios en el sistema, N(t)")
    ax.set_title("Determinación del estado estable con promedio móvil")
    ax.legend(loc="upper right", fontsize=8, ncol=2)
    ax.set_xlim(0, min(3000, times[-1]))
    _style_ax(ax)

    ax = axes[1]
    cumulative = np.cumsum(series) / np.arange(1, len(series) + 1)
    ax.plot(times, cumulative, color="#2980b9", linewidth=1.8, label="Media acumulada con transitorio")
    after_series = series[int(cut) :]
    after_times = times[int(cut) :]
    cumulative_after = np.cumsum(after_series) / np.arange(1, len(after_series) + 1)
    ax.plot(
        after_times,
        cumulative_after,
        color=COLORS["ok"],
        linewidth=2.2,
        label="Media acumulada sin transitorio",
    )
    ax.axhline(ref, color=COLORS["gray"], linestyle=":", linewidth=1.0)
    ax.axvline(cut, color=COLORS["fail"], linestyle="--", linewidth=1.8)
    ax.set_xlabel("Tiempo (minutos)")
    ax.set_ylabel("Media acumulada de N(t)")
    ax.set_title("Antes y después de eliminar el estado transitorio")
    ax.legend(loc="lower right", fontsize=9)
    ax.set_xlim(0, min(3000, times[-1]))
    _style_ax(ax)

    fig.tight_layout()
    fig.savefig(path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_convergencia(customers_by_replica: pd.DataFrame, path: Path) -> None:
    """Media acumulada de Wq por número de réplicas, con IC 95 %."""
    df = customers_by_replica.sort_values("replica")
    values = df["mean_wait"].to_numpy(dtype=float)
    n = np.arange(1, len(values) + 1)
    cumulative = np.cumsum(values) / n
    cumulative_std = np.array(
        [np.std(values[:k], ddof=1) if k > 1 else 0.0 for k in n]
    )
    half = 1.96 * cumulative_std / np.sqrt(n)

    fig, ax = plt.subplots(figsize=(10.5, 5.4))
    ax.plot(n, cumulative, color=COLORS["blue"], linewidth=2.0, label="Media acumulada de Wq")
    ax.fill_between(n, cumulative - half, cumulative + half, color=COLORS["blue"], alpha=0.15, label="IC 95 %")
    ax.axhline(values.mean(), color=COLORS["fail"], linestyle="--", linewidth=1.3, label=f"Media final = {values.mean():.2f} min")
    ax.axvline(len(values), color=COLORS["ok"], linestyle=":", linewidth=1.4, label=f"{len(values)} réplicas")
    ax.set_xlabel("Número de réplicas")
    ax.set_ylabel("Tiempo promedio en cola, Wq (min)")
    ax.set_title("Convergencia de la media con el número de réplicas")
    ax.legend()
    _style_ax(ax)
    fig.tight_layout()
    fig.savefig(path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_cajeros(point1: pd.DataFrame, test: dict[str, object], path: Path) -> None:
    """Tiempo promedio de atención por cajero con IC 95 %."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 5.0))
    ax = axes[0]
    labels = [f"Cajero {int(c)}" for c in point1["cajero"]]
    values = point1["tiempo_servicio_prom"].to_numpy(dtype=float)
    errors = np.vstack(
        [
            values - point1["tiempo_servicio_ic95_inf"].to_numpy(dtype=float),
            point1["tiempo_servicio_ic95_sup"].to_numpy(dtype=float) - values,
        ]
    )
    colors = [COLORS["blue"]] * len(point1)
    bars = ax.bar(labels, values, yerr=errors, capsize=8, color=colors, alpha=0.85, edgecolor="white")
    ax.axhline(mean_service_min(), color="#e67e22", linestyle="--", linewidth=1.2, label=f"Media global = {mean_service_min():.2f} min")
    for position, (bar, value) in enumerate(zip(bars, values)):
        top = value + float(errors[1][position]) + 0.07
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            top,
            f"{value:.2f}",
            ha="center",
            fontsize=10,
            weight="bold",
        )
        if bool(point1["menor_tiempo_servicio"].iloc[position]):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                top + 0.16,
                "menor",
                ha="center",
                fontsize=8,
                color=COLORS["ok"],
                weight="bold",
            )
        if bool(point1["mayor_tiempo_servicio"].iloc[position]):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                top + 0.16,
                "mayor",
                ha="center",
                fontsize=8,
                color=COLORS["fail"],
                weight="bold",
            )
    ax.set_ylabel("Tiempo promedio de atención (min)")
    ax.set_title("Punto A: tiempo de atención por cajero")
    ax.set_ylim(0, (values + errors[1]).max() * 1.45)
    ax.legend(fontsize=8)
    _style_ax(ax)

    ax = axes[1]
    utilization = point1["utilizacion_prom"].to_numpy(dtype=float) * 100.0
    bars = ax.bar(labels, utilization, color=COLORS["blue"], alpha=0.8)
    for bar, value in zip(bars, utilization):
        ax.text(bar.get_x() + bar.get_width() / 2, value + 0.8, f"{value:.1f}%", ha="center", fontsize=10)
    ax.set_ylabel("Utilización promedio (%)")
    ax.set_title("Utilización de cada cajero")
    ax.set_ylim(0, max(utilization) * 1.4)
    _style_ax(ax)

    fig.suptitle(
        f"Friedman: p = {float(test.get('p_value', float('nan'))):.3f}; "
        "no hay diferencias significativas entre cajeros",
        fontsize=10,
        y=0.02,
    )
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    fig.savefig(path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_tipos(point2: pd.DataFrame, path: Path) -> None:
    """Composición observada vs esperada y esperas por tipo."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 5.0))
    labels = point2["tipo"].tolist()
    x = np.arange(len(labels))
    width = 0.38

    ax = axes[0]
    ax.bar(x - width / 2, point2["porcentaje_observado"], width, label="Observado", color=COLORS["blue"])
    ax.bar(x + width / 2, point2["porcentaje_esperado"], width, label="Esperado", color="#95a5a6", alpha=0.85)
    for i, row in point2.reset_index(drop=True).iterrows():
        ax.text(i - width / 2, row["porcentaje_observado"] + 0.5, f"{row['porcentaje_observado']:.1f}%", ha="center", fontsize=8)
        ax.text(i + width / 2, row["porcentaje_esperado"] + 0.5, f"{row['porcentaje_esperado']:.1f}%", ha="center", fontsize=8, color="#555555")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("Porcentaje de usuarios (%)")
    ax.set_title("Punto B: composición de la demanda")
    ax.legend()
    ax.set_ylim(0, max(point2["porcentaje_observado"].max(), 30) * 1.25)
    _style_ax(ax)

    ax = axes[1]
    values = point2["espera_prom"].to_numpy(dtype=float)
    errors = np.vstack(
        [
            values - point2["espera_ic95_inf"].to_numpy(dtype=float),
            point2["espera_ic95_sup"].to_numpy(dtype=float) - values,
        ]
    )
    bars = ax.bar(
        labels,
        values,
        yerr=errors,
        capsize=7,
        color=[COLORS[t] for t in point2["user_type"]],
        alpha=0.85,
    )
    for bar, value in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, value + 0.08, f"{value:.2f}", ha="center", fontsize=9, weight="bold")
    ax.set_ylabel("Tiempo promedio en cola (min)")
    ax.set_title("Espera por tipo de usuario (IC 95 %)")
    ax.set_ylim(0, max(values) * 1.4)
    _style_ax(ax)

    fig.tight_layout()
    fig.savefig(path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_escenarios(comparison: pd.DataFrame, path: Path) -> None:
    """Wq y P(espera > 5) por escenario."""
    df = comparison.sort_values("espera_cola_prom", ascending=True)
    labels = df["escenario_etiqueta"].tolist()
    y = np.arange(len(labels))
    colors = [COLORS["ok"] if ok else COLORS["fail"] for ok in df["cumple_servicio"]]

    fig, axes = plt.subplots(1, 2, figsize=(14, 6.6), sharey=True)
    ax = axes[0]
    ax.barh(y, df["espera_cola_prom"], color=colors, alpha=0.85)
    for i, value in enumerate(df["espera_cola_prom"]):
        ax.text(value + 0.03, i, f"{value:.2f}", va="center", fontsize=8)
    ax.axvline(3.0, color=COLORS["blue"], linestyle="--", linewidth=1.2, label="Umbral aceptable: 3 min")
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=8)
    ax.set_xlabel("Tiempo promedio en cola, Wq (min)")
    ax.set_title("Punto C: espera en cola por escenario")
    ax.legend(fontsize=8)
    _style_ax(ax)

    ax = axes[1]
    ax.barh(y, df["prob_espera_mayor_5"] * 100.0, color=colors, alpha=0.85)
    for i, value in enumerate(df["prob_espera_mayor_5"] * 100.0):
        ax.text(value + 0.3, i, f"{value:.1f}%", va="center", fontsize=8)
    ax.axvline(10.0, color=COLORS["blue"], linestyle="--", linewidth=1.2, label="Umbral: 10 %")
    ax.set_xlabel("Usuarios con espera > 5 min (%)")
    ax.set_title("Probabilidad de espera mayor a 5 min")
    ax.legend(fontsize=8)
    _style_ax(ax)

    fig.tight_layout()
    fig.savefig(path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_vv(path: Path, verification: pd.DataFrame) -> None:
    """Diagrama de flujo del proceso de verificación, calibración y validación."""
    fig, ax = plt.subplots(figsize=(10.5, 10.0))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 12)
    ax.axis("off")

    boxes = [
        (5.0, 11.0, "Definición del problema", "#dfe6e9", COLORS["blue"]),
        (5.0, 9.6, "Modelo conceptual M/M/1\npor cajero y supuestos", "#dfe6e9", COLORS["blue"]),
        (5.0, 8.2, "Implementación en Python\n(Simulación de eventos discretos)", "#e8f4f8", "#2980b9"),
        (5.0, 6.8, f"VERIFICACIÓN\n{int(verification['estado'].sum())}/{len(verification)} pruebas cumplidas", "#fdecea", COLORS["fail"]),
        (5.0, 5.4, "CALIBRACIÓN\nAjuste de λ y μ; KS y composición", "#fff3e0", "#e67e22"),
        (5.0, 4.0, "VALIDACIÓN\nM/M/1 exacta y M/G/1 por cajero", "#eafaf1", COLORS["ok"]),
        (5.0, 2.6, "Modelo validado\nResultados y decisiones", COLORS["ok"], "#ffffff"),
    ]
    for x, y, text, face, edge in boxes:
        ax.add_patch(
            FancyBboxPatch(
                (x - 3.3, y - 0.5),
                6.6,
                1.0,
                boxstyle="round,pad=0.06",
                facecolor=face,
                edgecolor=edge,
                linewidth=1.6,
            )
        )
        ax.text(
            x,
            y,
            text,
            ha="center",
            va="center",
            fontsize=9.5,
            weight="bold",
            color="#1a1a2e" if face != COLORS["ok"] else "#ffffff",
        )

    for y_top, y_bottom in zip(
        [10.5, 9.1, 7.7, 6.3, 4.9, 3.5],
        [10.1, 8.7, 7.3, 5.9, 4.5, 3.1],
    ):
        ax.add_patch(
            FancyArrowPatch(
                (5.0, y_top),
                (5.0, y_bottom),
                arrowstyle="-|>",
                mutation_scale=14,
                color="#7f8c8d",
                linewidth=1.4,
            )
        )

    # Lazos de corrección.
    ax.add_patch(
        FancyArrowPatch(
            (8.35, 6.8),
            (8.35, 8.2),
            arrowstyle="-|>",
            mutation_scale=12,
            color=COLORS["fail"],
            linewidth=1.2,
            connectionstyle="arc3,rad=-0.45",
        )
    )
    ax.text(9.1, 7.5, "No: corregir", color=COLORS["fail"], fontsize=8.5, rotation=90, va="center")
    ax.add_patch(
        FancyArrowPatch(
            (8.35, 4.0),
            (8.35, 5.4),
            arrowstyle="-|>",
            mutation_scale=12,
            color="#e67e22",
            linewidth=1.2,
            connectionstyle="arc3,rad=-0.45",
        )
    )
    ax.text(9.1, 4.7, "No: recalibrar", color="#e67e22", fontsize=8.5, rotation=90, va="center")

    ax.text(5.0, 1.35, "Registro de pruebas, parámetros y resultados en outputs/", ha="center", fontsize=9, color="#555555")
    ax.set_title("Proceso de verificación, calibración y validación (V&V)", fontsize=13, weight="bold")
    fig.tight_layout()
    fig.savefig(path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_validacion(
    validation_types: pd.DataFrame,
    validation_aggregate: pd.DataFrame,
    path: Path,
) -> None:
    """Comparación teoría vs simulación."""
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.4))

    ax = axes[0]
    df = validation_types[validation_types["metrica"].str.startswith("Tiempo en cola")]
    labels = df["tipo"].tolist()
    x = np.arange(len(labels))
    width = 0.36
    ax.bar(x - width / 2, df["teorico"], width, label="Teoría M/M/1", color="#95a5a6")
    simulated = df["simulado"].to_numpy(dtype=float)
    errors = np.vstack(
        [
            simulated - df["ic95_inf"].to_numpy(dtype=float),
            df["ic95_sup"].to_numpy(dtype=float) - simulated,
        ]
    )
    ax.bar(x + width / 2, simulated, width, yerr=errors, capsize=5, label="Simulación", color=COLORS["blue"])
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("Tiempo promedio en cola, Wq (min)")
    ax.set_title("Validación por tipo (un cajero M/M/1)")
    ax.legend(fontsize=8)
    _style_ax(ax)

    ax = axes[1]
    labels = ["Wq", "W", "Lq"]
    theory = [
        float(validation_aggregate.loc[validation_aggregate["metrica"].str.startswith("Tiempo en cola"), "teorico_mg1"].iloc[0]),
        float(validation_aggregate.loc[validation_aggregate["metrica"].str.startswith("Tiempo en el sistema"), "teorico_mg1"].iloc[0]),
        float(validation_aggregate.loc[validation_aggregate["metrica"].str.startswith("Usuarios en cola"), "teorico_mg1"].iloc[0]),
    ]
    simulated = [
        float(validation_aggregate.loc[validation_aggregate["metrica"].str.startswith("Tiempo en cola"), "simulado"].iloc[0]),
        float(validation_aggregate.loc[validation_aggregate["metrica"].str.startswith("Tiempo en el sistema"), "simulado"].iloc[0]),
        float(validation_aggregate.loc[validation_aggregate["metrica"].str.startswith("Usuarios en cola"), "simulado"].iloc[0]),
    ]
    x = np.arange(len(labels))
    ax.bar(x - width / 2, theory, width, label="Aproximación M/G/1", color="#95a5a6")
    ax.bar(x + width / 2, simulated, width, label="Simulación", color=COLORS["ok"])
    for i, (t, s) in enumerate(zip(theory, simulated)):
        ax.text(i - width / 2, t + 0.05, f"{t:.2f}", ha="center", fontsize=8)
        ax.text(i + width / 2, s + 0.05, f"{s:.2f}", ha="center", fontsize=8)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_title("Validación agregada por cajero")
    ax.legend(fontsize=8)
    _style_ax(ax)

    fig.tight_layout()
    fig.savefig(path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_calibracion(base_customers: pd.DataFrame, path: Path) -> None:
    """Histogramas de tiempos de servicio con la exponencial teórica."""
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    for ax, user_type in zip(axes.ravel(), USER_TYPES):
        sample = base_customers.loc[
            base_customers["user_type"] == user_type, "service_time"
        ].to_numpy(dtype=float)
        mean = SERVICE_MEAN_MIN[user_type]
        ax.hist(sample, bins=45, density=True, alpha=0.65, color=COLORS[user_type], edgecolor="white")
        x = np.linspace(0, max(sample.max(), mean * 4), 400)
        ax.plot(x, (1 / mean) * np.exp(-x / mean), color="#1a1a2e", linewidth=2.0, label=f"Exp(media = {mean:g} min)")
        ax.set_title(f"{USER_TYPE_LABELS[user_type]} (n = {len(sample)})")
        ax.set_xlabel("Tiempo de servicio (min)")
        ax.set_ylabel("Densidad")
        ax.legend(fontsize=8)
        _style_ax(ax)
    fig.suptitle("Calibración: tiempos de servicio observados vs exponencial teórica", fontsize=13, weight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    fig.savefig(path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_antes_despues(
    pilot: pd.DataFrame,
    point5: pd.DataFrame,
    meta: dict[str, object],
    path: Path,
) -> None:
    """Antes y después de eliminar el transitorio."""
    series = pilot["n_en_sistema"].to_numpy(dtype=float)
    times = pilot["minuto"].to_numpy(dtype=float)
    cut = float(meta["calentamiento_min"])
    cumulative = np.cumsum(series) / np.arange(1, len(series) + 1)
    after_series = series[int(cut) :]
    after_times = times[int(cut) :]
    cumulative_after = np.cumsum(after_series) / np.arange(1, len(after_series) + 1)

    fig, axes = plt.subplots(1, 3, figsize=(15, 4.8), gridspec_kw={"width_ratios": [1.6, 1, 1]})
    ax = axes[0]
    ax.plot(times, cumulative, color="#2980b9", linewidth=1.9, label="Con transitorio")
    ax.plot(after_times, cumulative_after, color=COLORS["ok"], linewidth=2.1, label="Sin transitorio")
    ax.axvline(cut, color=COLORS["fail"], linestyle="--", linewidth=1.6)
    ax.set_xlim(0, min(3000, times[-1]))
    ax.set_xlabel("Tiempo (min)")
    ax.set_ylabel("Media acumulada de N(t)")
    ax.set_title("Media acumulada: antes y después")
    ax.legend(fontsize=8)
    _style_ax(ax)

    rows = point5[point5["metrica"].str.startswith("Tiempo promedio en cola")].iloc[0]
    ax = axes[1]
    bars = ax.bar(["Antes", "Después"], [rows["antes"], rows["despues"]], color=["#95a5a6", COLORS["ok"]])
    for bar, value in zip(bars, [rows["antes"], rows["despues"]]):
        ax.text(bar.get_x() + bar.get_width() / 2, value + 0.03, f"{value:.2f}", ha="center", fontsize=10, weight="bold")
    ax.set_ylabel("Wq (min)")
    ax.set_title("Espera en cola")
    ax.set_ylim(0, max(rows["antes"], rows["despues"]) * 1.35)
    _style_ax(ax)

    rows = point5[point5["metrica"].str.startswith("Longitud promedio de la cola")].iloc[0]
    ax = axes[2]
    bars = ax.bar(["Antes", "Después"], [rows["antes"], rows["despues"]], color=["#95a5a6", COLORS["ok"]])
    for bar, value in zip(bars, [rows["antes"], rows["despues"]]):
        ax.text(bar.get_x() + bar.get_width() / 2, value + 0.01, f"{value:.3f}", ha="center", fontsize=10, weight="bold")
    ax.set_ylabel("Lq (usuarios)")
    ax.set_title("Longitud de la cola")
    ax.set_ylim(0, max(rows["antes"], rows["despues"]) * 1.35)
    _style_ax(ax)

    fig.suptitle(f"Punto E: eliminación del estado transitorio (corte = {cut:.0f} min)", fontsize=12, weight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(path, dpi=300, bbox_inches="tight")
    plt.close(fig)


# ----------------------------------------------------------------------
# Resumen en Markdown
# ----------------------------------------------------------------------
def build_summary_md(
    metadata: dict[str, object],
    point1: pd.DataFrame,
    point1_test: dict[str, object],
    point2: pd.DataFrame,
    point2_test: dict[str, object],
    comparison: pd.DataFrame,
    decision: dict[str, object],
    verification: pd.DataFrame,
    calibration_service: pd.DataFrame,
    calibration_arrival: pd.DataFrame,
    validation_types: pd.DataFrame,
    validation_aggregate: pd.DataFrame,
    point5: pd.DataFrame,
    point5_summary: dict[str, object],
) -> str:
    lines: list[str] = []
    lines.append("# Resumen de ejecución — AE4 Parqueadero\n")
    lines.append(
        "> Todas las cifras son simuladas.  No provienen de datos reales del "
        "Centro Comercial Supercentro.\n"
    )
    lines.append("## Configuración del experimento\n")
    lines.append(
        f"- Réplicas: **{metadata['replicas']}**\n"
        f"- Jornada simulada: **{metadata['duration_min']:.0f} min** "
        f"({metadata['duration_hours']:.0f} h)\n"
        f"- Calentamiento eliminado: **{metadata['warmup_min']:.0f} min**\n"
        f"- Semilla maestra: **{metadata['master_seed']}**\n"
        f"- Media entre llegadas: **{metadata['mean_interarrival_min']:.3f} min**\n"
        f"- Media de servicio: **{metadata['mean_service_min']:.3f} min**\n"
        f"- Carga ofrecida: **{metadata['offered_load_erlangs']:.3f} erlangs**\n"
    )

    lines.append("\n## Punto A — Estadísticas por cajero\n")
    lines.append(
        _md_table(
            point1,
            [
                ("cajero", "Cajero"),
                ("clientes_atendidos_prom", "Atendidos"),
                ("tiempo_servicio_prom", "Servicio prom. (min)"),
                ("tiempo_servicio_ic95_inf", "IC inf."),
                ("tiempo_servicio_ic95_sup", "IC sup."),
                ("tiempo_servicio_min_observado", "Mín. obs."),
                ("tiempo_servicio_max_observado", "Máx. obs."),
                ("tiempo_espera_prom", "Espera prom. (min)"),
                ("utilizacion_prom", "Utilización"),
            ],
        )
    )
    lines.append(
        f"\n**Prueba de Friedman:** p = {float(point1_test.get('p_value', float('nan'))):.3f}. "
        f"{point1_test.get('interpretacion', '')}\n"
    )

    lines.append("\n## Punto B — Promedio de usuarios por tipo\n")
    lines.append(
        _md_table(
            point2,
            [
                ("tipo", "Tipo"),
                ("promedio_usuarios", "Promedio"),
                ("usuarios_ic95_inf", "IC inf."),
                ("usuarios_ic95_sup", "IC sup."),
                ("porcentaje_observado", "% obs."),
                ("porcentaje_esperado", "% esp."),
                ("servicio_prom", "Servicio (min)"),
                ("espera_prom", "Espera (min)"),
                ("espera_p90", "P90 espera"),
                ("sistema_prom", "Sistema (min)"),
            ],
        )
    )
    lines.append(
        f"\n**Chi-cuadrado de composición:** χ² = {float(point2_test.get('chi2', float('nan'))):.3f}, "
        f"p = {float(point2_test.get('p_value', float('nan'))):.3f}. "
        f"{point2_test.get('interpretacion', '')}\n"
    )

    lines.append("\n## Punto C — Comparación de escenarios\n")
    lines.append(
        _md_table(
            comparison,
            [
                ("ranking", "Ranking"),
                ("escenario_etiqueta", "Escenario"),
                ("cajeros", "Cajeros"),
                ("espera_cola_prom", "Wq (min)"),
                ("espera_sistema_prom", "W (min)"),
                ("cola_prom", "Lq"),
                ("utilizacion_max", "Util. máx."),
                ("prob_espera_mayor_5", "P(>5 min)"),
                ("cumple_servicio", "¿Cumple?"),
                ("recomendado", "Recomendado"),
            ],
        )
    )
    lines.append("\n### Decisión\n")
    lines.append(f"**{decision.get('justificacion', '')}**\n")
    cheapest = decision.get("opcion_de_menor_costo_que_cumple") or {}
    if cheapest:
        lines.append(
            f"\n- Opción de menor costo que cumple: **{cheapest.get('etiqueta')}** "
            f"({cheapest.get('cajeros')} cajeros, Wq = {float(cheapest.get('espera_cola_prom', 0)):.2f} min).\n"
        )
    lines.append(
        f"- Mejor desempeño absoluto: **{decision.get('mejor_desempeno', {}).get('etiqueta')}** "
        f"(Wq = {float(decision.get('mejor_desempeno', {}).get('espera_cola_prom', 0)):.2f} min).\n"
    )

    lines.append("\n## Punto D — Verificación, calibración y validación\n")
    lines.append(
        _md_table(
            verification,
            [("prueba", "Prueba"), ("resultado", "Resultado"), ("detalle", "Detalle")],
        )
    )
    lines.append("\n### Calibración de tiempos de servicio\n")
    lines.append(
        _md_table(
            calibration_service,
            [
                ("parametro", "Parámetro"),
                ("nominal_min", "Nominal"),
                ("estimado_min", "Estimado"),
                ("error_relativo_pct", "Error (%)"),
                ("n", "n"),
                ("ks_estadistico", "KS"),
                ("ks_p_value", "p KS"),
                ("ajuste_exponencial", "Ajusta"),
            ],
        )
    )
    if not calibration_arrival.empty:
        lines.append("\n### Calibración de la tasa de llegadas\n")
        lines.append(
            _md_table(
                calibration_arrival,
                [
                    ("parametro", "Parámetro"),
                    ("nominal_por_min", "Nominal"),
                    ("estimado_por_min", "Estimado"),
                    ("error_relativo_pct", "Error (%)"),
                    ("ic95_inf", "IC inf."),
                    ("ic95_sup", "IC sup."),
                ],
                4,
            )
        )
    lines.append("\n### Validación contra la teoría\n")
    lines.append(
        _md_table(
            validation_types,
            [
                ("tipo", "Tipo"),
                ("metrica", "Métrica"),
                ("teorico", "Teoría"),
                ("simulado", "Simulación"),
                ("error_relativo_pct", "Error (%)"),
                ("p_value", "p"),
                ("validado", "Validado"),
            ],
        )
    )
    lines.append("\n")
    lines.append(
        _md_table(
            validation_aggregate,
            [
                ("metrica", "Métrica"),
                ("teorico_mg1", "M/G/1"),
                ("simulado", "Simulación"),
                ("error_relativo_pct", "Error (%)"),
                ("validado", "Validado"),
            ],
        )
    )

    lines.append("\n## Punto E — Eliminación del estado transitorio\n")
    lines.append(
        f"- Corte detectado: **{float(point5_summary.get('calentamiento_min', 0)):.0f} min**.\n"
        f"- Media de N(t) en el primer bloque: **{float(point5_summary.get('n_primer_bloque', 0)):.3f}** usuarios.\n"
        f"- Media de N(t) después del corte: **{float(point5_summary.get('n_despues', 0)):.3f}** usuarios.\n"
    )
    lines.append(
        _md_table(
            point5,
            [
                ("metrica", "Métrica"),
                ("antes", "Antes"),
                ("despues", "Después"),
                ("diferencia", "Diferencia"),
                ("cambio_pct", "Cambio (%)"),
            ],
        )
    )

    lines.append("\n## Figuras\n")
    for name, caption in (
        ("fig_sistema.png", "Esquema del sistema de tres cajeros independientes."),
        ("fig_transitorio.png", "Determinación del estado estable con promedio móvil."),
        ("fig_replicas_convergencia.png", "Convergencia de la media con el número de réplicas."),
        ("fig_cajeros.png", "Tiempo de atención y utilización por cajero."),
        ("fig_tipos.png", "Composición de la demanda y esperas por tipo."),
        ("fig_escenarios.png", "Comparación de escenarios y criterios."),
        ("fig_vv_flujo.png", "Proceso de verificación, calibración y validación."),
        ("fig_validacion.png", "Validación contra la teoría M/M/1 y M/G/1."),
        ("fig_calibracion.png", "Calibración de tiempos de servicio."),
        ("fig_antes_despues.png", "Antes y después de eliminar el transitorio."),
    ):
        lines.append(f"- `outputs/figuras/{name}`: {caption}")
    lines.append("")
    return "\n".join(lines)


# ----------------------------------------------------------------------
# Script principal
# ----------------------------------------------------------------------
def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    FIG_DIR.mkdir(parents=True, exist_ok=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Leyendo resultados crudos...")
    replicas = pd.read_csv(OUT_DIR / "replicas.csv")
    tellers = pd.read_csv(OUT_DIR / "cajeros.csv")
    customers = pd.read_csv(OUT_DIR / "clientes.csv")
    payload = json.loads((OUT_DIR / "resultados.json").read_text(encoding="utf-8"))
    metadata = payload["metadata"]
    pilot_summary = json.loads(
        (OUT_DIR / "pilot_resumen.json").read_text(encoding="utf-8")
    )
    pilot_df = pd.read_csv(OUT_DIR / "pilot_serie.csv")

    print("Construyendo resúmenes y tablas de los cinco puntos...")
    core = build_core_summaries(replicas, tellers, customers)
    point1, point1_test = build_point1_table(tellers)
    point2, point2_test, point2_by_teller = build_point2_table(
        core["tipos_por_replica"],
        customers,
        num_tellers=int(
            metadata["scenarios"][MAIN_SCENARIO]["num_tellers"]
        ),
    )
    criteria, comparison, decision = build_point3_tables(
        core["resumen_global"], metadata
    )
    verification = build_verification_table(customers, replicas, metadata)
    base_customers = customers[customers["scenario"] == MAIN_SCENARIO]
    calibration_service, calibration_arrival = build_calibration_tables(
        base_customers, replicas, metadata
    )

    print("Ejecutando validación M/M/1 (30 réplicas de 10 000 min por tipo)...")
    validation_results = [
        run_single_type_experiment(
            user_type,
            replicas=30,
            duration_min=10_000,
            warmup_min=2_000,
            master_seed=DEFAULT_MASTER_SEED,
        )
        for user_type in ("rapido", "lento", "muy_lento")
    ]
    validation_types, validation_aggregate = build_validation_tables(
        validation_results, tellers
    )

    print("Calculando el antes y el después del estado transitorio...")
    before = run_experiment(
        replicas=int(metadata["replicas"]),
        duration_min=float(metadata["duration_min"]),
        warmup_min=0.0,
        master_seed=int(metadata["master_seed"]),
        scenario_keys=[MAIN_SCENARIO],
    )
    before_rows = pd.DataFrame(before.replica_rows)
    pilot_for_point5 = {
        "series": pilot_df["n_en_sistema"].to_numpy(dtype=float),
        "duration_min": float(pilot_summary["duracion_min"]),
        "cut_min": float(pilot_summary["calentamiento_min"]),
        "window": int(pilot_summary["ventana_promedio_movil_min"]),
        "reference_mean": float(pilot_summary["referencia_n"]),
        "tolerance": float(pilot_summary["tolerancia"]),
    }
    point5, point5_summary = build_point5_table(
        pilot_for_point5, before_rows, core["replicas"]
    )

    print("Guardando tablas derivadas...")
    for df, name in (
        (point1, "punto1_cajeros.csv"),
        (point2, "punto2_tipos.csv"),
        (point2_by_teller, "punto2_por_cajero.csv"),
        (criteria, "punto3_criterios.csv"),
        (comparison, "punto3_comparacion.csv"),
        (verification, "punto4_verificacion.csv"),
        (calibration_service, "punto4_calibracion_servicio.csv"),
        (calibration_arrival, "punto4_calibracion_llegadas.csv"),
        (validation_types, "punto4_validacion_tipos.csv"),
        (validation_aggregate, "punto4_validacion_agregada.csv"),
        (point5, "punto5_antes_despues.csv"),
        (core["resumen_global"], "resumen_global.csv"),
        (core["resumen_cajeros"], "resumen_cajeros.csv"),
        (core["resumen_tipos"], "resumen_tipos.csv"),
    ):
        save_csv(df, name)

    save_json(
        {
            "punto1_prueba": point1_test,
            "punto2_prueba": point2_test,
            "punto3_decision": decision,
            "punto5_resumen": point5_summary,
            "calibracion_llegadas": (
                calibration_arrival.to_dict("records")
                if not calibration_arrival.empty
                else []
            ),
        },
        "decisiones.json",
    )

    print("Generando figuras...")
    plot_sistema(FIG_DIR / "fig_sistema.png")
    plot_transitorio(pilot_df, pilot_summary, FIG_DIR / "fig_transitorio.png")
    plot_convergencia(
        replicas[replicas["scenario"] == MAIN_SCENARIO],
        FIG_DIR / "fig_replicas_convergencia.png",
    )
    plot_cajeros(point1, point1_test, FIG_DIR / "fig_cajeros.png")
    plot_tipos(point2, FIG_DIR / "fig_tipos.png")
    plot_escenarios(comparison, FIG_DIR / "fig_escenarios.png")
    plot_vv(FIG_DIR / "fig_vv_flujo.png", verification)
    plot_validacion(
        validation_types, validation_aggregate, FIG_DIR / "fig_validacion.png"
    )
    plot_calibracion(base_customers, FIG_DIR / "fig_calibracion.png")
    plot_antes_despues(
        pilot_df, point5, pilot_summary, FIG_DIR / "fig_antes_despues.png"
    )

    print("Escribiendo resumen de ejecución...")
    summary = build_summary_md(
        metadata,
        point1,
        point1_test,
        point2,
        point2_test,
        comparison,
        decision,
        verification,
        calibration_service,
        calibration_arrival,
        validation_types,
        validation_aggregate,
        point5,
        point5_summary,
    )
    (OUT_DIR / "resumen_ejecucion.md").write_text(summary, encoding="utf-8")

    print("")
    print("Listo. Archivos generados en outputs/ y outputs/figuras/.")
    print(f"Decisión recomendada: {decision.get('recomendado_etiqueta')}")
    print(f"Wq actual: {float(decision.get('espera_cola_actual', 0)):.2f} min")
    print(
        "Wq recomendada: "
        f"{float(decision.get('espera_cola_recomendada', 0)):.2f} min"
    )


if __name__ == "__main__":
    main()
