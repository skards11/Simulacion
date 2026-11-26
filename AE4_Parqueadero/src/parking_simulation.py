"""Simulación de eventos discretos del problema de parqueaderos (AE4).

Contexto del enunciado
----------------------
El Centro Comercial Supercentro cobra el parqueadero en tres cajeros por
salida.  Cada cajero es un servidor independiente con su propia fila FIFO,
sin cambio de fila y sin deserción.  Los usuarios se clasifican en cuatro
tipos (rápido, normal, lento y muy lento) con tiempos de servicio y tiempos
entre llegadas exponenciales.

Modelo implementado
-------------------
* Un día de operación de 720 minutos (12 horas), configurable.
* La composición de la demanda es 25 % rápida, 20 % normal, 27.5 % lenta y
  27.5 % muy lenta.  En cada llegada se sortea primero el tipo de usuario y
  luego el tiempo hasta la siguiente llegada con una exponencial cuya media
  depende del tipo (Tabla del enunciado).  Así se respeta exactamente la
  composición de usuarios pedida en el punto B.
* El tiempo de servicio de cada usuario es exponencial con media según su
  tipo.
* Cada cajero es un servidor con cola FIFO propia.  Por defecto, el usuario
  elige un cajero al azar entre los disponibles y no cambia de fila; esto es
  la interpretación literal de "tres M/M/1 independientes".  También se
  simulan variantes con fila única compartida y con cajeros especializados
  para el análisis de escenarios (punto C).
* Se generan llegadas hasta el minuto 720 y luego se drena el sistema: los
  usuarios que alcanzaron a llegar terminan su servicio aunque el reloj
  supere las 12 horas.  Esto evita truncar las esperas más largas.
* Se descarta un período de calentamiento (warm-up) calculado con el método
  del promedio móvil sobre el número de usuarios en el sistema.  Solo se
  reportan las estadísticas del estado estable (punto E).
* Diseño de números aleatorios comunes: dentro de una réplica, todos los
  escenarios reciben exactamente las mismas llegadas, tipos de usuario y
  tiempos de servicio.  Solo cambia la política de filas.  Así la comparación
  entre escenarios es pareada y el ruido muestral se reduce.

Las cifras que produce este módulo son simuladas.  No provienen de datos
reales del Centro Comercial Supercentro.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field, replace
import heapq
import math
from typing import Iterable, Sequence

import numpy as np

# ----------------------------------------------------------------------
# Datos del enunciado
# ----------------------------------------------------------------------
USER_TYPES: tuple[str, ...] = ("rapido", "normal", "lento", "muy_lento")
USER_TYPE_LABELS: dict[str, str] = {
    "rapido": "Rápido",
    "normal": "Normal",
    "lento": "Lento",
    "muy_lento": "Muy lento",
}

# Media del tiempo de servicio en minutos (Tabla del enunciado).
SERVICE_MEAN_MIN: dict[str, float] = {
    "rapido": 1.0,
    "normal": 3.0,
    "lento": 4.0,
    "muy_lento": 6.0,
}

# Media del tiempo entre llegadas en minutos (Tabla del enunciado).
ARRIVAL_MEAN_MIN: dict[str, float] = {
    "rapido": 3.0,
    "normal": 3.0,
    "lento": 5.0,
    "muy_lento": 7.0,
}

# Composición de la demanda.  El enunciado fija 25 % y 20 % para rápidos y
# normales; el 55 % restante se reparte por igual entre lentos y muy lentos.
TYPE_PROB: dict[str, float] = {
    "rapido": 0.25,
    "normal": 0.20,
    "lento": 0.275,
    "muy_lento": 0.275,
}

DEFAULT_DURATION_MIN: float = 720.0  # 12 horas (jornada típica de centro comercial)
DEFAULT_REPLICAS: int = 30
DEFAULT_MASTER_SEED: int = 42
DEFAULT_WARMUP_MIN: float = 30.0
DEFAULT_PILOT_DURATION_MIN: float = 10_000.0

# Criterios de decisión (punto C).  Se toman de la guía del laboratorio y se
# documentan como supuestos: el centro comercial puede cambiarlos.
CRITERIA: dict[str, float] = {
    "espera_cola_aceptable_min": 3.0,
    "espera_cola_critica_min": 5.0,
    "espera_sistema_aceptable_min": 5.0,
    "espera_sistema_critica_min": 8.0,
    "utilizacion_minima_eficiente": 0.60,
    "utilizacion_maxima": 0.85,
    "cola_maxima_aceptable": 3.0,
    "cola_critica": 5.0,
    "prob_espera_5_max": 0.10,
    "prob_espera_5_critica": 0.20,
}


# ----------------------------------------------------------------------
# Escenarios
# ----------------------------------------------------------------------
@dataclass(frozen=True)
class Scenario:
    """Configuración de cajeros y política de filas de un escenario.

    ``teller_allowed[i]`` es la tupla de tipos de usuario que puede atender
    el cajero ``i``; ``None`` significa que atiende todos los tipos.
    """

    key: str
    label: str
    description: str
    teller_allowed: tuple[tuple[str, ...] | None, ...]
    shared_queue: bool = False
    assignment: str = "random"  # "random" | "shortest"

    @property
    def num_tellers(self) -> int:
        return len(self.teller_allowed)

    @property
    def policy_label(self) -> str:
        if self.shared_queue:
            return "Fila única compartida"
        if self.assignment == "shortest":
            return "Filas independientes (cola más corta)"
        if self.assignment == "idle_shortest":
            return "Filas independientes (libre al azar / cola más corta)"
        if any(allowed is not None for allowed in self.teller_allowed):
            return "Filas independientes especializadas"
        return "Filas independientes (elección aleatoria)"

    def accepts(self, teller: int, user_type: str) -> bool:
        allowed = self.teller_allowed[teller]
        return allowed is None or user_type in allowed

    def to_dict(self) -> dict[str, object]:
        return {
            "key": self.key,
            "label": self.label,
            "description": self.description,
            "num_tellers": self.num_tellers,
            "shared_queue": self.shared_queue,
            "assignment": self.assignment,
            "policy_label": self.policy_label,
            "teller_allowed": [
                list(allowed) if allowed is not None else None
                for allowed in self.teller_allowed
            ],
        }


def _make_scenario(
    key: str,
    label: str,
    description: str,
    teller_allowed: Sequence[Sequence[str] | None],
    *,
    shared_queue: bool = False,
    assignment: str = "random",
) -> Scenario:
    allowed_tuple = tuple(
        (tuple(allowed) if allowed is not None else None) for allowed in teller_allowed
    )
    return Scenario(
        key=key,
        label=label,
        description=description,
        teller_allowed=allowed_tuple,
        shared_queue=shared_queue,
        assignment=assignment,
    )


SCENARIOS: dict[str, Scenario] = {
    "indep_2": _make_scenario(
        "indep_2",
        "2 cajeros con filas independientes",
        "Reduce la capacidad actual a dos cajeros con filas independientes.",
        (None, None),
    ),
    "indep_3": _make_scenario(
        "indep_3",
        "3 cajeros con filas independientes (actual)",
        "Situación actual: tres cajeros, cada uno con su propia fila FIFO.",
        (None, None, None),
    ),
    "indep_3_corta": _make_scenario(
        "indep_3_corta",
        "3 cajeros: cada usuario elige la cola más corta",
        "Mejora operativa sin compartir fila: al llegar se elige la cola "
        "más corta, pero el usuario ya no cambia de fila.",
        (None, None, None),
        assignment="shortest",
    ),
    "indep_3_adaptativa": _make_scenario(
        "indep_3_adaptativa",
        "3 cajeros: libre al azar y, si todos ocupados, cola más corta",
        "Política adaptativa: si hay un cajero libre se elige al azar; si "
        "todos están ocupados se elige la cola más corta.",
        (None, None, None),
        assignment="idle_shortest",
    ),
    "indep_4": _make_scenario(
        "indep_4",
        "4 cajeros con filas independientes",
        "Agrega un cuarto cajero manteniendo filas independientes.",
        (None, None, None, None),
    ),
    "indep_5": _make_scenario(
        "indep_5",
        "5 cajeros con filas independientes",
        "Agrega dos cajeros manteniendo filas independientes.",
        (None, None, None, None, None),
    ),
    "unica_2": _make_scenario(
        "unica_2",
        "2 cajeros con fila única",
        "Dos cajeros que atienden una sola fila compartida (M/G/2).",
        (None, None),
        shared_queue=True,
    ),
    "unica_3": _make_scenario(
        "unica_3",
        "3 cajeros con fila única (mejora propuesta)",
        "Los tres cajeros actuales atienden una sola fila compartida.",
        (None, None, None),
        shared_queue=True,
    ),
    "unica_4": _make_scenario(
        "unica_4",
        "4 cajeros con fila única",
        "Cuatro cajeros atendiendo una sola fila compartida.",
        (None, None, None, None),
        shared_queue=True,
    ),
    "especializado_3": _make_scenario(
        "especializado_3",
        "1 cajero para lentos + 2 para rápidos/normales",
        "Especialización por tipo de usuario: un cajero atiende a los lentos "
        "y muy lentos, y dos atienden a los rápidos y normales.",
        (("lento", "muy_lento"), ("rapido", "normal"), ("rapido", "normal")),
    ),
}

DEFAULT_SCENARIO_KEYS: tuple[str, ...] = tuple(SCENARIOS)
MAIN_SCENARIO: str = "indep_3"


# ----------------------------------------------------------------------
# Utilidades estadísticas y carga ofrecida
# ----------------------------------------------------------------------
def _weighted_mean(values: Sequence[float], weights: Sequence[float]) -> float:
    return float(sum(v * w for v, w in zip(values, weights)))


def mean_interarrival_min() -> float:
    """Media incondicional del tiempo entre llegadas de un usuario cualquiera."""
    return _weighted_mean(
        [ARRIVAL_MEAN_MIN[t] for t in USER_TYPES],
        [TYPE_PROB[t] for t in USER_TYPES],
    )


def mean_service_min() -> float:
    """Media incondicional del tiempo de servicio de un usuario cualquiera."""
    return _weighted_mean(
        [SERVICE_MEAN_MIN[t] for t in USER_TYPES],
        [TYPE_PROB[t] for t in USER_TYPES],
    )


def second_moment_service_min2() -> float:
    """Segundo momento de una exponencial con media ``s``: E[S^2] = 2 s^2."""
    return _weighted_mean(
        [2.0 * SERVICE_MEAN_MIN[t] ** 2 for t in USER_TYPES],
        [TYPE_PROB[t] for t in USER_TYPES],
    )


def offered_load_erlangs() -> float:
    """Carga ofrecida total (en servidores) del flujo de usuarios."""
    return mean_service_min() / mean_interarrival_min()


def theoretical_mm1(user_type: str) -> dict[str, float]:
    """Métricas M/M/1 exactas si un cajero atendiera solo ese tipo."""
    lam = 1.0 / ARRIVAL_MEAN_MIN[user_type]
    mu = 1.0 / SERVICE_MEAN_MIN[user_type]
    rho = lam / mu
    if rho >= 1.0:
        return {
            "lambda": lam,
            "mu": mu,
            "rho": rho,
            "L": math.inf,
            "Lq": math.inf,
            "W": math.inf,
            "Wq": math.inf,
            "P0": 0.0,
        }
    return {
        "lambda": lam,
        "mu": mu,
        "rho": rho,
        "L": rho / (1.0 - rho),
        "Lq": rho**2 / (1.0 - rho),
        "W": 1.0 / (mu - lam),
        "Wq": rho / (mu - lam),
        "P0": 1.0 - rho,
    }


def theoretical_mg1_per_teller(num_tellers: int = 3) -> dict[str, float]:
    """Aproximación M/G/1 por cajero con servicio hiperexponencial.

    Al repartir las llegadas al azar entre ``c`` cajeros, cada uno recibe una
    tasa ``lambda/c``.  La fórmula de Pollaczek-Khinchine entrega el tiempo
    medio en cola.  Es una aproximación porque el flujo agregado no es
    Poisson, pero sirve como referencia de validación.
    """
    lam_total = 1.0 / mean_interarrival_min()
    lam = lam_total / num_tellers
    service = mean_service_min()
    second = second_moment_service_min2()
    rho = lam * service
    if rho >= 1.0:
        return {"lambda": lam, "rho": rho, "Wq": math.inf, "W": math.inf}
    wq = lam * second / (2.0 * (1.0 - rho))
    return {
        "lambda": lam,
        "rho": rho,
        "Wq": wq,
        "W": wq + service,
        "Lq": lam * wq,
        "L": lam * (wq + service),
    }


# ----------------------------------------------------------------------
# Entidades de la simulación
# ----------------------------------------------------------------------
@dataclass
class Customer:
    customer_id: int
    user_type: str
    arrival_time: float
    service_time: float = 0.0
    teller: int | None = None
    service_start: float | None = None
    service_end: float | None = None

    @property
    def wait_time(self) -> float:
        if self.service_start is None:
            return 0.0
        return max(0.0, self.service_start - self.arrival_time)

    @property
    def system_time(self) -> float:
        if self.service_end is None:
            return 0.0
        return max(0.0, self.service_end - self.arrival_time)


def generate_arrivals(
    duration_min: float,
    rng: np.random.Generator,
    *,
    only_type: str | None = None,
    type_prob: dict[str, float] | None = None,
    arrival_mean: dict[str, float] | None = None,
) -> list[Customer]:
    """Genera las llegadas de una jornada.

    En cada iteración se sortea el tipo de usuario y luego el tiempo hasta la
    siguiente llegada con una exponencial cuya media depende del tipo.  La
    primera llegada ocurre después de un tiempo exponencial; no se fuerza un
    usuario en ``t = 0``.  Se incluyen las llegadas con ``t <= duration_min``.
    """
    probs = type_prob or TYPE_PROB
    means = arrival_mean or ARRIVAL_MEAN_MIN
    types = (only_type,) if only_type is not None else USER_TYPES
    weights = np.array(
        [1.0] if only_type is not None else [probs[t] for t in types], dtype=float
    )

    arrivals: list[Customer] = []
    t = 0.0
    customer_id = 0
    while True:
        type_index = int(rng.choice(len(types), p=weights))
        user_type = types[type_index]
        t += float(rng.exponential(means[user_type]))
        if t > duration_min:
            break
        arrivals.append(
            Customer(
                customer_id=customer_id,
                user_type=user_type,
                arrival_time=t,
            )
        )
        customer_id += 1
    return arrivals


def assign_service_times(
    arrivals: Iterable[Customer],
    rng: np.random.Generator,
    *,
    service_mean: dict[str, float] | None = None,
) -> None:
    """Asigna a cada usuario su tiempo de servicio exponencial (in situ)."""
    means = service_mean or SERVICE_MEAN_MIN
    for customer in arrivals:
        customer.service_time = float(rng.exponential(means[customer.user_type]))


class _Simulator:
    """Motor de eventos discretos para un escenario y una réplica."""

    def __init__(self, scenario: Scenario, rng: np.random.Generator) -> None:
        self.scenario = scenario
        self.rng = rng
        self.queues: list[deque[Customer]] = [
            deque() for _ in range(scenario.num_tellers)
        ]
        self.shared_queue: deque[Customer] = deque()
        self.busy: list[bool] = [False] * scenario.num_tellers
        self.current: list[Customer | None] = [None] * scenario.num_tellers
        # (tiempo_fin, cajero, secuencia) para desempatar eventos simultáneos.
        self.completion_heap: list[tuple[float, int, int]] = []
        self.event_sequence = 0
        self.records: list[Customer] = []

    def _start_service(
        self,
        customer: Customer,
        teller: int,
        start_time: float,
    ) -> None:
        if not self.scenario.accepts(teller, customer.user_type):
            raise ValueError(
                f"El cajero {teller} no atiende usuarios de tipo "
                f"{customer.user_type}."
            )
        customer.teller = teller
        customer.service_start = start_time
        customer.service_end = start_time + customer.service_time
        self.current[teller] = customer
        self.busy[teller] = True
        self.records.append(customer)
        heapq.heappush(
            self.completion_heap,
            (customer.service_end, teller, self.event_sequence),
        )
        self.event_sequence += 1

    def _process_completion(self) -> float:
        finish_time, teller, _ = heapq.heappop(self.completion_heap)
        self.busy[teller] = False
        self.current[teller] = None

        if self.scenario.shared_queue and self.shared_queue:
            next_customer = self.shared_queue.popleft()
            self._start_service(next_customer, teller, finish_time)
        elif self.queues[teller]:
            next_customer = self.queues[teller].popleft()
            self._start_service(next_customer, teller, finish_time)
        return finish_time

    def _eligible_tellers(self, user_type: str) -> list[int]:
        eligible = [
            teller
            for teller in range(self.scenario.num_tellers)
            if self.scenario.accepts(teller, user_type)
        ]
        if not eligible:
            raise ValueError(
                f"Ningún cajero puede atender a un usuario de tipo {user_type}."
            )
        return eligible

    def _arrive(self, customer: Customer) -> None:
        eligible = self._eligible_tellers(customer.user_type)

        if self.scenario.shared_queue:
            idle = [teller for teller in eligible if not self.busy[teller]]
            if idle:
                teller = idle[int(self.rng.integers(len(idle)))]
                self._start_service(customer, teller, customer.arrival_time)
            else:
                self.shared_queue.append(customer)
            return

        if self.scenario.assignment == "shortest":
            min_queue = min(len(self.queues[teller]) for teller in eligible)
            candidates = [
                teller
                for teller in eligible
                if len(self.queues[teller]) == min_queue
            ]
            teller = candidates[int(self.rng.integers(len(candidates)))]
        elif self.scenario.assignment == "idle_shortest":
            idle = [teller for teller in eligible if not self.busy[teller]]
            if idle:
                teller = idle[int(self.rng.integers(len(idle)))]
            else:
                min_queue = min(len(self.queues[teller]) for teller in eligible)
                candidates = [
                    teller
                    for teller in eligible
                    if len(self.queues[teller]) == min_queue
                ]
                teller = candidates[int(self.rng.integers(len(candidates)))]
        else:
            teller = eligible[int(self.rng.integers(len(eligible)))]

        if not self.busy[teller] and not self.queues[teller]:
            self._start_service(customer, teller, customer.arrival_time)
        else:
            self.queues[teller].append(customer)

    def run(self, arrivals: Sequence[Customer]) -> list[Customer]:
        # Se copian los usuarios para no modificar los datos compartidos entre
        # escenarios (diseño de números aleatorios comunes).
        customers = [replace(customer) for customer in arrivals]

        for customer in customers:
            # Los fines de servicio anteriores o simultáneos liberan cajeros
            # antes de ubicar al nuevo usuario.
            while (
                self.completion_heap
                and self.completion_heap[0][0] <= customer.arrival_time
            ):
                self._process_completion()
            self._arrive(customer)

        # Drenaje: se atienden todos los usuarios que ya habían llegado.
        while self.completion_heap:
            self._process_completion()

        return sorted(self.records, key=lambda c: c.customer_id)


def simulate_scenario(
    scenario: Scenario,
    arrivals: Sequence[Customer],
    rng: np.random.Generator,
) -> list[Customer]:
    """Simula un escenario con una lista de llegadas ya generadas."""
    return _Simulator(scenario, rng).run(arrivals)


# ----------------------------------------------------------------------
# Métricas
# ----------------------------------------------------------------------
def _overlap(start: float, end: float, lo: float, hi: float) -> float:
    """Longitud de la intersección entre ``[start, end]`` y ``[lo, hi]``."""
    return max(0.0, min(end, hi) - max(start, lo))


def _mean(values: Sequence[float]) -> float:
    return float(np.mean(values)) if len(values) else 0.0


def _std(values: Sequence[float]) -> float:
    return float(np.std(values, ddof=1)) if len(values) > 1 else 0.0


def _percentile(values: Sequence[float], q: float) -> float:
    return float(np.percentile(values, q)) if len(values) else 0.0


def _fraction(values: Sequence[float], threshold: float) -> float:
    return float(np.mean(np.asarray(values) > threshold)) if len(values) else 0.0


def compute_replica_metrics(
    records: Sequence[Customer],
    scenario: Scenario,
    duration_min: float,
    warmup_min: float = 0.0,
) -> dict[str, object]:
    """Calcula las métricas de una réplica en el período de estado estable.

    Las estadísticas por usuario usan solo a quienes llegan después del
    calentamiento.  Las integrales de cola y de sistema cubren la ventana
    ``[warmup_min, duration_min]`` e incluyen a los usuarios que ya estaban
    en el sistema al inicio de la ventana.
    """
    if warmup_min >= duration_min:
        raise ValueError("El calentamiento debe ser menor que la duración.")
    window = duration_min - warmup_min

    in_window = [c for c in records if c.arrival_time >= warmup_min]
    waits = [c.wait_time for c in in_window]
    services = [c.service_time for c in in_window]
    systems = [c.system_time for c in in_window]

    queue_area = sum(
        _overlap(c.arrival_time, c.service_start or c.arrival_time, warmup_min, duration_min)
        for c in records
    )
    system_area = sum(
        _overlap(c.arrival_time, c.service_end or c.arrival_time, warmup_min, duration_min)
        for c in records
    )

    teller_rows: list[dict[str, float]] = []
    for teller in range(scenario.num_tellers):
        subset_all = [c for c in records if c.teller == teller]
        subset = [c for c in subset_all if c.arrival_time >= warmup_min]
        busy_time = sum(
            _overlap(
                c.service_start or 0.0,
                c.service_end or 0.0,
                warmup_min,
                duration_min,
            )
            for c in subset_all
        )
        teller_queue_area = sum(
            _overlap(
                c.arrival_time,
                c.service_start or c.arrival_time,
                warmup_min,
                duration_min,
            )
            for c in subset_all
        )
        teller_rows.append(
            {
                "served": float(len(subset)),
                "mean_service": _mean([c.service_time for c in subset]),
                "std_service": _std([c.service_time for c in subset]),
                "min_service": (
                    float(min(c.service_time for c in subset)) if subset else 0.0
                ),
                "max_service": (
                    float(max(c.service_time for c in subset)) if subset else 0.0
                ),
                "mean_wait": _mean([c.wait_time for c in subset]),
                "p90_wait": _percentile([c.wait_time for c in subset], 90),
                "mean_system": _mean([c.system_time for c in subset]),
                "utilization": busy_time / window if window else 0.0,
                "mean_queue_length": teller_queue_area / window if window else 0.0,
                "busy_minutes": busy_time,
            }
        )

    result: dict[str, object] = {
        "scenario": scenario.key,
        "scenario_label": scenario.label,
        "policy": scenario.policy_label,
        "num_tellers": scenario.num_tellers,
        "warmup_min": warmup_min,
        "window_min": window,
        "total_customers": len(in_window),
        "throughput_per_hour": len(in_window) / (window / 60.0) if window else 0.0,
        "mean_wait": _mean(waits),
        "std_wait": _std(waits),
        "p50_wait": _percentile(waits, 50),
        "p90_wait": _percentile(waits, 90),
        "p95_wait": _percentile(waits, 95),
        "max_wait": float(max(waits)) if waits else 0.0,
        "mean_service": _mean(services),
        "std_service": _std(services),
        "mean_system": _mean(systems),
        "p90_system": _percentile(systems, 90),
        "Lq": queue_area / window if window else 0.0,
        "L": system_area / window if window else 0.0,
        "utilization": (
            sum(float(row["utilization"]) for row in teller_rows)
            / scenario.num_tellers
            if scenario.num_tellers
            else 0.0
        ),
        "max_teller_utilization": max(
            (float(row["utilization"]) for row in teller_rows), default=0.0
        ),
        "frac_wait_gt_3": _fraction(waits, 3.0),
        "frac_wait_gt_5": _fraction(waits, 5.0),
        "frac_wait_gt_10": _fraction(waits, 10.0),
        "unfinished_at_close": sum(
            1 for c in in_window if (c.service_end or 0.0) > duration_min
        ),
        "waiting_at_close": sum(
            1 for c in in_window if (c.service_start or 0.0) > duration_min
        ),
    }

    for user_type in USER_TYPES:
        subset = [c for c in in_window if c.user_type == user_type]
        result[f"n_{user_type}"] = len(subset)
        result[f"mean_wait_{user_type}"] = _mean([c.wait_time for c in subset])
        result[f"p90_wait_{user_type}"] = _percentile(
            [c.wait_time for c in subset], 90
        )
        result[f"mean_service_{user_type}"] = _mean([c.service_time for c in subset])
        result[f"mean_system_{user_type}"] = _mean([c.system_time for c in subset])

    result["_teller_rows"] = teller_rows
    return result


def compute_teller_rows(
    metrics: dict[str, object],
    scenario: Scenario,
    replica: int,
) -> list[dict[str, object]]:
    """Convierte las métricas internas por cajero en filas planas."""
    rows: list[dict[str, object]] = []
    for teller, teller_metrics in enumerate(metrics["_teller_rows"]):  # type: ignore[arg-type]
        row: dict[str, object] = {
            "scenario": scenario.key,
            "scenario_label": scenario.label,
            "replica": replica,
            "teller": teller,
            "teller_label": f"Cajero {teller + 1}",
            "allowed_types": (
                "Todos"
                if scenario.teller_allowed[teller] is None
                else ", ".join(
                    USER_TYPE_LABELS[t] for t in scenario.teller_allowed[teller]  # type: ignore[index]
                )
            ),
        }
        row.update(teller_metrics)  # type: ignore[arg-type]
        rows.append(row)
    return rows


def customer_to_row(
    customer: Customer,
    scenario: Scenario,
    replica: int,
) -> dict[str, object]:
    """Convierte un usuario simulado en una fila plana para CSV."""
    return {
        "scenario": scenario.key,
        "scenario_label": scenario.label,
        "policy": scenario.policy_label,
        "replica": replica,
        "customer_id": customer.customer_id,
        "teller": customer.teller,
        "teller_label": (
            f"Cajero {customer.teller + 1}" if customer.teller is not None else ""
        ),
        "user_type": customer.user_type,
        "user_type_label": USER_TYPE_LABELS[customer.user_type],
        "arrival_time": customer.arrival_time,
        "service_start": customer.service_start,
        "service_end": customer.service_end,
        "wait_time": customer.wait_time,
        "service_time": customer.service_time,
        "system_time": customer.system_time,
    }


# ----------------------------------------------------------------------
# Estado estable, calentamiento y número de réplicas
# ----------------------------------------------------------------------
def number_in_system_series(
    records: Sequence[Customer],
    horizon_min: float,
    step_min: float = 1.0,
) -> tuple[np.ndarray, np.ndarray]:
    """Serie temporal del número de usuarios en el sistema N(t).

    Se muestrea en una grilla de ``step_min`` minutos, usando un arreglo de
    diferencias para que el cálculo sea O(n + m).
    """
    if step_min <= 0:
        raise ValueError("El paso debe ser positivo.")
    n_steps = int(math.ceil(horizon_min / step_min)) + 1
    diff = np.zeros(n_steps + 2, dtype=np.int32)
    for customer in records:
        start = customer.arrival_time
        end = customer.service_end if customer.service_end is not None else start
        lo = int(math.ceil(start / step_min))
        hi = int(math.ceil(end / step_min))
        lo = max(0, min(n_steps, lo))
        hi = max(0, min(n_steps + 1, hi))
        if hi > lo:
            diff[lo] += 1
            diff[hi] -= 1
    values = np.cumsum(diff[:n_steps])
    times = np.arange(n_steps, dtype=float) * step_min
    return times, values


def detectar_warmup_promedio_movil(
    series: Sequence[float],
    *,
    window: int = 60,
    tolerance_rel: float = 0.15,
) -> dict[str, object]:
    """Detecta el fin del transitorio con el método gráfico del promedio móvil.

    Procedimiento (tipo Welch):

    1. Se calcula el promedio móvil de ``window`` observaciones de la serie.
    2. La referencia de estado estable es la media de la segunda mitad.
    3. La banda de aceptación es
       ``max(tolerance_rel * |referencia|, 2 * s / sqrt(window))``, donde
       ``s`` es la desviación estándar de la segunda mitad.  El segundo
       término reconoce el ruido propio del promedio móvil.
    4. El corte es el final de la primera ventana que entra en la banda y,
       además, deja una media posterior dentro de la misma banda.  Con eso se
       evita confundir una fluctuación aislada con el fin del transitorio.

    Devuelve el índice y el minuto de corte (la serie se muestrea cada
    minuto), la serie suavizada y los parámetros usados.
    """
    x = np.asarray(series, dtype=float)
    n = len(x)
    if n < 4:
        return {
            "cut_index": 0,
            "cut_min": 0.0,
            "moving_average": np.array([], dtype=float),
            "reference_mean": float(np.mean(x)) if n else 0.0,
            "tolerance": 0.0,
            "window": window,
        }

    window = int(max(5, min(window, n // 4)))
    kernel = np.ones(window, dtype=float) / window
    moving_average = np.convolve(x, kernel, mode="valid")

    steady = x[n // 2 :]
    reference_mean = float(np.mean(steady))
    steady_std = float(np.std(steady, ddof=1)) if len(steady) > 1 else 0.0
    tolerance = max(
        tolerance_rel * abs(reference_mean),
        2.0 * steady_std / math.sqrt(window),
    )
    if tolerance <= 0:
        tolerance = 1e-9

    cut_index = 0
    for i in range(len(moving_average)):
        after = x[i + window :]
        if len(after) < 2 * window:
            break
        if (
            abs(float(moving_average[i]) - reference_mean) <= tolerance
            and abs(float(np.mean(after)) - reference_mean) <= tolerance
        ):
            # La ventana i cubre x[i : i + window]; el transitorio termina
            # al final de esa ventana.
            cut_index = min(n, i + window)
            break

    return {
        "cut_index": int(cut_index),
        "cut_min": float(cut_index),
        "moving_average": moving_average,
        "reference_mean": reference_mean,
        "tolerance": float(tolerance),
        "window": window,
    }


def run_pilot(
    duration_min: float = DEFAULT_PILOT_DURATION_MIN,
    *,
    master_seed: int = DEFAULT_MASTER_SEED,
    scenario_key: str = MAIN_SCENARIO,
) -> dict[str, object]:
    """Corrida piloto larga para estimar el calentamiento y la convergencia."""
    scenario = SCENARIOS[scenario_key]
    root = np.random.SeedSequence(master_seed)
    arrival_sequence, service_sequence, dispatch_sequence = root.spawn(3)
    arrivals = generate_arrivals(
        duration_min, np.random.default_rng(arrival_sequence)
    )
    assign_service_times(arrivals, np.random.default_rng(service_sequence))
    records = simulate_scenario(
        scenario, arrivals, np.random.default_rng(dispatch_sequence)
    )
    times, series = number_in_system_series(records, duration_min, step_min=1.0)
    moving = detectar_warmup_promedio_movil(series)

    # La media acumulada permite mostrar el "antes" y el "después".
    cumulative = np.cumsum(series) / np.arange(1, len(series) + 1)
    cut = int(moving["cut_index"])
    after = series[cut:]
    cumulative_after = np.cumsum(after) / np.arange(1, len(after) + 1)

    return {
        "duration_min": duration_min,
        "scenario": scenario_key,
        "times": times,
        "series": series,
        "cumulative": cumulative,
        "moving_average": moving["moving_average"],
        "cut_index": cut,
        "cut_min": float(cut),
        "reference_mean": moving["reference_mean"],
        "tolerance": moving["tolerance"],
        "window": moving["window"],
        "after": after,
        "cumulative_after": cumulative_after,
        "mean_before": float(np.mean(series)),
        "mean_after": float(np.mean(after)) if len(after) else 0.0,
        "records": records,
    }


def estimar_replicas_requeridas(
    values: Sequence[float],
    *,
    target_relative_error: float = 0.10,
    confidence: float = 0.95,
    min_replicas: int = DEFAULT_REPLICAS,
    max_replicas: int = 200,
) -> dict[str, object]:
    """Número de réplicas para un error relativo objetivo del IC 95 %.

    Usa la aproximación normal/t de Student: ``n = (t * s / (e * media))^2``.
    Se itera porque ``t`` depende de los grados de libertad.
    """
    from scipy import stats  # import local para no cargar SciPy en el motor

    data = np.asarray([v for v in values if np.isfinite(v)], dtype=float)
    if len(data) < 2:
        return {
            "n_actual": len(data),
            "n_requerido": min_replicas,
            "media": float(np.mean(data)) if len(data) else 0.0,
            "desviacion": 0.0,
            "error_relativo_actual": float("nan"),
            "target_relative_error": target_relative_error,
        }

    mean = float(np.mean(data))
    std = float(np.std(data, ddof=1))
    n_actual = len(data)
    n_required = n_actual
    if mean > 0 and std > 0:
        n_required = n_actual
        for _ in range(50):
            critical = float(stats.t.ppf((1 + confidence) / 2, max(1, n_required - 1)))
            candidate = int(
                math.ceil((critical * std / (target_relative_error * mean)) ** 2)
            )
            candidate = max(min_replicas, min(max_replicas, candidate))
            if candidate == n_required:
                break
            n_required = candidate

    critical_actual = float(stats.t.ppf((1 + confidence) / 2, max(1, n_actual - 1)))
    half_width_actual = critical_actual * std / math.sqrt(n_actual)
    return {
        "n_actual": n_actual,
        "n_requerido": int(n_required),
        "media": mean,
        "desviacion": std,
        "error_relativo_actual": (
            half_width_actual / mean if mean else float("nan")
        ),
        "target_relative_error": target_relative_error,
    }


# ----------------------------------------------------------------------
# Experimento completo
# ----------------------------------------------------------------------
@dataclass
class ExperimentResult:
    """Resultado completo del experimento de parqueaderos."""

    metadata: dict[str, object]
    replica_rows: list[dict[str, object]] = field(default_factory=list)
    teller_rows: list[dict[str, object]] = field(default_factory=list)
    customer_rows: list[dict[str, object]] = field(default_factory=list)

    def to_dict(self, include_customers: bool = False) -> dict[str, object]:
        payload: dict[str, object] = {
            "metadata": self.metadata,
            "replicas": self.replica_rows,
            "tellers": self.teller_rows,
        }
        if include_customers:
            payload["customers"] = self.customer_rows
        return payload


def run_experiment(
    replicas: int = DEFAULT_REPLICAS,
    duration_min: float = DEFAULT_DURATION_MIN,
    warmup_min: float = DEFAULT_WARMUP_MIN,
    master_seed: int = DEFAULT_MASTER_SEED,
    scenario_keys: Sequence[str] | None = None,
) -> ExperimentResult:
    """Ejecuta el experimento completo para todos los escenarios.

    Para cada réplica se generan una sola vez las llegadas y los tiempos de
    servicio.  Luego se simulan todos los escenarios con esos mismos usuarios;
    solo cambia la política de filas.
    """
    if replicas < 1:
        raise ValueError("El número de réplicas debe ser al menos 1.")
    if duration_min <= 0:
        raise ValueError("La duración debe ser positiva.")
    if not 0 <= warmup_min < duration_min:
        raise ValueError("El calentamiento debe estar en [0, duración).")

    keys = tuple(scenario_keys) if scenario_keys is not None else DEFAULT_SCENARIO_KEYS
    unknown = [key for key in keys if key not in SCENARIOS]
    if unknown:
        raise ValueError(f"Escenarios desconocidos: {unknown}")
    scenarios = [SCENARIOS[key] for key in keys]

    replica_rows: list[dict[str, object]] = []
    teller_rows: list[dict[str, object]] = []
    customer_rows: list[dict[str, object]] = []

    root_sequence = np.random.SeedSequence(master_seed)
    replica_sequences = root_sequence.spawn(replicas)

    for replica, replica_sequence in enumerate(replica_sequences, start=1):
        arrival_sequence, service_sequence, dispatch_sequence = replica_sequence.spawn(3)
        arrivals = generate_arrivals(
            duration_min, np.random.default_rng(arrival_sequence)
        )
        assign_service_times(arrivals, np.random.default_rng(service_sequence))

        for scenario in scenarios:
            records = simulate_scenario(
                scenario,
                arrivals,
                # La misma secuencia de despacho se reinicia para cada
                # escenario: las diferencias provienen de la política de filas.
                np.random.default_rng(dispatch_sequence),
            )
            metrics = compute_replica_metrics(
                records, scenario, duration_min, warmup_min
            )
            metrics["replica"] = replica
            replica_rows.append(metrics)
            teller_rows.extend(compute_teller_rows(metrics, scenario, replica))
            for customer in records:
                customer_rows.append(customer_to_row(customer, scenario, replica))

    scenario_metadata: dict[str, object] = {}
    for scenario in scenarios:
        info = scenario.to_dict()
        info["offered_load"] = {
            "carga_total_erlangs": offered_load_erlangs(),
            "rho_por_cajero": offered_load_erlangs() / scenario.num_tellers,
            "estable": offered_load_erlangs() / scenario.num_tellers < 1.0,
        }
        scenario_metadata[scenario.key] = info

    metadata: dict[str, object] = {
        "activity": "AE4 - Solución de un problema de parqueaderos",
        "model": (
            "Servidores independientes con cola FIFO propia (M/M/1 por cajero) "
            "y llegadas marcadas por tipo de usuario"
        ),
        "duration_min": duration_min,
        "duration_hours": duration_min / 60.0,
        "warmup_min": warmup_min,
        "stable_window_min": duration_min - warmup_min,
        "replicas": replicas,
        "master_seed": master_seed,
        "seed_scheme": (
            "np.random.SeedSequence(master_seed).spawn(replicas); cada réplica "
            "se divide en tres secuencias hijas: llegadas, servicios y despacho."
        ),
        "common_random_numbers": (
            "Dentro de una réplica, todos los escenarios usan las mismas "
            "llegadas, tipos y tiempos de servicio; solo cambia la política "
            "de filas."
        ),
        "arrival_model": (
            "En cada llegada se sortea el tipo con probabilidades "
            "25/20/27.5/27.5 y luego el tiempo hasta la siguiente llegada con "
            "una exponencial cuya media depende del tipo (3, 3, 5 y 7 min)."
        ),
        "service_model": (
            "Tiempo de servicio exponencial con media según tipo "
            "(1, 3, 4 y 6 min)."
        ),
        "assignment_model": (
            "Por defecto, cada usuario elige un cajero al azar entre los tres "
            "y no cambia de fila.  Se simulan variantes de fila única, cola "
            "más corta y especialización."
        ),
        "drain_policy": (
            "Se generan llegadas hasta el minuto de cierre y luego se drena el "
            "sistema: todos los usuarios que llegaron terminan su servicio."
        ),
        "criteria": dict(CRITERIA),
        "scenarios": scenario_metadata,
        "mean_interarrival_min": mean_interarrival_min(),
        "mean_service_min": mean_service_min(),
        "offered_load_erlangs": offered_load_erlangs(),
        "theoretical_mm1_by_type": {
            user_type: theoretical_mm1(user_type) for user_type in USER_TYPES
        },
        "theoretical_mg1_per_teller": theoretical_mg1_per_teller(3),
    }

    return ExperimentResult(
        metadata=metadata,
        replica_rows=replica_rows,
        teller_rows=teller_rows,
        customer_rows=customer_rows,
    )


# ----------------------------------------------------------------------
# Validación con la teoría M/M/1
# ----------------------------------------------------------------------
def run_single_type_experiment(
    user_type: str,
    *,
    replicas: int = DEFAULT_REPLICAS,
    duration_min: float = 5_000.0,
    warmup_min: float = 500.0,
    master_seed: int = DEFAULT_MASTER_SEED,
) -> dict[str, object]:
    """Simula un sistema de un cajero que atiende solo un tipo de usuario.

    En este caso el modelo es exactamente M/M/1: llegadas exponenciales con
    media ``ARRIVAL_MEAN_MIN[user_type]`` y servicio exponencial con media
    ``SERVICE_MEAN_MIN[user_type]``.  Sirve para validar el simulador contra
    las fórmulas analíticas.
    """
    scenario = Scenario(
        key=f"validacion_{user_type}",
        label=f"Validación M/M/1 - {USER_TYPE_LABELS[user_type]}",
        description="Un cajero dedicado a un solo tipo de usuario.",
        teller_allowed=(None,),
    )
    root = np.random.SeedSequence(master_seed)
    rows: list[dict[str, object]] = []
    for replica, replica_sequence in enumerate(root.spawn(replicas), start=1):
        arrival_sequence, service_sequence, dispatch_sequence = replica_sequence.spawn(3)
        arrivals = generate_arrivals(
            duration_min,
            np.random.default_rng(arrival_sequence),
            only_type=user_type,
        )
        assign_service_times(arrivals, np.random.default_rng(service_sequence))
        records = simulate_scenario(
            scenario, arrivals, np.random.default_rng(dispatch_sequence)
        )
        metrics = compute_replica_metrics(
            records, scenario, duration_min, warmup_min
        )
        rows.append(
            {
                "user_type": user_type,
                "user_type_label": USER_TYPE_LABELS[user_type],
                "replica": replica,
                "mean_wait": metrics["mean_wait"],
                "mean_system": metrics["mean_system"],
                "Lq": metrics["Lq"],
                "L": metrics["L"],
                "utilization": metrics["utilization"],
                "n": metrics["total_customers"],
            }
        )
    return {
        "user_type": user_type,
        "theory": theoretical_mm1(user_type),
        "rows": rows,
    }


# ----------------------------------------------------------------------
# Resumen para consola
# ----------------------------------------------------------------------
def evaluate_criteria(metrics: dict[str, object]) -> dict[str, object]:
    """Evalúa un escenario contra los criterios de decisión del punto C."""
    wq = float(metrics["mean_wait"])
    w = float(metrics["mean_system"])
    lq = float(metrics["Lq"])
    util = float(metrics["max_teller_utilization"])
    p5 = float(metrics["frac_wait_gt_5"])

    checks = {
        "espera_cola": wq <= CRITERIA["espera_cola_aceptable_min"],
        "espera_sistema": w <= CRITERIA["espera_sistema_critica_min"],
        "cola_promedio": lq <= CRITERIA["cola_maxima_aceptable"],
        "utilizacion": util <= CRITERIA["utilizacion_maxima"],
        "prob_espera_5": p5 <= CRITERIA["prob_espera_5_max"],
    }
    return {
        **checks,
        "cumple_servicio": all(checks.values()),
        "utilizacion_en_rango_eficiente": (
            CRITERIA["utilizacion_minima_eficiente"] <= util <= CRITERIA["utilizacion_maxima"]
        ),
        "sobrecapacidad": util < CRITERIA["utilizacion_minima_eficiente"],
        "espera_cola_critica": wq > CRITERIA["espera_cola_critica_min"],
        "espera_sistema_critica": w > CRITERIA["espera_sistema_critica_min"],
        "valor_wq": wq,
        "valor_w": w,
        "valor_lq": lq,
        "valor_utilizacion": util,
        "valor_p5": p5,
    }


def format_summary(result: ExperimentResult) -> str:
    """Resumen legible para consola."""
    lines: list[str] = []
    lines.append("=" * 92)
    lines.append("EXPERIMENTO PARQUEADERO - RESUMEN")
    lines.append("=" * 92)
    lines.append(
        f"Réplicas: {result.metadata['replicas']} | "
        f"Duración: {result.metadata['duration_min']} min | "
        f"Calentamiento: {result.metadata['warmup_min']} min | "
        f"Semilla: {result.metadata['master_seed']}"
    )
    lines.append(
        f"Media entre llegadas: {result.metadata['mean_interarrival_min']:.3f} min | "
        f"Media de servicio: {result.metadata['mean_service_min']:.3f} min | "
        f"Carga ofrecida: {result.metadata['offered_load_erlangs']:.3f} erlangs"
    )
    lines.append("")
    lines.append(
        f"{'Escenario':<46} {'Caj.':>4} {'Wq':>6} {'W':>6} "
        f"{'Lq':>5} {'Util.':>6} {'P>5':>6} {'¿Cumple?':>9}"
    )
    lines.append("-" * 92)

    for key, info in result.metadata["scenarios"].items():  # type: ignore[union-attr]
        rows = [r for r in result.replica_rows if r["scenario"] == key]
        if not rows:
            continue
        mean_wq = sum(float(r["mean_wait"]) for r in rows) / len(rows)
        mean_w = sum(float(r["mean_system"]) for r in rows) / len(rows)
        mean_lq = sum(float(r["Lq"]) for r in rows) / len(rows)
        max_util = sum(float(r["max_teller_utilization"]) for r in rows) / len(rows)
        mean_p5 = sum(float(r["frac_wait_gt_5"]) for r in rows) / len(rows)
        evaluation = evaluate_criteria(
            {
                "mean_wait": mean_wq,
                "mean_system": mean_w,
                "Lq": mean_lq,
                "max_teller_utilization": max_util,
                "frac_wait_gt_5": mean_p5,
            }
        )
        lines.append(
            f"{info['label']:<46} {info['num_tellers']:>4} "
            f"{mean_wq:>6.2f} {mean_w:>6.2f} {mean_lq:>5.2f} "
            f"{max_util:>6.1%} {mean_p5:>6.1%} "
            f"{'Sí' if evaluation['cumple_servicio'] else 'No':>9}"
        )

    lines.append("")
    lines.append("Las cifras son simuladas. Ver outputs/ para tablas y figuras.")
    return "\n".join(lines)
