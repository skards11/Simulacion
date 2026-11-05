"""Paquete del modelo HMM para riesgo de incendio forestal."""

from .hmm_model import (
    DEFAULT_EMISSION_MATRIX,
    DEFAULT_INITIAL_PROBABILITIES,
    DEFAULT_TRANSITION_MATRIX,
    HMM,
    OBSERVATIONS,
    RISK_SCORES,
    STATES,
)
from .simulation import (
    HUMIDITY_RANGES,
    STATE_COLORS,
    SeasonSimulation,
    compute_metrics,
    run_simulation,
)

__all__ = [
    "HMM",
    "STATES",
    "OBSERVATIONS",
    "RISK_SCORES",
    "DEFAULT_TRANSITION_MATRIX",
    "DEFAULT_EMISSION_MATRIX",
    "DEFAULT_INITIAL_PROBABILITIES",
    "SeasonSimulation",
    "run_simulation",
    "compute_metrics",
    "HUMIDITY_RANGES",
    "STATE_COLORS",
]
