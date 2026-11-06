# Bitácora de decisiones — Caso HMM riesgo de incendio forestal

- **Proyecto:** AE2_HMM
- **Fecha de registro:** 2026-11-05
- **Estado:** protocolo en curso; sin experimentos ejecutados ni resultados
- **Fuentes leídas:** `.agents/skills/articulo-hmm/SKILL.md`, `materiales/caso_riesgo_de_incendio_forestal.md`

## Regla de registro

Solo se registra una decisión cuando el equipo la expresa. El silencio, la ausencia de objeciones o el uso de la skill **no** equivalen a aprobación. Las propuestas de la IA quedan marcadas como tales hasta que el equipo se pronuncie.

## Decisiones registradas

| ID | Decisión | Estado | Evidencia |
|---|---|---|---|
| **D1** | Ejercicio didáctico, sin búsqueda de validez ecológica ni datos de campo | Registrada | Expresada por el equipo, 2026-11-05 |
| **D2** | Trabajar con escenarios hipotéticos; A, B y π como generador; toda cifra se rotula como simulada | Registrada | Expresada por el equipo, 2026-11-05 |
| **D3.1** | Estados como **etiquetas puras** (s₁, s₂, s₃), sin definición física; "Riesgo Bajo/Moderado/Extremo" es alias mnemónico | Registrada | Expresada por el equipo, 2026-11-05 |
| **D3.2** | Humedad **ordinal** (Alta > Media > Baja). No se inventan umbrales numéricos en % | Registrada | Expresada por el equipo, 2026-11-05 |
| **D3.3** | Un paso = **ocasión de observación**, sin unidad física; "día" solo como convención editorial si se requiere | Fijada por delegación del equipo | El equipo pidió sugerencia; sugerencia adoptada |
| **D3.4** | Constructo con la **opción honesta**: "regímenes latentes asociados a humedad"; "riesgo" como etiqueta didáctica | Registrada | Expresada por el equipo, 2026-11-05 |
| **D3.5** | K = 3; π = [0.50, 0.30, 0.20] como distribución **inicial en t = 1**; A, B y π fijos | Registrada | Expresada por el equipo, 2026-11-05 |
| **D4** | Comparación T1 (decodificación): M0, M1 y M2; macro-F1 principal; recall de "Extremo" y exactitud como secundarias; diseño pareado; T = 500; N = 2000; escenario secundario con B alterada | Registrada | Expresada por el equipo, 2026-11-05 |

## Convenciones y parámetros fijados

- **Notación:** S = {s₁, s₂, s₃}; alfabeto de observación {Alta, Media, Baja}; orden de filas y columnas como en el material.
- **A, B y π:** se usan tal como aparecen en el caso; son matrices estocásticas válidas (filas y π suman 1).
- **π no es estacionaria:** π·A ≈ [0.46, 0.335, 0.205] ≠ π. Se trata como prior en t = 1, no como equilibrio. La estacionaria de A es ≈ [0.424, 0.348, 0.227].
- **Persistencia:** duración media en cada estado ≈ 1/(1 − pᵢᵢ) → 3.3, 2.0 y 2.5 pasos.
- **Supuesto ya incorporado en B:** más humedad ⇒ menos riesgo (RB concentra masa en Alta; RE en Baja). Es un supuesto del material, no evidencia.
- **Especificación técnica de la comparación:**
  - **M0** umbral determinista: asigna a cada humedad el estado con mayor probabilidad en B (Alta→s₁, Media→s₂, Baja→s₃).
  - **M1** cadena de Markov observable: usa la ley observable exacta derivada de A, B y la distribución estacionaria de A (mejor baseline que solo modela humedad observada).
  - **M2** HMM: usa A, B y π dados.
  - Los tres reciben parámetros "oráculo", de modo que la comparación aísla la estructura del modelo, no la calidad de la estimación.
- **Tamaño del experimento:** T = 500 pasos, N = 2000 secuencias, una semilla distinta por réplica, semillas registradas. Justificación: con duración media de 2–3.3 pasos, T = 500 produce ~150–250 segmentos de estado por secuencia; el error Monte Carlo del promedio es ≈ sd/√N ≈ sd/44.7 (≈ 0.001 si sd ≈ 0.05). Se hará piloto N = 200 para estimar sd y se reportará IC por bootstrap de secuencias.
- **Cota teórica útil:** en t = 1, con π, el mejor clasificador que solo mira una observación acierta como máximo ≈ 0.67; los errores se concentran entre estados adyacentes.
- **Independencia:** la unidad independiente es la secuencia, no el paso de tiempo. Las métricas se calculan por secuencia y luego se agregan (promedio ± desviación / IC).
- **Estado de ejecución:** no se ha ejecutado código ni generado resultados. La secuencia de 5 observaciones del material es solo demostrativa.

## Decisiones pendientes

### D5 — Inferencia vs. entrenamiento

| Opción | Contenido | Valoración |
|---|---|---|
| **D5a** | Solo decodificación con A, B y π fijos: Forward, Forward–Backward, Viterbi | Recomendada como núcleo; coherente con D1–D2 |
| **D5b** | D5a + segundo experimento de entrenamiento con Baum-Welch sobre corpus simulado, evaluación en secuencias reservadas | Opcional como anexo; exige partición por secuencia, inicializaciones múltiples, alineación de etiquetas y control de convergencia |
| **D5c** | Solo entrenamiento | No recomendada |

Condiciones no negociables si se elige D5b: partición por secuencia; ~20 inicializaciones seleccionadas por validación (nunca por prueba); alineación de estados (Hungarian) antes de comparar; reportar error de Frobenius en A y B, macro-F1 en prueba, log-probabilidades, tolerancia, semillas y corridas no convergidas.

### D6 — Aprobación y alcance

Pendiente de que el equipo exprese:

1. **Aprobador y revisor** (nombres reales).
2. **Mecanismo de aprobación:** explícito, escrito, con fecha y versión.
3. **Alcance de las conclusiones:** solo simulado y didáctico; sin validez ecológica; sin afirmar superioridad del HMM; el hallazgo interesante está en el escenario con B alterada.
4. **Etiqueta del entregable:** "anteproyecto" si no se ejecutan los experimentos; "final" solo con la lista de verificación completa.

Lista de verificación para cerrar: protocolo con parámetros y semillas; código reproducible y versiones; cada cifra trazable a una ejecución; tablas y figuras generadas por código; referencias verificadas o marcadas como no verificadas; limitaciones y declaración de uso de IA; pendientes explícitos sin invención.

## Próximo paso

El equipo debe pronunciarse sobre **D5** (D5a, D5a + D5b, o D5c) y **D6** (aprobador/revisor y etiqueta del entregable). Con esas respuestas se cierra el protocolo y se redacta el esqueleto del manuscrito, marcando como pendiente todo resultado experimental no ejecutado.

## Bitácora

| Fecha | Consulta | Propuesta | Verificación | Decisión humana | Evidencia |
|---|---|---|---|---|---|
| 2026-11-05 | Estructura de siete etapas para el caso | Tabla con acciones mecánicas y decisiones científicas separadas | Lectura directa de la skill y del caso | Sin aprobaciones en ese momento | `SKILL.md`; `caso_riesgo_de_incendio_forestal.md` |
| 2026-11-05 | Alcance y datos | Ejercicio didáctico con escenarios hipotéticos | Coherente con el material: no hay dataset real | **D1 y D2 registradas** | Mensaje del equipo |
| 2026-11-05 | Semántica del modelo | Definiciones 3.1–3.5 | Detectado que B ya codifica humedad↔riesgo; π no estacionaria | **D3 registrada** | Matrices del caso |
| 2026-11-05 | Comparación | T1 + M0/M1/M2 + macro-F1 + T=500/N=2000 | Cota 0.67 en t=1; independencia por secuencia | **D4 registrada** | Cálculo aritmético sobre π y B |
| 2026-11-05 | Entrenamiento y cierre | Opciones D5a/D5b/D5c y protocolo D6 | Reglas técnicas de la skill (partición, etiquetas, semillas) | **D5 y D6 pendientes** | `SKILL.md` |

## Cómo retomar

Abrir una sesión en `AE2_HMM` y usar un mensaje como:

> Retomamos el proyecto AE2_HMM. Lee `.agents/skills/articulo-hmm/SKILL.md`, `materiales/caso_riesgo_de_incendio_forestal.md` y `decisiones.md`. Estamos en el punto D5/D6. No registres aprobaciones que no expresemos. Primero confirma el estado leyendo la bitácora y luego propón cómo cerrar D5 y D6.
