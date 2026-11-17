"""Simulación de eventos discretos del problema bancario (AE3).

Modelo implementado
-------------------
* Un día de operación de 480 minutos (8 horas), configurable.
* Llegadas generadas de forma secuencial: primero se sortea la acción
  (70 % retiro, 30 % consignación/pago), luego el tipo de usuario con las
  probabilidades condicionales de la Tabla 2 y finalmente el tiempo entre
  llegadas con una distribución exponencial cuya media depende del tipo
  (Tabla 1).
* Cada cajero es un servidor M/M/1 independiente con cola FIFO propia.
  El tiempo de servicio es exponencial con media según acción y tipo.
* Asignación de clientes: entre los cajeros que pueden atender la acción,
  se elige uno libre al azar; si todos están ocupados, se elige el de menor
  cola (desempate aleatorio). Así se evita favorecer siempre al cajero 1.
* Se generan llegadas hasta el minuto 480, pero el sistema se drena: los
  clientes que ya llegaron terminan su servicio aunque el reloj supere las
  8 horas. Esto evita truncar las esperas más largas.
* Diseño de números aleatorios comunes: para una misma réplica, todas las
  configuraciones reciben exactamente las mismas llegadas, tipos de usuario
  y tiempos de servicio. Solo cambia la asignación a cajeros. Esto permite
  comparar configuraciones de forma pareada y reducir el ruido.

Las cifras que produce este módulo son simuladas y no provienen de datos
reales del Banco de Colombia.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field, replace
import heapq
from typing import Iterable, Sequence

import numpy as np

# ----------------------------------------------------------------------
# Datos del enunciado
# ----------------------------------------------------------------------
ACTIONS: tuple[str, ...] = ("retiro", "pago")
ACTION_LABELS: dict[str, str] = {
    "retiro": "Retiro",
    "pago": "Consignación o pago",
}

USER_TYPES: tuple[str, ...] = ("rapido", "normal", "lento", "muy_lento")
USER_TYPE_LABELS: dict[str, str] = {
    "rapido": "Rápido",
    "normal": "Normal",
    "lento": "Lento",
    "muy_lento": "Muy lento",
}

DEFAULT_DURATION_MIN: int = 480
DEFAULT_REPLICAS: int = 30
DEFAULT_MASTER_SEED: int = 42

ACTION_PROB: dict[str, float] = {
    "retiro": 0.70,
    "pago": 0.30,
}

# Probabilidad del tipo de usuario condicionada a la acción (Tabla 2).
TYPE_PROB: dict[str, tuple[float, ...]] = {
    "retiro": (0.23, 0.40, 0.17, 0.20),
    "pago": (0.10, 0.20, 0.30, 0.40),
}

# Media del tiempo de servicio en minutos (Tabla 1).
SERVICE_MEAN: dict[str, tuple[float, ...]] = {
    "retiro": (1.0, 2.0, 3.0, 4.0),
    "pago": (3.0, 3.0, 5.0, 7.0),
}

# Media del tiempo entre llegadas en minutos (Tabla 1).
ARRIVAL_MEAN: dict[str, tuple[float, ...]] = {
    "retiro": (1.0, 2.0, 3.0, 3.0),
    "pago": (1.0, 2.0, 3.0, 4.0),
}

# Criterios de decisión usados en el análisis (punto 4 y 5).
# Son supuestos documentables: el banco puede cambiarlos.
SLA_DEFAULT: dict[str, float] = {
    "espera_promedio_max_min": 5.0,
    "espera_p90_max_min": 10.0,
    "fraccion_espera_mayor_10_max": 0.10,
    "utilizacion_maxima": 0.85,
}


# ----------------------------------------------------------------------
# Configuraciones de cajeros
# ----------------------------------------------------------------------
@dataclass(frozen=True)
class CashierSpec:
    """Especificación de una caja.

    ``action=None`` significa caja mixta (atiende retiros y pagos).
    """

    cashier_id: int
    action: str | None = None

    def accepts(self, action: str) -> bool:
        return self.action is None or self.action == action

    @property
    def label(self) -> str:
        if self.action is None:
            return "Mixta"
        return ACTION_LABELS[self.action]

    @property
    def action_key(self) -> str:
        return "mixto" if self.action is None else self.action


@dataclass(frozen=True)
class Scenario:
    """Configuración completa de cajeros de un escenario."""

    key: str
    label: str
    description: str
    cashiers: tuple[CashierSpec, ...]

    @property
    def num_cashiers(self) -> int:
        return len(self.cashiers)

    @property
    def num_retiro(self) -> int:
        return sum(1 for c in self.cashiers if c.action == "retiro")

    @property
    def num_pago(self) -> int:
        return sum(1 for c in self.cashiers if c.action == "pago")

    @property
    def num_mixto(self) -> int:
        return sum(1 for c in self.cashiers if c.action is None)

    def to_dict(self) -> dict[str, object]:
        return {
            "key": self.key,
            "label": self.label,
            "description": self.description,
            "num_cashiers": self.num_cashiers,
            "num_retiro": self.num_retiro,
            "num_pago": self.num_pago,
            "num_mixto": self.num_mixto,
            "cashiers": [
                {
                    "cashier_id": c.cashier_id,
                    "action": c.action_key,
                    "label": c.label,
                }
                for c in self.cashiers
            ],
        }


def _make_scenario(
    key: str,
    label: str,
    description: str,
    actions: Sequence[str | None],
) -> Scenario:
    cashiers = tuple(
        CashierSpec(cashier_id=i, action=action)
        for i, action in enumerate(actions)
    )
    return Scenario(key=key, label=label, description=description, cashiers=cashiers)


SCENARIOS: dict[str, Scenario] = {
    "mixto_3": _make_scenario(
        "mixto_3",
        "3 cajas mixtas (actual)",
        "Las tres cajas atienden retiros y pagos.",
        (None, None, None),
    ),
    "retiro_1_pago_2": _make_scenario(
        "retiro_1_pago_2",
        "1 caja de retiros + 2 de pagos",
        "Una caja exclusiva para retiros y dos exclusivas para pagos.",
        ("retiro", "pago", "pago"),
    ),
    "retiro_2_pago_1": _make_scenario(
        "retiro_2_pago_1",
        "2 cajas de retiros + 1 de pagos",
        "Dos cajas exclusivas para retiros y una exclusiva para pagos.",
        ("retiro", "retiro", "pago"),
    ),
    "mixto_4": _make_scenario(
        "mixto_4",
        "4 cajas mixtas",
        "Se agrega una cuarta caja que atiende retiros y pagos.",
        (None, None, None, None),
    ),
    "retiro_2_pago_2": _make_scenario(
        "retiro_2_pago_2",
        "2 cajas de retiros + 2 de pagos",
        "Configuración especializada con cuatro cajas.",
        ("retiro", "retiro", "pago", "pago"),
    ),
    "retiro_3_pago_1": _make_scenario(
        "retiro_3_pago_1",
        "3 cajas de retiros + 1 de pagos",
        "Configuración especializada con cuatro cajas, priorizando retiros.",
        ("retiro", "retiro", "retiro", "pago"),
    ),
    "retiro_1_pago_3": _make_scenario(
        "retiro_1_pago_3",
        "1 caja de retiros + 3 de pagos",
        "Configuración especializada con cuatro cajas, priorizando pagos.",
        ("retiro", "pago", "pago", "pago"),
    ),
}

DEFAULT_SCENARIO_KEYS: tuple[str, ...] = tuple(SCENARIOS)


# ----------------------------------------------------------------------
# Utilidades estadísticas y de carga ofrecida
# ----------------------------------------------------------------------
def _weighted_mean(values: Sequence[float], weights: Sequence[float]) -> float:
    return float(sum(v * w for v, w in zip(values, weights)))


def mean_interarrival_min() -> float:
    """Media incondicional del tiempo entre llegadas de una llegada cualquiera."""
    return sum(
        ACTION_PROB[action] * _weighted_mean(ARRIVAL_MEAN[action], TYPE_PROB[action])
        for action in ACTIONS
    )


def mean_service_min() -> float:
    """Media incondicional del tiempo de servicio de un cliente cualquiera."""
    return sum(
        ACTION_PROB[action] * _weighted_mean(SERVICE_MEAN[action], TYPE_PROB[action])
        for action in ACTIONS
    )


def action_offered_load(action: str) -> float:
    """Carga ofrecida (en servidores) que genera una acción por unidad de tiempo."""
    return (
        ACTION_PROB[action]
        * _weighted_mean(SERVICE_MEAN[action], TYPE_PROB[action])
        / mean_interarrival_min()
    )


def scenario_offered_load(scenario: Scenario) -> dict[str, float]:
    """Carga ofrecida y utilización teórica aproximada por grupo de cajas."""
    total_load = sum(action_offered_load(action) for action in ACTIONS)
    rho_global = total_load / scenario.num_cashiers
    result: dict[str, float] = {"carga_total": total_load, "rho_global": rho_global}
    for action in ACTIONS:
        n_servers = sum(1 for c in scenario.cashiers if c.accepts(action))
        load = action_offered_load(action)
        result[f"carga_{action}"] = load
        result[f"rho_{action}"] = load / n_servers if n_servers else float("inf")
    result["estable"] = all(
        result[f"rho_{action}"] < 1.0 for action in ACTIONS
    ) and rho_global < 1.0
    return result


# ----------------------------------------------------------------------
# Entidades de la simulación
# ----------------------------------------------------------------------
@dataclass
class Customer:
    customer_id: int
    action: str
    user_type: str
    arrival_time: float
    service_time: float
    cashier: int | None = None
    service_start: float | None = None
    service_end: float | None = None

    @property
    def wait_time(self) -> float:
        if self.service_start is None:
            return 0.0
        return self.service_start - self.arrival_time

    @property
    def system_time(self) -> float:
        if self.service_end is None:
            return 0.0
        return self.service_end - self.arrival_time


def generate_arrivals(
    duration_min: float,
    rng: np.random.Generator,
) -> list[Customer]:
    """Genera las llegadas de un día de operación.

    La primera llegada ocurre después de un tiempo exponencial; no se fuerza
    un cliente en t=0. Se incluyen las llegadas con tiempo <= duration_min.
    """
    arrivals: list[Customer] = []
    t = 0.0
    customer_id = 0
    while True:
        action = "retiro" if rng.random() < ACTION_PROB["retiro"] else "pago"
        type_index = int(rng.choice(len(USER_TYPES), p=TYPE_PROB[action]))
        t += float(rng.exponential(ARRIVAL_MEAN[action][type_index]))
        if t > duration_min:
            break
        arrivals.append(
            Customer(
                customer_id=customer_id,
                action=action,
                user_type=USER_TYPES[type_index],
                arrival_time=t,
                service_time=0.0,
            )
        )
        customer_id += 1
    return arrivals


def assign_service_times(
    arrivals: Iterable[Customer],
    rng: np.random.Generator,
) -> None:
    """Asigna a cada cliente su tiempo de servicio exponencial (in situ)."""
    for customer in arrivals:
        type_index = USER_TYPES.index(customer.user_type)
        customer.service_time = float(
            rng.exponential(SERVICE_MEAN[customer.action][type_index])
        )


class _Simulator:
    """Motor de eventos discretos para una configuración y una réplica."""

    def __init__(self, scenario: Scenario, rng: np.random.Generator) -> None:
        self.scenario = scenario
        self.rng = rng
        self.queues: list[deque[Customer]] = [
            deque() for _ in scenario.cashiers
        ]
        self.busy: list[bool] = [False] * scenario.num_cashiers
        self.current: list[Customer | None] = [None] * scenario.num_cashiers
        # (tiempo_fin, cajero, secuencia) para desempatar eventos simultáneos.
        self.completion_heap: list[tuple[float, int, int]] = []
        self.event_sequence = 0
        self.records: list[Customer] = []

    def _start_service(
        self,
        customer: Customer,
        cashier_id: int,
        start_time: float,
    ) -> None:
        spec = self.scenario.cashiers[cashier_id]
        if not spec.accepts(customer.action):
            raise ValueError(
                f"El cajero {cashier_id} no atiende la acción {customer.action}."
            )
        customer.cashier = cashier_id
        customer.service_start = start_time
        customer.service_end = start_time + customer.service_time
        self.current[cashier_id] = customer
        self.busy[cashier_id] = True
        self.records.append(customer)
        heapq.heappush(
            self.completion_heap,
            (customer.service_end, cashier_id, self.event_sequence),
        )
        self.event_sequence += 1

    def _process_completion(self) -> float:
        finish_time, cashier_id, _ = heapq.heappop(self.completion_heap)
        self.busy[cashier_id] = False
        self.current[cashier_id] = None

        # Si hay cola, el siguiente cliente comienza en el instante de salida.
        if self.queues[cashier_id]:
            next_customer = self.queues[cashier_id].popleft()
            self._start_service(next_customer, cashier_id, finish_time)
        return finish_time

    def _arrive(self, customer: Customer) -> None:
        eligible = [
            spec.cashier_id
            for spec in self.scenario.cashiers
            if spec.accepts(customer.action)
        ]
        if not eligible:
            raise ValueError(
                f"No hay cajeros que atiendan la acción {customer.action}."
            )

        idle = [i for i in eligible if not self.busy[i]]
        if idle:
            # Elección aleatoria entre cajas libres para no sesgar la carga.
            cashier_id = idle[int(self.rng.integers(len(idle)))]
            self._start_service(customer, cashier_id, customer.arrival_time)
            return

        # Todas ocupadas: la cola más corta; desempate aleatorio.
        min_queue = min(len(self.queues[i]) for i in eligible)
        candidates = [
            i for i in eligible if len(self.queues[i]) == min_queue
        ]
        cashier_id = candidates[int(self.rng.integers(len(candidates)))]
        self.queues[cashier_id].append(customer)

    def run(self, arrivals: Sequence[Customer]) -> list[Customer]:
        # Se copian los clientes para no modificar los datos compartidos entre
        # configuraciones (diseño de números aleatorios comunes).
        customers = [replace(customer) for customer in arrivals]

        for customer in customers:
            # Los fines de servicio anteriores o simultáneos liberan la caja
            # antes de asignar al nuevo cliente.
            while (
                self.completion_heap
                and self.completion_heap[0][0] <= customer.arrival_time
            ):
                self._process_completion()
            self._arrive(customer)

        # Drenaje: se atienden todos los clientes que ya habían llegado.
        while self.completion_heap:
            self._process_completion()

        return sorted(self.records, key=lambda c: c.customer_id)


def simulate_scenario(
    scenario: Scenario,
    arrivals: Sequence[Customer],
    rng: np.random.Generator,
) -> list[Customer]:
    """Simula una configuración con una lista de llegadas ya generadas."""
    return _Simulator(scenario, rng).run(arrivals)


# ----------------------------------------------------------------------
# Métricas
# ----------------------------------------------------------------------
def _overlap(start: float, end: float, lo: float, hi: float) -> float:
    """Longitud de la intersección entre [start, end] y [lo, hi]."""
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
) -> dict[str, object]:
    """Calcula las métricas de una réplica y una configuración."""
    records = list(records)
    waits = [c.wait_time for c in records]
    services = [c.service_time for c in records]
    systems = [c.system_time for c in records]

    by_action: dict[str, list[Customer]] = {
        action: [c for c in records if c.action == action] for action in ACTIONS
    }
    by_type: dict[str, list[Customer]] = {
        user_type: [c for c in records if c.user_type == user_type]
        for user_type in USER_TYPES
    }

    # Áreas para promedios temporales durante las 8 horas de operación.
    queue_area = sum(
        _overlap(c.arrival_time, c.service_start or c.arrival_time, 0.0, duration_min)
        for c in records
    )
    system_area = sum(
        _overlap(c.arrival_time, c.service_end or c.arrival_time, 0.0, duration_min)
        for c in records
    )

    cashier_rows: list[dict[str, float]] = []
    for spec in scenario.cashiers:
        subset = [c for c in records if c.cashier == spec.cashier_id]
        busy_time = sum(
            _overlap(
                c.service_start or 0.0,
                c.service_end or 0.0,
                0.0,
                duration_min,
            )
            for c in subset
        )
        cashier_queue_area = sum(
            _overlap(
                c.arrival_time,
                c.service_start or c.arrival_time,
                0.0,
                duration_min,
            )
            for c in subset
        )
        cashier_rows.append(
            {
                "cashier": spec.cashier_id,
                "served": len(subset),
                "mean_service": _mean([c.service_time for c in subset]),
                "mean_wait": _mean([c.wait_time for c in subset]),
                "utilization": busy_time / duration_min if duration_min else 0.0,
                "mean_queue_length": (
                    cashier_queue_area / duration_min if duration_min else 0.0
                ),
            }
        )

    result: dict[str, object] = {
        "scenario": scenario.key,
        "scenario_label": scenario.label,
        "num_cashiers": scenario.num_cashiers,
        "total_customers": len(records),
        "n_retiro": len(by_action["retiro"]),
        "n_pago": len(by_action["pago"]),
        "mean_wait": _mean(waits),
        "std_wait": _std(waits),
        "p50_wait": _percentile(waits, 50),
        "p90_wait": _percentile(waits, 90),
        "p95_wait": _percentile(waits, 95),
        "max_wait": float(max(waits)) if waits else 0.0,
        "mean_service": _mean(services),
        "std_service": _std(services),
        "mean_system": _mean(systems),
        "Lq": queue_area / duration_min if duration_min else 0.0,
        "L": system_area / duration_min if duration_min else 0.0,
        "utilization": (
            sum(float(row["utilization"]) for row in cashier_rows)
            / scenario.num_cashiers
            if scenario.num_cashiers
            else 0.0
        ),
        "max_cashier_utilization": max(
            (float(row["utilization"]) for row in cashier_rows), default=0.0
        ),
        "throughput_per_hour": (
            len(records) / (duration_min / 60.0) if duration_min else 0.0
        ),
        "frac_wait_gt_5": _fraction(waits, 5.0),
        "frac_wait_gt_10": _fraction(waits, 10.0),
        "frac_wait_gt_15": _fraction(waits, 15.0),
        "unfinished_at_close": sum(
            1 for c in records if (c.service_end or 0.0) > duration_min
        ),
        "waiting_at_close": sum(
            1 for c in records if (c.service_start or 0.0) > duration_min
        ),
    }

    for action in ACTIONS:
        subset = by_action[action]
        action_waits = [c.wait_time for c in subset]
        result[f"mean_wait_{action}"] = _mean(action_waits)
        result[f"p90_wait_{action}"] = _percentile(action_waits, 90)
        result[f"frac_wait_gt_10_{action}"] = _fraction(action_waits, 10.0)
        result[f"mean_service_{action}"] = _mean([c.service_time for c in subset])
        result[f"n_{action}"] = len(subset)

    for user_type in USER_TYPES:
        subset = by_type[user_type]
        result[f"n_{user_type}"] = len(subset)
        result[f"mean_wait_{user_type}"] = _mean([c.wait_time for c in subset])

    return result


def compute_cashier_row(
    records: Sequence[Customer],
    scenario: Scenario,
    spec: CashierSpec,
    replica: int,
    duration_min: float,
) -> dict[str, object]:
    """Fila de resultados por cajero y réplica."""
    subset = [c for c in records if c.cashier == spec.cashier_id]
    waits = [c.wait_time for c in subset]
    services = [c.service_time for c in subset]
    systems = [c.system_time for c in subset]
    busy_time = sum(
        _overlap(
            c.service_start or 0.0,
            c.service_end or 0.0,
            0.0,
            duration_min,
        )
        for c in subset
    )
    queue_area = sum(
        _overlap(
            c.arrival_time,
            c.service_start or c.arrival_time,
            0.0,
            duration_min,
        )
        for c in subset
    )
    return {
        "scenario": scenario.key,
        "scenario_label": scenario.label,
        "replica": replica,
        "cashier": spec.cashier_id,
        "cashier_label": spec.label,
        "allowed_action": spec.action_key,
        "served": len(subset),
        "n_retiro": sum(1 for c in subset if c.action == "retiro"),
        "n_pago": sum(1 for c in subset if c.action == "pago"),
        "mean_service": _mean(services),
        "std_service": _std(services),
        "mean_wait": _mean(waits),
        "p90_wait": _percentile(waits, 90),
        "max_wait": float(max(waits)) if waits else 0.0,
        "mean_system": _mean(systems),
        "p90_system": _percentile(systems, 90),
        "utilization": busy_time / duration_min if duration_min else 0.0,
        "mean_queue_length": queue_area / duration_min if duration_min else 0.0,
        "busy_minutes": busy_time,
    }


def customer_to_row(
    customer: Customer,
    scenario: Scenario,
    replica: int,
) -> dict[str, object]:
    """Convierte un cliente simulado en una fila plana para CSV."""
    cashier_label = ""
    if customer.cashier is not None:
        cashier_label = scenario.cashiers[customer.cashier].label
    return {
        "scenario": scenario.key,
        "scenario_label": scenario.label,
        "replica": replica,
        "customer_id": customer.customer_id,
        "cashier": customer.cashier,
        "cashier_label": cashier_label,
        "action": customer.action,
        "action_label": ACTION_LABELS[customer.action],
        "user_type": customer.user_type,
        "user_type_label": USER_TYPE_LABELS[customer.user_type],
        "arrival_time": customer.arrival_time,
        "service_start": customer.service_start,
        "service_end": customer.service_end,
        "wait_time": customer.wait_time,
        "service_time": customer.service_time,
        "system_time": customer.system_time,
    }


@dataclass
class ExperimentResult:
    """Resultado completo del experimento bancario."""

    metadata: dict[str, object]
    replica_rows: list[dict[str, object]] = field(default_factory=list)
    cashier_rows: list[dict[str, object]] = field(default_factory=list)
    customer_rows: list[dict[str, object]] = field(default_factory=list)
    type_count_rows: list[dict[str, object]] = field(default_factory=list)

    def to_dict(self, include_customers: bool = False) -> dict[str, object]:
        payload: dict[str, object] = {
            "metadata": self.metadata,
            "replicas": self.replica_rows,
            "cashiers": self.cashier_rows,
            "type_counts": self.type_count_rows,
        }
        if include_customers:
            payload["customers"] = self.customer_rows
        return payload


def run_experiment(
    replicas: int = DEFAULT_REPLICAS,
    duration_min: float = DEFAULT_DURATION_MIN,
    master_seed: int = DEFAULT_MASTER_SEED,
    scenario_keys: Sequence[str] | None = None,
) -> ExperimentResult:
    """Ejecuta el experimento completo para todas las configuraciones.

    Para cada réplica se generan una sola vez las llegadas y los tiempos de
    servicio. Luego se simulan todas las configuraciones con esos mismos
    clientes, cambiando únicamente la asignación a cajeros.
    """
    if replicas < 1:
        raise ValueError("El número de réplicas debe ser al menos 1.")
    if duration_min <= 0:
        raise ValueError("La duración debe ser positiva.")

    keys = tuple(scenario_keys) if scenario_keys is not None else DEFAULT_SCENARIO_KEYS
    unknown = [key for key in keys if key not in SCENARIOS]
    if unknown:
        raise ValueError(f"Escenarios desconocidos: {unknown}")
    scenarios = [SCENARIOS[key] for key in keys]

    replica_rows: list[dict[str, object]] = []
    cashier_rows: list[dict[str, object]] = []
    customer_rows: list[dict[str, object]] = []
    type_count_rows: list[dict[str, object]] = []

    root_sequence = np.random.SeedSequence(master_seed)
    replica_sequences = root_sequence.spawn(replicas)

    for replica, replica_sequence in enumerate(replica_sequences, start=1):
        arrival_sequence, service_sequence, dispatch_sequence = replica_sequence.spawn(3)

        arrivals = generate_arrivals(
            duration_min,
            np.random.default_rng(arrival_sequence),
        )
        assign_service_times(
            arrivals,
            np.random.default_rng(service_sequence),
        )

        for scenario in scenarios:
            # La misma secuencia de despacho se reinicia para cada escenario:
            # las diferencias provienen de la configuración, no de otra semilla.
            records = simulate_scenario(
                scenario,
                arrivals,
                np.random.default_rng(dispatch_sequence),
            )

            metrics = compute_replica_metrics(records, scenario, duration_min)
            metrics["replica"] = replica
            replica_rows.append(metrics)

            for customer in records:
                customer_rows.append(customer_to_row(customer, scenario, replica))

            for spec in scenario.cashiers:
                cashier_rows.append(
                    compute_cashier_row(
                        records,
                        scenario,
                        spec,
                        replica,
                        duration_min,
                    )
                )

            for action in ACTIONS:
                for user_type in USER_TYPES:
                    count = sum(
                        1
                        for c in records
                        if c.action == action and c.user_type == user_type
                    )
                    type_count_rows.append(
                        {
                            "scenario": scenario.key,
                            "scenario_label": scenario.label,
                            "replica": replica,
                            "action": action,
                            "action_label": ACTION_LABELS[action],
                            "user_type": user_type,
                            "user_type_label": USER_TYPE_LABELS[user_type],
                            "count": count,
                        }
                    )

    scenario_metadata: dict[str, object] = {}
    for scenario in scenarios:
        info = scenario.to_dict()
        info["offered_load"] = scenario_offered_load(scenario)
        scenario_metadata[scenario.key] = info

    metadata: dict[str, object] = {
        "activity": "AE3 - Problema bancario",
        "model": "M/M/1 independiente por cajero con colas FIFO",
        "duration_min": duration_min,
        "duration_hours": duration_min / 60.0,
        "replicas": replicas,
        "master_seed": master_seed,
        "seed_scheme": (
            "np.random.SeedSequence(master_seed).spawn(replicas); cada réplica "
            "se divide en tres secuencias hijas: llegadas, servicios y despacho."
        ),
        "common_random_numbers": (
            "Dentro de una réplica, todas las configuraciones usan las mismas "
            "llegadas, tipos de usuario y tiempos de servicio; solo cambia la "
            "asignación a cajeros."
        ),
        "arrival_model": (
            "Acción 70/30; tipo de usuario condicional a la acción (Tabla 2); "
            "tiempo entre llegadas exponencial con media de la Tabla 1."
        ),
        "service_model": (
            "Tiempo de servicio exponencial con media según acción y tipo "
            "(Tabla 1)."
        ),
        "assignment_model": (
            "Entre cajeros elegibles: si hay libres, se elige uno al azar; si "
            "todos están ocupados, se elige la cola más corta con desempate "
            "aleatorio."
        ),
        "drain_policy": (
            "Se generan llegadas hasta el minuto 480 y luego se drena el "
            "sistema: todos los clientes que llegaron terminan su servicio."
        ),
        "sla": dict(SLA_DEFAULT),
        "scenarios": scenario_metadata,
        "mean_interarrival_min": mean_interarrival_min(),
        "mean_service_min": mean_service_min(),
        "offered_load_total": sum(action_offered_load(a) for a in ACTIONS),
    }

    return ExperimentResult(
        metadata=metadata,
        replica_rows=replica_rows,
        cashier_rows=cashier_rows,
        customer_rows=customer_rows,
        type_count_rows=type_count_rows,
    )


def format_summary(result: ExperimentResult) -> str:
    """Resumen legible para consola."""
    lines: list[str] = []
    lines.append("=" * 78)
    lines.append("EXPERIMENTO BANCARIO - RESUMEN")
    lines.append("=" * 78)
    lines.append(
        f"Réplicas: {result.metadata['replicas']} | "
        f"Duración: {result.metadata['duration_min']} min | "
        f"Semilla: {result.metadata['master_seed']}"
    )
    lines.append(
        f"Media entre llegadas: {result.metadata['mean_interarrival_min']:.3f} min | "
        f"Media de servicio: {result.metadata['mean_service_min']:.3f} min"
    )
    lines.append("")
    lines.append(
        f"{'Escenario':<24} {'Cajas':>5} {'Espera':>8} {'P90':>8} "
        f"{'Retiro':>8} {'Pago':>8} {'Util.':>7}"
    )
    lines.append("-" * 78)

    # Promedio simple por escenario (el análisis formal usa pandas y IC).
    for key, info in result.metadata["scenarios"].items():  # type: ignore[union-attr]
        rows = [r for r in result.replica_rows if r["scenario"] == key]
        if not rows:
            continue
        mean_wait = sum(float(r["mean_wait"]) for r in rows) / len(rows)
        p90 = sum(float(r["p90_wait"]) for r in rows) / len(rows)
        wait_retiro = sum(float(r["mean_wait_retiro"]) for r in rows) / len(rows)
        wait_pago = sum(float(r["mean_wait_pago"]) for r in rows) / len(rows)
        util = sum(float(r["utilization"]) for r in rows) / len(rows)
        lines.append(
            f"{info['label']:<24} {info['num_cashiers']:>5} "
            f"{mean_wait:>8.2f} {p90:>8.2f} {wait_retiro:>8.2f} "
            f"{wait_pago:>8.2f} {util:>7.3f}"
        )

    lines.append("")
    lines.append("Las cifras son simuladas. Ver outputs/ para tablas y figuras.")
    return "\n".join(lines)
