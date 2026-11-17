"""Agregación estadística y tablas de respuesta para el laboratorio bancario.

Este módulo convierte los resultados crudos de ``bank_simulation`` en:

* resúmenes con media, desviación estándar e intervalo de confianza del 95 %;
* tablas para los cinco puntos solicitados;
* criterios de decisión para el cajero adicional y para la configuración final.

Todas las tablas se guardan en español para que puedan pasarse casi
directamente al documento de entrega.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Iterable, Sequence

import numpy as np
import pandas as pd
from scipy import stats

from .bank_simulation import (
    ACTIONS,
    ACTION_LABELS,
    SCENARIOS,
    SLA_DEFAULT,
    USER_TYPES,
    USER_TYPE_LABELS,
)

MAIN_SCENARIO = "mixto_3"
FOUR_CASHIER_SCENARIO = "mixto_4"

GLOBAL_METRICS: tuple[str, ...] = (
    "total_customers",
    "mean_wait",
    "std_wait",
    "p50_wait",
    "p90_wait",
    "p95_wait",
    "max_wait",
    "mean_service",
    "std_service",
    "mean_system",
    "Lq",
    "L",
    "utilization",
    "max_cashier_utilization",
    "throughput_per_hour",
    "frac_wait_gt_5",
    "frac_wait_gt_10",
    "frac_wait_gt_15",
    "unfinished_at_close",
    "waiting_at_close",
    "mean_wait_retiro",
    "mean_wait_pago",
    "p90_wait_retiro",
    "p90_wait_pago",
    "frac_wait_gt_10_retiro",
    "frac_wait_gt_10_pago",
    "mean_service_retiro",
    "mean_service_pago",
    "max_mean_wait_tipo",
    "max_mean_wait_accion",
)

CASHIER_METRICS: tuple[str, ...] = (
    "served",
    "mean_service",
    "std_service",
    "mean_wait",
    "p90_wait",
    "max_wait",
    "mean_system",
    "utilization",
    "mean_queue_length",
    "busy_minutes",
)


# ----------------------------------------------------------------------
# Conversión y enriquecimiento
# ----------------------------------------------------------------------
def result_to_dataframes(result) -> dict[str, pd.DataFrame]:
    """Convierte un ``ExperimentResult`` en DataFrames."""
    return {
        "replicas": pd.DataFrame(result.replica_rows),
        "cajeros": pd.DataFrame(result.cashier_rows),
        "clientes": pd.DataFrame(result.customer_rows),
        "conteos": pd.DataFrame(result.type_count_rows),
    }


def enrich_replicas(replica_df: pd.DataFrame) -> pd.DataFrame:
    """Agrega métricas auxiliares de peor caso por tipo y por acción."""
    df = replica_df.copy()
    type_columns = [f"mean_wait_{user_type}" for user_type in USER_TYPES]
    action_columns = [f"mean_wait_{action}" for action in ACTIONS]
    df["max_mean_wait_tipo"] = df[type_columns].max(axis=1)
    df["max_mean_wait_accion"] = df[action_columns].max(axis=1)
    return df


def summarize_metrics(
    df: pd.DataFrame,
    group_columns: Sequence[str],
    metric_columns: Sequence[str],
    confidence: float = 0.95,
) -> pd.DataFrame:
    """Resume métricas por grupo con media, DE e IC t de Student."""
    rows: list[dict[str, object]] = []
    if df.empty:
        return pd.DataFrame(
            columns=[
                *group_columns,
                "metric",
                "n",
                "mean",
                "std",
                "se",
                "ci_low",
                "ci_high",
                "min",
                "max",
                "median",
            ]
        )

    for keys, group in df.groupby(list(group_columns), dropna=False, observed=True):
        if not isinstance(keys, tuple):
            keys = (keys,)
        group_key = dict(zip(group_columns, keys))
        n = len(group)
        for metric in metric_columns:
            if metric not in group:
                continue
            values = pd.to_numeric(group[metric], errors="coerce").dropna()
            if values.empty:
                continue
            mean = float(values.mean())
            std = float(values.std(ddof=1)) if len(values) > 1 else 0.0
            se = std / np.sqrt(len(values)) if len(values) > 1 else 0.0
            if len(values) > 1:
                critical = float(stats.t.ppf((1 + confidence) / 2, len(values) - 1))
            else:
                critical = float("nan")
            rows.append(
                {
                    **group_key,
                    "metric": metric,
                    "n": n,
                    "mean": mean,
                    "std": std,
                    "se": se,
                    "ci_low": mean - critical * se if len(values) > 1 else mean,
                    "ci_high": mean + critical * se if len(values) > 1 else mean,
                    "min": float(values.min()),
                    "max": float(values.max()),
                    "median": float(values.median()),
                }
            )
    return pd.DataFrame(rows)


def build_action_metrics(clientes_df: pd.DataFrame) -> pd.DataFrame:
    """Métricas por réplica y acción (retiro/pago)."""
    if clientes_df.empty:
        return pd.DataFrame()
    grouped = (
        clientes_df.groupby(
            ["scenario", "scenario_label", "replica", "action", "action_label"],
            observed=True,
        )
        .agg(
            n=("customer_id", "size"),
            mean_wait=("wait_time", "mean"),
            p90_wait=("wait_time", lambda s: s.quantile(0.90)),
            frac_wait_gt_10=("wait_time", lambda s: float((s > 10.0).mean())),
            mean_service=("service_time", "mean"),
        )
        .reset_index()
    )
    return grouped


def build_type_metrics(clientes_df: pd.DataFrame) -> pd.DataFrame:
    """Métricas por réplica y tipo de usuario, sumando retiros y pagos."""
    if clientes_df.empty:
        return pd.DataFrame()
    grouped = (
        clientes_df.groupby(
            ["scenario", "scenario_label", "replica", "user_type", "user_type_label"],
            observed=True,
        )
        .agg(
            n=("customer_id", "size"),
            mean_wait=("wait_time", "mean"),
            p90_wait=("wait_time", lambda s: s.quantile(0.90)),
            mean_service=("service_time", "mean"),
        )
        .reset_index()
    )
    return grouped


# ----------------------------------------------------------------------
# Resúmenes base
# ----------------------------------------------------------------------
def build_core_summaries(
    replica_df: pd.DataFrame,
    cashier_df: pd.DataFrame,
    clientes_df: pd.DataFrame,
) -> dict[str, pd.DataFrame]:
    """Construye los resúmenes que alimentan las tablas de los 5 puntos."""
    replica_df = enrich_replicas(replica_df)
    action_df = build_action_metrics(clientes_df)
    type_df = build_type_metrics(clientes_df)

    summary_global = summarize_metrics(
        replica_df,
        ["scenario", "scenario_label"],
        GLOBAL_METRICS,
    )
    summary_action = summarize_metrics(
        action_df,
        ["scenario", "scenario_label", "action", "action_label"],
        ("n", "mean_wait", "p90_wait", "frac_wait_gt_10", "mean_service"),
    )
    summary_type = summarize_metrics(
        type_df,
        ["scenario", "scenario_label", "user_type", "user_type_label"],
        ("n", "mean_wait", "p90_wait", "mean_service"),
    )
    summary_cashier = summarize_metrics(
        cashier_df,
        [
            "scenario",
            "scenario_label",
            "cashier",
            "cashier_label",
            "allowed_action",
        ],
        CASHIER_METRICS,
    )
    return {
        "replicas_enriquecidas": replica_df,
        "acciones_replica": action_df,
        "tipos_replica": type_df,
        "resumen_global": summary_global,
        "resumen_acciones": summary_action,
        "resumen_tipos": summary_type,
        "resumen_cajeros": summary_cashier,
    }


def summary_metric(
    summary: pd.DataFrame,
    scenario: str,
    metric: str,
    column: str = "mean",
    default: float = float("nan"),
) -> float:
    """Extrae un valor de la tabla resumen larga."""
    subset = summary[(summary["scenario"] == scenario) & (summary["metric"] == metric)]
    if subset.empty:
        return default
    return float(subset.iloc[0][column])


# ----------------------------------------------------------------------
# Punto 1: cajero con menor y mayor tiempo de atención
# ----------------------------------------------------------------------
def build_point1_table(
    summary_cashier: pd.DataFrame,
    scenario_keys: Sequence[str] | None = None,
) -> pd.DataFrame:
    """Tabla por cajero, con marca de menor/mayor tiempo promedio de servicio."""
    if summary_cashier.empty:
        return pd.DataFrame()

    keys = (
        list(scenario_keys)
        if scenario_keys is not None
        else list(summary_cashier["scenario"].drop_duplicates())
    )
    subset = summary_cashier[summary_cashier["scenario"].isin(keys)].copy()

    def value(cashier: int, scenario: str, metric: str, column: str = "mean") -> float:
        row = subset[
            (subset["scenario"] == scenario)
            & (subset["cashier"] == cashier)
            & (subset["metric"] == metric)
        ]
        return float(row.iloc[0][column]) if not row.empty else float("nan")

    rows: list[dict[str, object]] = []
    for scenario in keys:
        scenario_rows = subset[subset["scenario"] == scenario]
        cashiers = sorted(scenario_rows["cashier"].unique())
        data: list[dict[str, object]] = []
        for cashier in cashiers:
            label_rows = scenario_rows[scenario_rows["cashier"] == cashier]
            data.append(
                {
                    "escenario": scenario,
                    "escenario_etiqueta": str(label_rows["scenario_label"].iloc[0]),
                    "cajero": int(cashier),
                    "tipo_caja": str(label_rows["cashier_label"].iloc[0]),
                    "clientes_atendidos_prom": value(cashier, scenario, "served"),
                    "tiempo_servicio_prom": value(cashier, scenario, "mean_service"),
                    "tiempo_servicio_ic_inf": value(
                        cashier, scenario, "mean_service", "ci_low"
                    ),
                    "tiempo_servicio_ic_sup": value(
                        cashier, scenario, "mean_service", "ci_high"
                    ),
                    "tiempo_espera_prom": value(cashier, scenario, "mean_wait"),
                    "tiempo_espera_p90": value(cashier, scenario, "p90_wait"),
                    "tiempo_sistema_prom": value(cashier, scenario, "mean_system"),
                    "utilizacion_prom": value(cashier, scenario, "utilization"),
                    "cola_prom": value(cashier, scenario, "mean_queue_length"),
                }
            )
        scenario_table = pd.DataFrame(data)
        min_service = scenario_table["tiempo_servicio_prom"].min()
        max_service = scenario_table["tiempo_servicio_prom"].max()
        min_wait = scenario_table["tiempo_espera_prom"].min()
        max_wait = scenario_table["tiempo_espera_prom"].max()
        scenario_table["menor_tiempo_servicio"] = (
            scenario_table["tiempo_servicio_prom"] == min_service
        )
        scenario_table["mayor_tiempo_servicio"] = (
            scenario_table["tiempo_servicio_prom"] == max_service
        )
        scenario_table["menor_tiempo_espera"] = (
            scenario_table["tiempo_espera_prom"] == min_wait
        )
        scenario_table["mayor_tiempo_espera"] = (
            scenario_table["tiempo_espera_prom"] == max_wait
        )
        rows.extend(scenario_table.to_dict("records"))

    result = pd.DataFrame(rows)
    numeric = [
        "clientes_atendidos_prom",
        "tiempo_servicio_prom",
        "tiempo_servicio_ic_inf",
        "tiempo_servicio_ic_sup",
        "tiempo_espera_prom",
        "tiempo_espera_p90",
        "tiempo_sistema_prom",
        "utilizacion_prom",
        "cola_prom",
    ]
    for column in numeric:
        if column in result:
            result[column] = result[column].astype(float).round(4)
    return result


# ----------------------------------------------------------------------
# Punto 2: promedio de usuarios de cada tipo
# ----------------------------------------------------------------------
def _type_counts_by_replica(type_count_df: pd.DataFrame, scenario: str) -> pd.DataFrame:
    subset = type_count_df[type_count_df["scenario"] == scenario]
    if subset.empty:
        return pd.DataFrame()
    counts = (
        subset.groupby(
            ["replica", "user_type", "user_type_label"], observed=True
        )["count"]
        .sum()
        .reset_index()
    )
    return counts


def build_point2_table(
    type_count_df: pd.DataFrame,
    scenario: str = MAIN_SCENARIO,
    num_cashiers: int = 3,
) -> pd.DataFrame:
    """Promedio por réplica de usuarios de cada tipo, en la totalidad de cajas."""
    counts = _type_counts_by_replica(type_count_df, scenario)
    if counts.empty:
        return pd.DataFrame()

    summary = summarize_metrics(
        counts,
        ["user_type", "user_type_label"],
        ("count",),
    )
    total_mean = float(summary["mean"].sum()) if not summary.empty else 0.0
    summary = summary.rename(
        columns={
            "mean": "promedio_usuarios_por_replica",
            "std": "desviacion_estandar",
            "ci_low": "ic95_inferior",
            "ci_high": "ic95_superior",
            "min": "minimo",
            "max": "maximo",
            "median": "mediana",
            "n": "replicas",
        }
    )
    summary["porcentaje"] = (
        summary["promedio_usuarios_por_replica"] / total_mean * 100.0
        if total_mean
        else 0.0
    )
    summary["promedio_por_cajero"] = (
        summary["promedio_usuarios_por_replica"] / num_cashiers
        if num_cashiers
        else np.nan
    )
    summary["tipo_etiqueta"] = summary["user_type_label"]
    summary["user_type"] = pd.Categorical(
        summary["user_type"], categories=USER_TYPES, ordered=True
    )
    summary = summary.sort_values("user_type")
    columns = [
        "user_type",
        "tipo_etiqueta",
        "replicas",
        "promedio_usuarios_por_replica",
        "desviacion_estandar",
        "ic95_inferior",
        "ic95_superior",
        "minimo",
        "maximo",
        "mediana",
        "porcentaje",
        "promedio_por_cajero",
    ]
    result = summary[columns].copy()
    for column in [
        "promedio_usuarios_por_replica",
        "desviacion_estandar",
        "ic95_inferior",
        "ic95_superior",
        "minimo",
        "maximo",
        "mediana",
        "porcentaje",
        "promedio_por_cajero",
    ]:
        result[column] = result[column].astype(float).round(4)
    result.insert(0, "escenario", scenario)
    return result


def build_point2_action_table(
    type_count_df: pd.DataFrame,
    scenario: str = MAIN_SCENARIO,
) -> pd.DataFrame:
    """Desglose acción × tipo de usuario, útil como anexo."""
    subset = type_count_df[type_count_df["scenario"] == scenario].copy()
    if subset.empty:
        return pd.DataFrame()
    summary = summarize_metrics(
        subset,
        ["action", "action_label", "user_type", "user_type_label"],
        ("count",),
    )
    summary = summary.rename(
        columns={
            "mean": "promedio_por_replica",
            "std": "desviacion_estandar",
            "ci_low": "ic95_inferior",
            "ci_high": "ic95_superior",
            "min": "minimo",
            "max": "maximo",
            "n": "replicas",
        }
    )
    summary["escenario"] = scenario
    return summary[
        [
            "escenario",
            "action",
            "action_label",
            "user_type",
            "user_type_label",
            "replicas",
            "promedio_por_replica",
            "desviacion_estandar",
            "ic95_inferior",
            "ic95_superior",
            "minimo",
            "maximo",
        ]
    ].round(4)


# ----------------------------------------------------------------------
# Punto 3: total de usuarios por tipo en cada réplica
# ----------------------------------------------------------------------
def build_point3_replica_table(
    type_count_df: pd.DataFrame,
    scenario: str = MAIN_SCENARIO,
) -> pd.DataFrame:
    """Tabla réplica × tipo con el total de usuarios de cada tipo."""
    counts = _type_counts_by_replica(type_count_df, scenario)
    if counts.empty:
        return pd.DataFrame()

    pivot = (
        counts.pivot(index="replica", columns="user_type", values="count")
        .reindex(columns=USER_TYPES)
        .fillna(0)
        .astype(int)
        .reset_index()
    )
    pivot.columns = ["replica", *[USER_TYPE_LABELS[t] for t in USER_TYPES]]
    pivot["Total"] = pivot[list(USER_TYPE_LABELS.values())].sum(axis=1)
    pivot.insert(0, "escenario", scenario)
    return pivot.sort_values("replica").reset_index(drop=True)


def build_point3_min_table(
    type_count_df: pd.DataFrame,
    scenario: str = MAIN_SCENARIO,
) -> pd.DataFrame:
    """Réplica con menor cantidad de usuarios para cada tipo."""
    counts = _type_counts_by_replica(type_count_df, scenario)
    if counts.empty:
        return pd.DataFrame()
    rows: list[dict[str, object]] = []
    for user_type in USER_TYPES:
        subset = counts[counts["user_type"] == user_type]
        if subset.empty:
            continue
        min_count = int(subset["count"].min())
        min_rows = subset[subset["count"] == min_count].sort_values("replica")
        rows.append(
            {
                "escenario": scenario,
                "user_type": user_type,
                "tipo_etiqueta": USER_TYPE_LABELS[user_type],
                "replica_con_menor_cantidad": int(min_rows.iloc[0]["replica"]),
                "minimo": min_count,
                "promedio": round(float(subset["count"].mean()), 4),
                "maximo": int(subset["count"].max()),
                "desviacion_estandar": round(float(subset["count"].std(ddof=1)), 4),
                "replicas_empatadas": int(len(min_rows)),
            }
        )
    return pd.DataFrame(rows)


# ----------------------------------------------------------------------
# Punto 4: necesidad de un cajero adicional
# ----------------------------------------------------------------------
def build_sla_criteria(
    summary_global: pd.DataFrame,
    scenario_keys: Sequence[str] | None = None,
) -> pd.DataFrame:
    """Evalúa los criterios de servicio para cada escenario."""
    scenarios = (
        list(scenario_keys)
        if scenario_keys is not None
        else list(summary_global["scenario"].drop_duplicates())
    )
    rows: list[dict[str, object]] = []
    for scenario in scenarios:
        label = SCENARIOS[scenario].label if scenario in SCENARIOS else scenario
        criteria = [
            (
                "Espera promedio global",
                "mean_wait",
                "min",
                SLA_DEFAULT["espera_promedio_max_min"],
            ),
            (
                "Espera promedio de retiros",
                "mean_wait_retiro",
                "min",
                SLA_DEFAULT["espera_promedio_max_min"],
            ),
            (
                "Espera promedio de pagos",
                "mean_wait_pago",
                "min",
                SLA_DEFAULT["espera_promedio_max_min"],
            ),
            (
                "Espera promedio del peor tipo de usuario",
                "max_mean_wait_tipo",
                "min",
                SLA_DEFAULT["espera_promedio_max_min"],
            ),
            (
                "Espera p90 global",
                "p90_wait",
                "min",
                SLA_DEFAULT["espera_p90_max_min"],
            ),
            (
                "Espera p90 de retiros",
                "p90_wait_retiro",
                "min",
                SLA_DEFAULT["espera_p90_max_min"],
            ),
            (
                "Espera p90 de pagos",
                "p90_wait_pago",
                "min",
                SLA_DEFAULT["espera_p90_max_min"],
            ),
            (
                "Fracción con espera > 10 min",
                "frac_wait_gt_10",
                "max",
                SLA_DEFAULT["fraccion_espera_mayor_10_max"],
            ),
            (
                "Utilización máxima de una caja",
                "max_cashier_utilization",
                "max",
                SLA_DEFAULT["utilizacion_maxima"],
            ),
        ]
        scenario_values: list[dict[str, object]] = []
        for name, metric, direction, threshold in criteria:
            value = summary_metric(summary_global, scenario, metric)
            if direction == "min":
                complies = bool(value <= threshold)
                operator = "<="
            else:
                complies = bool(value <= threshold)
                operator = "<="
            scenario_values.append(
                {
                    "escenario": scenario,
                    "escenario_etiqueta": label,
                    "criterio": name,
                    "metrica": metric,
                    "operador": operator,
                    "umbral": threshold,
                    "valor": round(value, 4),
                    "cumple": complies,
                }
            )
        rows.extend(scenario_values)
    return pd.DataFrame(rows)


def build_point4_comparison(
    summary_global: pd.DataFrame,
) -> pd.DataFrame:
    """Comparación 3 cajas mixtas vs 4 cajas mixtas."""
    metrics = [
        ("Espera promedio global (min)", "mean_wait"),
        ("Espera promedio retiros (min)", "mean_wait_retiro"),
        ("Espera promedio pagos (min)", "mean_wait_pago"),
        ("Espera promedio peor tipo (min)", "max_mean_wait_tipo"),
        ("Espera p90 global (min)", "p90_wait"),
        ("Fracción con espera > 10 min", "frac_wait_gt_10"),
        ("Utilización promedio", "utilization"),
        ("Utilización máxima de una caja", "max_cashier_utilization"),
        ("Usuarios que terminan después de las 8 h", "unfinished_at_close"),
    ]
    rows: list[dict[str, object]] = []
    for label, metric in metrics:
        three = summary_metric(summary_global, MAIN_SCENARIO, metric)
        four = summary_metric(summary_global, FOUR_CASHIER_SCENARIO, metric)
        rows.append(
            {
                "metrica": label,
                "tres_cajas_mixtas": round(three, 4),
                "cuatro_cajas_mixtas": round(four, 4),
                "diferencia_4_menos_3": round(four - three, 4),
                "mejora_porcentual": (
                    round((three - four) / three * 100.0, 2) if three else np.nan
                ),
            }
        )
    return pd.DataFrame(rows)


def build_point4_decision(
    summary_global: pd.DataFrame,
    criteria_df: pd.DataFrame,
) -> dict[str, object]:
    """Decide si hace falta un cuarto cajero con los criterios definidos."""
    three_criteria = criteria_df[criteria_df["escenario"] == MAIN_SCENARIO]
    four_criteria = criteria_df[criteria_df["escenario"] == FOUR_CASHIER_SCENARIO]
    three_ok = bool(three_criteria["cumple"].all()) if not three_criteria.empty else False
    four_ok = bool(four_criteria["cumple"].all()) if not four_criteria.empty else False
    failed_three = three_criteria[~three_criteria["cumple"]]["criterio"].tolist()

    wait_3 = summary_metric(summary_global, MAIN_SCENARIO, "mean_wait")
    wait_4 = summary_metric(summary_global, FOUR_CASHIER_SCENARIO, "mean_wait")
    util_3 = summary_metric(summary_global, MAIN_SCENARIO, "max_cashier_utilization")

    if three_ok:
        needed = False
        justification = (
            "Con 3 cajas mixtas se cumplen todos los criterios de servicio "
            f"(espera promedio {wait_3:.2f} min y utilización máxima "
            f"{util_3:.1%}). No se requiere crear un cuarto cajero para la "
            "demanda simulada."
        )
    elif four_ok:
        needed = True
        justification = (
            "Con 3 cajas mixtas no se cumplen estos criterios: "
            + ", ".join(failed_three)
            + f". Con 4 cajas mixtas la espera promedio baja a {wait_4:.2f} min "
            "y se cumplen los criterios, por lo que se recomienda crear un "
            "cuarto cajero."
        )
    else:
        needed = True
        justification = (
            "Ni con 3 ni con 4 cajas mixtas se cumplen todos los criterios. "
            "Se requiere más capacidad, revisar el supuesto de llegadas o "
            "relajar los criterios de servicio."
        )

    return {
        "criterios": SLA_DEFAULT,
        "tres_cajas_cumple_todos": three_ok,
        "cuatro_cajas_cumple_todos": four_ok,
        "criterios_incumplidos_con_3": failed_three,
        "espera_promedio_3_cajas_min": round(wait_3, 4),
        "espera_promedio_4_cajas_min": round(wait_4, 4),
        "nuevo_cajero_necesario": needed,
        "justificacion": justification,
    }


# ----------------------------------------------------------------------
# Punto 5: configuración óptima
# ----------------------------------------------------------------------
def _scenario_metadata_rows(metadata: dict[str, object]) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    scenarios = metadata.get("scenarios", {})
    if not isinstance(scenarios, dict):
        return pd.DataFrame()
    for key, info in scenarios.items():
        if not isinstance(info, dict):
            continue
        load = info.get("offered_load", {})
        if not isinstance(load, dict):
            load = {}
        rows.append(
            {
                "scenario": key,
                "escenario_etiqueta": info.get("label", key),
                "num_cashiers": info.get("num_cashiers", 0),
                "num_retiro": info.get("num_retiro", 0),
                "num_pago": info.get("num_pago", 0),
                "num_mixto": info.get("num_mixto", 0),
                "rho_global": load.get("rho_global", np.nan),
                "rho_retiro": load.get("rho_retiro", np.nan),
                "rho_pago": load.get("rho_pago", np.nan),
            }
        )
    return pd.DataFrame(rows)


def build_point5_table(
    summary_global: pd.DataFrame,
    criteria_df: pd.DataFrame,
    metadata: dict[str, object],
) -> tuple[pd.DataFrame, dict[str, object]]:
    """Ranking de configuraciones y recomendación final."""
    meta = _scenario_metadata_rows(metadata)
    metrics = [
        "mean_wait",
        "mean_wait_retiro",
        "mean_wait_pago",
        "max_mean_wait_accion",
        "p90_wait",
        "max_mean_wait_tipo",
        "max_cashier_utilization",
        "frac_wait_gt_10",
        "unfinished_at_close",
    ]
    rows: list[dict[str, object]] = []
    for _, meta_row in meta.iterrows():
        scenario = str(meta_row["scenario"])
        row = meta_row.to_dict()
        for metric in metrics:
            row[metric] = summary_metric(summary_global, scenario, metric)
        scenario_criteria = criteria_df[criteria_df["escenario"] == scenario]
        row["cumple_todos_los_criterios"] = (
            bool(scenario_criteria["cumple"].all())
            if not scenario_criteria.empty
            else False
        )
        rows.append(row)

    table = pd.DataFrame(rows)
    if table.empty:
        return table, {}

    table["_cumple_orden"] = (~table["cumple_todos_los_criterios"]).astype(int)
    table = table.sort_values(
        [
            "_cumple_orden",
            "mean_wait",
            "max_mean_wait_accion",
            "max_cashier_utilization",
        ]
    ).reset_index(drop=True)
    table["ranking"] = np.arange(1, len(table) + 1)
    table = table.drop(columns=["_cumple_orden"])

    # Mejor opción exclusiva con 3 cajas (sin agregar cajeros), por si el
    # banco exige especialización total sin ampliar la capacidad.
    exclusive_3 = table[(table["num_mixto"] == 0) & (table["num_cashiers"] == 3)].copy()
    best_exclusive_3 = None
    if not exclusive_3.empty:
        exclusive_3 = exclusive_3.sort_values(
            ["max_mean_wait_accion", "mean_wait", "max_cashier_utilization"]
        ).reset_index(drop=True)
        best_exclusive_3 = exclusive_3.iloc[0].to_dict()

    # Mejor opción exclusiva con 4 cajas, por si el banco está dispuesto a
    # crear un cajero adicional y especializar todas las cajas.
    exclusive_4 = table[(table["num_mixto"] == 0) & (table["num_cashiers"] == 4)].copy()
    best_exclusive_4 = None
    if not exclusive_4.empty:
        exclusive_4 = exclusive_4.sort_values(
            ["max_mean_wait_accion", "mean_wait", "max_cashier_utilization"]
        ).reset_index(drop=True)
        best_exclusive_4 = exclusive_4.iloc[0].to_dict()

    # Recomendación costo-efectiva: si la configuración actual de 3 cajas
    # mixtas cumple los criterios, no se justifica agregar una cuarta caja
    # solo para reducir aún más una espera que ya es aceptable.
    current = table[table["scenario"] == MAIN_SCENARIO]
    current_ok = (
        bool(current.iloc[0]["cumple_todos_los_criterios"])
        if not current.empty
        else False
    )
    if current_ok:
        recommended = current.iloc[0].to_dict()
        selection_reason = (
            "La configuración actual de 3 cajas mixtas ya cumple todos los "
            "criterios de servicio; agregar una cuarta caja mejora la espera "
            "pero no es necesaria para la demanda simulada."
        )
    else:
        same_size = table[
            (table["num_cashiers"] == 3) & (table["cumple_todos_los_criterios"])
        ]
        if not same_size.empty:
            recommended = same_size.sort_values("mean_wait").iloc[0].to_dict()
            selection_reason = (
                "Se elige la mejor configuración de 3 cajas que cumple los "
                "criterios, sin aumentar el número de cajeros."
            )
        else:
            larger = table[
                (table["num_cashiers"] > 3) & (table["cumple_todos_los_criterios"])
            ]
            if not larger.empty:
                recommended = larger.sort_values("mean_wait").iloc[0].to_dict()
                selection_reason = (
                    "Ninguna configuración de 3 cajas cumple los criterios; se "
                    "recomienda la mejor configuración de 4 cajas."
                )
            else:
                recommended = table.iloc[0].to_dict()
                selection_reason = (
                    "Ninguna configuración cumple todos los criterios; se "
                    "muestra la de menor espera, pero la decisión requiere más "
                    "capacidad o revisar los supuestos."
                )

    recommended_scenario = str(recommended["scenario"])
    recommended_meta = SCENARIOS.get(recommended_scenario)
    best_performance = table.iloc[0].to_dict()
    recommendation: dict[str, object] = {
        "criterios": SLA_DEFAULT,
        "recomendado": recommended_scenario,
        "recomendado_etiqueta": recommended["escenario_etiqueta"],
        "cajas_totales": int(recommended["num_cashiers"]),
        "cajas_exclusivas_retiro": int(recommended["num_retiro"]),
        "cajas_exclusivas_pago": int(recommended["num_pago"]),
        "cajas_mixtas": int(recommended["num_mixto"]),
        "espera_promedio_global_min": round(float(recommended["mean_wait"]), 4),
        "espera_promedio_retiro_min": round(
            float(recommended["mean_wait_retiro"]), 4
        ),
        "espera_promedio_pago_min": round(float(recommended["mean_wait_pago"]), 4),
        "utilizacion_maxima": round(
            float(recommended["max_cashier_utilization"]), 4
        ),
        "cumple_todos_los_criterios": bool(
            recommended["cumple_todos_los_criterios"]
        ),
        "advertencia": (
            ""
            if recommended["cumple_todos_los_criterios"]
            else (
                "La configuración recomendada no cumple todos los criterios; "
                "se requiere revisar la capacidad o los supuestos."
            )
        ),
        "motivo_de_la_recomendacion": selection_reason,
        "mejor_desempeno": {
            "escenario": best_performance["scenario"],
            "etiqueta": best_performance["escenario_etiqueta"],
            "espera_promedio_global_min": round(
                float(best_performance["mean_wait"]), 4
            ),
            "cajas_totales": int(best_performance["num_cashiers"]),
            "nota": (
                "Es la configuración con menor espera promedio, pero puede "
                "requerir más cajas de las necesarias para cumplir el servicio."
            ),
        },
        "justificacion": (
            f"La recomendación es '{recommended['escenario_etiqueta']}' "
            f"({int(recommended['num_retiro'])} cajas exclusivas de retiro, "
            f"{int(recommended['num_pago'])} de pago y "
            f"{int(recommended['num_mixto'])} mixtas), con una espera promedio "
            f"global de {float(recommended['mean_wait']):.2f} min, espera de "
            f"retiros de {float(recommended['mean_wait_retiro']):.2f} min y "
            f"espera de pagos de {float(recommended['mean_wait_pago']):.2f} min. "
            + selection_reason
            + (
                " Cumple todos los criterios de servicio definidos."
                if recommended["cumple_todos_los_criterios"]
                else " No cumple todos los criterios de servicio definidos."
            )
        ),
        "mejor_opcion_exclusiva_3_cajas": (
            {
                "escenario": best_exclusive_3["scenario"],
                "etiqueta": best_exclusive_3["escenario_etiqueta"],
                "cajas_exclusivas_retiro": int(best_exclusive_3["num_retiro"]),
                "cajas_exclusivas_pago": int(best_exclusive_3["num_pago"]),
                "espera_promedio_global_min": round(
                    float(best_exclusive_3["mean_wait"]), 4
                ),
                "espera_promedio_retiro_min": round(
                    float(best_exclusive_3["mean_wait_retiro"]), 4
                ),
                "espera_promedio_pago_min": round(
                    float(best_exclusive_3["mean_wait_pago"]), 4
                ),
                "peor_espera_por_accion_min": round(
                    float(best_exclusive_3["max_mean_wait_accion"]), 4
                ),
                "cumple_todos_los_criterios": bool(
                    best_exclusive_3["cumple_todos_los_criterios"]
                ),
            }
            if best_exclusive_3 is not None
            else None
        ),
        "mejor_opcion_exclusiva_4_cajas": (
            {
                "escenario": best_exclusive_4["scenario"],
                "etiqueta": best_exclusive_4["escenario_etiqueta"],
                "cajas_exclusivas_retiro": int(best_exclusive_4["num_retiro"]),
                "cajas_exclusivas_pago": int(best_exclusive_4["num_pago"]),
                "espera_promedio_global_min": round(
                    float(best_exclusive_4["mean_wait"]), 4
                ),
                "espera_promedio_retiro_min": round(
                    float(best_exclusive_4["mean_wait_retiro"]), 4
                ),
                "espera_promedio_pago_min": round(
                    float(best_exclusive_4["mean_wait_pago"]), 4
                ),
                "peor_espera_por_accion_min": round(
                    float(best_exclusive_4["max_mean_wait_accion"]), 4
                ),
                "cumple_todos_los_criterios": bool(
                    best_exclusive_4["cumple_todos_los_criterios"]
                ),
            }
            if best_exclusive_4 is not None
            else None
        ),
    }
    if recommended_meta is not None:
        recommendation["descripcion_configuracion"] = recommended_meta.description

    table["recomendado"] = table["scenario"] == recommended_scenario

    columns = [
        "ranking",
        "recomendado",
        "scenario",
        "escenario_etiqueta",
        "num_cashiers",
        "num_retiro",
        "num_pago",
        "num_mixto",
        "rho_global",
        "rho_retiro",
        "rho_pago",
        "mean_wait",
        "mean_wait_retiro",
        "mean_wait_pago",
        "max_mean_wait_accion",
        "p90_wait",
        "max_mean_wait_tipo",
        "max_cashier_utilization",
        "frac_wait_gt_10",
        "unfinished_at_close",
        "cumple_todos_los_criterios",
    ]
    table = table[columns].round(4)
    return table, recommendation


# ----------------------------------------------------------------------
# Construcción completa
# ----------------------------------------------------------------------
@dataclass
class ReportTables:
    """Conjunto de tablas y decisiones listas para el documento."""

    resumen_global: pd.DataFrame
    resumen_acciones: pd.DataFrame
    resumen_tipos: pd.DataFrame
    resumen_cajeros: pd.DataFrame
    punto1: pd.DataFrame
    punto2: pd.DataFrame
    punto2_accion: pd.DataFrame
    punto3_replicas: pd.DataFrame
    punto3_minimos: pd.DataFrame
    punto4_criterios: pd.DataFrame
    punto4_comparacion: pd.DataFrame
    punto4_decision: dict[str, object]
    punto5: pd.DataFrame
    punto5_recomendacion: dict[str, object]

    def to_json(self) -> str:
        return json.dumps(
            {
                "punto4_decision": self.punto4_decision,
                "punto5_recomendacion": self.punto5_recomendacion,
            },
            indent=2,
            ensure_ascii=False,
        )


def build_report_tables(
    replica_df: pd.DataFrame,
    cashier_df: pd.DataFrame,
    clientes_df: pd.DataFrame,
    type_count_df: pd.DataFrame,
    metadata: dict[str, object],
) -> ReportTables:
    """Construye todas las tablas de los cinco puntos."""
    summaries = build_core_summaries(replica_df, cashier_df, clientes_df)
    summary_global = summaries["resumen_global"]
    summary_cashier = summaries["resumen_cajeros"]

    point1 = build_point1_table(summary_cashier)
    point2 = build_point2_table(type_count_df)
    point2_action = build_point2_action_table(type_count_df)
    point3_replicas = build_point3_replica_table(type_count_df)
    point3_minimos = build_point3_min_table(type_count_df)
    criteria = build_sla_criteria(summary_global)
    comparison = build_point4_comparison(summary_global)
    decision = build_point4_decision(summary_global, criteria)
    point5, recommendation = build_point5_table(summary_global, criteria, metadata)

    return ReportTables(
        resumen_global=summary_global,
        resumen_acciones=summaries["resumen_acciones"],
        resumen_tipos=summaries["resumen_tipos"],
        resumen_cajeros=summary_cashier,
        punto1=point1,
        punto2=point2,
        punto2_accion=point2_action,
        punto3_replicas=point3_replicas,
        punto3_minimos=point3_minimos,
        punto4_criterios=criteria,
        punto4_comparacion=comparison,
        punto4_decision=decision,
        punto5=point5,
        punto5_recomendacion=recommendation,
    )
