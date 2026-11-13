"""Pruebas del experimento HMM M0/M1/M2."""

import numpy as np
import pytest

from src.hmm_model import (
    DEFAULT_EMISSION_MATRIX,
    DEFAULT_INITIAL_PROBABILITIES,
    DEFAULT_TRANSITION_MATRIX,
    HMM,
    OBSERVATIONS,
    STATES,
)
from src.simulation import (
    ALTERED_MIXING,
    accuracy_score,
    altered_emission_matrix,
    cliff_delta_paired,
    compute_sequence_metrics,
    confusion_matrix_counts,
    decode_m0,
    decode_m1,
    decode_m2,
    format_summary,
    holm_bonferroni,
    macro_f1_score,
    paired_comparison,
    recall_score,
    replica_seed_sequences,
    run_experiment,
    summarize,
)


def test_default_labels_and_matrices_match_specification() -> None:
    model = HMM()

    assert STATES == (
        "Riesgo Bajo",
        "Riesgo Moderado",
        "Riesgo Extremo",
    )
    assert OBSERVATIONS == (
        "Humedad Alta",
        "Humedad Media",
        "Humedad Baja",
    )
    assert model.states == STATES
    assert model.observations == OBSERVATIONS
    assert np.allclose(model.A, DEFAULT_TRANSITION_MATRIX)
    assert np.allclose(model.B, DEFAULT_EMISSION_MATRIX)
    assert np.allclose(model.pi, DEFAULT_INITIAL_PROBABILITIES)


def test_matrices_are_stochastic() -> None:
    model = HMM()

    assert np.allclose(model.A.sum(axis=1), 1.0)
    assert np.allclose(model.B.sum(axis=1), 1.0)
    assert np.isclose(model.pi.sum(), 1.0)


def test_viterbi_is_log_space_and_recovers_clear_patterns() -> None:
    model = HMM()

    assert np.all(model.viterbi(np.zeros(25, dtype=int)) == 0)
    assert np.all(model.viterbi(np.full(25, 2, dtype=int)) == 2)


def test_m0_uses_viterbi_with_nominal_model() -> None:
    model = HMM()
    observations = np.array([0, 0, 1, 2, 2, 1, 0])

    assert np.array_equal(
        decode_m0(model, observations),
        model.viterbi(observations),
    )


def test_m1_is_memoryless_threshold() -> None:
    observations = np.array([0, 1, 2, 0, 2])

    predicted = decode_m1(observations, DEFAULT_EMISSION_MATRIX)

    assert np.array_equal(predicted, np.array([0, 1, 2, 0, 2]))
    # El pasado no altera la predicción puntual del paso actual.
    assert decode_m1(np.array([2, 0]), DEFAULT_EMISSION_MATRIX)[-1] == 0
    assert decode_m1(np.array([0]), DEFAULT_EMISSION_MATRIX)[0] == 0


def test_m2_uses_nominal_b_on_degraded_observations() -> None:
    model = HMM()
    altered = altered_emission_matrix(DEFAULT_EMISSION_MATRIX, ALTERED_MIXING)

    assert np.allclose(altered.sum(axis=1), 1.0)
    assert not np.allclose(altered, DEFAULT_EMISSION_MATRIX)

    observations = np.array([0, 0, 1, 2, 2, 1, 0])
    assert np.array_equal(
        decode_m2(model, observations),
        model.viterbi(observations),
    )


def test_replica_seed_sequences_are_unique_and_reproducible() -> None:
    first = replica_seed_sequences(42, 2000)
    second = replica_seed_sequences(42, 2000)

    assert len(first) == 2000
    assert [seed.spawn_key for seed in first] == [
        seed.spawn_key for seed in second
    ]
    assert len({seed.spawn_key for seed in first}) == 2000


def test_run_experiment_is_paired_and_reproducible() -> None:
    first = run_experiment(T=20, N=8, master_seed=42)
    second = run_experiment(T=20, N=8, master_seed=42)

    assert first.T == 20
    assert first.N == 8
    assert first.mixing == ALTERED_MIXING
    assert first.confusion_counts["M0"].shape == (3, 3)

    for model_name in ("M0", "M1", "M2"):
        for metric_name in ("macro_f1", "accuracy", "recall_s3"):
            assert np.array_equal(
                first.per_sequence[model_name][metric_name],
                second.per_sequence[model_name][metric_name],
            )
        stats = first.summary[model_name]["macro_f1"]
        assert 0.0 <= stats["mean"] <= 1.0
        assert stats["ci_low"] <= stats["ci_high"]

    for comparison_name in ("M0_vs_M1", "M0_vs_M2"):
        comparison = first.comparisons[comparison_name]
        assert 0.0 <= comparison["p_value_raw"] <= 1.0
        assert 0.0 <= comparison["p_value_holm"] <= 1.0


def test_macro_f1_known_example() -> None:
    y_true = np.array([0, 0, 1, 2])
    y_pred = np.array([0, 1, 1, 2])

    assert np.isclose(macro_f1_score(y_true, y_pred), 0.7777777, atol=1e-6)
    assert np.isclose(recall_score(y_true, y_pred, label=2), 1.0)
    assert np.isclose(accuracy_score(y_true, y_pred), 0.75)


def test_sequence_metrics_and_confusion_matrix() -> None:
    y_true = np.array([0, 0, 1, 2])
    y_pred = np.array([0, 1, 1, 2])

    metrics = compute_sequence_metrics(y_true, y_pred)
    counts = confusion_matrix_counts(y_true, y_pred)

    assert set(metrics) == {"macro_f1", "accuracy", "recall_s3"}
    assert counts.shape == (3, 3)
    assert counts.sum() == len(y_true)


def test_summarize_includes_requested_statistics() -> None:
    values = np.arange(1, 101, dtype=float)
    stats = summarize(values)

    assert set(stats) == {
        "mean",
        "sd",
        "min",
        "max",
        "median",
        "q1",
        "q3",
        "iqr",
        "ci_low",
        "ci_high",
        "n",
    }
    assert np.isclose(stats["mean"], 50.5)
    assert np.isclose(stats["median"], 50.5)
    assert stats["min"] == 1.0
    assert stats["max"] == 100.0
    assert stats["ci_low"] < stats["mean"] < stats["ci_high"]


def test_holm_bonferroni_adjustment() -> None:
    assert np.allclose(holm_bonferroni([0.01, 0.04]), [0.02, 0.04])
    assert np.allclose(holm_bonferroni([0.001, 0.04]), [0.002, 0.04])


def test_cliff_delta_and_paired_comparison() -> None:
    x = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    y = np.array([0.0, 1.0, 2.0, 3.0, 4.0])

    assert np.isclose(cliff_delta_paired(x, y), 1.0)
    comparison = paired_comparison(x, y)
    assert comparison["mean_difference"] == 1.0
    assert comparison["cliff_delta"] == 1.0
    assert comparison["n_positive"] == 5


def test_format_summary_mentions_models_and_metrics() -> None:
    result = run_experiment(T=20, N=6, master_seed=42)
    text = format_summary(result)

    for model_name in ("M0", "M1", "M2"):
        assert model_name in text
    assert "Macro-F1" in text
    assert "Cliff" in text


def test_invalid_mixing_is_rejected() -> None:
    with pytest.raises(ValueError):
        altered_emission_matrix(DEFAULT_EMISSION_MATRIX, mixing=1.5)
