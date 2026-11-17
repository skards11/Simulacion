"""Genera tablas de respuesta, figuras y resumen legible del laboratorio AE3.

Uso:
    python scripts/build_report_assets.py

Lee los archivos crudos de ``outputs/`` producidos por ``main.py`` y escribe
las tablas de los cinco puntos, las figuras y ``resumen_ejecucion.md``.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.analysis import (  # noqa: E402
    MAIN_SCENARIO,
    build_report_tables,
)
from src.bank_simulation import (  # noqa: E402
    USER_TYPES,
    USER_TYPE_LABELS,
)

PLOT_COLORS = {
    "mixto_3": "#1f4e79",
    "mixto_4": "#2e75b6",
    "retiro_1_pago_2": "#c55a11",
    "retiro_2_pago_1": "#548235",
    "retiro_2_pago_2": "#7030a0",
    "retiro_3_pago_1": "#bf9000",
    "retiro_1_pago_3": "#c00000",
}


def _read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, encoding="utf-8-sig")


def _write_csv(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, encoding="utf-8-sig")


def _safe_float(value: object, default: float = float("nan")) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _summary_row(
    summary: pd.DataFrame,
    scenario: str,
    metric: str,
) -> pd.Series | None:
    subset = summary[(summary["scenario"] == scenario) & (summary["metric"] == metric)]
    return subset.iloc[0] if not subset.empty else None


def _bar_with_ci(
    ax,
    labels: list[str],
    means: list[float],
    lower: list[float],
    upper: list[float],
    colors: list[str],
    ylabel: str,
    title: str,
    threshold: float | None = None,
    threshold_label: str = "",
) -> None:
    x = np.arange(len(labels))
    errors = np.array(
        [
            [max(0.0, m - lo) for m, lo in zip(means, lower)],
            [max(0.0, hi - m) for m, hi in zip(means, upper)],
        ]
    )
    ax.bar(x, means, color=colors, edgecolor="black", linewidth=0.6, yerr=errors, capsize=4)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=25, ha="right")
    ax.set_ylabel(ylabel)
    ax.set_title(title, fontsize=11, fontweight="bold")
    ax.grid(axis="y", alpha=0.25)
    if threshold is not None:
        ax.axhline(threshold, color="#c00000", linestyle="--", linewidth=1.2)
        ax.text(
            0.99,
            threshold,
            threshold_label,
            transform=ax.get_yaxis_transform(),
            ha="right",
            va="bottom",
            color="#c00000",
            fontsize=8,
        )


def build_figures(tables, outputs_dir: Path) -> list[Path]:
    """Crea las figuras del documento y devuelve sus rutas."""
    figures_dir = outputs_dir / "figuras"
    figures_dir.mkdir(parents=True, exist_ok=True)
    generated: list[Path] = []

    summary = tables.resumen_global.copy()
    scenario_order = tables.punto5["scenario"].tolist()
    labels = [
        str(
            summary[summary["scenario"] == scenario]["scenario_label"].iloc[0]
        )
        for scenario in scenario_order
    ]
    colors = [PLOT_COLORS.get(scenario, "#7f7f7f") for scenario in scenario_order]

    # Figura 1: espera promedio global con IC 95 %.
    rows = [summary[(summary["scenario"] == s) & (summary["metric"] == "mean_wait")].iloc[0] for s in scenario_order]
    means = [float(r["mean"]) for r in rows]
    lower = [float(r["ci_low"]) for r in rows]
    upper = [float(r["ci_high"]) for r in rows]
    fig, ax = plt.subplots(figsize=(10, 5.5))
    _bar_with_ci(
        ax,
        labels,
        means,
        lower,
        upper,
        colors,
        "Espera promedio (min)",
        "Espera promedio por configuración (IC 95 %)",
        threshold=5.0,
        threshold_label="Criterio 5 min",
    )
    fig.tight_layout()
    path = figures_dir / "fig_espera_por_configuracion.png"
    fig.savefig(path, dpi=300)
    plt.close(fig)
    generated.append(path)

    # Figura 2: espera promedio por acción.
    fig, ax = plt.subplots(figsize=(11, 5.8))
    width = 0.38
    x = np.arange(len(scenario_order))
    for offset, action, color in [
        (-width / 2, "retiro", "#1f4e79"),
        (width / 2, "pago", "#c55a11"),
    ]:
        metric = f"mean_wait_{action}"
        values = []
        errors_low = []
        errors_high = []
        for scenario in scenario_order:
            row = summary[(summary["scenario"] == scenario) & (summary["metric"] == metric)]
            if row.empty:
                values.append(0.0)
                errors_low.append(0.0)
                errors_high.append(0.0)
                continue
            r = row.iloc[0]
            values.append(float(r["mean"]))
            errors_low.append(max(0.0, float(r["mean"]) - float(r["ci_low"])))
            errors_high.append(max(0.0, float(r["ci_high"]) - float(r["mean"])))
        ax.bar(
            x + offset,
            values,
            width,
            label=f"Espera {'retiros' if action == 'retiro' else 'pagos'}",
            color=color,
            edgecolor="black",
            linewidth=0.5,
            yerr=[errors_low, errors_high],
            capsize=3,
        )
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=25, ha="right")
    ax.set_ylabel("Espera promedio (min)")
    ax.set_title("Espera promedio por tipo de operación (IC 95 %)", fontsize=11, fontweight="bold")
    ax.axhline(5.0, color="#c00000", linestyle="--", linewidth=1.2)
    ax.grid(axis="y", alpha=0.25)
    ax.legend()
    fig.tight_layout()
    path = figures_dir / "fig_espera_por_accion.png"
    fig.savefig(path, dpi=300)
    plt.close(fig)
    generated.append(path)

    # Figura 3: utilización máxima de una caja.
    rows = [
        summary[
            (summary["scenario"] == s) & (summary["metric"] == "max_cashier_utilization")
        ].iloc[0]
        for s in scenario_order
    ]
    means = [float(r["mean"]) for r in rows]
    lower = [float(r["ci_low"]) for r in rows]
    upper = [float(r["ci_high"]) for r in rows]
    fig, ax = plt.subplots(figsize=(10, 5.5))
    _bar_with_ci(
        ax,
        labels,
        means,
        lower,
        upper,
        colors,
        "Utilización máxima",
        "Utilización máxima de una caja (IC 95 %)",
        threshold=0.85,
        threshold_label="Criterio 85 %",
    )
    ax.set_ylim(0, 1.0)
    fig.tight_layout()
    path = figures_dir / "fig_utilizacion.png"
    fig.savefig(path, dpi=300)
    plt.close(fig)
    generated.append(path)

    # Figura 4: cajeros de la configuración actual.
    cashier_rows = tables.punto1[tables.punto1["escenario"] == MAIN_SCENARIO]
    if not cashier_rows.empty:
        fig, axes = plt.subplots(1, 2, figsize=(11, 4.8))
        x = np.arange(len(cashier_rows))
        labels_cashier = [
            f"Cajero {int(cashier)}" for cashier in cashier_rows["cajero"].tolist()
        ]
        for ax, column, ci_low, ci_high, title, color in [
            (
                axes[0],
                "tiempo_servicio_prom",
                "tiempo_servicio_ic_inf",
                "tiempo_servicio_ic_sup",
                "Tiempo promedio de servicio",
                "#1f4e79",
            ),
            (
                axes[1],
                "tiempo_espera_prom",
                None,
                None,
                "Tiempo promedio de espera",
                "#c55a11",
            ),
        ]:
            values = cashier_rows[column].astype(float).tolist()
            if ci_low and ci_high:
                low = cashier_rows[ci_low].astype(float).tolist()
                high = cashier_rows[ci_high].astype(float).tolist()
                errors = np.array(
                    [
                        [max(0.0, v - lo) for v, lo in zip(values, low)],
                        [max(0.0, hi - v) for v, hi in zip(values, high)],
                    ]
                )
                ax.bar(
                    x,
                    values,
                    color=color,
                    edgecolor="black",
                    linewidth=0.5,
                    yerr=errors,
                    capsize=4,
                )
            else:
                ax.bar(x, values, color=color, edgecolor="black", linewidth=0.5)
            ax.set_xticks(x)
            ax.set_xticklabels(labels_cashier)
            ax.set_ylabel("Minutos")
            ax.set_title(title, fontsize=11, fontweight="bold")
            ax.grid(axis="y", alpha=0.25)
        fig.suptitle(
            "Desempeño por cajero: configuración de 3 cajas mixtas",
            fontsize=12,
            fontweight="bold",
        )
        fig.tight_layout()
        path = figures_dir / "fig_cajeros_configuracion_actual.png"
        fig.savefig(path, dpi=300)
        plt.close(fig)
        generated.append(path)

    # Figura 5: conteos por tipo de usuario en cada réplica.
    point3 = tables.punto3_replicas
    if not point3.empty:
        fig, ax = plt.subplots(figsize=(9, 4.8))
        data = [
            point3[USER_TYPE_LABELS[user_type]].astype(float).tolist()
            for user_type in USER_TYPES
        ]
        ax.boxplot(data, tick_labels=[USER_TYPE_LABELS[t] for t in USER_TYPES], patch_artist=True)
        ax.set_ylabel("Usuarios por réplica")
        ax.set_title(
            "Distribución del total de usuarios por tipo (3 cajas mixtas)",
            fontsize=11,
            fontweight="bold",
        )
        ax.grid(axis="y", alpha=0.25)
        fig.tight_layout()
        path = figures_dir / "fig_conteos_por_tipo.png"
        fig.savefig(path, dpi=300)
        plt.close(fig)
        generated.append(path)

    # Figura 6: comparación 3 vs 4 cajas mixtas.
    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    comparison_metrics = [
        ("Espera global", "mean_wait"),
        ("Espera retiros", "mean_wait_retiro"),
        ("Espera pagos", "mean_wait_pago"),
        ("Espera p90", "p90_wait"),
    ]
    x = np.arange(len(comparison_metrics))
    width = 0.38
    for offset, scenario, color, label in [
        (-width / 2, "mixto_3", "#1f4e79", "3 cajas mixtas"),
        (width / 2, "mixto_4", "#2e75b6", "4 cajas mixtas"),
    ]:
        values = []
        for _, metric in comparison_metrics:
            row = summary[(summary["scenario"] == scenario) & (summary["metric"] == metric)]
            values.append(float(row.iloc[0]["mean"]) if not row.empty else 0.0)
        ax.bar(x + offset, values, width, label=label, color=color, edgecolor="black", linewidth=0.5)
    ax.set_xticks(x)
    ax.set_xticklabels([label for label, _ in comparison_metrics])
    ax.set_ylabel("Minutos")
    ax.set_title("Punto 4: comparación de 3 y 4 cajas mixtas", fontsize=11, fontweight="bold")
    ax.grid(axis="y", alpha=0.25)
    ax.legend()
    fig.tight_layout()
    path = figures_dir / "fig_punto4_comparacion.png"
    fig.savefig(path, dpi=300)
    plt.close(fig)
    generated.append(path)

    return generated


def _md_table(df: pd.DataFrame, floatfmt: str = ".3f") -> str:
    if df.empty:
        return "_Sin datos._"
    try:
        return df.to_markdown(index=False, floatfmt=floatfmt)
    except Exception:
        return "```\n" + df.to_string(index=False) + "\n```"


def build_markdown_summary(tables, metadata: dict[str, object], outputs_dir: Path) -> Path:
    """Escribe un resumen con cifras listas para citar en el documento."""
    lines: list[str] = []
    lines.append("# Resumen de ejecución — Problema bancario AE3")
    lines.append("")
    lines.append(
        "> Todas las cifras son simuladas. La fuente es "
        "`outputs/resultados.json` y los CSV de esta carpeta."
    )
    lines.append("")
    lines.append("## Configuración del experimento")
    lines.append("")
    lines.append(f"- Réplicas: **{metadata.get('replicas')}**")
    lines.append(f"- Duración por réplica: **{metadata.get('duration_min')} min**")
    lines.append(f"- Semilla maestra: **{metadata.get('master_seed')}**")
    lines.append(f"- Media entre llegadas: **{float(metadata.get('mean_interarrival_min', 0)):.3f} min**")
    lines.append(f"- Media de servicio: **{float(metadata.get('mean_service_min', 0)):.3f} min**")
    lines.append(f"- Carga ofrecida total: **{float(metadata.get('offered_load_total', 0)):.3f} servidores**")
    lines.append("")
    lines.append("## Ranking de configuraciones (punto 5)")
    lines.append("")
    ranking = tables.punto5.rename(
        columns={
            "ranking": "Puesto",
            "recomendado": "Recomendada",
            "escenario_etiqueta": "Configuración",
            "num_cashiers": "Cajas",
            "num_retiro": "Retiro",
            "num_pago": "Pago",
            "num_mixto": "Mixtas",
            "mean_wait": "Espera prom. (min)",
            "mean_wait_retiro": "Espera retiro (min)",
            "mean_wait_pago": "Espera pago (min)",
            "p90_wait": "P90 (min)",
            "max_cashier_utilization": "Util. máx.",
            "cumple_todos_los_criterios": "Cumple criterios",
        }
    )
    ranking = ranking[
        [
            "Puesto",
            "Recomendada",
            "Configuración",
            "Cajas",
            "Retiro",
            "Pago",
            "Mixtas",
            "Espera prom. (min)",
            "Espera retiro (min)",
            "Espera pago (min)",
            "P90 (min)",
            "Util. máx.",
            "Cumple criterios",
        ]
    ]
    lines.append(_md_table(ranking))
    lines.append("")
    lines.append("## Punto 1: cajero con menor y mayor tiempo de atención")
    lines.append("")
    point1 = tables.punto1[tables.punto1["escenario"] == MAIN_SCENARIO]
    if not point1.empty:
        best = point1[point1["menor_tiempo_servicio"]]
        worst = point1[point1["mayor_tiempo_servicio"]]
        lines.append(
            "- Menor tiempo promedio de servicio: "
            + ", ".join(
                f"Cajero {int(r['cajero'])} ({r['tipo_caja']}, {r['tiempo_servicio_prom']:.2f} min)"
                for _, r in best.iterrows()
            )
        )
        lines.append(
            "- Mayor tiempo promedio de servicio: "
            + ", ".join(
                f"Cajero {int(r['cajero'])} ({r['tipo_caja']}, {r['tiempo_servicio_prom']:.2f} min)"
                for _, r in worst.iterrows()
            )
        )
        lines.append("")
        lines.append(
            _md_table(
                point1[
                    [
                        "cajero",
                        "tipo_caja",
                        "clientes_atendidos_prom",
                        "tiempo_servicio_prom",
                        "tiempo_espera_prom",
                        "tiempo_sistema_prom",
                        "utilizacion_prom",
                    ]
                ].rename(
                    columns={
                        "cajero": "Cajero",
                        "tipo_caja": "Tipo de caja",
                        "clientes_atendidos_prom": "Clientes",
                        "tiempo_servicio_prom": "Servicio prom. (min)",
                        "tiempo_espera_prom": "Espera prom. (min)",
                        "tiempo_sistema_prom": "Sistema prom. (min)",
                        "utilizacion_prom": "Utilización",
                    }
                )
            )
        )
    lines.append("")
    lines.append("## Punto 2: promedio de usuarios de cada tipo")
    lines.append("")
    point2 = tables.punto2.rename(
        columns={
            "tipo_etiqueta": "Tipo de usuario",
            "promedio_usuarios_por_replica": "Promedio por réplica",
            "desviacion_estandar": "Desv. estándar",
            "ic95_inferior": "IC 95 % inf.",
            "ic95_superior": "IC 95 % sup.",
            "porcentaje": "Porcentaje (%)",
            "promedio_por_cajero": "Promedio por cajero",
        }
    )
    lines.append(
        _md_table(
            point2[
                [
                    "Tipo de usuario",
                    "Promedio por réplica",
                    "Desv. estándar",
                    "IC 95 % inf.",
                    "IC 95 % sup.",
                    "Porcentaje (%)",
                    "Promedio por cajero",
                ]
            ]
        )
    )
    lines.append("")
    lines.append("## Punto 3: total de usuarios por tipo en cada réplica")
    lines.append("")
    lines.append(
        "La tabla completa por réplica está en `outputs/punto3_replicas.csv`. "
        "La réplica con menor cantidad por tipo se resume así:"
    )
    lines.append("")
    lines.append(
        _md_table(
            tables.punto3_minimos.rename(
                columns={
                    "tipo_etiqueta": "Tipo",
                    "replica_con_menor_cantidad": "Réplica con mínimo",
                    "minimo": "Mínimo",
                    "promedio": "Promedio",
                    "maximo": "Máximo",
                    "desviacion_estandar": "Desv. estándar",
                    "replicas_empatadas": "Réplicas empatadas",
                }
            )[
                [
                    "Tipo",
                    "Réplica con mínimo",
                    "Mínimo",
                    "Promedio",
                    "Máximo",
                    "Desv. estándar",
                    "Réplicas empatadas",
                ]
            ]
        )
    )
    lines.append("")
    lines.append("## Punto 4: ¿se necesita un cajero adicional?")
    lines.append("")
    decision = tables.punto4_decision
    lines.append(f"**Decisión:** {'Sí' if decision['nuevo_cajero_necesario'] else 'No'} se necesita un cajero adicional.")
    lines.append("")
    lines.append(str(decision["justificacion"]))
    lines.append("")
    lines.append(
        _md_table(
            tables.punto4_comparacion.rename(
                columns={
                    "metrica": "Métrica",
                    "tres_cajas_mixtas": "3 cajas mixtas",
                    "cuatro_cajas_mixtas": "4 cajas mixtas",
                    "diferencia_4_menos_3": "Diferencia (4 - 3)",
                    "mejora_porcentual": "Mejora (%)",
                }
            )
        )
    )
    lines.append("")
    lines.append("## Punto 5: configuración óptima")
    lines.append("")
    recommendation = tables.punto5_recomendacion
    lines.append(
        f"**Recomendación costo-efectiva:** {recommendation.get('recomendado_etiqueta')} — "
        f"{recommendation.get('cajas_exclusivas_retiro')} cajas exclusivas de retiro, "
        f"{recommendation.get('cajas_exclusivas_pago')} de pago, "
        f"{recommendation.get('cajas_mixtas')} mixtas; "
        f"{recommendation.get('cajas_totales')} cajas en total."
    )
    lines.append("")
    lines.append(str(recommendation.get("justificacion", "")))
    if recommendation.get("advertencia"):
        lines.append("")
        lines.append(f"> **Advertencia:** {recommendation['advertencia']}")
    best_performance = recommendation.get("mejor_desempeno")
    if best_performance:
        lines.append("")
        lines.append(
            "**Mejor desempeño absoluto:** "
            f"{best_performance['etiqueta']} "
            f"({best_performance['cajas_totales']} cajas), con espera promedio "
            f"global de {best_performance['espera_promedio_global_min']:.2f} min. "
            "No se recomienda automáticamente porque puede implicar cajas "
            "adicionales que no son necesarias para cumplir los criterios."
        )
    best_exclusive_3 = recommendation.get("mejor_opcion_exclusiva_3_cajas")
    if best_exclusive_3:
        peor_3 = max(
            best_exclusive_3["espera_promedio_retiro_min"],
            best_exclusive_3["espera_promedio_pago_min"],
        )
        lines.append("")
        lines.append(
            "Si el banco exige especializar las **3 cajas existentes**, la opción "
            f"más balanceada es **{best_exclusive_3['etiqueta']}** "
            f"({best_exclusive_3['cajas_exclusivas_retiro']} de retiro y "
            f"{best_exclusive_3['cajas_exclusivas_pago']} de pago), con espera "
            f"promedio global de {best_exclusive_3['espera_promedio_global_min']:.2f} min "
            f"y espera de la operación más alta de {peor_3:.2f} min. "
            "Esta opción no cumple todos los criterios de servicio."
        )
    best_exclusive_4 = recommendation.get("mejor_opcion_exclusiva_4_cajas")
    if best_exclusive_4:
        peor_4 = max(
            best_exclusive_4["espera_promedio_retiro_min"],
            best_exclusive_4["espera_promedio_pago_min"],
        )
        lines.append("")
        lines.append(
            "Si el banco está dispuesto a crear una cuarta caja y especializar "
            f"todas las cajas, la mejor opción es **{best_exclusive_4['etiqueta']}** "
            f"({best_exclusive_4['cajas_exclusivas_retiro']} de retiro y "
            f"{best_exclusive_4['cajas_exclusivas_pago']} de pago), con espera "
            f"promedio global de {best_exclusive_4['espera_promedio_global_min']:.2f} min "
            f"y espera de la operación más alta de {peor_4:.2f} min."
        )
    lines.append("")
    lines.append("## Archivos generados")
    lines.append("")
    lines.append("| Archivo | Contenido |")
    lines.append("|---|---|")
    lines.append("| `replicas.csv` | Métricas agregadas por réplica y configuración. |")
    lines.append("| `cajeros.csv` | Métricas por cajero y réplica. |")
    lines.append("| `clientes.csv` | Detalle de cada cliente simulado. |")
    lines.append("| `conteos_tipo.csv` | Conteos por acción y tipo de usuario. |")
    lines.append("| `punto1_cajeros.csv` | Tabla del punto 1. |")
    lines.append("| `punto2_usuarios_tipo.csv` | Tabla del punto 2. |")
    lines.append("| `punto2_usuarios_tipo_accion.csv` | Desglose acción × tipo. |")
    lines.append("| `punto3_replicas.csv` | Tabla del punto 3 por réplica. |")
    lines.append("| `punto3_minimos.csv` | Réplica con mínimo por tipo. |")
    lines.append("| `punto4_criterios.csv` | Evaluación de criterios de servicio. |")
    lines.append("| `punto4_comparacion.csv` | Comparación 3 vs 4 cajas mixtas. |")
    lines.append("| `punto5_configuracion.csv` | Ranking de configuraciones. |")
    lines.append("| `decisiones.json` | Decisión del punto 4 y recomendación del punto 5. |")
    lines.append("| `figuras/` | Figuras a 300 dpi para el documento. |")
    lines.append("")

    path = outputs_dir / "resumen_ejecucion.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Genera tablas, figuras y resumen del laboratorio bancario."
    )
    parser.add_argument(
        "--outputs",
        type=Path,
        default=ROOT / "outputs",
        help="Carpeta con los CSV crudos y donde se escriben los derivados.",
    )
    args = parser.parse_args()
    outputs_dir: Path = args.outputs
    outputs_dir.mkdir(parents=True, exist_ok=True)

    required = [
        "replicas.csv",
        "cajeros.csv",
        "clientes.csv",
        "conteos_tipo.csv",
        "resultados.json",
    ]
    missing = [name for name in required if not (outputs_dir / name).exists()]
    if missing:
        raise FileNotFoundError(
            "Faltan archivos de entrada: " + ", ".join(missing)
            + ". Ejecuta primero: python main.py"
        )

    replica_df = _read_csv(outputs_dir / "replicas.csv")
    cashier_df = _read_csv(outputs_dir / "cajeros.csv")
    clientes_df = _read_csv(outputs_dir / "clientes.csv")
    type_count_df = _read_csv(outputs_dir / "conteos_tipo.csv")
    metadata = json.loads((outputs_dir / "resultados.json").read_text(encoding="utf-8"))[
        "metadata"
    ]

    tables = build_report_tables(
        replica_df,
        cashier_df,
        clientes_df,
        type_count_df,
        metadata,
    )

    _write_csv(tables.resumen_cajeros, outputs_dir / "resumen_cajeros.csv")
    _write_csv(tables.resumen_acciones, outputs_dir / "resumen_por_accion.csv")
    _write_csv(tables.resumen_tipos, outputs_dir / "resumen_por_tipo.csv")
    _write_csv(tables.punto1, outputs_dir / "punto1_cajeros.csv")
    _write_csv(tables.punto2, outputs_dir / "punto2_usuarios_tipo.csv")
    _write_csv(tables.punto2_accion, outputs_dir / "punto2_usuarios_tipo_accion.csv")
    _write_csv(tables.punto3_replicas, outputs_dir / "punto3_replicas.csv")
    _write_csv(tables.punto3_minimos, outputs_dir / "punto3_minimos.csv")
    _write_csv(tables.punto4_criterios, outputs_dir / "punto4_criterios.csv")
    _write_csv(tables.punto4_comparacion, outputs_dir / "punto4_comparacion.csv")
    _write_csv(tables.punto5, outputs_dir / "punto5_configuracion.csv")
    (outputs_dir / "decisiones.json").write_text(
        tables.to_json(), encoding="utf-8"
    )

    figures = build_figures(tables, outputs_dir)
    summary_path = build_markdown_summary(tables, metadata, outputs_dir)

    print("Tablas generadas en:", outputs_dir.resolve())
    print("Figuras generadas:", len(figures))
    for figure in figures:
        print("  -", figure.name)
    print("Resumen:", summary_path.name)


if __name__ == "__main__":
    main()
