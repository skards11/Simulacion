# Resultados simulados — experimento HMM M0/M1/M2

Cifras simuladas; no son evidencia de validez ecológica.

- T = 500
- N = 2000
- Semilla maestra = 42
- Secuencias de semilla: `np.random.SeedSequence(42).spawn(2000)`
- Mezcla de B alterada: m = 0.5
- Corrección: Holm-Bonferroni

## Métricas por modelo

| Modelo | Media | Desviación Estándar | Mínimo | Máximo | Mediana | RIC | IC 95 % [P2.5, P97.5] |
|---|---:|---:|---:|---:|---:|---:|---:|
| M0 | 0.6602 | 0.0263 | 0.5581 | 0.7356 | 0.6601 | 0.0353 | [0.6089, 0.7121] |
| M1 | 0.6603 | 0.0216 | 0.5907 | 0.7324 | 0.6611 | 0.0286 | [0.6167, 0.7027] |
| M2 | 0.4989 | 0.0292 | 0.3686 | 0.6019 | 0.4991 | 0.0386 | [0.4380, 0.5558] |

## Contrastes pareados

| Contraste | Diferencia media | p crudo | p Holm | Delta de Cliff |
|---|---:|---:|---:|---:|
| M0_vs_M1 | -0.0002 | 7.780e-01 | 7.780e-01 | -0.0060 |
| M0_vs_M2 | 0.1612 | 0.000e+00 | 0.000e+00 | 1.0000 |

## Criterios de éxito

- **criterion_1:** NO CUMPLE
- **criterion_2:** CUMPLE

## Matriz de confusión normalizada por fila

### M0

| Real \ Predicho | RB | RM | RE |
|---|---:|---:|---:|
| Riesgo Bajo | 0.8010 | 0.1717 | 0.0273 |
| Riesgo Moderado | 0.3039 | 0.5148 | 0.1813 |
| Riesgo Extremo | 0.0584 | 0.2650 | 0.6766 |

### M1

| Real \ Predicho | RB | RM | RE |
|---|---:|---:|---:|
| Riesgo Bajo | 0.7001 | 0.2499 | 0.0500 |
| Riesgo Moderado | 0.2010 | 0.5988 | 0.2002 |
| Riesgo Extremo | 0.0504 | 0.2508 | 0.6989 |

### M2

| Real \ Predicho | RB | RM | RE |
|---|---:|---:|---:|
| Riesgo Bajo | 0.5942 | 0.2734 | 0.1324 |
| Riesgo Moderado | 0.3341 | 0.4261 | 0.2398 |
| Riesgo Extremo | 0.1930 | 0.3147 | 0.4923 |
