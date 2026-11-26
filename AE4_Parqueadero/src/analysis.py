"""Agregación estadística, pruebas y tablas de respuesta del AE4.

Convierte los resultados crudos de ``parking_simulation`` en tablas listas
para el documento de entrega:

* resúmenes con media, desviación estándar e intervalo de confianza del 95 %;
* punto A: estadísticas por cajero y prueba de igualdad entre cajeros;
* punto B: promedio de usuarios por tipo y prueba de bondad de ajuste;
* punto C: criterios, comparación de escenarios y decisión;
* punto D: verificación, calibración y validación;
* punto E: eliminación del estado transitorio (antes vs después).

Todas las tablas se guardan en español y con nombres de columna estables.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
import math
from typing import Iterable, Sequence

import numpy as np
import pandas as pd
from scipy import stats

from .parking_simulation import (
    CRITERIA,
    MAIN_SCENARIO,
    SCENARIOS,
    SERVICE_MEAN_MIN,
    TYPE_PROB,
    USER_TYPES,
    USER_TYPE_LABELS,
    evaluate_criteria,
    mean_interarrival_min,
    theoretical_mg1_per_teller,
    theoretical_mm1,
)

GLOBAL_METRICS: tuple[str, ...] = (
    "total_customers",
    "throughput_per_hour",
    "mean_wait",
    "std_wait",
    "p50_wait",
    "p90_wait",
    "p95_wait",
    "max_wait",
    "mean_service",
    "std_service",
    "mean_system",
    "p90_system",
    "Lq",
    "L",
    "utilization",
    "max_teller_utilization",
    "frac_wait_gt_3",
    "frac_wait_gt_5",
    "frac_wait_gt_10",
    "unfinished_at_close",
    "waiting_at_close",
    "mean_wait_rapido",
    "mean_wait_normal",
    "mean_wait_lento",
    "mean_wait_muy_lento",
    "n_rapido",
    "n_normal",
    "n_lento",
    "n_muy_lento",
)

TELLER_METRICS: tuple[str, ...] = (
    "served",
    "mean_service",
    "std_service",
    "mean_wait",
    "p90_wait",
    "mean_system",
    "utilization",
    "mean_queue_length",
    "busy_minutes",
)

TYPE_REPLICA_METRICS: tuple[str, ...] = (
    "count",
    "mean_wait",
    "p90_wait",
    "mean_service",
    "mean_system",
)


# ----------------------------------------------------------------------
# Conversión y estadística descriptiva
# ----------------------------------------------------------------------
def result_to_dataframes(result) -> dict[str, pd.DataFrame]:
    """Convierte un ``ExperimentResult`` en DataFrames."""
    return {
        "replicas": pd.DataFrame(result.replica_rows),
        "cajeros": pd.DataFrame(result.teller_rows),
        "clientes": pd.DataFrame(result.customer_rows),
    }


def stats_row(values: Iterable[float], confidence: float = 0.95) -> dict[str, float]:
    """Media, desviación, error estándar e IC t de Student de una muestra."""
    data = np.asarray([v for v in values if v is not None], dtype=float)
    data = data[np.isfinite(data)]
    n = len(data)
    if n == 0:
        return {
            "n": 0,
            "mean": float("nan"),
            "std": float("nan"),
            "se": float("nan"),
            "ci_low": float("nan"),
            "ci_high": float("nan"),
            "min": float("nan"),
            "max": float("nan"),
            "median": float("nan"),
        }
    mean = float(np.mean(data))
    std = float(np.std(data, ddof=1)) if n > 1 else 0.0
    se = std / math.sqrt(n) if n > 1 else 0.0
    if n > 1:
        critical = float(stats.t.ppf((1 + confidence) / 2, n - 1))
    else:
        critical = float("nan")
    return {
        "n": n,
        "mean": mean,
        "std": std,
        "se": se,
        "ci_low": mean - critical * se if n > 1 else mean,
        "ci_high": mean + critical * se if n > 1 else mean,
        "min": float(np.min(data)),
        "max": float(np.max(data)),
        "median": float(np.median(data)),
    }


def summarize_metrics(
    df: pd.DataFrame,
    group_columns: Sequence[str],
    metric_columns: Sequence[str],
    confidence: float = 0.95,
) -> pd.DataFrame:
    """Resume métricas por grupo con media, desviación e IC t de Student."""
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
        for metric in metric_columns:
            if metric not in group:
                continue
            summary = stats_row(group[metric].tolist(), confidence)
            if summary["n"] == 0:
                continue
            rows.append({**group_key, "metric": metric, **summary})
    return pd.DataFrame(rows)


def summary_metric(
    summary: pd.DataFrame,
    scenario: str,
    metric: str,
    column: str = "mean",
    default: float = float("nan"),
) -> float:
    """Extrae un valor de una tabla resumen en formato largo."""
    subset = summary[(summary["scenario"] == scenario) & (summary["metric"] == metric)]
    if subset.empty:
        return default
    return float(subset.iloc[0][column])


def build_core_summaries(
    replica_df: pd.DataFrame,
    teller_df: pd.DataFrame,
    customer_df: pd.DataFrame,
) -> dict[str, pd.DataFrame]:
    """Construye los resúmenes base por escenario, cajero y tipo."""
    summary_global = summarize_metrics(
        replica_df,
        ["scenario", "scenario_label", "policy", "num_tellers"],
        GLOBAL_METRICS,
    )
    summary_tellers = summarize_metrics(
        teller_df,
        ["scenario", "scenario_label", "teller", "teller_label"],
        TELLER_METRICS,
    )
    type_replica = build_type_replica_table(customer_df)
    summary_types = summarize_metrics(
        type_replica,
        ["scenario", "user_type", "user_type_label"],
        TYPE_REPLICA_METRICS,
    )
    return {
        "replicas": replica_df,
        "cajeros": teller_df,
        "clientes": customer_df,
        "tipos_por_replica": type_replica,
        "resumen_global": summary_global,
        "resumen_cajeros": summary_tellers,
        "resumen_tipos": summary_types,
    }


def build_type_replica_table(customer_df: pd.DataFrame) -> pd.DataFrame:
    """Métricas por réplica y tipo de usuario, sumando los tres cajeros."""
    if customer_df.empty:
        return pd.DataFrame()
    grouped = (
        customer_df.groupby(
            ["scenario", "replica", "user_type", "user_type_label"],
            observed=True,
        )
        .agg(
            count=("customer_id", "size"),
            mean_wait=("wait_time", "mean"),
            p90_wait=("wait_time", lambda s: float(s.quantile(0.90))),
            mean_service=("service_time", "mean"),
            mean_system=("system_time", "mean"),
        )
        .reset_index()
    )
    return grouped


# ----------------------------------------------------------------------
# Punto A: cajero con menor y mayor tiempo promedio de atención
# ----------------------------------------------------------------------
def build_point1_table(
    teller_df: pd.DataFrame,
    scenario: str = MAIN_SCENARIO,
) -> tuple[pd.DataFrame, dict[str, object]]:
    """Estadísticas por cajero y prueba de igualdad de tiempos de atención."""
    subset = teller_df[teller_df["scenario"] == scenario].copy()
    if subset.empty:
        return pd.DataFrame(), {}

    rows: list[dict[str, object]] = []
    for teller, group in subset.groupby("teller", observed=True):
        service = stats_row(group["mean_service"].tolist())
        wait = stats_row(group["mean_wait"].tolist())
        system = stats_row(group["mean_system"].tolist())
        util = stats_row(group["utilization"].tolist())
        queue = stats_row(group["mean_queue_length"].tolist())
        rows.append(
            {
                "cajero": int(teller) + 1,
                "cajero_id": int(teller),
                "clientes_atendidos_prom": float(group["served"].mean()),
                "tiempo_servicio_prom": service["mean"],
                "tiempo_servicio_desv": service["std"],
                "tiempo_servicio_ic95_inf": service["ci_low"],
                "tiempo_servicio_ic95_sup": service["ci_high"],
                "tiempo_servicio_min_observado": float(group["min_service"].min()),
                "tiempo_servicio_max_observado": float(group["max_service"].max()),
                "tiempo_espera_prom": wait["mean"],
                "tiempo_espera_ic95_inf": wait["ci_low"],
                "tiempo_espera_ic95_sup": wait["ci_high"],
                "tiempo_espera_p90": float(group["p90_wait"].mean()),
                "tiempo_sistema_prom": system["mean"],
                "utilizacion_prom": util["mean"],
                "cola_prom": queue["mean"],
                "replicas": int(len(group)),
            }
        )

    table = pd.DataFrame(rows)
    min_service = table["tiempo_servicio_prom"].min()
    max_service = table["tiempo_servicio_prom"].max()
    table["menor_tiempo_servicio"] = table["tiempo_servicio_prom"] == min_service
    table["mayor_tiempo_servicio"] = table["tiempo_servicio_prom"] == max_service
    table["diferencia_vs_media_min"] = (
        table["tiempo_servicio_prom"] - table["tiempo_servicio_prom"].mean()
    )

    # Prueba de Friedman: mismas réplicas, tres cajeros (medidas repetidas).
    pivot = subset.pivot_table(
        index="replica", columns="teller", values="mean_service", aggfunc="mean"
    ).dropna()
    test: dict[str, object] = {
        "prueba": "Friedman",
        "cajeros_comparados": int(pivot.shape[1]),
        "replicas": int(pivot.shape[0]),
    }
    if pivot.shape[0] >= 3 and pivot.shape[1] >= 2:
        statistic, p_value = stats.friedmanchisquare(
            *[pivot[column].to_numpy() for column in pivot.columns]
        )
        test.update(
            {
                "estadistico": float(statistic),
                "p_value": float(p_value),
                "kendall_w": float(
                    statistic / (pivot.shape[0] * (pivot.shape[1] - 1))
                ),
                "interpretacion": (
                    "No hay evidencia de diferencias significativas entre los "
                    "tiempos promedio de atención de los cajeros (p > 0.05)."
                    if p_value > 0.05
                    else "Hay diferencias significativas entre cajeros (p <= 0.05)."
                ),
            }
        )
    else:
        test["interpretacion"] = "No hay suficientes réplicas para la prueba."

    return table.round(4), test


# ----------------------------------------------------------------------
# Punto B: promedio de usuarios de cada tipo en la totalidad de cajeros
# ----------------------------------------------------------------------
def build_point2_table(
    type_replica: pd.DataFrame,
    customer_df: pd.DataFrame,
    scenario: str = MAIN_SCENARIO,
    num_tellers: int = 3,
) -> tuple[pd.DataFrame, dict[str, object], pd.DataFrame]:
    """Promedio de usuarios de cada tipo y prueba de composición."""
    subset = type_replica[type_replica["scenario"] == scenario]
    if subset.empty:
        return pd.DataFrame(), {}, pd.DataFrame()

    total_mean = float(subset.groupby("replica")["count"].sum().mean())
    counts_all = subset.groupby("user_type", observed=True)["count"].sum()
    rows: list[dict[str, object]] = []
    for user_type in USER_TYPES:
        group = subset[subset["user_type"] == user_type]
        count = stats_row(group["count"].tolist())
        wait = stats_row(group["mean_wait"].tolist())
        service = stats_row(group["mean_service"].tolist())
        system = stats_row(group["mean_system"].tolist())
        p90 = stats_row(group["p90_wait"].tolist())
        observed_pct = (
            float(counts_all.get(user_type, 0)) / float(counts_all.sum()) * 100.0
            if counts_all.sum()
            else 0.0
        )
        rows.append(
            {
                "user_type": user_type,
                "tipo": USER_TYPE_LABELS[user_type],
                "replicas": count["n"],
                "promedio_usuarios": count["mean"],
                "desv_usuarios": count["std"],
                "usuarios_ic95_inf": count["ci_low"],
                "usuarios_ic95_sup": count["ci_high"],
                "minimo": count["min"],
                "maximo": count["max"],
                "porcentaje_observado": observed_pct,
                "porcentaje_esperado": TYPE_PROB[user_type] * 100.0,
                "diferencia_pp": observed_pct - TYPE_PROB[user_type] * 100.0,
                "promedio_por_cajero": count["mean"] / num_tellers,
                "servicio_prom": service["mean"],
                "espera_prom": wait["mean"],
                "espera_ic95_inf": wait["ci_low"],
                "espera_ic95_sup": wait["ci_high"],
                "espera_p90": p90["mean"],
                "sistema_prom": system["mean"],
            }
        )

    table = pd.DataFrame(rows)

    observed = np.array([float(counts_all.get(t, 0)) for t in USER_TYPES])
    probabilities = np.array([TYPE_PROB[t] for t in USER_TYPES])
    expected = probabilities * observed.sum()
    valid = np.all(expected >= 5)
    if valid:
        statistic, p_value = stats.chisquare(observed, f_exp=expected)
    else:
        statistic, p_value = float("nan"), float("nan")
    test = {
        "prueba": "Chi-cuadrado de bondad de ajuste",
        "chi2": float(statistic),
        "gl": len(USER_TYPES) - 1,
        "p_value": float(p_value),
        "total_observado": int(observed.sum()),
        "composicion_observada_pct": {
            t: float(o / observed.sum() * 100.0) for t, o in zip(USER_TYPES, observed)
        },
        "composicion_esperada_pct": {
            t: float(p * 100.0) for t, p in zip(USER_TYPES, probabilities)
        },
        "interpretacion": (
            "La composición observada no difiere significativamente de la "
            "esperada 25/20/27.5/27.5 (p > 0.05)."
            if p_value > 0.05
            else "La composición observada difiere de la esperada (p <= 0.05)."
        ),
    }

    by_teller = build_type_teller_table(customer_df, scenario)
    return table.round(4), test, by_teller


def build_type_teller_table(
    customer_df: pd.DataFrame,
    scenario: str = MAIN_SCENARIO,
) -> pd.DataFrame:
    """Promedio por réplica de usuarios y servicio por cajero y tipo."""
    subset = customer_df[customer_df["scenario"] == scenario]
    if subset.empty:
        return pd.DataFrame()
    per_replica = (
        subset.groupby(
            ["replica", "teller", "teller_label", "user_type", "user_type_label"],
            observed=True,
        )
        .agg(
            count=("customer_id", "size"),
            mean_service=("service_time", "mean"),
            mean_wait=("wait_time", "mean"),
        )
        .reset_index()
    )
    summary = summarize_metrics(
        per_replica,
        ["teller", "teller_label", "user_type", "user_type_label"],
        ("count", "mean_service", "mean_wait"),
    )
    if summary.empty:
        return summary
    wide = summary.pivot_table(
        index=["teller", "teller_label", "user_type", "user_type_label"],
        columns="metric",
        values="mean",
    ).reset_index()
    wide.columns.name = None
    wide = wide.rename(
        columns={
            "count": "usuarios_prom_por_replica",
            "mean_service": "servicio_prom",
            "mean_wait": "espera_prom",
        }
    )
    order = {t: i for i, t in enumerate(USER_TYPES)}
    wide["_orden"] = wide["user_type"].map(order)
    wide = wide.sort_values(["teller", "_orden"]).drop(columns=["_orden"])
    return wide.round(4)


# ----------------------------------------------------------------------
# Punto C: estrategia de mejora
# ----------------------------------------------------------------------
def build_point3_tables(
    summary_global: pd.DataFrame,
    metadata: dict[str, object],
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, object]]:
    """Criterios, comparación de escenarios y decisión recomendada."""
    scenarios_meta = metadata.get("scenarios", {})
    if not isinstance(scenarios_meta, dict):
        return pd.DataFrame(), pd.DataFrame(), {}

    keys = list(scenarios_meta)
    criteria_rows: list[dict[str, object]] = []
    comparison_rows: list[dict[str, object]] = []

    for key in keys:
        info = scenarios_meta[key]
        label = str(info.get("label", key))
        num_tellers = int(info.get("num_tellers", 0))
        policy = str(info.get("policy_label", ""))
        values = {
            "mean_wait": summary_metric(summary_global, key, "mean_wait"),
            "mean_system": summary_metric(summary_global, key, "mean_system"),
            "Lq": summary_metric(summary_global, key, "Lq"),
            "L": summary_metric(summary_global, key, "L"),
            "max_teller_utilization": summary_metric(
                summary_global, key, "max_teller_utilization"
            ),
            "frac_wait_gt_5": summary_metric(summary_global, key, "frac_wait_gt_5"),
        }
        evaluation = evaluate_criteria(values)

        criteria = [
            (
                "Tiempo promedio en cola (Wq)",
                "mean_wait",
                CRITERIA["espera_cola_aceptable_min"],
                "min",
            ),
            (
                "Tiempo promedio en el sistema (W)",
                "mean_system",
                CRITERIA["espera_sistema_critica_min"],
                "min",
            ),
            (
                "Longitud promedio de la cola (Lq)",
                "Lq",
                CRITERIA["cola_maxima_aceptable"],
                "min",
            ),
            (
                "Utilización máxima de un cajero",
                "max_teller_utilization",
                CRITERIA["utilizacion_maxima"],
                "min",
            ),
            (
                "Probabilidad de esperar más de 5 min",
                "frac_wait_gt_5",
                CRITERIA["prob_espera_5_max"],
                "min",
            ),
        ]
        for name, metric, threshold, direction in criteria:
            value = float(values[metric])
            complies = value <= threshold
            criteria_rows.append(
                {
                    "scenario": key,
                    "escenario_etiqueta": label,
                    "cajeros": num_tellers,
                    "politica": policy,
                    "criterio": name,
                    "metrica": metric,
                    "valor": round(value, 4),
                    "umbral": threshold,
                    "cumple": bool(complies),
                }
            )

        comparison_rows.append(
            {
                "scenario": key,
                "escenario_etiqueta": label,
                "politica": policy,
                "cajeros": num_tellers,
                "espera_cola_prom": round(float(values["mean_wait"]), 4),
                "espera_sistema_prom": round(float(values["mean_system"]), 4),
                "cola_prom": round(float(values["Lq"]), 4),
                "sistema_prom": round(float(values["L"]), 4),
                "utilizacion_max": round(
                    float(values["max_teller_utilization"]), 4
                ),
                "prob_espera_mayor_5": round(float(values["frac_wait_gt_5"]), 4),
                "cumple_servicio": bool(evaluation["cumple_servicio"]),
                "utilizacion_en_rango_eficiente": bool(
                    evaluation["utilizacion_en_rango_eficiente"]
                ),
                "sobrecapacidad": bool(evaluation["sobrecapacidad"]),
            }
        )

    comparison = pd.DataFrame(comparison_rows)
    comparison = comparison.sort_values(
        ["cumple_servicio", "espera_cola_prom", "cajeros"],
        ascending=[False, True, True],
    ).reset_index(drop=True)
    comparison["ranking"] = np.arange(1, len(comparison) + 1)

    decision = _build_decision(comparison, criteria_rows, scenarios_meta)
    comparison["recomendado"] = comparison["scenario"] == decision["recomendado"]

    criteria_df = pd.DataFrame(criteria_rows)
    return criteria_df.round(4), comparison.round(4), decision


def _evaluation_for(comparison: pd.DataFrame, scenario: str) -> dict[str, object]:
    row = comparison[comparison["scenario"] == scenario]
    if row.empty:
        return {"cumple_servicio": False}
    r = row.iloc[0]
    return evaluate_criteria(
        {
            "mean_wait": float(r["espera_cola_prom"]),
            "mean_system": float(r["espera_sistema_prom"]),
            "Lq": float(r["cola_prom"]),
            "max_teller_utilization": float(r["utilizacion_max"]),
            "frac_wait_gt_5": float(r["prob_espera_mayor_5"]),
        }
    )


def _build_decision(
    comparison: pd.DataFrame,
    criteria_rows: list[dict[str, object]],
    scenarios_meta: dict[str, object],
) -> dict[str, object]:
    """Aplica una regla de decisión explícita y costo-efectiva."""
    current_key = MAIN_SCENARIO
    current = comparison[comparison["scenario"] == current_key].iloc[0]
    current_eval = _evaluation_for(comparison, current_key)
    current_ok = bool(current_eval["cumple_servicio"])
    failures = [
        row["criterio"]
        for row in criteria_rows
        if row["scenario"] == current_key and not row["cumple"]
    ]

    same_size = comparison[
        (comparison["cajeros"] == int(current["cajeros"]))
        & (comparison["scenario"] != current_key)
        & (comparison["cumple_servicio"])
    ].sort_values("espera_cola_prom")
    larger = comparison[
        (comparison["cajeros"] > int(current["cajeros"]))
        & (comparison["cumple_servicio"])
    ].sort_values(["espera_cola_prom", "cajeros"])

    if current_ok:
        recommended = current
        reason = (
            "La configuración actual ya cumple todos los criterios de servicio; "
            "no se justifica agregar cajeros ni cambiar la operación."
        )
        cambio = "Ninguno"
    elif not same_size.empty:
        recommended = same_size.iloc[0]
        reason = (
            "La configuración actual no cumple todos los criterios, pero con "
            "los mismos tres cajeros existe una alternativa que sí cumple: "
            f"{recommended['escenario_etiqueta']}. Por eso no es necesario "
            "instalar cajeros adicionales; se cambia la política de filas."
        )
        cambio = "Política de filas"
    elif not larger.empty:
        recommended = larger.iloc[0]
        reason = (
            "Ninguna alternativa con tres cajeros cumple los criterios; se "
            "recomienda la configuración que cumple con el menor número de "
            "cajeros adicionales."
        )
        cambio = "Capacidad y política de filas"
    else:
        recommended = comparison.sort_values("espera_cola_prom").iloc[0]
        reason = (
            "Ningún escenario cumple todos los criterios; se muestra el de "
            "menor espera, pero la decisión exige revisar la demanda o los "
            "criterios."
        )
        cambio = "Revisión del sistema"

    # Opción de menor costo que cumple: menos cajeros y, a igualdad, menor Wq.
    compliant = comparison[comparison["cumple_servicio"]].copy()
    cheapest = None
    if not compliant.empty:
        cheapest_row = compliant.sort_values(
            ["cajeros", "espera_cola_prom"]
        ).iloc[0]
        cheapest = {
            "scenario": cheapest_row["scenario"],
            "etiqueta": cheapest_row["escenario_etiqueta"],
            "cajeros": int(cheapest_row["cajeros"]),
            "espera_cola_prom": float(cheapest_row["espera_cola_prom"]),
            "politica": cheapest_row["politica"],
        }

    best = comparison.sort_values("espera_cola_prom").iloc[0]
    new_tellers = int(recommended["cajeros"]) - int(current["cajeros"])

    justification = (
        f"Con la configuración actual ({int(current['cajeros'])} cajeros, "
        f"{current['politica']}) la espera promedio en cola es "
        f"{float(current['espera_cola_prom']):.2f} min, el tiempo en el "
        f"sistema es {float(current['espera_sistema_prom']):.2f} min y "
        f"{float(current['prob_espera_mayor_5']):.1%} de los usuarios espera "
        f"más de 5 min. "
        + (
            "Cumple todos los criterios."
            if current_ok
            else "Incumple: " + ", ".join(failures) + ". "
        )
        + f"La recomendación es '{recommended['escenario_etiqueta']}': "
        f"espera en cola {float(recommended['espera_cola_prom']):.2f} min, "
        f"tiempo en el sistema {float(recommended['espera_sistema_prom']):.2f} "
        f"min y {float(recommended['prob_espera_mayor_5']):.1%} de usuarios "
        f"con espera mayor a 5 min. "
        + reason
    )

    return {
        "criterios": dict(CRITERIA),
        "recomendado": str(recommended["scenario"]),
        "recomendado_etiqueta": str(recommended["escenario_etiqueta"]),
        "cajeros_recomendados": int(recommended["cajeros"]),
        "nuevos_cajeros": new_tellers,
        "politica_recomendada": str(recommended["politica"]),
        "tipo_de_cambio": cambio,
        "configuracion_actual_cumple": current_ok,
        "criterios_incumplidos_actual": failures,
        "espera_cola_actual": round(float(current["espera_cola_prom"]), 4),
        "espera_cola_recomendada": round(
            float(recommended["espera_cola_prom"]), 4
        ),
        "espera_sistema_recomendada": round(
            float(recommended["espera_sistema_prom"]), 4
        ),
        "prob_espera_mayor_5_recomendada": round(
            float(recommended["prob_espera_mayor_5"]), 4
        ),
        "mejor_desempeno": {
            "scenario": str(best["scenario"]),
            "etiqueta": str(best["escenario_etiqueta"]),
            "cajeros": int(best["cajeros"]),
            "espera_cola_prom": round(float(best["espera_cola_prom"]), 4),
            "nota": (
                "Es el escenario de menor espera, pero puede requerir más "
                "cajeros o una reorganización de la operación."
            ),
        },
        "opcion_de_menor_costo_que_cumple": cheapest,
        "justificacion": justification,
    }


# ----------------------------------------------------------------------
# Punto D: verificación, calibración y validación
# ----------------------------------------------------------------------
def build_verification_table(
    customer_df: pd.DataFrame,
    replica_df: pd.DataFrame,
    metadata: dict[str, object],
) -> pd.DataFrame:
    """Pruebas de verificación que se pueden calcular con los datos crudos."""
    rows: list[dict[str, object]] = []

    def add(name: str, ok: bool, detail: str) -> None:
        rows.append(
            {
                "prueba": name,
                "resultado": "Cumple" if ok else "No cumple",
                "detalle": detail,
                "estado": ok,
            }
        )

    key = ["scenario", "replica", "customer_id"]
    duplicated = int(customer_df.duplicated(key).sum()) if not customer_df.empty else 0
    add(
        "Identificadores únicos por escenario y réplica",
        duplicated == 0,
        f"{duplicated} duplicados encontrados.",
    )

    served = bool(
        customer_df["service_start"].notna().all()
        and customer_df["service_end"].notna().all()
    )
    add(
        "Todos los usuarios que llegan terminan su servicio (drenaje)",
        served,
        f"{len(customer_df)} registros con inicio y fin de servicio.",
    )

    start_ok = bool(
        (customer_df["service_start"] >= customer_df["arrival_time"] - 1e-9).all()
    )
    add(
        "El servicio nunca inicia antes de la llegada",
        start_ok,
        f"Violaciones: {int((customer_df['service_start'] < customer_df['arrival_time'] - 1e-9).sum())}.",
    )

    end_ok = bool(
        (customer_df["service_end"] >= customer_df["service_start"] - 1e-9).all()
    )
    add(
        "El servicio termina después de iniciar",
        end_ok,
        f"Violaciones: {int((customer_df['service_end'] < customer_df['service_start'] - 1e-9).sum())}.",
    )

    positive = bool(
        (customer_df["service_time"] > 0).all()
        and (customer_df["wait_time"] >= -1e-9).all()
    )
    add(
        "Tiempos de servicio positivos y esperas no negativas",
        positive,
        "Se verifican todas las filas de clientes.",
    )

    teller_ok = True
    for scenario, info in metadata.get("scenarios", {}).items():  # type: ignore[union-attr]
        num_tellers = int(info.get("num_tellers", 0))
        subset = customer_df[
            (customer_df["scenario"] == scenario) & customer_df["teller"].notna()
        ]
        if not subset.empty and (
            (subset["teller"] < 0).any() or (subset["teller"] >= num_tellers).any()
        ):
            teller_ok = False
    add(
        "Cada usuario es atendido por un cajero válido y solo uno",
        teller_ok,
        "No hay usuarios con más de un cajero ni cajeros fuera de rango.",
    )

    util = replica_df["utilization"].astype(float)
    util_ok = bool(((util >= 0) & (util <= 1)).all())
    add(
        "Utilización de cada cajero en [0, 1]",
        util_ok,
        f"Rango observado: [{util.min():.3f}, {util.max():.3f}].",
    )

    area_ok = bool((replica_df["Lq"] >= 0).all() and (replica_df["L"] >= 0).all())
    add(
        "Longitudes promedio de cola y sistema no negativas",
        area_ok,
        "Integración temporal sobre la ventana de estado estable.",
    )

    conservation_ok = True
    for (scenario, replica), group in customer_df.groupby(
        ["scenario", "replica"], observed=True
    ):
        ids = group["customer_id"].to_numpy()
        if len(ids) != int(ids.max()) + 1 or ids.min() != 0:
            conservation_ok = False
            break
    add(
        "Conservación de usuarios (sin pérdidas ni duplicados)",
        conservation_ok,
        "Los identificadores consecutivos cubren todas las llegadas.",
    )

    return pd.DataFrame(rows)


def build_calibration_tables(
    calibration_customer_df: pd.DataFrame,
    replica_df: pd.DataFrame,
    metadata: dict[str, object],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Calibración de las distribuciones y de la tasa de llegadas.

    ``calibration_customer_df`` contiene los tiempos de servicio observados
    (por ejemplo, todos los clientes de la configuración actual).  La
    estimación de cada media es el estimador de máxima verosimilitud de la
    exponencial (la media muestral).  La prueba KS contrasta la muestra con
    una exponencial de media nominal.
    """
    service_rows: list[dict[str, object]] = []
    for user_type in USER_TYPES:
        sample = calibration_customer_df.loc[
            calibration_customer_df["user_type"] == user_type, "service_time"
        ].to_numpy(dtype=float)
        nominal = SERVICE_MEAN_MIN[user_type]
        if len(sample) < 2:
            continue
        estimated = float(np.mean(sample))
        ks_stat, ks_p = stats.kstest(sample, "expon", args=(0.0, nominal))
        service_rows.append(
            {
                "parametro": f"Tiempo de servicio - {USER_TYPE_LABELS[user_type]}",
                "nominal_min": nominal,
                "estimado_min": round(estimated, 4),
                "error_relativo_pct": round((estimated - nominal) / nominal * 100.0, 2),
                "n": len(sample),
                "ks_estadistico": round(float(ks_stat), 4),
                "ks_p_value": round(float(ks_p), 4),
                "ajuste_exponencial": bool(ks_p > 0.05),
            }
        )

    service_table = pd.DataFrame(service_rows)

    main = replica_df[replica_df["scenario"] == MAIN_SCENARIO]
    window = float(metadata.get("stable_window_min", 0.0))
    if not main.empty and window > 0:
        rates = (main["total_customers"].astype(float) / window).tolist()
        rate_stats = stats_row(rates)
        nominal_rate = 1.0 / mean_interarrival_min()
        arrival_table = pd.DataFrame(
            [
                {
                    "parametro": "Tasa de llegadas (λ)",
                    "nominal_por_min": round(nominal_rate, 4),
                    "estimado_por_min": round(rate_stats["mean"], 4),
                    "error_relativo_pct": round(
                        (rate_stats["mean"] - nominal_rate) / nominal_rate * 100.0,
                        2,
                    ),
                    "ic95_inf": round(rate_stats["ci_low"], 4),
                    "ic95_sup": round(rate_stats["ci_high"], 4),
                    "n_replicas": int(rate_stats["n"]),
                }
            ]
        )
    else:
        arrival_table = pd.DataFrame()
    return service_table, arrival_table


def build_validation_tables(
    validation_results: Sequence[dict[str, object]],
    teller_df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Compara la simulación con la teoría M/M/1 y la aproximación M/G/1."""
    rows: list[dict[str, object]] = []
    for result in validation_results:
        user_type = str(result["user_type"])
        theory = result["theory"]
        replica_rows = pd.DataFrame(result["rows"])
        for metric, theory_key, label in (
            ("mean_system", "W", "Tiempo en el sistema (W)"),
            ("mean_wait", "Wq", "Tiempo en cola (Wq)"),
            ("L", "L", "Usuarios en el sistema (L)"),
            ("Lq", "Lq", "Usuarios en cola (Lq)"),
        ):
            simulated = stats_row(replica_rows[metric].tolist())
            theoretical = float(theory[theory_key])
            if not np.isfinite(theoretical):
                rows.append(
                    {
                        "tipo": USER_TYPE_LABELS[user_type],
                        "metrica": label,
                        "teorico": float("inf"),
                        "simulado": round(simulated["mean"], 4),
                        "ic95_inf": round(simulated["ci_low"], 4),
                        "ic95_sup": round(simulated["ci_high"], 4),
                        "error_relativo_pct": float("nan"),
                        "p_value": float("nan"),
                        "validado": False,
                        "nota": "Sistema crítico (rho = 1): la teoría no es finita.",
                    }
                )
                continue
            error = (
                (simulated["mean"] - theoretical) / theoretical * 100.0
                if theoretical
                else float("nan")
            )
            if metric == "mean_system":
                _, p_value = stats.ttest_1samp(
                    replica_rows[metric].to_numpy(), theoretical
                )
            elif metric == "mean_wait":
                _, p_value = stats.ttest_1samp(
                    replica_rows[metric].to_numpy(), theoretical
                )
            else:
                p_value = float("nan")
            validated = abs(error) <= 10.0
            rows.append(
                {
                    "tipo": USER_TYPE_LABELS[user_type],
                    "metrica": label,
                    "teorico": round(theoretical, 4),
                    "simulado": round(simulated["mean"], 4),
                    "ic95_inf": round(simulated["ci_low"], 4),
                    "ic95_sup": round(simulated["ci_high"], 4),
                    "error_relativo_pct": round(float(error), 2),
                    "p_value": (
                        round(float(p_value), 4) if np.isfinite(p_value) else float("nan")
                    ),
                    "validado": bool(validated),
                    "nota": "",
                }
            )
    type_table = pd.DataFrame(rows)

    main_tellers = teller_df[teller_df["scenario"] == MAIN_SCENARIO]
    theory = theoretical_mg1_per_teller(3)
    aggregate_rows: list[dict[str, object]] = []
    for metric, theory_key, label in (
        ("mean_wait", "Wq", "Tiempo en cola (Wq)"),
        ("mean_system", "W", "Tiempo en el sistema (W)"),
        ("mean_queue_length", "Lq", "Usuarios en cola (Lq)"),
    ):
        simulated = stats_row(main_tellers[metric].tolist())
        theoretical = float(theory[theory_key])
        error = (
            (simulated["mean"] - theoretical) / theoretical * 100.0
            if theoretical
            else float("nan")
        )
        aggregate_rows.append(
            {
                "metrica": label,
                "teorico_mg1": round(theoretical, 4),
                "simulado": round(simulated["mean"], 4),
                "ic95_inf": round(simulated["ci_low"], 4),
                "ic95_sup": round(simulated["ci_high"], 4),
                "error_relativo_pct": round(float(error), 2),
                "validado": bool(abs(error) <= 15.0),
                "nota": (
                    "Aproximación M/G/1 con servicio hiperexponencial; "
                    "se acepta un error de hasta 15 %."
                ),
            }
        )
    aggregate_table = pd.DataFrame(aggregate_rows)
    return type_table, aggregate_table


# ----------------------------------------------------------------------
# Punto E: eliminación del estado transitorio
# ----------------------------------------------------------------------
def build_point5_table(
    pilot: dict[str, object],
    before_rows: pd.DataFrame,
    after_rows: pd.DataFrame,
    *,
    scenario: str = MAIN_SCENARIO,
) -> tuple[pd.DataFrame, dict[str, object]]:
    """Compara las estadísticas antes y después de eliminar el transitorio."""
    cut = float(pilot["cut_min"])
    series = np.asarray(pilot["series"], dtype=float)
    first_block = float(np.mean(series[: int(cut)])) if cut > 0 else float("nan")
    after_block = float(np.mean(series[int(cut) :]))
    all_block = float(np.mean(series))

    before = before_rows[before_rows["scenario"] == scenario]
    after = after_rows[after_rows["scenario"] == scenario]
    if before.empty or after.empty:
        return pd.DataFrame(), {}

    def mean_of(df: pd.DataFrame, column: str) -> float:
        return float(df[column].astype(float).mean())

    def ci_of(df: pd.DataFrame, column: str) -> tuple[float, float]:
        summary = stats_row(df[column].tolist())
        return float(summary["ci_low"]), float(summary["ci_high"])

    rows: list[dict[str, object]] = [
        {
            "metrica": f"N(t): primeros {cut:.0f} min",
            "antes": round(first_block, 4),
            "despues": round(after_block, 4),
            "diferencia": round(after_block - first_block, 4),
            "cambio_pct": (
                round((after_block - first_block) / first_block * 100.0, 2)
                if first_block
                else float("nan")
            ),
            "ic95_despues_inf": float("nan"),
            "ic95_despues_sup": float("nan"),
        },
        {
            "metrica": "N(t): horizonte completo",
            "antes": round(all_block, 4),
            "despues": round(after_block, 4),
            "diferencia": round(after_block - all_block, 4),
            "cambio_pct": (
                round((after_block - all_block) / all_block * 100.0, 2)
                if all_block
                else float("nan")
            ),
            "ic95_despues_inf": float("nan"),
            "ic95_despues_sup": float("nan"),
        },
    ]

    for metric, label in (
        ("mean_wait", "Tiempo promedio en cola (Wq, min)"),
        ("mean_system", "Tiempo promedio en el sistema (W, min)"),
        ("Lq", "Longitud promedio de la cola (Lq)"),
        ("L", "Usuarios promedio en el sistema (L)"),
        ("mean_service", "Tiempo promedio de servicio (min)"),
    ):
        before_mean = mean_of(before, metric)
        after_mean = mean_of(after, metric)
        ci_low, ci_high = ci_of(after, metric)
        rows.append(
            {
                "metrica": label,
                "antes": round(before_mean, 4),
                "despues": round(after_mean, 4),
                "diferencia": round(after_mean - before_mean, 4),
                "cambio_pct": (
                    round((after_mean - before_mean) / before_mean * 100.0, 2)
                    if before_mean
                    else float("nan")
                ),
                "ic95_despues_inf": round(ci_low, 4),
                "ic95_despues_sup": round(ci_high, 4),
            }
        )

    table = pd.DataFrame(rows)
    summary = {
        "calentamiento_min": round(cut, 2),
        "ventana_estable_min": round(float(pilot["duration_min"]) - cut, 2),
        "ventana_promedio_movil_min": int(pilot["window"]),
        "referencia_n": round(float(pilot["reference_mean"]), 4),
        "tolerancia": round(float(pilot["tolerance"]), 4),
        "n_todo": round(all_block, 4),
        "n_primer_bloque": round(first_block, 4),
        "n_despues": round(after_block, 4),
        "sesgo_inicial_pct": (
            round((all_block - after_block) / after_block * 100.0, 2)
            if after_block
            else float("nan")
        ),
    }
    return table, summary


# ----------------------------------------------------------------------
# Empaquetado
# ----------------------------------------------------------------------
@dataclass
class AnalysisBundle:
    """Tablas, pruebas y decisiones listas para el documento."""

    resumen_global: pd.DataFrame
    resumen_cajeros: pd.DataFrame
    resumen_tipos: pd.DataFrame
    tipos_por_replica: pd.DataFrame
    punto1: pd.DataFrame
    punto1_prueba: dict[str, object]
    punto2: pd.DataFrame
    punto2_prueba: dict[str, object]
    punto2_por_cajero: pd.DataFrame
    punto3_criterios: pd.DataFrame
    punto3_comparacion: pd.DataFrame
    punto3_decision: dict[str, object]
    punto4_verificacion: pd.DataFrame
    punto4_calibracion_servicio: pd.DataFrame
    punto4_calibracion_llegadas: pd.DataFrame
    punto4_validacion_tipos: pd.DataFrame
    punto4_validacion_agregada: pd.DataFrame
    punto5: pd.DataFrame
    punto5_resumen: dict[str, object]

    def decisions_json(self) -> str:
        return json.dumps(
            {
                "punto1_prueba": self.punto1_prueba,
                "punto2_prueba": self.punto2_prueba,
                "punto3_decision": self.punto3_decision,
                "punto5_resumen": self.punto5_resumen,
            },
            indent=2,
            ensure_ascii=False,
        )
