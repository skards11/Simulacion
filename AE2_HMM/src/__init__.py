"""Paquete del HMM para el protocolo D4.

La carpeta ``legacy/`` conserva la simulación exploratoria anterior. Este
paquete implementa la decodificación con A, B y π fijos (D5a) y el
experimento comparativo M0/M1/M2 de D4.
"""

from .hmm_model import (
    DEFAULT_EMISSION_MATRIX,
    DEFAULT_INITIAL_PROBABILITIES,
    DEFAULT_TRANSITION_MATRIX,
    HMM,
    OBSERVATIONS,
    STATE_ALIASES,
    STATES,
    stationary_distribution,
)
from .simulation import (
    DEFAULT_MASTER_SEED,
    DEFAULT_N,
    DEFAULT_T,
    METRIC_NAMES,
    MODEL_NAMES,
    PROVISIONAL_ALTERED_MIXING,
    ExperimentResult,
    accuracy_score,
    compute_sequence_metrics,
    decode_m0,
    decode_m1,
    decode_m2,
    format_summary,
    macro_f1_score,
    make_altered_emission_matrix,
    observable_markov_law,
    recall_score,
    run_d4_experiment,
    run_experiment,
)

__all__ = [
    "HMM",
    "STATES",
    "STATE_ALIASES",
    "OBSERVATIONS",
    "DEFAULT_TRANSITION_MATRIX",
    "DEFAULT_EMISSION_MATRIX",
    "DEFAULT_INITIAL_PROBABILITIES",
    "stationary_distribution",
    "DEFAULT_T",
    "DEFAULT_N",
    "DEFAULT_MASTER_SEED",
    "MODEL_NAMES",
    "METRIC_NAMES",
    "PROVISIONAL_ALTERED_MIXING",
    "ExperimentResult",
    "run_experiment",
    "run_d4_experiment",
    "compute_sequence_metrics",
    "macro_f1_score",
    "recall_score",
    "accuracy_score",
    "decode_m0",
    "decode_m1",
    "decode_m2",
    "observable_markov_law",
    "make_altered_emission_matrix",
    "format_summary",
]
