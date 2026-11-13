"""Modelo Oculto de Markov (HMM) para el experimento de decodificación.

Estados latentes
----------------
Los estados canónicos son ``Riesgo Bajo``, ``Riesgo Moderado`` y
``Riesgo Extremo``. Son etiquetas didácticas puras: no implican una medición
física de riesgo.

Observaciones
-------------
``Humedad Alta`` > ``Humedad Media`` > ``Humedad Baja`` es una escala ordinal
de humedad. No se asignan porcentajes ni umbrales numéricos.

Este módulo implementa únicamente inferencia con A, B y π fijos (D5a):
simulación, Forward, Forward–Backward y Viterbi. No implementa Baum-Welch.
"""

from __future__ import annotations

from typing import Sequence

import numpy as np

# Etiquetas canónicas de los estados latentes.
STATES: tuple[str, ...] = (
    "Riesgo Bajo",
    "Riesgo Moderado",
    "Riesgo Extremo",
)

# Alias de presentación: coinciden con los estados canónicos.
STATE_ALIASES: tuple[str, ...] = STATES

# Observaciones ordinales de humedad.
OBSERVATIONS: tuple[str, ...] = (
    "Humedad Alta",
    "Humedad Media",
    "Humedad Baja",
)

# Matriz de transición A: A[i, j] = P(S_t = j | S_{t-1} = i).
DEFAULT_TRANSITION_MATRIX: np.ndarray = np.array(
    [
        [0.70, 0.25, 0.05],
        [0.30, 0.50, 0.20],
        [0.10, 0.30, 0.60],
    ],
    dtype=float,
)

# Matriz de emisión B: B[i, k] = P(O_t = k | S_t = i).
DEFAULT_EMISSION_MATRIX: np.ndarray = np.array(
    [
        [0.70, 0.25, 0.05],
        [0.20, 0.60, 0.20],
        [0.05, 0.25, 0.70],
    ],
    dtype=float,
)

# Distribución inicial π: π[i] = P(S_1 = i). Es un prior en t = 1,
# no la distribución estacionaria de A.
DEFAULT_INITIAL_PROBABILITIES: np.ndarray = np.array(
    [0.50, 0.30, 0.20],
    dtype=float,
)


class HMM:
    """HMM discreto de tres estados y tres observaciones.

    Parameters
    ----------
    transition_matrix:
        Matriz A de tamaño (K, K). Cada fila debe sumar 1.
    emission_matrix:
        Matriz B de tamaño (K, O). Cada fila debe sumar 1.
    initial_probabilities:
        Vector π de tamaño (K,). Debe sumar 1.
    states:
        Nombres de los estados latentes. Por defecto usa ``STATES``.
    observations:
        Nombres de las observaciones. Por defecto usa ``OBSERVATIONS``.
    seed:
        Semilla opcional para ``simulate`` cuando no se pasa un ``rng``.
    """

    def __init__(
        self,
        transition_matrix: Sequence[Sequence[float]] | np.ndarray | None = None,
        emission_matrix: Sequence[Sequence[float]] | np.ndarray | None = None,
        initial_probabilities: Sequence[float] | np.ndarray | None = None,
        states: Sequence[str] = STATES,
        observations: Sequence[str] = OBSERVATIONS,
        seed: int | None = None,
    ) -> None:
        self.states = tuple(states)
        self.observations = tuple(observations)

        if len(self.states) != len(self.observations):
            raise ValueError(
                "El número de estados y observaciones debe coincidir en este modelo."
            )

        n_states = len(self.states)
        n_observations = len(self.observations)

        if transition_matrix is None:
            transition_matrix = DEFAULT_TRANSITION_MATRIX
        if emission_matrix is None:
            emission_matrix = DEFAULT_EMISSION_MATRIX
        if initial_probabilities is None:
            initial_probabilities = DEFAULT_INITIAL_PROBABILITIES

        self.transition_matrix = self._validate_matrix(
            "transition_matrix", transition_matrix, n_states, n_states
        )
        self.emission_matrix = self._validate_matrix(
            "emission_matrix", emission_matrix, n_states, n_observations
        )
        self.initial_probabilities = self._validate_distribution(
            "initial_probabilities", initial_probabilities, n_states
        )

        self.rng = np.random.default_rng(seed)

    # ------------------------------------------------------------------
    # Propiedades básicas
    # ------------------------------------------------------------------
    @property
    def n_states(self) -> int:
        return len(self.states)

    @property
    def n_observations(self) -> int:
        return len(self.observations)

    @property
    def A(self) -> np.ndarray:
        return self.transition_matrix

    @property
    def B(self) -> np.ndarray:
        return self.emission_matrix

    @property
    def pi(self) -> np.ndarray:
        return self.initial_probabilities

    @property
    def state_aliases(self) -> tuple[str, ...]:
        """Alias mnemónicos, en el mismo orden que ``states``."""
        if len(self.states) == len(STATE_ALIASES):
            return STATE_ALIASES
        return self.states

    def state_index(self, state: str) -> int:
        try:
            return self.states.index(state)
        except ValueError as exc:
            raise ValueError(f"Estado desconocido: {state!r}") from exc

    def observation_index(self, observation: str) -> int:
        try:
            return self.observations.index(observation)
        except ValueError as exc:
            raise ValueError(f"Observación desconocida: {observation!r}") from exc

    # ------------------------------------------------------------------
    # Simulación
    # ------------------------------------------------------------------
    def simulate(
        self,
        n_steps: int,
        rng: np.random.Generator | None = None,
    ) -> dict[str, np.ndarray]:
        """Genera una secuencia de estados latentes y observaciones.

        Un paso es una ocasión de observación, sin unidad física (D3.3).
        """
        if n_steps <= 0:
            raise ValueError("n_steps debe ser mayor que cero.")

        rng = self.rng if rng is None else rng
        state_indices = np.empty(n_steps, dtype=int)
        observation_indices = np.empty(n_steps, dtype=int)

        state_indices[0] = rng.choice(self.n_states, p=self.pi)
        observation_indices[0] = rng.choice(
            self.n_observations, p=self.B[state_indices[0]]
        )

        for t in range(1, n_steps):
            state_indices[t] = rng.choice(
                self.n_states, p=self.A[state_indices[t - 1]]
            )
            observation_indices[t] = rng.choice(
                self.n_observations, p=self.B[state_indices[t]]
            )

        return {
            "states": state_indices,
            "observations": observation_indices,
        }

    # ------------------------------------------------------------------
    # Forward
    # ------------------------------------------------------------------
    def forward(
        self,
        observations: Sequence[int | str] | np.ndarray,
    ) -> dict[str, np.ndarray | float]:
        """Calcula α escalada y la log-verosimilitud de la secuencia.

        Returns
        -------
        dict
            ``alpha``: matriz (T, K) con α normalizada por paso.
            ``log_likelihood``: log P(O_1:T).
            ``scales``: factores de escala de cada paso.
        """
        obs = self._as_observation_indices(observations)
        n_steps = len(obs)

        if n_steps == 0:
            return {
                "alpha": np.empty((0, self.n_states), dtype=float),
                "log_likelihood": 0.0,
                "scales": np.empty(0, dtype=float),
            }

        alpha = np.zeros((n_steps, self.n_states), dtype=float)
        scales = np.ones(n_steps, dtype=float)
        log_likelihood = 0.0

        alpha[0] = self.pi * self.B[:, obs[0]]
        scales[0] = alpha[0].sum()
        if scales[0] <= 0:
            return {
                "alpha": alpha,
                "log_likelihood": float("-inf"),
                "scales": scales,
            }
        alpha[0] /= scales[0]
        log_likelihood += float(np.log(scales[0]))

        for t in range(1, n_steps):
            alpha[t] = (alpha[t - 1] @ self.A) * self.B[:, obs[t]]
            scales[t] = alpha[t].sum()
            if scales[t] <= 0:
                return {
                    "alpha": alpha,
                    "log_likelihood": float("-inf"),
                    "scales": scales,
                }
            alpha[t] /= scales[t]
            log_likelihood += float(np.log(scales[t]))

        return {
            "alpha": alpha,
            "log_likelihood": log_likelihood,
            "scales": scales,
        }

    # ------------------------------------------------------------------
    # Forward–Backward (posteriores marginales)
    # ------------------------------------------------------------------
    def forward_backward(
        self,
        observations: Sequence[int | str] | np.ndarray,
    ) -> np.ndarray:
        """Calcula P(S_t | O_1:T) con escalamiento numérico.

        Returns
        -------
        np.ndarray
            Matriz (T, K) con las probabilidades posteriores.
        """
        obs = self._as_observation_indices(observations)
        n_steps = len(obs)

        if n_steps == 0:
            return np.empty((0, self.n_states), dtype=float)

        alpha = np.zeros((n_steps, self.n_states), dtype=float)
        beta = np.zeros((n_steps, self.n_states), dtype=float)
        scales = np.ones(n_steps, dtype=float)

        alpha[0] = self.pi * self.B[:, obs[0]]
        scales[0] = alpha[0].sum()
        if scales[0] <= 0:
            raise ValueError("La secuencia tiene probabilidad cero bajo el modelo.")
        alpha[0] /= scales[0]

        for t in range(1, n_steps):
            alpha[t] = (alpha[t - 1] @ self.A) * self.B[:, obs[t]]
            scales[t] = alpha[t].sum()
            if scales[t] <= 0:
                raise ValueError(
                    "La secuencia tiene probabilidad cero bajo el modelo."
                )
            alpha[t] /= scales[t]

        beta[-1] = 1.0
        for t in range(n_steps - 2, -1, -1):
            beta[t] = (
                self.A @ (self.B[:, obs[t + 1]] * beta[t + 1])
            ) / scales[t + 1]

        posterior = alpha * beta
        row_sums = posterior.sum(axis=1, keepdims=True)
        row_sums[row_sums == 0] = 1.0
        return posterior / row_sums

    # ------------------------------------------------------------------
    # Viterbi
    # ------------------------------------------------------------------
    def viterbi(
        self,
        observations: Sequence[int | str] | np.ndarray,
    ) -> np.ndarray:
        """Infiere la secuencia de estados más probable (ruta MAP)."""
        obs = self._as_observation_indices(observations)
        n_steps = len(obs)

        if n_steps == 0:
            return np.empty(0, dtype=int)

        log_pi = self._safe_log(self.pi)
        log_a = self._safe_log(self.A)
        log_b = self._safe_log(self.B)

        delta = np.empty((n_steps, self.n_states), dtype=float)
        psi = np.zeros((n_steps, self.n_states), dtype=int)

        delta[0] = log_pi + log_b[:, obs[0]]

        for t in range(1, n_steps):
            for state in range(self.n_states):
                candidates = delta[t - 1] + log_a[:, state]
                psi[t, state] = int(np.argmax(candidates))
                delta[t, state] = (
                    candidates[psi[t, state]] + log_b[state, obs[t]]
                )

        path = np.empty(n_steps, dtype=int)
        path[-1] = int(np.argmax(delta[-1]))

        for t in range(n_steps - 2, -1, -1):
            path[t] = psi[t + 1, path[t + 1]]

        return path

    # ------------------------------------------------------------------
    # Utilidades internas
    # ------------------------------------------------------------------
    def _as_observation_indices(
        self,
        observations: Sequence[int | str] | np.ndarray,
    ) -> np.ndarray:
        array = np.asarray(observations)

        if array.ndim != 1:
            raise ValueError("observations debe ser una secuencia unidimensional.")

        if array.dtype.kind in "iu":
            indices = array.astype(int)
            if np.any(indices < 0) or np.any(indices >= self.n_observations):
                raise ValueError("Hay índices de observación fuera de rango.")
            return indices

        indices = np.array(
            [self.observation_index(str(value)) for value in array],
            dtype=int,
        )
        return indices

    @staticmethod
    def _safe_log(values: np.ndarray) -> np.ndarray:
        with np.errstate(divide="ignore"):
            return np.log(values)

    @staticmethod
    def _validate_matrix(
        name: str,
        matrix: Sequence[Sequence[float]] | np.ndarray,
        expected_rows: int,
        expected_columns: int,
    ) -> np.ndarray:
        array = np.asarray(matrix, dtype=float)

        if array.shape != (expected_rows, expected_columns):
            raise ValueError(
                f"{name} debe tener forma ({expected_rows}, {expected_columns}); "
                f"se recibió {array.shape}."
            )

        if np.any(array < 0):
            raise ValueError(f"{name} no puede contener valores negativos.")

        row_sums = array.sum(axis=1)
        if not np.allclose(row_sums, 1.0, atol=1e-9):
            raise ValueError(
                f"Cada fila de {name} debe sumar 1; se obtuvo {row_sums.tolist()}."
            )

        return array

    @staticmethod
    def _validate_distribution(
        name: str,
        distribution: Sequence[float] | np.ndarray,
        expected_size: int,
    ) -> np.ndarray:
        array = np.asarray(distribution, dtype=float)

        if array.shape != (expected_size,):
            raise ValueError(
                f"{name} debe tener forma ({expected_size},); "
                f"se recibió {array.shape}."
            )

        if np.any(array < 0):
            raise ValueError(f"{name} no puede contener valores negativos.")

        if not np.isclose(array.sum(), 1.0, atol=1e-9):
            raise ValueError(
                f"{name} debe sumar 1; se obtuvo {array.sum():.6f}."
            )

        return array

    def __repr__(self) -> str:
        return (
            f"HMM(n_states={self.n_states}, "
            f"n_observations={self.n_observations})"
        )


def stationary_distribution(
    transition_matrix: Sequence[Sequence[float]] | np.ndarray,
) -> np.ndarray:
    """Devuelve la distribución estacionaria de una matriz estocástica.

    Se resuelve el sistema (Aᵀ − I)ξ = 0 con la restricción Σξ = 1. La
    distribución resultante es una herramienta de diagnóstico; el protocolo
    experimental vigente no la usa como baseline.
    """
    A = np.asarray(transition_matrix, dtype=float)
    if A.ndim != 2 or A.shape[0] != A.shape[1]:
        raise ValueError("transition_matrix debe ser cuadrada.")

    n = A.shape[0]
    system = np.vstack([A.T - np.eye(n), np.ones((1, n))])
    target = np.zeros(n + 1)
    target[-1] = 1.0

    xi, *_ = np.linalg.lstsq(system, target, rcond=None)
    xi = np.clip(xi, 0.0, None)
    total = xi.sum()
    if total <= 0:
        raise ValueError("No se pudo calcular la distribución estacionaria.")
    return xi / total
