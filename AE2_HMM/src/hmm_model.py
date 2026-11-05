"""Modelo Oculto de Markov (HMM) para evaluar riesgo de incendio forestal.

Estados ocultos:
    - Riesgo Bajo
    - Riesgo Moderado
    - Riesgo Extremo

Observaciones:
    - Humedad Alta
    - Humedad Media
    - Humedad Baja
"""

from __future__ import annotations

from typing import Sequence

import numpy as np

# Estados ocultos del modelo.
STATES: tuple[str, ...] = (
    "Riesgo Bajo",
    "Riesgo Moderado",
    "Riesgo Extremo",
)

# Observaciones emitidas por cada estado oculto.
OBSERVATIONS: tuple[str, ...] = (
    "Humedad Alta",
    "Humedad Media",
    "Humedad Baja",
)

# Matriz de transición A: A[i, j] = P(S_t = j | S_{t-1} = i).
DEFAULT_TRANSITION_MATRIX: np.ndarray = np.array(
    [
        [0.70, 0.25, 0.05],  # Riesgo Bajo
        [0.30, 0.50, 0.20],  # Riesgo Moderado
        [0.10, 0.30, 0.60],  # Riesgo Extremo
    ],
    dtype=float,
)

# Matriz de emisión B: B[i, k] = P(O_t = k | S_t = i).
DEFAULT_EMISSION_MATRIX: np.ndarray = np.array(
    [
        [0.70, 0.25, 0.05],  # Riesgo Bajo   -> humedad alta
        [0.20, 0.60, 0.20],  # Riesgo Moderado
        [0.05, 0.25, 0.70],  # Riesgo Extremo -> humedad baja
    ],
    dtype=float,
)

# Distribución inicial pi: pi[i] = P(S_1 = i).
DEFAULT_INITIAL_PROBABILITIES: np.ndarray = np.array(
    [0.50, 0.30, 0.20],
    dtype=float,
)

# Puntuación de peligro asociada a cada estado para construir el índice 0-100.
RISK_SCORES: np.ndarray = np.array([10.0, 50.0, 100.0], dtype=float)


class HMM:
    """Modelo Oculto de Markov de tres estados y tres observaciones.

    Parameters
    ----------
    transition_matrix:
        Matriz A de tamaño (3, 3). Cada fila debe sumar 1.
    emission_matrix:
        Matriz B de tamaño (3, 3). Cada fila debe sumar 1.
    initial_probabilities:
        Vector pi de tamaño (3,). Debe sumar 1.
    states:
        Nombres de los estados ocultos. Por defecto usa ``STATES``.
    observations:
        Nombres de las observaciones. Por defecto usa ``OBSERVATIONS``.
    seed:
        Semilla opcional para reproducibilidad de las simulaciones.
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
        """Número de estados ocultos."""
        return len(self.states)

    @property
    def n_observations(self) -> int:
        """Número de observaciones posibles."""
        return len(self.observations)

    @property
    def A(self) -> np.ndarray:
        """Alias de la matriz de transición."""
        return self.transition_matrix

    @property
    def B(self) -> np.ndarray:
        """Alias de la matriz de emisión."""
        return self.emission_matrix

    @property
    def pi(self) -> np.ndarray:
        """Alias de la distribución inicial."""
        return self.initial_probabilities

    @property
    def extreme_state_index(self) -> int:
        """Índice del estado de riesgo extremo."""
        return self.n_states - 1

    def state_index(self, state: str) -> int:
        """Devuelve el índice de un estado oculto por su nombre."""
        try:
            return self.states.index(state)
        except ValueError as exc:
            raise ValueError(f"Estado desconocido: {state!r}") from exc

    def observation_index(self, observation: str) -> int:
        """Devuelve el índice de una observación por su nombre."""
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
        """Genera una secuencia de estados ocultos y observaciones.

        Parameters
        ----------
        n_steps:
            Número de días a simular.
        rng:
            Generador aleatorio opcional. Si no se indica, usa ``self.rng``.

        Returns
        -------
        dict
            Diccionario con ``states`` y ``observations`` como índices enteros.
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
    # Decodificación de Viterbi
    # ------------------------------------------------------------------
    def viterbi(
        self,
        observations: Sequence[int | str] | np.ndarray,
    ) -> np.ndarray:
        """Infiere la secuencia de estados más probable (algoritmo de Viterbi).

        Parameters
        ----------
        observations:
            Secuencia de índices o nombres de observaciones.

        Returns
        -------
        np.ndarray
            Índices de los estados ocultos más probables para cada día.
        """
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
                delta[t, state] = candidates[psi[t, state]] + log_b[state, obs[t]]

        path = np.empty(n_steps, dtype=int)
        path[-1] = int(np.argmax(delta[-1]))

        for t in range(n_steps - 2, -1, -1):
            path[t] = psi[t + 1, path[t + 1]]

        return path

    # ------------------------------------------------------------------
    # Probabilidades posteriores (forward-backward)
    # ------------------------------------------------------------------
    def forward_backward(
        self,
        observations: Sequence[int | str] | np.ndarray,
    ) -> np.ndarray:
        """Calcula P(S_t | O_1:T) para cada día usando escalamiento numérico.

        Returns
        -------
        np.ndarray
            Matriz de forma (T, n_states) con las probabilidades posteriores.
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
        alpha[0] /= scales[0]

        for t in range(1, n_steps):
            alpha[t] = (alpha[t - 1] @ self.A) * self.B[:, obs[t]]
            scales[t] = alpha[t].sum()
            if scales[t] == 0:
                scales[t] = 1.0
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
    # Índice de peligro y transiciones
    # ------------------------------------------------------------------
    def danger_index(
        self,
        posterior: np.ndarray,
        risk_scores: Sequence[float] | np.ndarray = RISK_SCORES,
    ) -> np.ndarray:
        """Convierte las probabilidades posteriores en un índice de 0 a 100.

        El índice es el valor esperado del peligro de los estados:
        Riesgo Bajo = 10, Moderado = 50, Extremo = 100.
        """
        scores = np.asarray(risk_scores, dtype=float)
        if scores.shape != (self.n_states,):
            raise ValueError(
                f"risk_scores debe tener forma ({self.n_states},)."
            )

        probabilities = np.asarray(posterior, dtype=float)
        if probabilities.ndim != 2 or probabilities.shape[1] != self.n_states:
            raise ValueError(
                "posterior debe tener forma (T, n_states)."
            )

        return np.clip(probabilities @ scores, 0.0, 100.0)

    def transition_probability_to_extreme(
        self,
        current_state: int | str | None = None,
    ) -> float | np.ndarray:
        """Probabilidad de pasar al estado de riesgo extremo.

        Si se indica un estado, devuelve P(S_t = Extremo | S_{t-1} = estado).
        Si no, devuelve el vector de probabilidades para cada estado de origen.
        """
        probabilities = self.A[:, self.extreme_state_index]

        if current_state is None:
            return probabilities.copy()

        index = self._as_state_index(current_state)
        return float(probabilities[index])

    def expected_transition_to_extreme(
        self,
        current_distribution: Sequence[float] | np.ndarray,
    ) -> float:
        """Probabilidad de riesgo extremo mañana dada una distribución actual."""
        distribution = self._validate_distribution(
            "current_distribution", current_distribution, self.n_states
        )
        return float(distribution @ self.A[:, self.extreme_state_index])

    # ------------------------------------------------------------------
    # Utilidades internas
    # ------------------------------------------------------------------
    def _as_state_index(self, state: int | str) -> int:
        if isinstance(state, str):
            return self.state_index(state)
        index = int(state)
        if not 0 <= index < self.n_states:
            raise ValueError(f"Índice de estado fuera de rango: {index}")
        return index

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
        """Valida forma, no negatividad y suma estocástica por fila."""
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
        """Valida forma, no negatividad y suma unitaria de una distribución."""
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
