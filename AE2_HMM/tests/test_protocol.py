"""Pruebas del protocolo D4 (decodificación y comparación M0/M1/M2)."""

import numpy as np
import pytest

from src.hmm_model import (
    DEFAULT_EMISSION_MATRIX,
    DEFAULT_INITIAL_PROBABILITIES,
    DEFAULT_TRANSITION_MATRIX,
    HMM,
    stationary_distribution,
)
from src.simulation import (
    accuracy_score,
    decode_m0,
    decode_m1,
    decode_m2,
    format_summary,
    macro_f1_score,
    make_altered_emission_matrix,
    observable_markov_law,
    recall_score,
    run_experiment,
)


def test_default_matrices_match_specification() -> None:
    model = HMM()

    assert np.allclose(model.A, DEFAULT_TRANSITION_MATRIX)
    assert np.allclose(model.B, DEFAULT_EMISSION_MATRIX)
    assert np.allclose(model.pi, DEFAULT_INITIAL_PROBABILITIES)
    assert model.states == ("s1", "s2", "s3")
    assert model.observations == ("Alta", "Media", "Baja")


def test_matrices_are_stochastic() -> None:
    model = HMM()

    assert np.allclose(model.A.sum(axis=1), 1.0)
    assert np.allclose(model.B.sum(axis=1), 1.0)
    assert np.isclose(model.pi.sum(), 1.0)


def test_invalid_transition_matrix_is_rejected() -> None:
    with pytest.raises(ValueError):
        HMM(transition_matrix=np.ones((3, 3)))


def test_simulation_shapes_and_ranges() -> None:
    model = HMM(seed=7)
    generated = model.simulate(120)

    assert generated["states"].shape == (120,)
    assert generated["observations"].shape == (120,)
    assert np.all((0 <= generated["states"]) & (generated["states"] < 3))
    assert np.all(
        (0 <= generated["observations"]) & (generated["observations"] < 3)
    )


def test_viterbi_identifies_clear_patterns() -> None:
    model = HMM()

    assert np.all(model.viterbi(np.zeros(25, dtype=int)) == 0)
    assert np.all(model.viterbi(np.full(25, 2, dtype=int)) == 2)


def test_forward_backward_returns_valid_posteriors() -> None:
    model = HMM(seed=3)
    observations = model.simulate(30)["observations"]

    posterior = model.forward_backward(observations)

    assert posterior.shape == (30, 3)
    assert np.allclose(posterior.sum(axis=1), 1.0)
    assert np.all(posterior >= 0.0)


def test_forward_returns_log_likelihood() -> None:
    model = HMM()
    observations = np.array([0, 0, 1, 2, 2])

    result = model.forward(observations)

    assert result["alpha"].shape == (5, 3)
    assert np.isfinite(result["log_likelihood"])


def test_stationary_distribution_matches_reference() -> None:
    xi = stationary_distribution(DEFAULT_TRANSITION_MATRIX)

    assert np.isclose(xi.sum(), 1.0)
    assert np.allclose(xi, [0.424, 0.348, 0.227], atol=2e-3)


def test_observable_law_is_stochastic() -> None:
    p_observations, q_observations, state_given_observation = (
        observable_markov_law(DEFAULT_TRANSITION_MATRIX, DEFAULT_EMISSION_MATRIX)
    )

    assert np.isclose(p_observations.sum(), 1.0)
    assert np.allclose(q_observations.sum(axis=1), 1.0)
    assert np.allclose(state_given_observation.sum(axis=0), 1.0)


def test_m0_maps_each_observation_to_expected_state() -> None:
    observations = np.array([0, 1, 2, 0, 2])

    predicted = decode_m0(observations, DEFAULT_EMISSION_MATRIX)

    assert np.array_equal(predicted, np.array([0, 1, 2, 0, 2]))


def test_m1_and_m2_return_valid_state_labels() -> None:
    observations = np.array([0, 0, 1, 2, 2, 1, 0])

    m1 = decode_m1(
        observations,
        DEFAULT_TRANSITION_MATRIX,
        DEFAULT_EMISSION_MATRIX,
    )
    m2 = decode_m2(observations, HMM(), decoder="posterior")
    m2_viterbi = decode_m2(observations, HMM(), decoder="viterbi")

    for predicted in (m1, m2, m2_viterbi):
        assert predicted.shape == observations.shape
        assert np.all((0 <= predicted) & (predicted < 3))


def test_macro_f1_known_example() -> None:
    y_true = np.array([0, 0, 1, 2])
    y_pred = np.array([0, 1, 1, 2])

    assert np.isclose(macro_f1_score(y_true, y_pred), 0.7777777, atol=1e-6)
    assert np.isclose(recall_score(y_true, y_pred, label=2), 1.0)
    assert np.isclose(accuracy_score(y_true, y_pred), 0.75)


def test_run_experiment_is_paired_and_reproducible() -> None:
    first = run_experiment(T=30, N=8, seed=123, bootstrap_samples=50)
    second = run_experiment(T=30, N=8, seed=123, bootstrap_samples=50)

    assert first.T == 30
    assert first.N == 8
    assert len(np.unique(first.seeds)) == 8

    for model_name in ("M0", "M1", "M2"):
        for metric_name in ("macro_f1", "recall_s3", "accuracy"):
            assert np.array_equal(
                first.per_sequence[model_name][metric_name],
                second.per_sequence[model_name][metric_name],
            )
            stats = first.summary[model_name][metric_name]
            assert 0.0 <= stats["mean"] <= 1.0
            assert stats["ci_low"] is not None
            assert stats["ci_high"] is not None


def test_altered_emission_matrix_is_stochastic_and_different() -> None:
    altered = make_altered_emission_matrix(DEFAULT_EMISSION_MATRIX, mixing=0.5)

    assert np.allclose(altered.sum(axis=1), 1.0)
    assert not np.allclose(altered, DEFAULT_EMISSION_MATRIX)


def test_format_summary_mentions_models_and_metrics() -> None:
    result = run_experiment(T=20, N=4, seed=9, bootstrap_samples=20)
    text = format_summary(result)

    for model_name in ("M0", "M1", "M2"):
        assert model_name in text
    assert "Macro-F1" in text
    assert "recall s3" in text
