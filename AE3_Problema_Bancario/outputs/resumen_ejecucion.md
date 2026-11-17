# Resumen de ejecución — Problema bancario AE3

> Todas las cifras son simuladas. La fuente es `outputs/resultados.json` y los CSV de esta carpeta.

## Configuración del experimento

- Réplicas: **30**
- Duración por réplica: **480.0 min**
- Semilla maestra: **42**
- Media entre llegadas: **2.398 min**
- Media de servicio: **3.198 min**
- Carga ofrecida total: **1.334 servidores**

## Ranking de configuraciones (punto 5)

|   Puesto | Recomendada   | Configuración                   |   Cajas |   Retiro |   Pago |   Mixtas |   Espera prom. (min) |   Espera retiro (min) |   Espera pago (min) |   P90 (min) |   Util. máx. | Cumple criterios   |
|---------:|:--------------|:--------------------------------|--------:|---------:|-------:|---------:|---------------------:|----------------------:|--------------------:|------------:|-------------:|:-------------------|
|        1 | False         | 4 cajas mixtas                  |       4 |        0 |      0 |        4 |                0.213 |                 0.209 |               0.224 |       0.024 |        0.364 | True               |
|        2 | False         | 2 cajas de retiros + 2 de pagos |       4 |        2 |      2 |        0 |                0.660 |                 0.566 |               0.864 |       1.685 |        0.382 | True               |
|        3 | True          | 3 cajas mixtas (actual)         |       3 |        0 |      0 |        3 |                0.781 |                 0.837 |               0.663 |       2.088 |        0.469 | True               |
|        4 | False         | 3 cajas de retiros + 1 de pagos |       4 |        3 |      1 |        0 |                2.663 |                 0.091 |               8.526 |      10.188 |        0.619 | False              |
|        5 | False         | 2 cajas de retiros + 1 de pagos |       3 |        2 |      1 |        0 |                2.983 |                 0.550 |               8.526 |      11.265 |        0.619 | False              |
|        6 | False         | 1 caja de retiros + 3 de pagos  |       4 |        1 |      3 |        0 |                3.938 |                 5.551 |               0.163 |      13.672 |        0.660 | False              |
|        7 | False         | 1 caja de retiros + 2 de pagos  |       3 |        1 |      2 |        0 |                4.159 |                 5.551 |               0.889 |      14.054 |        0.660 | False              |

## Punto 1: cajero con menor y mayor tiempo de atención

- Menor tiempo promedio de servicio: Cajero 0 (Mixta, 3.16 min)
- Mayor tiempo promedio de servicio: Cajero 2 (Mixta, 3.23 min)

|   Cajero | Tipo de caja   |   Clientes |   Servicio prom. (min) |   Espera prom. (min) |   Sistema prom. (min) |   Utilización |
|---------:|:---------------|-----------:|-----------------------:|---------------------:|----------------------:|--------------:|
|        0 | Mixta          |     66.233 |                  3.162 |                0.852 |                 4.014 |         0.428 |
|        1 | Mixta          |     66.467 |                  3.201 |                0.816 |                 4.017 |         0.433 |
|        2 | Mixta          |     65.367 |                  3.232 |                0.718 |                 3.949 |         0.431 |

## Punto 2: promedio de usuarios de cada tipo

| Tipo de usuario   |   Promedio por réplica |   Desv. estándar |   IC 95 % inf. |   IC 95 % sup. |   Porcentaje (%) |   Promedio por cajero |
|:------------------|-----------------------:|-----------------:|---------------:|---------------:|-----------------:|----------------------:|
| Rápido            |                 38.233 |            8.728 |         34.974 |         41.493 |           19.303 |                12.744 |
| Normal            |                 67.700 |            8.133 |         64.663 |         70.737 |           34.180 |                22.567 |
| Lento             |                 40.467 |            6.437 |         38.063 |         42.870 |           20.431 |                13.489 |
| Muy lento         |                 51.667 |            6.228 |         49.341 |         53.992 |           26.085 |                17.222 |

## Punto 3: total de usuarios por tipo en cada réplica

La tabla completa por réplica está en `outputs/punto3_replicas.csv`. La réplica con menor cantidad por tipo se resume así:

| Tipo      |   Réplica con mínimo |   Mínimo |   Promedio |   Máximo |   Desv. estándar |   Réplicas empatadas |
|:----------|---------------------:|---------:|-----------:|---------:|-----------------:|---------------------:|
| Rápido    |                   12 |       24 |     38.233 |       55 |            8.728 |                    1 |
| Normal    |                   12 |       54 |     67.700 |       86 |            8.133 |                    1 |
| Lento     |                   27 |       27 |     40.467 |       51 |            6.437 |                    1 |
| Muy lento |                    4 |       40 |     51.667 |       63 |            6.228 |                    1 |

## Punto 4: ¿se necesita un cajero adicional?

**Decisión:** No se necesita un cajero adicional.

Con 3 cajas mixtas se cumplen todos los criterios de servicio (espera promedio 0.78 min y utilización máxima 46.9%). No se requiere crear un cuarto cajero para la demanda simulada.

| Métrica                                  |   3 cajas mixtas |   4 cajas mixtas |   Diferencia (4 - 3) |   Mejora (%) |
|:-----------------------------------------|-----------------:|-----------------:|---------------------:|-------------:|
| Espera promedio global (min)             |            0.781 |            0.213 |               -0.568 |       72.760 |
| Espera promedio retiros (min)            |            0.837 |            0.209 |               -0.628 |       75.060 |
| Espera promedio pagos (min)              |            0.663 |            0.224 |               -0.439 |       66.220 |
| Espera promedio peor tipo (min)          |            1.166 |            0.473 |               -0.693 |       59.430 |
| Espera p90 global (min)                  |            2.088 |            0.024 |               -2.064 |       98.860 |
| Fracción con espera > 10 min             |            0.019 |            0.006 |               -0.014 |       70.250 |
| Utilización promedio                     |            0.431 |            0.323 |               -0.107 |       24.920 |
| Utilización máxima de una caja           |            0.469 |            0.364 |               -0.104 |       22.270 |
| Usuarios que terminan después de las 8 h |            1.533 |            1.300 |               -0.233 |       15.220 |

## Punto 5: configuración óptima

**Recomendación costo-efectiva:** 3 cajas mixtas (actual) — 0 cajas exclusivas de retiro, 0 de pago, 3 mixtas; 3 cajas en total.

La recomendación es '3 cajas mixtas (actual)' (0 cajas exclusivas de retiro, 0 de pago y 3 mixtas), con una espera promedio global de 0.78 min, espera de retiros de 0.84 min y espera de pagos de 0.66 min. La configuración actual de 3 cajas mixtas ya cumple todos los criterios de servicio; agregar una cuarta caja mejora la espera pero no es necesaria para la demanda simulada. Cumple todos los criterios de servicio definidos.

**Mejor desempeño absoluto:** 4 cajas mixtas (4 cajas), con espera promedio global de 0.21 min. No se recomienda automáticamente porque puede implicar cajas adicionales que no son necesarias para cumplir los criterios.

Si el banco exige especializar las **3 cajas existentes**, la opción más balanceada es **1 caja de retiros + 2 de pagos** (1 de retiro y 2 de pago), con espera promedio global de 4.16 min y espera de la operación más alta de 5.55 min. Esta opción no cumple todos los criterios de servicio.

Si el banco está dispuesto a crear una cuarta caja y especializar todas las cajas, la mejor opción es **2 cajas de retiros + 2 de pagos** (2 de retiro y 2 de pago), con espera promedio global de 0.66 min y espera de la operación más alta de 0.86 min.

## Archivos generados

| Archivo | Contenido |
|---|---|
| `replicas.csv` | Métricas agregadas por réplica y configuración. |
| `cajeros.csv` | Métricas por cajero y réplica. |
| `clientes.csv` | Detalle de cada cliente simulado. |
| `conteos_tipo.csv` | Conteos por acción y tipo de usuario. |
| `punto1_cajeros.csv` | Tabla del punto 1. |
| `punto2_usuarios_tipo.csv` | Tabla del punto 2. |
| `punto2_usuarios_tipo_accion.csv` | Desglose acción × tipo. |
| `punto3_replicas.csv` | Tabla del punto 3 por réplica. |
| `punto3_minimos.csv` | Réplica con mínimo por tipo. |
| `punto4_criterios.csv` | Evaluación de criterios de servicio. |
| `punto4_comparacion.csv` | Comparación 3 vs 4 cajas mixtas. |
| `punto5_configuracion.csv` | Ranking de configuraciones. |
| `decisiones.json` | Decisión del punto 4 y recomendación del punto 5. |
| `figuras/` | Figuras a 300 dpi para el documento. |
