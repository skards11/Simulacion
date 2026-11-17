"""Pruebas del laboratorio AE3 - Problema bancario."""

from __future__ import annotations

import numpy as np
import pytest

from src.bank_simulation import (
    ACTIONS,
    DEFAULT_DURATION_MIN,
    SCENARIOS,
    USER_TYPES,
    assign_service_times,
    compute_replica_metrics,
    generate_arrivals,
    run_experiment,
    scenario_offered_load,
    simulate_scenario,
)


def _arrivals(seed: int = 123, duration: float = DEFAULT_DURATION_MIN):
    rng = np.random.default_rng(seed)
    arrivals = generate_arrivals(duration, rng)
    assign_service_times(arrivals, np.random.default_rng(seed + 1))
    return arrivals


def test_arrivals_are_within_duration_and_have_valid_types():
    arrivals = _arrivals(duration=480)
    assert arrivals
    assert all(0.0 < c.arrival_time <= 480 for c in arrivals)
    assert all(c.action in ACTIONS for c in arrivals)
    assert all(c.user_type in USER_TYPES for c in arrivals)
    assert [c.customer_id for c in arrivals] == list(range(len(arrivals)))


def test_action_share_is_close_to_seventy_thirty():
    arrivals = _arrivals(seed=7, duration=20_000)
    retiro_share = sum(c.action == "retiro" for c in arrivals) / len(arrivals)
    assert 0.67 <= retiro_share <= 0.73


def test_service_times_are_positive():
    arrivals = _arrivals()
    assert all(c.service_time > 0 for c in arrivals)


def test_simulation_preserves_every_customer():
    arrivals = _arrivals()
    scenario = SCENARIOS["mixto_3"]
    records = simulate_scenario(scenario, arrivals, np.random.default_rng(99))
    assert len(records) == len(arrivals)
    assert {c.customer_id for c in records} == {c.customer_id for c in arrivals}


def test_dedicated_cashiers_only_receive_their_action():
    arrivals = _arrivals()
    scenario = SCENARIOS["retiro_1_pago_2"]
    records = simulate_scenario(scenario, arrivals, np.random.default_rng(99))
    for customer in records:
        assert customer.cashier is not None
        spec = scenario.cashiers[customer.cashier]
        assert spec.accepts(customer.action)
        if customer.action == "retiro":
            assert customer.cashier == 0
        else:
            assert customer.cashier in (1, 2)


def test_times_are_consistent():
    arrivals = _arrivals()
    scenario = SCENARIOS["mixto_3"]
    records = simulate_scenario(scenario, arrivals, np.random.default_rng(99))
    for customer in records:
        assert customer.service_start is not None
        assert customer.service_end is not None
        assert customer.service_start >= customer.arrival_time - 1e-9
        assert customer.wait_time >= -1e-9
        assert customer.service_end == pytest.approx(
            customer.service_start + customer.service_time
        )
        assert customer.system_time == pytest.approx(
            customer.wait_time + customer.service_time
        )


def test_metrics_are_nonnegative_and_utilization_is_bounded():
    arrivals = _arrivals()
    scenario = SCENARIOS["mixto_3"]
    records = simulate_scenario(scenario, arrivals, np.random.default_rng(99))
    metrics = compute_replica_metrics(records, scenario, DEFAULT_DURATION_MIN)
    for key in ("mean_wait", "p90_wait", "Lq", "L", "mean_service"):
        assert metrics[key] >= 0
    assert 0.0 <= metrics["utilization"] <= 1.0 + 1e-9
    assert 0.0 <= metrics["max_cashier_utilization"] <= 1.0 + 1e-9


def test_all_scenarios_are_theoretically_stable():
    for scenario in SCENARIOS.values():
        load = scenario_offered_load(scenario)
        assert load["rho_global"] < 1.0
        assert load["rho_retiro"] < 1.0
        assert load["rho_pago"] < 1.0
        assert load["estable"] is True


def test_experiment_is_reproducible():
    kwargs = dict(
        replicas=2,
        duration_min=120.0,
        master_seed=2026,
        scenario_keys=("mixto_3", "retiro_1_pago_2"),
    )
    first = run_experiment(**kwargs)
    second = run_experiment(**kwargs)
    assert first.replica_rows == second.replica_rows
    assert first.cashier_rows == second.cashier_rows
    assert first.type_count_rows == second.type_count_rows


def test_experiment_smoke_and_count_consistency():
    result = run_experiment(
        replicas=2,
        duration_min=90.0,
        master_seed=11,
        scenario_keys=("mixto_3", "retiro_2_pago_1"),
    )
    assert len(result.replica_rows) == 2 * 2
    assert len(result.cashier_rows) == 2 * (3 + 3)
    assert len(result.customer_rows) == sum(
        int(row["total_customers"]) for row in result.replica_rows
    )
    # Los conteos por acción y tipo deben sumar el total de cada réplica.
    for row in result.replica_rows:
        subset = [
            item
            for item in result.type_count_rows
            if item["scenario"] == row["scenario"]
            and item["replica"] == row["replica"]
        ]
        assert sum(int(item["count"]) for item in subset) == int(
            row["total_customers"]
        )


def test_mixed_configuration_distributes_load_across_cashiers():
    arrivals = _arrivals(duration=480)
    scenario = SCENARIOS["mixto_3"]
    records = simulate_scenario(scenario, arrivals, np.random.default_rng(99))
    served = [
        sum(1 for c in records if c.cashier == cashier_id)
        for cashier_id in range(scenario.num_cashiers)
    ]
    assert all(count > 0 for count in served)
    assert max(served) / min(served) < 2.0


def test_queue_drains_after_closing_time():
    arrivals = _arrivals(duration=480)
    scenario = SCENARIOS["mixto_3"]
    records = simulate_scenario(scenario, arrivals, np.random.default_rng(99))
    assert all(c.service_end is not None for c in records)
    # Todos los clientes que llegaron antes del cierre deben haber terminado.
    assert all(c.service_end >= c.service_start for c in records)
    assert all(c.service_start is not None for c in records)
