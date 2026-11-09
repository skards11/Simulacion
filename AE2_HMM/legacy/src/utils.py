"""Gráficos y reportes para el sistema HMM de riesgo de incendios."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch

from .simulation import (
    STATE_COLORS,
    SeasonSimulation,
    compute_metrics,
)


def _risk_legend_handles() -> list[Patch]:
    return [
        Patch(facecolor=color, edgecolor="none", alpha=0.45, label=label)
        for color, label in zip(
            STATE_COLORS,
            ("Riesgo Bajo", "Riesgo Moderado", "Riesgo Extremo"),
        )
    ]


def plot_humidity_and_risk(
    sim: SeasonSimulation,
    save_path: str | Path | None = None,
) -> plt.Figure:
    """Grafica humedad diaria, bandas de riesgo inferido y focos simulados."""
    fig, ax = plt.subplots(figsize=(16, 6))

    for day, state in zip(sim.days, sim.inferred_states):
        ax.axvspan(
            day - 0.5,
            day + 0.5,
            color=STATE_COLORS[int(state)],
            alpha=0.20,
            linewidth=0,
        )

    ax.plot(
        sim.days,
        sim.humidity,
        color="#0d47a1",
        linewidth=1.8,
        marker="o",
        markersize=2.6,
        label="Humedad relativa (%)",
        zorder=4,
    )

    fire_days = sim.days[sim.fire_events]
    if len(fire_days):
        ax.scatter(
            fire_days,
            sim.humidity[sim.fire_events],
            marker="v",
            s=95,
            color="#b71c1c",
            edgecolor="white",
            linewidth=1.0,
            zorder=6,
            label="Posible foco de incendio",
        )

    ax.set_xlim(0.5, sim.n_days + 0.5)
    ax.set_ylim(0, 105)
    ax.set_xlabel("Día de la temporada")
    ax.set_ylabel("Humedad relativa (%)")
    ax.set_title(
        "Humedad ambiental y bandas de riesgo inferido (Viterbi)",
        fontsize=14,
        fontweight="bold",
    )
    ax.grid(axis="y", alpha=0.25)
    ax.set_xticks(np.arange(0, sim.n_days + 1, 10))
    ax.legend(handles=_risk_legend_handles() + ax.get_legend_handles_labels()[0],
              loc="lower left", ncols=2, frameon=True)

    fig.tight_layout()
    if save_path is not None:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
    return fig


def plot_danger_index_and_comparison(
    sim: SeasonSimulation,
    save_path: str | Path | None = None,
) -> plt.Figure:
    """Grafica el índice de peligro y compara riesgo real vs inferido."""
    fig, (ax_index, ax_compare) = plt.subplots(
        2,
        1,
        figsize=(16, 9),
        sharex=True,
        gridspec_kw={"height_ratios": [1.35, 1.0]},
    )

    ax_index.fill_between(sim.days, 0, 40, color="#2e7d32", alpha=0.08)
    ax_index.fill_between(sim.days, 40, 75, color="#f9a825", alpha=0.10)
    ax_index.fill_between(sim.days, 75, 100, color="#c62828", alpha=0.10)
    ax_index.plot(
        sim.days,
        sim.danger_index,
        color="#4a148c",
        linewidth=2.0,
        label="Índice de peligro HMM (0-100)",
    )
    ax_index.axhline(
        75,
        color="#b71c1c",
        linestyle="--",
        linewidth=1.3,
        label="Umbral de alerta (75)",
    )

    fire_days = sim.days[sim.fire_events]
    if len(fire_days):
        ax_index.scatter(
            fire_days,
            sim.danger_index[sim.fire_events],
            marker="v",
            s=90,
            color="#b71c1c",
            edgecolor="white",
            linewidth=1.0,
            zorder=5,
            label="Posible foco",
        )

    ax_index.set_ylim(0, 105)
    ax_index.set_ylabel("Índice de peligro")
    ax_index.set_title(
        "Índice de peligro de incendio derivado del HMM",
        fontsize=14,
        fontweight="bold",
    )
    ax_index.grid(axis="y", alpha=0.25)
    ax_index.legend(loc="upper left", ncols=3)

    ax_compare.step(
        sim.days,
        sim.true_states,
        where="mid",
        color="#212121",
        linewidth=1.8,
        label="Riesgo real simulado",
    )
    ax_compare.step(
        sim.days,
        sim.inferred_states,
        where="mid",
        color="#1565c0",
        linewidth=1.5,
        linestyle="--",
        label="Riesgo inferido con Viterbi",
    )
    ax_compare.set_yticks([0, 1, 2], labels=sim.model.states)
    ax_compare.set_ylim(-0.4, 2.4)
    ax_compare.set_xlabel("Día de la temporada")
    ax_compare.set_ylabel("Nivel de riesgo")
    ax_compare.set_title(
        "Comparación entre nivel de riesgo real e inferido",
        fontsize=13,
        fontweight="bold",
    )
    ax_compare.grid(axis="y", alpha=0.25)
    ax_compare.legend(loc="upper right", ncols=2)

    fig.tight_layout()
    if save_path is not None:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
    return fig


def plot_summary_dashboard(
    sim: SeasonSimulation,
    save_path: str | Path | None = None,
) -> plt.Figure:
    """Resume conteos, matriz de confusión y tasa de focos por humedad."""
    metrics = compute_metrics(sim)
    comparison = metrics["comparison"]
    humidity_data = metrics["humidity_fire"]

    fig, axes = plt.subplots(1, 3, figsize=(19, 5.5))

    # 1) Días por nivel de riesgo.
    ax = axes[0]
    labels = sim.model.states
    positions = np.arange(len(labels))
    true_counts = [metrics["risk_counts_true"][name] for name in labels]
    inferred_counts = [metrics["risk_counts_inferred"][name] for name in labels]
    width = 0.36

    ax.bar(
        positions - width / 2,
        true_counts,
        width,
        color=STATE_COLORS,
        alpha=0.90,
        label="Real",
    )
    ax.bar(
        positions + width / 2,
        inferred_counts,
        width,
        color=STATE_COLORS,
        alpha=0.45,
        hatch="//",
        edgecolor="white",
        label="Inferido",
    )
    ax.set_xticks(positions, labels=labels, rotation=15)
    ax.set_ylabel("Días")
    ax.set_title("Días por nivel de riesgo", fontweight="bold")
    ax.grid(axis="y", alpha=0.25)
    ax.legend()

    # 2) Matriz de confusión.
    ax = axes[1]
    confusion = comparison["confusion_matrix"]
    image = ax.imshow(confusion, cmap="Blues")
    for row in range(confusion.shape[0]):
        for column in range(confusion.shape[1]):
            value = confusion[row, column]
            color = "white" if value > confusion.max() * 0.55 else "black"
            ax.text(
                column,
                row,
                str(value),
                ha="center",
                va="center",
                color=color,
                fontweight="bold",
            )
    ax.set_xticks(np.arange(len(labels)), labels=labels, rotation=20)
    ax.set_yticks(np.arange(len(labels)), labels=labels)
    ax.set_xlabel("Riesgo inferido")
    ax.set_ylabel("Riesgo real")
    ax.set_title(
        f"Matriz de confusión (exactitud {comparison['accuracy']:.1%})",
        fontweight="bold",
    )
    fig.colorbar(image, ax=ax, fraction=0.046, pad=0.04)

    # 3) Tasa de focos por banda de humedad.
    ax = axes[2]
    band_names = list(humidity_data["humidity_bands"].keys())
    rates = [
        humidity_data["humidity_bands"][name]["event_rate"] * 100
        for name in band_names
    ]
    fire_counts = [
        humidity_data["humidity_bands"][name]["fire_events"]
        for name in band_names
    ]
    bars = ax.bar(band_names, rates, color=STATE_COLORS, alpha=0.85)
    for bar, count, rate in zip(bars, fire_counts, rates):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.2,
            f"{count} focos\n{rate:.1f}%",
            ha="center",
            va="bottom",
            fontsize=9,
        )
    ax.set_ylabel("Días con posible foco (%)")
    ax.set_title("Focos simulados por humedad", fontweight="bold")
    ax.grid(axis="y", alpha=0.25)
    ax.set_ylim(0, max(rates + [1.0]) * 1.35)

    fig.tight_layout()
    if save_path is not None:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
    return fig


def results_dataframe(sim: SeasonSimulation):
    """Devuelve un DataFrame diario listo para exportar o inspeccionar."""
    import pandas as pd

    alerts_by_day = {
        int(alert["day"]): str(alert["level"]) for alert in sim.alerts
    }

    return pd.DataFrame(
        {
            "Día": sim.days,
            "Humedad (%)": np.round(sim.humidity, 1),
            "Observación": sim.observation_names,
            "Riesgo real": sim.true_state_names,
            "Riesgo inferido": sim.inferred_state_names,
            "Índice de peligro": np.round(sim.danger_index, 1),
            "Posible foco": sim.fire_events,
            "Alerta": [alerts_by_day.get(int(day), "") for day in sim.days],
        }
    )


def format_report(
    sim: SeasonSimulation,
    metrics: dict[str, object] | None = None,
) -> str:
    """Construye un reporte operativo en texto para consola."""
    if metrics is None:
        metrics = compute_metrics(sim)

    comparison = metrics["comparison"]
    humidity_data = metrics["humidity_fire"]
    transition = metrics["transition_to_extreme_observed"]
    windows = metrics["extreme_windows"]

    lines: list[str] = []
    lines.append("=" * 78)
    lines.append("SISTEMA HMM DE RIESGO DE INCENDIOS FORESTALES")
    lines.append("=" * 78)
    lines.append(f"Temporada simulada: {sim.n_days} días | semilla: {sim.seed}")
    lines.append(f"Humedad media: {metrics['mean_humidity']:.1f} %")
    lines.append(
        f"Índice de peligro medio: {metrics['mean_danger_index']:.1f}/100 | "
        f"máximo: {metrics['max_danger_index']:.1f}/100"
    )
    lines.append("")

    lines.append("DÍAS EN CADA NIVEL DE RIESGO")
    lines.append("-" * 78)
    for name in sim.model.states:
        lines.append(
            f"  {name:<18} real: {metrics['risk_counts_true'][name]:>3} días | "
            f"inferido: {metrics['risk_counts_inferred'][name]:>3} días"
        )
    lines.append("")

    lines.append("VENTANAS DE PELIGRO EXTREMO CONTINUADO (inferidas, >= 2 días)")
    lines.append("-" * 78)
    if windows:
        for window in windows:
            lines.append(
                f"  Días {window['start_day']:>3}-{window['end_day']:<3} "
                f"({window['length']} días consecutivos)"
            )
    else:
        lines.append("  No se detectaron ventanas de riesgo extremo continuado.")
    lines.append(
        f"  Total de días en riesgo extremo inferido: "
        f"{metrics['extreme_days_inferred']}"
    )
    lines.append("")

    lines.append("PROBABILIDAD DE TRANSICIÓN A RIESGO EXTREMO")
    lines.append("-" * 78)
    model_p = metrics["model_transition_to_extreme"]
    lines.append("  Modelo (P(Extremo | estado actual)):")
    for name, probability in zip(sim.model.states, model_p):
        lines.append(f"    {name:<18}: {probability:.2%}")
    lines.append(
        f"  Observada en la simulación real: "
        f"{transition['overall_probability']:.2%} "
        f"({transition['entries_to_extreme']}/{transition['opportunities']} "
        "oportunidades desde estados no extremos)"
    )
    lines.append("")

    lines.append("VALIDACIÓN DEL ALGORITMO DE VITERBI")
    lines.append("-" * 78)
    lines.append(
        f"  Exactitud: {comparison['accuracy']:.2%} "
        f"({comparison['correct_days']}/{comparison['total_days']} días)"
    )
    lines.append("  Matriz de confusión (filas = real, columnas = inferido):")
    lines.append("                  " + "  ".join(f"{name[:9]:>9}" for name in sim.model.states))
    for name, row in zip(sim.model.states, comparison["confusion_matrix"]):
        lines.append(
            f"  {name:<16} " + "  ".join(f"{int(value):>9}" for value in row)
        )
    lines.append("")

    lines.append("ALERTAS DE QUEMAS")
    lines.append("-" * 78)
    lines.append(f"  Total de días con alerta: {metrics['alert_count']}")
    lines.append(f"  Prohibición total: {metrics['burn_ban_days']} días")
    lines.append(f"  Restricción preventiva: {metrics['restriction_days']} días")
    if metrics["alert_windows"]:
        ranges = ", ".join(
            f"{start}-{end}" if start != end else str(start)
            for start, end in metrics["alert_windows"]
        )
        lines.append(f"  Periodos de alerta: {ranges}")
    lines.append("")

    lines.append("CORRELACIÓN HUMEDAD / INCENDIOS")
    lines.append("-" * 78)
    lines.append(
        f"  Correlación humedad-foco (Pearson): "
        f"{humidity_data['humidity_event_correlation']:.3f}"
    )
    lines.append(
        f"  Correlación índice-foco (Pearson): "
        f"{humidity_data['danger_event_correlation']:.3f}"
    )
    lines.append(
        f"  Tasa de focos con humedad baja: "
        f"{humidity_data['low_humidity_event_rate']:.2%} | "
        f"otras humedades: {humidity_data['other_humidity_event_rate']:.2%}"
    )
    risk_ratio = humidity_data["low_humidity_risk_ratio"]
    if np.isfinite(risk_ratio):
        ratio_text = f"{risk_ratio:.2f}"
    elif np.isinf(risk_ratio):
        ratio_text = "muy alta (no hubo focos con otras humedades)"
    else:
        ratio_text = "no estimable (no hubo focos)"
    lines.append(
        f"  Razón de riesgo (humedad baja / otras): {ratio_text}"
    )
    lines.append("  Detalle por banda:")
    for name, band in humidity_data["humidity_bands"].items():
        lines.append(
            f"    {name:<14} {band['days']:>3} días | "
            f"{band['fire_events']:>2} focos | "
            f"tasa {band['event_rate']:.2%} | "
            f"humedad media {band['mean_humidity']:.1f}%"
        )
    lines.append("")

    lines.append("RECOMENDACIÓN OPERATIVA")
    lines.append("-" * 78)
    if metrics["burn_ban_days"] > 0:
        lines.append(
            "  Mantener prohibición de quemas durante los periodos de riesgo "
            "extremo y reforzar vigilancia en las ventanas indicadas."
        )
    elif metrics["restriction_days"] > 0:
        lines.append(
            "  Aplicar restricciones preventivas y monitoreo reforzado."
        )
    else:
        lines.append("  Mantener monitoreo rutinario; no se activaron alertas.")
    lines.append("=" * 78)

    return "\n".join(lines)
