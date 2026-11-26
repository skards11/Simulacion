# Resumen de ejecución — AE4 Parqueadero

> Todas las cifras son simuladas.  No provienen de datos reales del Centro Comercial Supercentro.

## Configuración del experimento

- Réplicas: **32**
- Jornada simulada: **720 min** (12 h)
- Calentamiento eliminado: **102 min**
- Semilla maestra: **42**
- Media entre llegadas: **4.650 min**
- Media de servicio: **3.600 min**
- Carga ofrecida: **0.774 erlangs**


## Punto A — Estadísticas por cajero

| Cajero | Atendidos | Servicio prom. (min) | IC inf. | IC sup. | Mín. obs. | Máx. obs. | Espera prom. (min) | Utilización |
|---|---|---|---|---|---|---|---|---|
| 1 | 44.75 | 3.52 | 3.30 | 3.74 | 0.00 | 38.64 | 1.57 | 0.26 |
| 2 | 45.34 | 3.53 | 3.30 | 3.76 | 0.00 | 46.85 | 1.64 | 0.26 |
| 3 | 43.59 | 3.56 | 3.34 | 3.79 | 0.00 | 48.96 | 1.52 | 0.25 |

**Prueba de Friedman:** p = 0.804. No hay evidencia de diferencias significativas entre los tiempos promedio de atención de los cajeros (p > 0.05).


## Punto B — Promedio de usuarios por tipo

| Tipo | Promedio | IC inf. | IC sup. | % obs. | % esp. | Servicio (min) | Espera (min) | P90 espera | Sistema (min) |
|---|---|---|---|---|---|---|---|---|---|
| Rápido | 39.81 | 36.97 | 42.66 | 25.50 | 25.00 | 0.98 | 2.01 | 6.97 | 2.99 |
| Normal | 31.44 | 28.99 | 33.88 | 20.13 | 20.00 | 2.97 | 1.62 | 4.94 | 4.58 |
| Lento | 41.75 | 39.71 | 43.79 | 26.74 | 27.50 | 4.02 | 1.55 | 5.86 | 5.56 |
| Muy lento | 43.16 | 40.97 | 45.34 | 27.64 | 27.50 | 5.85 | 1.20 | 4.03 | 7.05 |

**Chi-cuadrado de composición:** χ² = 1.628, p = 0.653. La composición observada no difiere significativamente de la esperada 25/20/27.5/27.5 (p > 0.05).


## Punto C — Comparación de escenarios

| Ranking | Escenario | Cajeros | Wq (min) | W (min) | Lq | Util. máx. | P(>5 min) | ¿Cumple? | Recomendado |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 cajeros con fila única | 4 | 0.01 | 3.54 | 0.00 | 0.23 | 0.00 | Sí | No |
| 2 | 3 cajeros con fila única (mejora propuesta) | 3 | 0.08 | 3.61 | 0.02 | 0.29 | 0.00 | Sí | Sí |
| 3 | 3 cajeros: libre al azar y, si todos ocupados, cola más corta | 3 | 0.20 | 3.74 | 0.04 | 0.29 | 0.01 | Sí | No |
| 4 | 2 cajeros con fila única | 2 | 0.73 | 4.26 | 0.16 | 0.41 | 0.05 | Sí | No |
| 5 | 5 cajeros con filas independientes | 5 | 0.93 | 4.47 | 0.20 | 0.21 | 0.06 | Sí | No |
| 6 | 3 cajeros: cada usuario elige la cola más corta | 3 | 0.97 | 4.51 | 0.21 | 0.30 | 0.07 | Sí | No |
| 7 | 4 cajeros con filas independientes | 4 | 1.07 | 4.61 | 0.23 | 0.24 | 0.08 | Sí | No |
| 8 | 3 cajeros con filas independientes (actual) | 3 | 1.61 | 5.15 | 0.35 | 0.30 | 0.12 | No | No |
| 9 | 2 cajeros con filas independientes | 2 | 2.77 | 6.30 | 0.61 | 0.42 | 0.19 | No | No |
| 10 | 1 cajero para lentos + 2 para rápidos/normales | 3 | 3.59 | 7.13 | 0.79 | 0.59 | 0.21 | No | No |

### Decisión

**Con la configuración actual (3 cajeros, Filas independientes (elección aleatoria)) la espera promedio en cola es 1.61 min, el tiempo en el sistema es 5.15 min y 12.0% de los usuarios espera más de 5 min. Incumple: Probabilidad de esperar más de 5 min. La recomendación es '3 cajeros con fila única (mejora propuesta)': espera en cola 0.08 min, tiempo en el sistema 3.61 min y 0.2% de usuarios con espera mayor a 5 min. La configuración actual no cumple todos los criterios, pero con los mismos tres cajeros existe una alternativa que sí cumple: 3 cajeros con fila única (mejora propuesta). Por eso no es necesario instalar cajeros adicionales; se cambia la política de filas.**


- Opción de menor costo que cumple: **2 cajeros con fila única** (2 cajeros, Wq = 0.73 min).

- Mejor desempeño absoluto: **4 cajeros con fila única** (Wq = 0.01 min).


## Punto D — Verificación, calibración y validación

| Prueba | Resultado | Detalle |
|---|---|---|
| Identificadores únicos por escenario y réplica | Cumple | 0 duplicados encontrados. |
| Todos los usuarios que llegan terminan su servicio (drenaje) | Cumple | 49970 registros con inicio y fin de servicio. |
| El servicio nunca inicia antes de la llegada | Cumple | Violaciones: 0. |
| El servicio termina después de iniciar | Cumple | Violaciones: 0. |
| Tiempos de servicio positivos y esperas no negativas | Cumple | Se verifican todas las filas de clientes. |
| Cada usuario es atendido por un cajero válido y solo uno | Cumple | No hay usuarios con más de un cajero ni cajeros fuera de rango. |
| Utilización de cada cajero en [0, 1] | Cumple | Rango observado: [0.124, 0.486]. |
| Longitudes promedio de cola y sistema no negativas | Cumple | Integración temporal sobre la ventana de estado estable. |
| Conservación de usuarios (sin pérdidas ni duplicados) | Cumple | Los identificadores consecutivos cubren todas las llegadas. |

### Calibración de tiempos de servicio

| Parámetro | Nominal | Estimado | Error (%) | n | KS | p KS | Ajusta |
|---|---|---|---|---|---|---|---|
| Tiempo de servicio - Rápido | 1.00 | 0.98 | -2.41 | 1274 | 0.02 | 0.84 | Sí |
| Tiempo de servicio - Normal | 3.00 | 2.95 | -1.59 | 1006 | 0.02 | 0.82 | Sí |
| Tiempo de servicio - Lento | 4.00 | 4.01 | 0.20 | 1336 | 0.01 | 0.92 | Sí |
| Tiempo de servicio - Muy lento | 6.00 | 5.86 | -2.38 | 1381 | 0.01 | 0.95 | Sí |

### Calibración de la tasa de llegadas

| Parámetro | Nominal | Estimado | Error (%) | IC inf. | IC sup. |
|---|---|---|---|---|---|
| Tasa de llegadas (λ) | 0.2151 | 0.2163 | 0.5900 | 0.2103 | 0.2223 |

### Validación contra la teoría

| Tipo | Métrica | Teoría | Simulación | Error (%) | p | Validado |
|---|---|---|---|---|---|---|
| Rápido | Tiempo en el sistema (W) | 1.50 | 1.49 | -0.39 | 0.57 | Sí |
| Rápido | Tiempo en cola (Wq) | 0.50 | 0.49 | -1.05 | 0.53 | Sí |
| Rápido | Usuarios en el sistema (L) | 0.50 | 0.50 | -0.07 | — | Sí |
| Rápido | Usuarios en cola (Lq) | 0.17 | 0.17 | -0.71 | — | Sí |
| Lento | Tiempo en el sistema (W) | 20.00 | 19.91 | -0.48 | 0.91 | Sí |
| Lento | Tiempo en cola (Wq) | 16.00 | 15.91 | -0.55 | 0.91 | Sí |
| Lento | Usuarios en el sistema (L) | 4.00 | 3.98 | -0.51 | — | Sí |
| Lento | Usuarios en cola (Lq) | 3.20 | 3.18 | -0.52 | — | Sí |
| Muy lento | Tiempo en el sistema (W) | 42.00 | 41.04 | -2.28 | 0.74 | Sí |
| Muy lento | Tiempo en cola (Wq) | 36.00 | 35.06 | -2.61 | 0.74 | Sí |
| Muy lento | Usuarios en el sistema (L) | 6.00 | 5.85 | -2.45 | — | Sí |
| Muy lento | Usuarios en cola (Lq) | 5.14 | 5.01 | -2.67 | — | Sí |


| Métrica | M/G/1 | Simulación | Error (%) | Validado |
|---|---|---|---|---|
| Tiempo en cola (Wq) | 1.58 | 1.58 | -0.19 | Sí |
| Tiempo en el sistema (W) | 5.18 | 5.11 | -1.28 | Sí |
| Usuarios en cola (Lq) | 0.11 | 0.12 | 3.43 | Sí |

## Punto E — Eliminación del estado transitorio

- Corte detectado: **102 min**.
- Media de N(t) en el primer bloque: **0.598** usuarios.
- Media de N(t) después del corte: **1.189** usuarios.

| Métrica | Antes | Después | Diferencia | Cambio (%) |
|---|---|---|---|---|
| N(t): primeros 102 min | 0.60 | 1.19 | 0.59 | 98.78 |
| N(t): horizonte completo | 1.18 | 1.19 | 0.01 | 0.51 |
| Tiempo promedio en cola (Wq, min) | 1.57 | 1.61 | 0.04 | 2.66 |
| Tiempo promedio en el sistema (W, min) | 5.11 | 5.15 | 0.04 | 0.73 |
| Longitud promedio de la cola (Lq) | 0.34 | 0.35 | 0.01 | 3.35 |
| Usuarios promedio en el sistema (L) | 1.10 | 1.12 | 0.02 | 1.51 |
| Tiempo promedio de servicio (min) | 3.54 | 3.54 | -0.00 | -0.13 |

## Figuras

- `outputs/figuras/fig_sistema.png`: Esquema del sistema de tres cajeros independientes.
- `outputs/figuras/fig_transitorio.png`: Determinación del estado estable con promedio móvil.
- `outputs/figuras/fig_replicas_convergencia.png`: Convergencia de la media con el número de réplicas.
- `outputs/figuras/fig_cajeros.png`: Tiempo de atención y utilización por cajero.
- `outputs/figuras/fig_tipos.png`: Composición de la demanda y esperas por tipo.
- `outputs/figuras/fig_escenarios.png`: Comparación de escenarios y criterios.
- `outputs/figuras/fig_vv_flujo.png`: Proceso de verificación, calibración y validación.
- `outputs/figuras/fig_validacion.png`: Validación contra la teoría M/M/1 y M/G/1.
- `outputs/figuras/fig_calibracion.png`: Calibración de tiempos de servicio.
- `outputs/figuras/fig_antes_despues.png`: Antes y después de eliminar el transitorio.
