# Bitácora de decisiones — Caso HMM riesgo de incendio forestal

- **Proyecto:** AE2_HMM
- **Fecha de registro:** 2026-11-05
- **Última actualización:** 2026-11-09
- **Estado:** D1–D6 registradas; etiqueta Git `anteproyecto`; sin experimentos ejecutados bajo el protocolo ni resultados del protocolo
- **Hito 2026-11-09:** fase de diseño procedimental D1–D6 concluida; código legado aislado en `legacy/`; raíz refactorizada para D4
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
| **D5** | **D5a**: solo decodificación con A, B y π fijos (Forward, Forward–Backward y Viterbi). Baum-Welch queda fuera del núcleo; D5b solo como anexo si se activa expresamente | Registrada | Expresada por el equipo (grupo de trabajo 11), 2026-11-09 |
| **D6.1** | Aprobador y revisor: **grupo de trabajo 11** (ambos roles) | Registrada | Expresada por el equipo, 2026-11-09 |
| **D6.2** | Alcance de las conclusiones: se adopta el texto sugerido (solo simulado y didáctico; sin validez ecológica; sin afirmar superioridad del HMM; interés en el escenario con B alterada) | Registrada | Expresada por el equipo, 2026-11-09 |
| **D6.3** | Mecanismo de aprobación: registro explícito en esta bitácora con fecha y versión, más etiqueta Git `anteproyecto` | Registrada | Expresada por el equipo, 2026-11-09 |
| **D6.4** | Etiqueta del entregable: **`anteproyecto`**; `final` solo al completar la lista de verificación | Registrada | Expresada por el equipo, 2026-11-09 |
| **D6.5** | Legado: mover la versión de 120 días (`main.py`, notebook, `src/`, `tests/`, `outputs/`) a `legacy/`; la raíz se refactoriza para D4 | Registrada | Expresada por el equipo, 2026-11-09 |

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
- **Estado de ejecución:** no se ha ejecutado el protocolo D4 ni generado resultados del protocolo. La secuencia de 5 observaciones del material es solo demostrativa. La versión de 120 días se trasladó a `legacy/`; la raíz implementa D4, pero todavía no produce resultados.

## Decisiones registradas y pendientes

### D5 — Inferencia vs. entrenamiento (cerrada: D5a)

**Registrada:** D5a — solo decodificación con A, B y π fijos: Forward, Forward–Backward y Viterbi. Baum-Welch queda fuera del núcleo.

**Anexo opcional D5b:** solo si el equipo lo activa expresamente. Condiciones no negociables: partición por secuencia; ~20 inicializaciones seleccionadas por validación (nunca por prueba); alineación de estados (Hungarian) antes de comparar; reportar error de Frobenius en A y B, macro-F1 en prueba, log-probabilidades, tolerancia, semillas y corridas no convergidas.

**D5c:** descartada.

### D6 — Aprobación y alcance (cerrada)

Registrado el 2026-11-09:

1. **Aprobador y revisor:** grupo de trabajo 11 (ambos roles).
2. **Alcance de las conclusiones:** se adopta el texto sugerido:
   > Los resultados son simulados y didácticos. No se afirma validez ecológica, ni superioridad general del HMM, ni capacidad predictiva sobre incendios reales. Toda cifra se rotula como simulada. El hallazgo de interés, si se ejecuta el experimento, está en el escenario con B alterada; cualquier conclusión se limita a ese escenario y a las métricas reportadas.
3. **Mecanismo de aprobación:** registro explícito en esta bitácora, con fecha y versión, más etiqueta Git `anteproyecto`.
4. **Etiqueta del entregable:** **`anteproyecto`**. La etiqueta `final` solo se asignará cuando se complete la lista de verificación.
5. **Legado:** la versión de 120 días se traslada a `legacy/`; la raíz se refactoriza para D4.

Lista de verificación para pasar a `final`: protocolo con parámetros y semillas; código reproducible y versiones; cada cifra trazable a una ejecución; tablas y figuras generadas por código; referencias verificadas o marcadas como no verificadas; limitaciones y declaración de uso de IA; pendientes explícitos sin invención.

### Resuelto — legado de código y resultados

La versión de 120 días (humedad en porcentaje, focos de incendio, alertas de quema e índice de peligro) se trasladó a `legacy/` junto con su notebook, `src/`, pruebas y `outputs/`. Esos artefactos **no son resultados del protocolo actual**.

Documentación adoptada:

> La carpeta `legacy/` contiene una simulación exploratoria previa con variables continuas y reglas de negocio de incendios. El protocolo formal del artículo científico se implementa en la raíz bajo las especificaciones D1–D6.

La raíz quedó refactorizada para D4: HMM con Forward, Forward–Backward y Viterbi; simulación de secuencias sintéticas con T = 500 y N = 2000; comparación M0/M1/M2; macro-F1 por secuencia con agregación e IC por bootstrap. **No se ejecutaron experimentos del protocolo.**

### Notas de implementación (no son decisiones nuevas)

- **M1:** se implementó como HMM con A, B y la distribución estacionaria ξ de A, que es la forma no degenerada de usar la ley observable exacta; `observable_markov_law` calcula y prueba Q y la distribución observable. Si el equipo quería otra definición de M1, debe pronunciarse antes de reportar resultados.
- **B alterada:** el escenario secundario usa una mezcla provisional del 50 % con la distribución uniforme (`PROVISIONAL_ALTERED_MIXING = 0.5`). Ese valor no está aprobado y debe fijarse antes de reportar ese escenario.

## Próximo paso

D1–D6 están cerradas. La implementación de la raíz está lista para ejecutar D4, pero todavía no se ha ejecutado. Siguiente: verificar las pruebas, ejecutar el protocolo con las semillas registradas, generar tablas y figuras trazables, y redactar el manuscrito como **anteproyecto**, marcando como pendiente todo resultado experimental no ejecutado.

## Bitácora

| Fecha | Consulta | Propuesta | Verificación | Decisión humana | Evidencia |
|---|---|---|---|---|---|
| 2026-11-05 | Estructura de siete etapas para el caso | Tabla con acciones mecánicas y decisiones científicas separadas | Lectura directa de la skill y del caso | Sin aprobaciones en ese momento | `SKILL.md`; `caso_riesgo_de_incendio_forestal.md` |
| 2026-11-05 | Alcance y datos | Ejercicio didáctico con escenarios hipotéticos | Coherente con el material: no hay dataset real | **D1 y D2 registradas** | Mensaje del equipo |
| 2026-11-05 | Semántica del modelo | Definiciones 3.1–3.5 | Detectado que B ya codifica humedad↔riesgo; π no estacionaria | **D3 registrada** | Matrices del caso |
| 2026-11-05 | Comparación | T1 + M0/M1/M2 + macro-F1 + T=500/N=2000 | Cota 0.67 en t=1; independencia por secuencia | **D4 registrada** | Cálculo aritmético sobre π y B |
| 2026-11-05 | Entrenamiento y cierre | Opciones D5a/D5b/D5c y protocolo D6 | Reglas técnicas de la skill (partición, etiquetas, semillas) | **D5 y D6 pendientes** | `SKILL.md` |
| 2026-11-09 | Inferencia vs. entrenamiento | D5a como núcleo; D5b solo anexo condicionado | Coherente con D1–D2; no hay datos reales | **D5a registrada (grupo de trabajo 11)** | Mensaje del equipo |
| 2026-11-09 | Aprobación y alcance | Aprobador/revisor y alcance sugerido | El alcance no excede la evidencia disponible | **D6.1 y D6.2 registradas** | Mensaje del equipo |
| 2026-11-09 | Cierre de D6 | Etiqueta `anteproyecto`; registro en bitácora + tag Git; legado a `legacy/` | D1–D6 completas; legado aislado | **D6.3–D6.5 registradas; D6 cerrada** | Mensaje del equipo |
| 2026-11-09 | Aislamiento legacy y refactor D4 | Mover versión de 120 días a `legacy/`; raíz con T=500/N=2000 y macro-F1 | Pruebas del protocolo; código legado congelado | **Reubicación y refactor ejecutados** | Cambios en el repositorio; `legacy/README.md` |

## Cómo retomar

Abrir una sesión en `AE2_HMM` y usar un mensaje como:

> Retomamos el proyecto AE2_HMM. Lee `.agents/skills/articulo-hmm/SKILL.md`, `materiales/caso_riesgo_de_incendio_forestal.md` y `decisiones.md`. D1–D6 están cerradas y el entregable es anteproyecto. No registres aprobaciones que no expresemos. Primero confirma el estado leyendo la bitácora y luego propón el siguiente paso del protocolo.
