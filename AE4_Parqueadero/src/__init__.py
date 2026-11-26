"""Paquete del laboratorio AE4 - Solución de un problema de parqueaderos."""

from .parking_simulation import (
    CRITERIA,
    DEFAULT_DURATION_MIN,
    DEFAULT_MASTER_SEED,
    DEFAULT_REPLICAS,
    DEFAULT_WARMUP_MIN,
    SCENARIOS,
    Scenario,
    run_experiment,
)

__all__ = [
    "CRITERIA",
    "DEFAULT_DURATION_MIN",
    "DEFAULT_MASTER_SEED",
    "DEFAULT_REPLICAS",
    "DEFAULT_WARMUP_MIN",
    "SCENARIOS",
    "Scenario",
    "run_experiment",
]
