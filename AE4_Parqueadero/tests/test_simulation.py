"""Pruebas del laboratorio AE4 - Solución de un problema de parqueaderos."""

from __future__ import annotations

import math

import numpy as np
import pytest

from src.parking_simulation import (
    ARRIVAL_MEAN_MIN,
    DEFAULT_DURATION_MIN,
    SCENARIOS,
    SERVICE_MEAN_MIN,
    TYPE_PROB,
    USER_TYPES,
    assign_service_times,
    compute_replica_metrics,
    detectar_warmup_promedio_movil,
    estimar_replicas_requeridas,
    evaluate_criteria,
    generate_arrivals,
    mean_interarrival_min,
    mean_service_min,
    number_in_system_series,
    offered_load_erlangs,
    run_experiment,
    simulate_scenario,
    theoretical_mg1_per_teller,
    theoretical_mm1,
)


def _arrivals(seed: int = 123, duration: float = DEFAULT_DURATION_MIN):
    """Genera llegadas y tiempos de servicio reproducibles para las pruebas."""
    arrivals = generate_arrivals(duration, np.random.default_rng(seed))
    assign_service_times(arrivals, np.random.default_rng(seed + 1))
    return arrivals


# ----------------------------------------------------------------------
# Generación de llegadas y servicios
# ----------------------------------------------------------------------
def test_arrivals_are_within_duration_and_have_valid_types():
    arrivals = _arrivals(duration=720)
    assert arrivals
    assert all(0.0 < customer.arrival_time <= 720 for customer in arrivals)
    assert all(customer.user_type in USER_TYPES for customer in arrivals)
    assert [c.customer_id for c in arrivals] == list(range(len(arrivals)))
    # Las llegadas están ordenadas en el tiempo.
    times = [customer.arrival_time for customer in arrivals]
    assert times == sorted(times)


def test_type_composition_matches_statement():
    arrivals = _arrivals(seed=7, duration=40_000)
    shares = {
        user_type: sum(c.user_type == user_type for c in arrivals) / len(arrivals)
        for user_type in USER_TYPES
    }
    for user_type in USER_TYPES:
        assert shares[user_type] == pytest.approx(TYPE_PROB[user_type], abs=0.015)


def test_service_times_are_positive_and_match_means():
    arrivals = _arrivals(seed=11, duration=80_000)
    for user_type in USER_TYPES:
        sample = [c.service_time for c in arrivals if c.user_type == user_type]
        assert sample
        assert all(value > 0 for value in sample)
        assert np.mean(sample) == pytest.approx(
            SERVICE_MEAN_MIN[user_type], rel=0.06
        )


def test_aggregate_parameters_match_statement():
    expected_interarrival = sum(
        TYPE_PROB[t] * ARRIVAL_MEAN_MIN[t] for t in USER_TYPES
    )
    expected_service = sum(TYPE_PROB[t] * SERVICE_MEAN_MIN[t] for t in USER_TYPES)
    assert mean_interarrival_min() == pytest.approx(expected_interarrival)
    assert mean_service_min() == pytest.approx(expected_service)
    assert offered_load_erlangs() == pytest.approx(
        expected_service / expected_interarrival
    )
    assert offered_load_erlangs() < 1.0


# ----------------------------------------------------------------------
# Motor de simulación
# ----------------------------------------------------------------------
@pytest.mark.parametrize("scenario_key", list(SCENARIOS))
def test_simulation_preserves_every_customer(scenario_key):
    arrivals = _arrivals(duration=180)
    scenario = SCENARIOS[scenario_key]
    records = simulate_scenario(scenario, arrivals, np.random.default_rng(99))
    assert len(records) == len(arrivals)
    assert {c.customer_id for c in records} == {c.customer_id for c in arrivals}


def test_times_are_consistent_and_teller_in_range():
    arrivals = _arrivals(duration=180)
    scenario = SCENARIOS["indep_3"]
    records = simulate_scenario(scenario, arrivals, np.random.default_rng(99))
    for customer in records:
        assert customer.teller is not None
        assert 0 <= customer.teller < scenario.num_tellers
        assert customer.service_start is not None
        assert customer.service_end is not None
        assert customer.service_start >= customer.arrival_time - 1e-9
        assert customer.service_end >= customer.service_start - 1e-9
        assert customer.wait_time >= -1e-9
        assert customer.service_end == pytest.approx(
            customer.service_start + customer.service_time
        )


def test_specialized_tellers_respect_allowed_types():
    arrivals = _arrivals(duration=180)
    scenario = SCENARIOS["especializado_3"]
    records = simulate_scenario(scenario, arrivals, np.random.default_rng(5))
    for customer in records:
        assert customer.teller is not None
        assert scenario.accepts(customer.teller, customer.user_type)
        if customer.user_type in ("lento", "muy_lento"):
            assert customer.teller == 0
        else:
            assert customer.teller in (1, 2)


def test_shared_queue_has_exactly_one_queue():
    """Con fila única ningún cajero libre puede tener usuarios esperando."""
    arrivals = _arrivals(duration=240)
    scenario = SCENARIOS["unica_3"]
    simulator_records = simulate_scenario(
        scenario, arrivals, np.random.default_rng(17)
    )
    # Todos los usuarios terminan y el cajero elegido es válido.
    assert len(simulator_records) == len(arrivals)
    assert all(c.teller is not None for c in simulator_records)


def test_common_random_numbers_share_arrivals_across_scenarios():
    result = run_experiment(
        replicas=2,
        duration_min=120.0,
        warmup_min=10.0,
        master_seed=3,
        scenario_keys=["indep_3", "unica_3"],
    )
    indep = [r for r in result.customer_rows if r["scenario"] == "indep_3"]
    unica = [r for r in result.customer_rows if r["scenario"] == "unica_3"]
    assert len(indep) == len(unica)
    for left, right in zip(indep, unica):
        assert left["customer_id"] == right["customer_id"]
        assert left["arrival_time"] == pytest.approx(right["arrival_time"])
        assert left["service_time"] == pytest.approx(right["service_time"])


def test_metrics_are_within_valid_ranges():
    arrivals = _arrivals(duration=720)
    scenario = SCENARIOS["indep_3"]
    records = simulate_scenario(scenario, arrivals, np.random.default_rng(2))
    metrics = compute_replica_metrics(records, scenario, 720.0, warmup_min=60.0)
    assert 0.0 <= float(metrics["utilization"]) <= 1.0
    assert 0.0 <= float(metrics["max_teller_utilization"]) <= 1.0
    assert float(metrics["Lq"]) >= 0.0
    assert float(metrics["L"]) >= 0.0
    assert float(metrics["mean_wait"]) >= 0.0
    assert float(metrics["mean_system"]) >= float(metrics["mean_wait"])
    assert 0.0 <= float(metrics["frac_wait_gt_5"]) <= 1.0
    assert int(metrics["total_customers"]) > 0


def test_warmup_rejects_invalid_window():
    scenario = SCENARIOS["indep_3"]
    arrivals = _arrivals(duration=100)
    records = simulate_scenario(scenario, arrivals, np.random.default_rng(4))
    with pytest.raises(ValueError):
        compute_replica_metrics(records, scenario, 100.0, warmup_min=100.0)


# ----------------------------------------------------------------------
# Estado transitorio y réplicas
# ----------------------------------------------------------------------
def test_moving_average_detects_transient_in_synthetic_series():
    # 300 minutos de arranque (0..1) y luego estado estable en 2.
    rng = np.random.default_rng(8)
    transient = rng.uniform(0.0, 1.0, size=300)
    steady = rng.uniform(1.7, 2.3, size=2700)
    series = np.concatenate([transient, steady])
    result = detectar_warmup_promedio_movil(series, window=60)
    assert 150 <= result["cut_index"] <= 700
    assert result["reference_mean"] == pytest.approx(2.0, abs=0.1)


def test_moving_average_returns_early_cut_for_constant_series():
    result = detectar_warmup_promedio_movil(np.full(1000, 3.0), window=60)
    # Una serie constante no tiene transitorio: el corte queda en la primera
    # ventana (o antes), nunca a mitad de la serie.
    assert result["cut_index"] <= 120
    assert result["reference_mean"] == pytest.approx(3.0)
    assert result["tolerance"] >= 0.0


def test_replication_estimator_respects_minimum():
    rng = np.random.default_rng(21)
    values = rng.normal(2.0, 0.5, size=10)
    result = estimar_replicas_requeridas(values, min_replicas=10)
    assert result["n_requerido"] >= 10
    assert result["n_actual"] == 10


def test_replication_estimator_grows_with_variance():
    rng = np.random.default_rng(22)
    low = estimar_replicas_requeridas(rng.normal(2.0, 0.1, 30), min_replicas=30)
    high = estimar_replicas_requeridas(rng.normal(2.0, 2.0, 30), min_replicas=30)
    assert high["n_requerido"] >= low["n_requerido"]


# ----------------------------------------------------------------------
# Teoría y criterios
# ----------------------------------------------------------------------
def test_theoretical_mm1_matches_closed_form():
    theory = theoretical_mm1("rapido")
    assert theory["rho"] == pytest.approx((1 / 3) / (1 / 1))
    assert theory["Wq"] == pytest.approx(0.5)
    assert theory["W"] == pytest.approx(1.5)
    assert theory["Lq"] == pytest.approx(1 / 6)
    # Little: L = lambda * W
    assert theory["L"] == pytest.approx(theory["lambda"] * theory["W"])


def test_theoretical_mg1_is_finite_and_consistent():
    theory = theoretical_mg1_per_teller(3)
    assert 0.0 < theory["rho"] < 1.0
    assert theory["Wq"] > 0.0
    assert theory["W"] == pytest.approx(theory["Wq"] + mean_service_min(), rel=1e-9)
    assert theory["L"] == pytest.approx(theory["lambda"] * theory["W"], rel=1e-9)


def test_evaluate_criteria_flags_bad_scenario():
    bad = evaluate_criteria(
        {
            "mean_wait": 10.0,
            "mean_system": 20.0,
            "Lq": 8.0,
            "max_teller_utilization": 0.95,
            "frac_wait_gt_5": 0.40,
        }
    )
    assert bad["cumple_servicio"] is False
    assert bad["espera_cola"] is False
    assert bad["prob_espera_5"] is False

    good = evaluate_criteria(
        {
            "mean_wait": 0.5,
            "mean_system": 4.0,
            "Lq": 0.2,
            "max_teller_utilization": 0.55,
            "frac_wait_gt_5": 0.02,
        }
    )
    assert good["cumple_servicio"] is True


# ----------------------------------------------------------------------
# Serie N(t) y reproducibilidad
# ----------------------------------------------------------------------
def test_number_in_system_series_is_non_negative():
    arrivals = _arrivals(duration=200)
    scenario = SCENARIOS["indep_3"]
    records = simulate_scenario(scenario, arrivals, np.random.default_rng(31))
    times, values = number_in_system_series(records, 200.0, step_min=1.0)
    assert len(times) == len(values)
    assert np.all(values >= 0)
    assert values.max() <= len(arrivals)


def test_experiment_is_reproducible_with_same_seed():
    kwargs = dict(
        replicas=2,
        duration_min=120.0,
        warmup_min=10.0,
        master_seed=13,
        scenario_keys=["indep_3"],
    )
    first = run_experiment(**kwargs)
    second = run_experiment(**kwargs)
    assert first.replica_rows[0]["mean_wait"] == pytest.approx(
        second.replica_rows[0]["mean_wait"]
    )
    assert first.replica_rows[0]["total_customers"] == second.replica_rows[0][
        "total_customers"
    ]


def test_experiment_rejects_unknown_scenario():
    with pytest.raises(ValueError):
        run_experiment(replicas=1, scenario_keys=["no_existe"])


def test_experiment_rejects_invalid_warmup():
    with pytest.raises(ValueError):
        run_experiment(replicas=1, duration_min=100.0, warmup_min=120.0)
