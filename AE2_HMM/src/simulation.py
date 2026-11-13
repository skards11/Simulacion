"""Experimento de decodificación HMM: M0, M1 y M2.

Protocolo vigente
-----------------
* T = 500 pasos por secuencia.
* N = 2000 réplicas independientes derivadas de
  ``np.random.SeedSequence(42).spawn(2000)``.
* M0: Viterbi en espacio logarítmico con A, B y π nominales.
* M1: clasificador puntual sin memoria temporal,
  ``argmax_i B[i, O_t]``, sobre las observaciones nominales.
* M2: Viterbi con A, B y π nominales sobre observaciones generadas con
  ``B(m) = (1 - m) B + m U``, con ``m = 0.5`` y ``U_ij = 1/3``.

Las cifras son simuladas. No son evidencia de validez ecológica ni de
superioridad general del HMM.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.stats import wilcoxon

from .hmm_model import HMM

DEFAULT_T: int = 500
DEFAULT_N: int = 2000
DEFAULT_MASTER_SEED: int = 42
DEFAULT_ALPHA: float = 0.01
ALTERED_MIXING: float = 0.5
CLIFF_DELTA_THRESHOLD: float = 0.474
CRITERION_1_MIN_DIFFERENCE: float = 0.05
CRITERION_2_MIN_MACRO_F1: float = 0.333

MODEL_NAMES: tuple[str, ...] = ("M0", "M1", "M2")
METRIC_NAMES: tuple[str, ...] = ("macro_f1", "accuracy", "recall_s3")
N_CLASSES: int = 3


@dataclass
class ExperimentResult:
    """Resultado completo del experimento M0/M1/M2."""

    T: int
    N: int
    master_seed: int
    mixing: float
    seed_sequence_repr: str
    per_sequence: dict[str, dict[str, np.ndarray]]
    confusion_counts: dict[str, np.ndarray]
    summary: dict[str, dict[str, dict[str, float]]]
    comparisons: dict[str, dict[str, object]]
    criteria: dict[str, dict[str, object]]

    def to_dict(self) -> dict[str, object]:
        """Versión serializable (sin objetos numpy) para JSON."""
        payload = {
            "metadata": {
                "T": self.T,
                "N": self.N,
                "master_seed": self.master_seed,
                "mixing": self.mixing,
                "seed_sequence": self.seed_sequence_repr,
                "alpha": DEFAULT_ALPHA,
                "holm_correction": "Holm-Bonferroni",
                "models": {
                    "M0": "HMM nominal con Viterbi logarítmico (A, B, pi).",
                    "M1": "Baseline puntual sin memoria: argmax_i B[i, O_t].",
                    "M2": "Viterbi nominal sobre observaciones con B(m=0.5).",
                },
            },
            "models": {
                model_name: {
                    **{
                        metric_name: self.summary[model_name][metric_name]
                        for metric_name in METRIC_NAMES
                    },
                    "confusion_matrix_counts": self.confusion_counts[model_name],
                    "confusion_matrix_normalized": _normalize_confusion(
                        self.confusion_counts[model_name]
                    ),
                }
                for model_name in MODEL_NAMES
            },
            "comparisons": self.comparisons,
            "criteria": self.criteria,
            "per_sequence": self.per_sequence,
        }
        return _jsonable(payload)


# ----------------------------------------------------------------------
# Métricas
# ----------------------------------------------------------------------
def macro_f1_score(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    n_classes: int = N_CLASSES,
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
    """Calcula las métricas de una secuencia."""
    return {
        "macro_f1": macro_f1_score(y_true, y_pred),
        "accuracy": accuracy_score(y_true, y_pred),
        "recall_s3": recall_score(y_true, y_pred, label=2),
    }


def confusion_matrix_counts(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    n_classes: int = N_CLASSES,
) -> np.ndarray:
    """Matriz de confusión con filas = estado real y columnas = predicho."""
    y_true = np.asarray(y_true, dtype=int)
    y_pred = np.asarray(y_pred, dtype=int)
    if y_true.shape != y_pred.shape:
        raise ValueError("y_true e y_pred deben tener la misma forma.")

    matrix = np.zeros((n_classes, n_classes), dtype=int)
    for true_label, predicted_label in zip(y_true, y_pred):
        matrix[int(true_label), int(predicted_label)] += 1
    return matrix


def _normalize_confusion(counts: np.ndarray) -> np.ndarray:
    """Normaliza cada fila (estado real) para que sume 1."""
    counts = np.asarray(counts, dtype=float)
    row_sums = counts.sum(axis=1, keepdims=True)
    normalized = np.zeros_like(counts, dtype=float)
    np.divide(counts, row_sums, out=normalized, where=row_sums > 0)
    return normalized


# ----------------------------------------------------------------------
# Modelos comparados
# ----------------------------------------------------------------------
def altered_emission_matrix(
    emission_matrix: np.ndarray,
    mixing: float = ALTERED_MIXING,
) -> np.ndarray:
    """Construye B(m) = (1 - m) B + m U, con U_ij = 1/3."""
    if not 0.0 <= mixing <= 1.0:
        raise ValueError("mixing debe estar en [0, 1].")

    B = np.asarray(emission_matrix, dtype=float)
    uniform = np.full_like(B, 1.0 / B.shape[1])
    return (1.0 - mixing) * B + mixing * uniform


def decode_m0(model: HMM, observations: np.ndarray) -> np.ndarray:
    """M0: Viterbi logarítmico con A, B y π nominales."""
    return model.viterbi(observations)


def decode_m1(observations: np.ndarray, emission_matrix: np.ndarray) -> np.ndarray:
    """M1: clasificador puntual sin memoria temporal.

    Asigna a cada observación el estado con mayor probabilidad de emisión
    bajo la matriz B nominal. No usa A ni π.
    """
    obs = np.asarray(observations, dtype=int)
    B = np.asarray(emission_matrix, dtype=float)
    return np.argmax(B[:, obs], axis=0)


def decode_m2(model: HMM, observations: np.ndarray) -> np.ndarray:
    """M2: Viterbi con A, B y π nominales sobre observaciones degradadas."""
    return model.viterbi(observations)


def _emit_from_states(
    states: np.ndarray,
    emission_matrix: np.ndarray,
    rng: np.random.Generator,
) -> np.ndarray:
    """Genera observaciones a partir de estados y una matriz de emisión."""
    B = np.asarray(emission_matrix, dtype=float)
    observations = np.empty(len(states), dtype=int)
    for index, state in enumerate(states):
        observations[index] = rng.choice(B.shape[1], p=B[int(state)])
    return observations


# ----------------------------------------------------------------------
# Semillas y estadística
# ----------------------------------------------------------------------
def replica_seed_sequences(
    master_seed: int = DEFAULT_MASTER_SEED,
    n_replicas: int = DEFAULT_N,
) -> list[np.random.SeedSequence]:
    """Genera N secuencias de semilla independientes con SeedSequence.spawn."""
    if n_replicas <= 0:
        raise ValueError("n_replicas debe ser mayor que cero.")
    return list(np.random.SeedSequence(master_seed).spawn(n_replicas))


def summarize(values: np.ndarray) -> dict[str, float]:
    """Media, SD, mínimo, máximo, mediana, RIC e IC percentil 2.5–97.5."""
    values = np.asarray(values, dtype=float)
    if values.size == 0:
        raise ValueError("No se puede resumir un arreglo vacío.")

    q1, median, q3 = np.percentile(values, [25.0, 50.0, 75.0])
    ci_low, ci_high = np.percentile(values, [2.5, 97.5])
    return {
        "mean": float(np.mean(values)),
        "sd": float(np.std(values, ddof=1)) if values.size > 1 else 0.0,
        "min": float(np.min(values)),
        "max": float(np.max(values)),
        "median": float(median),
        "q1": float(q1),
        "q3": float(q3),
        "iqr": float(q3 - q1),
        "ci_low": float(ci_low),
        "ci_high": float(ci_high),
        "n": int(values.size),
    }


def cliff_delta_paired(x: np.ndarray, y: np.ndarray) -> float:
    """Delta de Cliff para datos pareados: (n_pos - n_neg) / n."""
    difference = np.asarray(x, dtype=float) - np.asarray(y, dtype=float)
    n = difference.size
    if n == 0:
        raise ValueError("Los arreglos no pueden estar vacíos.")
    positive = int(np.count_nonzero(difference > 0))
    negative = int(np.count_nonzero(difference < 0))
    return float((positive - negative) / n)


def paired_comparison(x: np.ndarray, y: np.ndarray) -> dict[str, object]:
    """Wilcoxon bilateral pareado y Delta de Cliff para x - y."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if x.shape != y.shape:
        raise ValueError("x e y deben tener la misma forma.")

    difference = x - y
    if np.allclose(difference, 0.0):
        statistic = 0.0
        p_value = 1.0
    else:
        result = wilcoxon(
            difference,
            alternative="two-sided",
            zero_method="wilcox",
            correction=False,
        )
        statistic = float(result.statistic)
        p_value = float(result.pvalue)

    return {
        "mean_difference": float(np.mean(difference)),
        "median_difference": float(np.median(difference)),
        "wilcoxon_statistic": statistic,
        "p_value_raw": p_value,
        "cliff_delta": cliff_delta_paired(x, y),
        "n_pairs": int(difference.size),
        "n_positive": int(np.count_nonzero(difference > 0)),
        "n_negative": int(np.count_nonzero(difference < 0)),
        "n_ties": int(np.count_nonzero(difference == 0)),
    }


def holm_bonferroni(p_values: list[float]) -> list[float]:
    """Ajuste de Holm-Bonferroni, manteniendo el orden de entrada."""
    p_values_array = np.asarray(p_values, dtype=float)
    m = p_values_array.size
    order = np.argsort(p_values_array)
    adjusted = np.empty(m, dtype=float)
    running = 0.0

    for rank, index in enumerate(order, start=1):
        candidate = (m - rank + 1) * p_values_array[index]
        running = max(running, candidate)
        adjusted[index] = min(running, 1.0)

    return [float(value) for value in adjusted]


# ----------------------------------------------------------------------
# Experimento
# ----------------------------------------------------------------------
def run_experiment(
    T: int = DEFAULT_T,
    N: int = DEFAULT_N,
    master_seed: int = DEFAULT_MASTER_SEED,
    mixing: float = ALTERED_MIXING,
) -> ExperimentResult:
    """Ejecuta las N réplicas pareadas de M0, M1 y M2."""
    if T <= 0 or N <= 0:
        raise ValueError("T y N deben ser mayores que cero.")

    model = HMM()
    B_altered = altered_emission_matrix(model.B, mixing)
    seed_sequences = replica_seed_sequences(master_seed, N)

    per_sequence: dict[str, dict[str, np.ndarray]] = {
        model_name: {
            metric_name: np.empty(N, dtype=float)
            for metric_name in METRIC_NAMES
        }
        for model_name in MODEL_NAMES
    }
    confusion_counts: dict[str, np.ndarray] = {
        model_name: np.zeros((N_CLASSES, N_CLASSES), dtype=int)
        for model_name in MODEL_NAMES
    }

    for replica_index, seed_sequence in enumerate(seed_sequences):
        nominal_rng = np.random.default_rng(seed_sequence)
        degraded_rng = np.random.default_rng(seed_sequence.spawn(1)[0])

        generated = model.simulate(T, rng=nominal_rng)
        true_states = generated["states"]
        nominal_observations = generated["observations"]
        degraded_observations = _emit_from_states(
            true_states,
            B_altered,
            degraded_rng,
        )

        predictions = {
            "M0": decode_m0(model, nominal_observations),
            "M1": decode_m1(nominal_observations, model.B),
            "M2": decode_m2(model, degraded_observations),
        }

        for model_name, predicted in predictions.items():
            metrics = compute_sequence_metrics(true_states, predicted)
            for metric_name, value in metrics.items():
                per_sequence[model_name][metric_name][replica_index] = value
            confusion_counts[model_name] += confusion_matrix_counts(
                true_states,
                predicted,
            )

    summary = {
        model_name: {
            metric_name: summarize(per_sequence[model_name][metric_name])
            for metric_name in METRIC_NAMES
        }
        for model_name in MODEL_NAMES
    }

    comparisons = {
        "M0_vs_M1": paired_comparison(
            per_sequence["M0"]["macro_f1"],
            per_sequence["M1"]["macro_f1"],
        ),
        "M0_vs_M2": paired_comparison(
            per_sequence["M0"]["macro_f1"],
            per_sequence["M2"]["macro_f1"],
        ),
    }
    raw_p_values = [
        float(comparisons["M0_vs_M1"]["p_value_raw"]),
        float(comparisons["M0_vs_M2"]["p_value_raw"]),
    ]
    adjusted_p_values = holm_bonferroni(raw_p_values)
    comparisons["M0_vs_M1"]["p_value_holm"] = adjusted_p_values[0]
    comparisons["M0_vs_M2"]["p_value_holm"] = adjusted_p_values[1]

    comparison_m0_m1 = comparisons["M0_vs_M1"]
    comparison_m0_m2 = comparisons["M0_vs_M2"]
    mean_m0 = summary["M0"]["macro_f1"]["mean"]
    mean_m1 = summary["M1"]["macro_f1"]["mean"]
    mean_m2 = summary["M2"]["macro_f1"]["mean"]

    criterion_1_met = bool(
        (mean_m0 - mean_m1) >= CRITERION_1_MIN_DIFFERENCE
        and float(comparison_m0_m1["p_value_holm"]) < DEFAULT_ALPHA
        and abs(float(comparison_m0_m1["cliff_delta"])) >= CLIFF_DELTA_THRESHOLD
    )
    criterion_2_met = bool(
        (mean_m0 - mean_m2) > 0.0
        and float(comparison_m0_m2["p_value_holm"]) < DEFAULT_ALPHA
        and mean_m2 > CRITERION_2_MIN_MACRO_F1
    )

    criteria = {
        "criterion_1": {
            "met": criterion_1_met,
            "mean_difference_m0_minus_m1": float(mean_m0 - mean_m1),
            "minimum_mean_difference": CRITERION_1_MIN_DIFFERENCE,
            "p_value_holm": float(comparison_m0_m1["p_value_holm"]),
            "alpha": DEFAULT_ALPHA,
            "cliff_delta": float(comparison_m0_m1["cliff_delta"]),
            "minimum_abs_cliff_delta": CLIFF_DELTA_THRESHOLD,
        },
        "criterion_2": {
            "met": criterion_2_met,
            "mean_drop_m0_minus_m2": float(mean_m0 - mean_m2),
            "p_value_holm": float(comparison_m0_m2["p_value_holm"]),
            "alpha": DEFAULT_ALPHA,
            "mean_macro_f1_m2": float(mean_m2),
            "minimum_macro_f1_m2": CRITERION_2_MIN_MACRO_F1,
        },
    }

    return ExperimentResult(
        T=T,
        N=N,
        master_seed=master_seed,
        mixing=mixing,
        seed_sequence_repr=f"np.random.SeedSequence({master_seed}).spawn({N})",
        per_sequence=per_sequence,
        confusion_counts=confusion_counts,
        summary=summary,
        comparisons=comparisons,
        criteria=criteria,
    )


def format_summary(result: ExperimentResult) -> str:
    """Resumen legible de métricas, contrastes y criterios."""
    lines = [
        f"Experimento HMM | T={result.T} | N={result.N} | "
        f"SeedSequence({result.master_seed}).spawn({result.N}) | m={result.mixing}",
        "Cifras simuladas; no son evidencia de validez ecológica.",
        "",
        "Macro-F1 por modelo:",
        f"{'Modelo':<7} {'Media':>9} {'SD':>8} {'Mín':>9} {'Máx':>9} "
        f"{'Mediana':>9} {'RIC':>8} {'IC95%':>20}",
        "-" * 90,
    ]
    for model_name in MODEL_NAMES:
        stats = result.summary[model_name]["macro_f1"]
        lines.append(
            f"{model_name:<7} {stats['mean']:>9.4f} {stats['sd']:>8.4f} "
            f"{stats['min']:>9.4f} {stats['max']:>9.4f} "
            f"{stats['median']:>9.4f} {stats['iqr']:>8.4f} "
            f"[{stats['ci_low']:.4f}, {stats['ci_high']:.4f}]"
        )

    lines.append("")
    lines.append("Contrastes pareados (Wilcoxon bilateral, Holm-Bonferroni):")
    for comparison_name in ("M0_vs_M1", "M0_vs_M2"):
        comparison = result.comparisons[comparison_name]
        lines.append(
            f"  {comparison_name}: dif={comparison['mean_difference']:.4f}, "
            f"p_raw={comparison['p_value_raw']:.3e}, "
            f"p_holm={comparison['p_value_holm']:.3e}, "
            f"Cliff={comparison['cliff_delta']:.4f}"
        )

    lines.append("")
    lines.append("Criterios de éxito:")
    for criterion_name, criterion in result.criteria.items():
        lines.append(f"  {criterion_name}: {'CUMPLE' if criterion['met'] else 'NO CUMPLE'}")
    return "\n".join(lines)


def _jsonable(value: object) -> object:
    """Convierte recursivamente valores numpy a tipos JSON."""
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    return value
