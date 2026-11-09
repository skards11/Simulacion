"""Experimento D4: comparación de decodificación M0, M1 y M2.

Este módulo implementa el protocolo registrado en ``decisiones.md``:

* T = 500 pasos por secuencia y N = 2000 secuencias sintéticas.
* Diseño pareado: las tres variantes reciben exactamente las mismas
  observaciones y se comparan contra los mismos estados latentes.
* Métrica principal: macro-F1 por secuencia, agregada con media, desviación
  estándar e intervalo de confianza por bootstrap de secuencias.
* Métricas secundarias: recall de ``s3`` (alias "Riesgo Extremo") y exactitud.
* Escenario secundario con la matriz de emisión B alterada.

Las cifras que produzca este módulo son simuladas. No son evidencia de validez
ecológica ni de superioridad general del HMM.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

import numpy as np

from .hmm_model import (
    DEFAULT_EMISSION_MATRIX,
    DEFAULT_INITIAL_PROBABILITIES,
    DEFAULT_TRANSITION_MATRIX,
    HMM,
    OBSERVATIONS,
    STATES,
    stationary_distribution,
)

DEFAULT_T: int = 500
DEFAULT_N: int = 2000
DEFAULT_MASTER_SEED: int = 20261109
DEFAULT_BOOTSTRAP_SAMPLES: int = 1000

MODEL_NAMES: tuple[str, ...] = ("M0", "M1", "M2")
METRIC_NAMES: tuple[str, ...] = ("macro_f1", "recall_s3", "accuracy")

# Mezcla provisional con la distribución uniforme para el escenario de B
# alterada. No es una decisión científica registrada: el valor debe fijarse
# antes de reportar resultados del escenario secundario.
PROVISIONAL_ALTERED_MIXING: float = 0.5


@dataclass
class ExperimentResult:
    """Resultado completo de una corrida del protocolo D4."""

    T: int
    N: int
    master_seed: int
    seeds: np.ndarray
    emission_matrix: np.ndarray
    per_sequence: dict[str, dict[str, np.ndarray]]
    summary: dict[str, dict[str, dict[str, float | None]]]

    def to_dict(self) -> dict[str, object]:
        """Versión serializable (sin objetos numpy) para guardar o imprimir."""
        return {
            "T": self.T,
            "N": self.N,
            "master_seed": self.master_seed,
            "seeds": [int(seed) for seed in self.seeds],
            "emission_matrix": self.emission_matrix.tolist(),
            "summary": self.summary,
        }


# ----------------------------------------------------------------------
# Métricas por secuencia
# ----------------------------------------------------------------------
def macro_f1_score(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    n_classes: int = 3,
) -> float:
    """Macro-F1 con las clases 0..n_classes-1 fijas.

    Si una clase no aparece ni en la verdad ni en la predicción, su F1 es 0.
    Así la métrica no cambia de denominador entre secuencias.
    """
    y_true = np.asarray(y_true, dtype=int)
    y_pred = np.asarray(y_pred, dtype=int)

    if y_true.shape != y_pred.shape:
        raise ValueError("y_true e y_pred deben tener la misma forma.")

    f1_scores: list[float] = []
    for label in range(n_classes):
        true_positive = int(np.sum((y_true == label) & (y_pred == label)))
        false_positive = int(np.sum((y_true != label) & (y_pred == label)))
        false_negative = int(np.sum((y_true == label) & (y_pred != label)))

        precision = (
            true_positive / (true_positive + false_positive)
            if (true_positive + false_positive) > 0
            else 0.0
        )
        recall = (
            true_positive / (true_positive + false_negative)
            if (true_positive + false_negative) > 0
            else 0.0
        )
        f1 = (
            2.0 * precision * recall / (precision + recall)
            if (precision + recall) > 0
            else 0.0
        )
        f1_scores.append(float(f1))

    return float(np.mean(f1_scores))


def recall_score(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    label: int = 2,
) -> float:
    """Recall de una clase concreta."""
    y_true = np.asarray(y_true, dtype=int)
    y_pred = np.asarray(y_pred, dtype=int)

    support = int(np.sum(y_true == label))
    if support == 0:
        return 0.0
    return float(np.sum((y_true == label) & (y_pred == label)) / support)


def accuracy_score(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Exactitud global."""
    y_true = np.asarray(y_true, dtype=int)
    y_pred = np.asarray(y_pred, dtype=int)
    if y_true.shape != y_pred.shape:
        raise ValueError("y_true e y_pred deben tener la misma forma.")
    return float(np.mean(y_true == y_pred))


def compute_sequence_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
) -> dict[str, float]:
    """Calcula las tres métricas de una secuencia."""
    return {
        "macro_f1": macro_f1_score(y_true, y_pred),
        "recall_s3": recall_score(y_true, y_pred, label=2),
        "accuracy": accuracy_score(y_true, y_pred),
    }


# ----------------------------------------------------------------------
# Ley observable exacta (diagnóstico y baseline M1)
# ----------------------------------------------------------------------
def observable_markov_law(
    transition_matrix: np.ndarray,
    emission_matrix: np.ndarray,
    stationary: np.ndarray | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Deriva la ley exacta del proceso observable bajo estacionariedad.

    Returns
    -------
    p_observations:
        P(O = o) = Σ_i ξ_i B[i, o].
    q_observations:
        Q[o, o'] = P(O_{t+1}=o' | O_t=o).
    state_given_observation:
        P(S = i | O = o) bajo ξ.
    """
    A = np.asarray(transition_matrix, dtype=float)
    B = np.asarray(emission_matrix, dtype=float)
    xi = (
        stationary_distribution(A)
        if stationary is None
        else np.asarray(stationary, dtype=float)
    )

    p_observations = xi @ B
    if np.any(p_observations <= 0):
        raise ValueError("La ley observable contiene probabilidades nulas.")
    state_given_observation = (xi[:, None] * B) / p_observations[None, :]

    # P(O_{t+1}=o' | O_t=o) = Σ_i P(S_t=i|O_t=o) Σ_j A_ij B_j,o'
    q_observations = state_given_observation.T @ (A @ B)

    return p_observations, q_observations, state_given_observation


# ----------------------------------------------------------------------
# Decodificadores
# ----------------------------------------------------------------------
def decode_m0(observations: np.ndarray, emission_matrix: np.ndarray) -> np.ndarray:
    """M0: umbral determinista que solo mira la humedad actual.

    Asigna a cada observación el estado con mayor probabilidad en B:
    Alta → s1, Media → s2, Baja → s3 (con las matrices del caso).
    """
    obs = np.asarray(observations, dtype=int)
    mapping = np.argmax(np.asarray(emission_matrix, dtype=float), axis=0)
    return mapping[obs]


def decode_m1(
    observations: np.ndarray,
    transition_matrix: np.ndarray,
    emission_matrix: np.ndarray,
    stationary: np.ndarray | None = None,
) -> np.ndarray:
    """M1: baseline con la ley observable y prior estacionario.

    Para evitar la versión degenerada de una cadena sobre observaciones ya
    conocidas, M1 es el HMM con A, B y la distribución estacionaria ξ de A
    en lugar de π. Al ser el mapeo M0 biyectivo en este caso, esta es la
    forma no degenerada de explotar la ley observable sin usar las etiquetas
    latentes.
    """
    A = np.asarray(transition_matrix, dtype=float)
    B = np.asarray(emission_matrix, dtype=float)
    xi = (
        stationary_distribution(A)
        if stationary is None
        else np.asarray(stationary, dtype=float)
    )

    model = HMM(transition_matrix=A, emission_matrix=B, initial_probabilities=xi)
    posterior = model.forward_backward(observations)
    return np.argmax(posterior, axis=1)


def decode_m2(
    observations: np.ndarray,
    model: HMM,
    decoder: str = "posterior",
) -> np.ndarray:
    """M2: HMM completo con A, B y π.

    ``decoder="posterior"`` usa el argmax de la posterior marginal
    (Forward–Backward). ``decoder="viterbi"`` usa la ruta MAP de Viterbi.
    """
    if decoder == "posterior":
        posterior = model.forward_backward(observations)
        return np.argmax(posterior, axis=1)
    if decoder == "viterbi":
        return model.viterbi(observations)
    raise ValueError("decoder debe ser 'posterior' o 'viterbi'.")


# ----------------------------------------------------------------------
# Escenario con B alterada
# ----------------------------------------------------------------------
def make_altered_emission_matrix(
    emission_matrix: np.ndarray,
    mixing: float = PROVISIONAL_ALTERED_MIXING,
) -> np.ndarray:
    """Mezcla B con la distribución uniforme para reducir su separabilidad.

    ``mixing=0`` devuelve B original; ``mixing=1`` devuelve emisiones
    uniformes. El valor por defecto es provisional y debe registrarse antes
    de reportar el escenario secundario.
    """
    if not 0.0 <= mixing <= 1.0:
        raise ValueError("mixing debe estar en [0, 1].")

    B = np.asarray(emission_matrix, dtype=float)
    uniform = np.full_like(B, 1.0 / B.shape[1])
    return (1.0 - mixing) * B + mixing * uniform


# ----------------------------------------------------------------------
# Agregación
# ----------------------------------------------------------------------
def _bootstrap_ci(
    values: np.ndarray,
    rng: np.random.Generator,
    n_bootstrap: int,
    alpha: float = 0.05,
) -> tuple[float, float]:
    """IC percentil por bootstrap de secuencias (unidad independiente)."""
    if n_bootstrap <= 0 or len(values) == 0:
        return (float("nan"), float("nan"))

    indices = rng.integers(
        0,
        len(values),
        size=(n_bootstrap, len(values)),
    )
    means = values[indices].mean(axis=1)
    low, high = np.quantile(means, [alpha / 2.0, 1.0 - alpha / 2.0])
    return (float(low), float(high))


def _summarize(
    values: np.ndarray,
    rng: np.random.Generator,
    n_bootstrap: int,
) -> dict[str, float | None]:
    low, high = _bootstrap_ci(values, rng, n_bootstrap)
    return {
        "mean": float(np.mean(values)),
        "sd": float(np.std(values, ddof=1)) if len(values) > 1 else 0.0,
        "ci_low": low if np.isfinite(low) else None,
        "ci_high": high if np.isfinite(high) else None,
    }


# ----------------------------------------------------------------------
# Experimento
# ----------------------------------------------------------------------
def run_experiment(
    T: int = DEFAULT_T,
    N: int = DEFAULT_N,
    seed: int = DEFAULT_MASTER_SEED,
    emission_matrix: np.ndarray | None = None,
    initial_probabilities: np.ndarray | None = None,
    transition_matrix: np.ndarray | None = None,
    bootstrap_samples: int = DEFAULT_BOOTSTRAP_SAMPLES,
    decoder: str = "posterior",
) -> ExperimentResult:
    """Ejecuta una corrida del protocolo D4 para una matriz B.

    Una semilla distinta por secuencia, generada a partir de ``seed`` y
    registrada en ``ExperimentResult.seeds``. Las tres variantes usan las
    mismas secuencias (diseño pareado).
    """
    if T <= 0 or N <= 0:
        raise ValueError("T y N deben ser mayores que cero.")

    B = (
        DEFAULT_EMISSION_MATRIX
        if emission_matrix is None
        else np.asarray(emission_matrix, dtype=float)
    )
    A = (
        DEFAULT_TRANSITION_MATRIX
        if transition_matrix is None
        else np.asarray(transition_matrix, dtype=float)
    )
    pi = (
        DEFAULT_INITIAL_PROBABILITIES
        if initial_probabilities is None
        else np.asarray(initial_probabilities, dtype=float)
    )

    model = HMM(
        transition_matrix=A,
        emission_matrix=B,
        initial_probabilities=pi,
    )
    stationary = stationary_distribution(model.A)

    seeds = np.random.default_rng(seed).integers(
        0,
        np.iinfo(np.int64).max,
        size=N,
        dtype=np.int64,
    )

    per_sequence: dict[str, dict[str, np.ndarray]] = {
        model_name: {
            metric: np.empty(N, dtype=float) for metric in METRIC_NAMES
        }
        for model_name in MODEL_NAMES
    }

    for index in range(N):
        rng = np.random.default_rng(int(seeds[index]))
        generated = model.simulate(T, rng=rng)
        true_states = generated["states"]
        observations = generated["observations"]

        predictions = {
            "M0": decode_m0(observations, model.B),
            "M1": decode_m1(observations, model.A, model.B, stationary),
            "M2": decode_m2(observations, model, decoder=decoder),
        }

        for model_name, predicted in predictions.items():
            sequence_metrics = compute_sequence_metrics(true_states, predicted)
            for metric_name, value in sequence_metrics.items():
                per_sequence[model_name][metric_name][index] = value

    bootstrap_rng = np.random.default_rng(seed + 1)
    summary: dict[str, dict[str, dict[str, float | None]]] = {}
    for model_name in MODEL_NAMES:
        summary[model_name] = {}
        for metric_name in METRIC_NAMES:
            summary[model_name][metric_name] = _summarize(
                per_sequence[model_name][metric_name],
                bootstrap_rng,
                bootstrap_samples,
            )

    return ExperimentResult(
        T=T,
        N=N,
        master_seed=seed,
        seeds=seeds,
        emission_matrix=model.B.copy(),
        per_sequence=per_sequence,
        summary=summary,
    )


def run_d4_experiment(
    T: int = DEFAULT_T,
    N: int = DEFAULT_N,
    seed: int = DEFAULT_MASTER_SEED,
    bootstrap_samples: int = DEFAULT_BOOTSTRAP_SAMPLES,
    decoder: str = "posterior",
    altered_mixing: float = PROVISIONAL_ALTERED_MIXING,
) -> dict[str, ExperimentResult]:
    """Ejecuta el escenario base y el escenario con B alterada.

    Ambos escenarios comparten T, N, semilla maestra y regla de decisión.
    El valor de ``altered_mixing`` es provisional (ver
    ``PROVISIONAL_ALTERED_MIXING``).
    """
    base = run_experiment(
        T=T,
        N=N,
        seed=seed,
        bootstrap_samples=bootstrap_samples,
        decoder=decoder,
    )
    altered_B = make_altered_emission_matrix(
        DEFAULT_EMISSION_MATRIX,
        mixing=altered_mixing,
    )
    altered = run_experiment(
        T=T,
        N=N,
        seed=seed,
        emission_matrix=altered_B,
        bootstrap_samples=bootstrap_samples,
        decoder=decoder,
    )
    return {"base": base, "B_alterada": altered}


def format_summary(result: ExperimentResult) -> str:
    """Tabla legible con media, desviación e IC de cada modelo y métrica."""
    lines: list[str] = []
    lines.append(
        f"Protocolo D4 | T={result.T} | N={result.N} | "
        f"semilla maestra={result.master_seed}"
    )
    lines.append("Cifras simuladas; no son evidencia de validez ecológica.")
    lines.append("")
    header = (
        f"{'Modelo':<7} {'Macro-F1':>10} {'recall s3':>10} "
        f"{'exactitud':>10}"
    )
    lines.append(header)
    lines.append("-" * len(header))
    for model_name in MODEL_NAMES:
        values = []
        for metric_name in METRIC_NAMES:
            stats = result.summary[model_name][metric_name]
            mean = stats["mean"]
            values.append(f"{mean:.4f}" if mean is not None else "n/a")
        lines.append(
            f"{model_name:<7} {values[0]:>10} {values[1]:>10} {values[2]:>10}"
        )
    return "\n".join(lines)
