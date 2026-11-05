"""Simulación, métricas de prevención y análisis de riesgo de incendios.

Este módulo combina el HMM con variables físicas observables (humedad
relativa) para producir un informe operativo útil para brigadas forestales.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

import numpy as np

from .hmm_model import HMM

# Rangos de humedad relativa (%) asociados a cada observación.
HUMIDITY_RANGES: tuple[tuple[float, float], ...] = (
    (60.0, 100.0),  # Humedad Alta
    (30.0, 60.0),  # Humedad Media
    (0.0, 30.0),  # Humedad Baja
)

# Colores para gráficos y tablas: verde, ámbar y rojo.
STATE_COLORS: tuple[str, ...] = ("#2e7d32", "#f9a825", "#c62828")

# Factor de peligro asociado a cada estado para la probabilidad de ignición.
FIRE_STATE_FACTORS: np.ndarray = np.array([0.50, 1.20, 2.00], dtype=float)


@dataclass
class SeasonSimulation:
    """Resultado completo de una temporada simulada."""

    model: HMM
    days: np.ndarray
    true_states: np.ndarray
    observations: np.ndarray
    humidity: np.ndarray
    inferred_states: np.ndarray
    posterior: np.ndarray
    danger_index: np.ndarray
    fire_events: np.ndarray
    alerts: list[dict[str, object]] = field(default_factory=list)
    seed: int | None = None

    @property
    def n_days(self) -> int:
        return len(self.days)

    @property
    def true_state_names(self) -> np.ndarray:
        return np.array([self.model.states[i] for i in self.true_states])

    @property
    def inferred_state_names(self) -> np.ndarray:
        return np.array([self.model.states[i] for i in self.inferred_states])

    @property
    def observation_names(self) -> np.ndarray:
        return np.array([self.model.observations[i] for i in self.observations])


def sample_humidity(
    observation_indices: np.ndarray,
    rng: np.random.Generator,
) -> np.ndarray:
    """Convierte categorías de humedad en valores reales de humedad (%).

    Alta: 60-100 %, Media: 30-60 %, Baja: 0-30 %.
    """
    indices = np.asarray(observation_indices, dtype=int)
    if np.any(indices < 0) or np.any(indices >= len(HUMIDITY_RANGES)):
        raise ValueError("Hay índices de observación de humedad fuera de rango.")

    lows = np.array([limit[0] for limit in HUMIDITY_RANGES])[indices]
    highs = np.array([limit[1] for limit in HUMIDITY_RANGES])[indices]
    return rng.uniform(lows, highs)


def simulate_fire_events(
    states: np.ndarray,
    humidity: np.ndarray,
    rng: np.random.Generator,
    base_probability: float = 0.004,
    dryness_weight: float = 0.16,
) -> np.ndarray:
    """Simula posibles focos de incendio con probabilidad dependiente del riesgo.

    La probabilidad aumenta cuando la humedad es baja y cuando el estado
    oculto es más peligroso. No representa incendios confirmados, sino
    posibles focos compatibles con las condiciones simuladas.
    """
    states = np.asarray(states, dtype=int)
    humidity = np.asarray(humidity, dtype=float)

    dryness = np.clip(1.0 - humidity / 100.0, 0.0, 1.0)
    factors = FIRE_STATE_FACTORS[states]
    probabilities = base_probability + dryness_weight * (dryness**2) * factors
    probabilities = np.clip(probabilities, 0.0, 0.40)

    return rng.random(len(states)) < probabilities


def generate_burn_ban_alerts(
    days: np.ndarray,
    states: np.ndarray,
    danger_index: np.ndarray,
    danger_threshold: float = 75.0,
) -> list[dict[str, object]]:
    """Genera alertas de prohibición o restricción de quemas.

    El estado inferido de riesgo extremo activa prohibición total. Un índice
    de peligro alto sin estado extremo activa una restricción preventiva.
    """
    alerts: list[dict[str, object]] = []

    for day, state, index in zip(days, states, danger_index):
        if int(state) == 2:
            alerts.append(
                {
                    "day": int(day),
                    "level": "PROHIBICIÓN TOTAL",
                    "danger_index": float(index),
                    "message": (
                        f"Día {int(day)}: PROHIBIDA cualquier quema. "
                        f"Riesgo extremo inferido (índice {index:.1f}/100)."
                    ),
                }
            )
        elif index >= danger_threshold:
            alerts.append(
                {
                    "day": int(day),
                    "level": "RESTRICCIÓN PREVENTIVA",
                    "danger_index": float(index),
                    "message": (
                        f"Día {int(day)}: restricción preventiva de quemas. "
                        f"Índice de peligro {index:.1f}/100."
                    ),
                }
            )

    return alerts


def run_simulation(
    model: HMM | None = None,
    n_days: int = 120,
    seed: int | None = 42,
    alert_threshold: float = 75.0,
) -> SeasonSimulation:
    """Ejecuta una temporada completa de simulación y decodificación."""
    if n_days <= 0:
        raise ValueError("n_days debe ser mayor que cero.")

    if model is None:
        model = HMM(seed=seed)

    rng = np.random.default_rng(seed)
    generated = model.simulate(n_days, rng=rng)

    true_states = generated["states"]
    observations = generated["observations"]
    humidity = sample_humidity(observations, rng)
    fire_events = simulate_fire_events(true_states, humidity, rng)

    inferred_states = model.viterbi(observations)
    posterior = model.forward_backward(observations)
    danger_index = model.danger_index(posterior)

    days = np.arange(1, n_days + 1)
    alerts = generate_burn_ban_alerts(
        days, inferred_states, danger_index, danger_threshold=alert_threshold
    )

    return SeasonSimulation(
        model=model,
        days=days,
        true_states=true_states,
        observations=observations,
        humidity=humidity,
        inferred_states=inferred_states,
        posterior=posterior,
        danger_index=danger_index,
        fire_events=fire_events,
        alerts=alerts,
        seed=seed,
    )


def risk_counts(states: np.ndarray, model: HMM) -> dict[str, int]:
    """Cuenta los días de cada nivel de riesgo."""
    counts = np.bincount(np.asarray(states, dtype=int), minlength=model.n_states)
    return {name: int(counts[i]) for i, name in enumerate(model.states)}


def find_runs(values: np.ndarray, target: int) -> list[tuple[int, int]]:
    """Devuelve intervalos (inicio, fin) inclusivos, en índices 0-based."""
    values = np.asarray(values, dtype=int)
    runs: list[tuple[int, int]] = []
    start: int | None = None

    for index, value in enumerate(values):
        if value == target and start is None:
            start = index
        elif value != target and start is not None:
            runs.append((start, index - 1))
            start = None

    if start is not None:
        runs.append((start, len(values) - 1))

    return runs


def extreme_windows(
    states: np.ndarray,
    min_length: int = 2,
) -> list[dict[str, int]]:
    """Identifica ventanas continuas de riesgo extremo.

    Parameters
    ----------
    states:
        Secuencia de índices de estado.
    min_length:
        Longitud mínima para considerar que el peligro es "continuado".
    """
    windows: list[dict[str, int]] = []
    for start, end in find_runs(states, target=2):
        length = end - start + 1
        if length >= min_length:
            windows.append(
                {
                    "start_day": start + 1,
                    "end_day": end + 1,
                    "length": length,
                }
            )
    return windows


def empirical_transition_to_extreme(states: np.ndarray) -> dict[str, object]:
    """Estima empíricamente P(S_t = Extremo | S_{t-1} ≠ Extremo)."""
    states = np.asarray(states, dtype=int)
    by_source: dict[str, dict[str, float | int]] = {}

    for source in range(2):
        mask = states[:-1] == source
        opportunities = int(mask.sum())
        entries = int(np.sum(mask & (states[1:] == 2)))
        by_source[str(source)] = {
            "opportunities": opportunities,
            "entries_to_extreme": entries,
            "probability": entries / opportunities if opportunities else float("nan"),
        }

    non_extreme_previous = states[:-1] != 2
    opportunities = int(non_extreme_previous.sum())
    entries = int(np.sum(non_extreme_previous & (states[1:] == 2)))

    return {
        "overall_probability": entries / opportunities if opportunities else float("nan"),
        "entries_to_extreme": entries,
        "opportunities": opportunities,
        "by_source": by_source,
    }


def compare_states(
    true_states: np.ndarray,
    inferred_states: np.ndarray,
    model: HMM,
) -> dict[str, object]:
    """Compara estados reales e inferidos con exactitud y matriz de confusión."""
    true_states = np.asarray(true_states, dtype=int)
    inferred_states = np.asarray(inferred_states, dtype=int)

    if len(true_states) != len(inferred_states):
        raise ValueError("Las secuencias deben tener la misma longitud.")

    confusion = np.zeros((model.n_states, model.n_states), dtype=int)
    np.add.at(confusion, (true_states, inferred_states), 1)

    accuracy = float(np.mean(true_states == inferred_states))

    return {
        "accuracy": accuracy,
        "confusion_matrix": confusion,
        "correct_days": int(np.sum(true_states == inferred_states)),
        "total_days": int(len(true_states)),
    }


def _point_biserial_correlation(
    values: np.ndarray,
    events: np.ndarray,
) -> float:
    """Correlación de Pearson entre una variable continua y un evento binario."""
    values = np.asarray(values, dtype=float)
    events = np.asarray(events, dtype=float)

    if len(values) < 2:
        return float("nan")
    if np.std(values) == 0 or np.std(events) == 0:
        return float("nan")

    return float(np.corrcoef(values, events)[0, 1])


def humidity_fire_analysis(sim: SeasonSimulation) -> dict[str, object]:
    """Analiza la relación entre humedad, riesgo e incendios simulados."""
    events = sim.fire_events.astype(float)

    correlation = _point_biserial_correlation(sim.humidity, events)
    danger_correlation = _point_biserial_correlation(sim.danger_index, events)

    bands: dict[str, dict[str, float | int]] = {}
    for index, name in enumerate(sim.model.observations):
        mask = sim.observations == index
        days = int(mask.sum())
        fires = int(sim.fire_events[mask].sum())
        bands[name] = {
            "days": days,
            "fire_events": fires,
            "event_rate": fires / days if days else 0.0,
            "mean_humidity": (
                float(sim.humidity[mask].mean()) if days else float("nan")
            ),
        }

    low_mask = sim.observations == 2
    low_rate = (
        float(sim.fire_events[low_mask].mean()) if low_mask.any() else float("nan")
    )
    other_rate = (
        float(sim.fire_events[~low_mask].mean())
        if (~low_mask).any()
        else float("nan")
    )

    if np.isnan(low_rate) or np.isnan(other_rate):
        risk_ratio = float("nan")
    elif other_rate == 0:
        risk_ratio = float("inf") if low_rate > 0 else float("nan")
    else:
        risk_ratio = low_rate / other_rate

    return {
        "humidity_event_correlation": correlation,
        "danger_event_correlation": danger_correlation,
        "humidity_bands": bands,
        "low_humidity_event_rate": low_rate,
        "other_humidity_event_rate": other_rate,
        "low_humidity_risk_ratio": risk_ratio,
        "total_fire_events": int(sim.fire_events.sum()),
    }


def group_consecutive_days(days: Iterable[int]) -> list[tuple[int, int]]:
    """Agrupa días consecutivos en intervalos inclusivos."""
    ordered = sorted(set(int(day) for day in days))
    if not ordered:
        return []

    groups: list[tuple[int, int]] = []
    start = previous = ordered[0]

    for day in ordered[1:]:
        if day == previous + 1:
            previous = day
            continue
        groups.append((start, previous))
        start = previous = day

    groups.append((start, previous))
    return groups


def compute_metrics(sim: SeasonSimulation) -> dict[str, object]:
    """Calcula todas las métricas operativas y de validación del modelo."""
    transition_observed = empirical_transition_to_extreme(sim.true_states)
    transition_inferred = empirical_transition_to_extreme(sim.inferred_states)

    if sim.alerts:
        alert_days = [int(alert["day"]) for alert in sim.alerts]
        alert_windows = group_consecutive_days(alert_days)
    else:
        alert_windows = []

    return {
        "risk_counts_true": risk_counts(sim.true_states, sim.model),
        "risk_counts_inferred": risk_counts(sim.inferred_states, sim.model),
        "extreme_windows": extreme_windows(sim.inferred_states, min_length=2),
        "extreme_days_inferred": int(np.sum(sim.inferred_states == 2)),
        "transition_to_extreme_observed": transition_observed,
        "transition_to_extreme_inferred": transition_inferred,
        "model_transition_to_extreme": sim.model.transition_probability_to_extreme(),
        "comparison": compare_states(
            sim.true_states, sim.inferred_states, sim.model
        ),
        "humidity_fire": humidity_fire_analysis(sim),
        "alert_count": len(sim.alerts),
        "burn_ban_days": int(
            sum(alert["level"] == "PROHIBICIÓN TOTAL" for alert in sim.alerts)
        ),
        "restriction_days": int(
            sum(alert["level"] == "RESTRICCIÓN PREVENTIVA" for alert in sim.alerts)
        ),
        "alert_windows": alert_windows,
        "mean_danger_index": float(sim.danger_index.mean()),
        "max_danger_index": float(sim.danger_index.max()),
        "mean_humidity": float(sim.humidity.mean()),
    }
