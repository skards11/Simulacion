"""Pruebas del modelo HMM y de la simulación de riesgo de incendios."""

import numpy as np
import pytest

from src.hmm_model import HMM
from src.simulation import (
    HUMIDITY_RANGES,
    compute_metrics,
    extreme_windows,
    find_runs,
    run_simulation,
    sample_humidity,
    simulate_fire_events,
)


def test_default_matrices_match_specification() -> None:
    model = HMM()

    expected_transition = np.array(
        [
            [0.70, 0.25, 0.05],
            [0.30, 0.50, 0.20],
            [0.10, 0.30, 0.60],
        ]
    )
    expected_emission = np.array(
        [
            [0.70, 0.25, 0.05],
            [0.20, 0.60, 0.20],
            [0.05, 0.25, 0.70],
        ]
    )

    assert np.allclose(model.A, expected_transition)
    assert np.allclose(model.B, expected_emission)
    assert np.allclose(model.pi, [0.50, 0.30, 0.20])


def test_default_hmm_is_stochastic() -> None:
    model = HMM()

    assert model.A.shape == (3, 3)
    assert model.B.shape == (3, 3)
    assert model.pi.shape == (3,)
    assert np.allclose(model.A.sum(axis=1), 1.0)
    assert np.allclose(model.B.sum(axis=1), 1.0)
    assert np.isclose(model.pi.sum(), 1.0)


def test_invalid_transition_matrix_is_rejected() -> None:
    with pytest.raises(ValueError):
        HMM(transition_matrix=np.ones((3, 3)))


def test_simulation_lengths_and_state_ranges() -> None:
    model = HMM(seed=7)
    generated = model.simulate(120)

    assert generated["states"].shape == (120,)
    assert generated["observations"].shape == (120,)
    assert np.all((0 <= generated["states"]) & (generated["states"] < 3))
    assert np.all(
        (0 <= generated["observations"]) & (generated["observations"] < 3)
    )


def test_viterbi_identifies_clear_humidity_patterns() -> None:
    model = HMM()

    high_humidity = np.zeros(25, dtype=int)
    low_humidity = np.full(25, 2, dtype=int)

    assert np.all(model.viterbi(high_humidity) == 0)
    assert np.all(model.viterbi(low_humidity) == 2)


def test_forward_backward_returns_valid_probabilities() -> None:
    model = HMM(seed=3)
    observations = model.simulate(30)["observations"]

    posterior = model.forward_backward(observations)
    danger = model.danger_index(posterior)

    assert posterior.shape == (30, 3)
    assert np.allclose(posterior.sum(axis=1), 1.0)
    assert danger.shape == (30,)
    assert np.all((danger >= 0) & (danger <= 100))


def test_humidity_values_fall_inside_declared_ranges() -> None:
    rng = np.random.default_rng(11)
    observations = np.array([0, 1, 2] * 20)

    humidity = sample_humidity(observations, rng)

    for value, category in zip(humidity, observations):
        low, high = HUMIDITY_RANGES[category]
        assert low <= value <= high


def test_fire_events_are_boolean() -> None:
    rng = np.random.default_rng(5)
    states = np.array([0, 1, 2] * 20)
    humidity = np.array([80.0, 45.0, 15.0] * 20)

    events = simulate_fire_events(states, humidity, rng)

    assert events.dtype == bool
    assert events.shape == (60,)


def test_run_simulation_and_metrics() -> None:
    simulation = run_simulation(n_days=120, seed=42)
    metrics = compute_metrics(simulation)

    assert simulation.n_days == 120
    assert len(simulation.danger_index) == 120
    assert simulation.alerts == sorted(
        simulation.alerts, key=lambda alert: alert["day"]
    )
    assert 0 <= metrics["comparison"]["accuracy"] <= 1
    assert sum(metrics["risk_counts_inferred"].values()) == 120
    assert metrics["extreme_days_inferred"] == sum(
        1 for state in simulation.inferred_states if state == 2
    )


def test_find_runs_and_extreme_windows() -> None:
    states = np.array([0, 2, 2, 1, 2, 2, 2, 0])

    assert find_runs(states, target=2) == [(1, 2), (4, 6)]
    assert extreme_windows(states, min_length=2) == [
        {"start_day": 2, "end_day": 3, "length": 2},
        {"start_day": 5, "end_day": 7, "length": 3},
    ]
    assert extreme_windows(states, min_length=3) == [
        {"start_day": 5, "end_day": 7, "length": 3}
    ]
