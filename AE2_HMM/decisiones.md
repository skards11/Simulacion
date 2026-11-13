# Bitácora de decisiones — Caso HMM riesgo de incendio forestal

- **Proyecto:** AE2_HMM
- **Fecha de registro:** 2026-11-05
- **Última actualización:** 2026-11-11
- **Estado:** D1–D8 registradas; etiqueta Git `anteproyecto`; experimento D7 ejecutado, aprobado y reproducible; resultados simulados disponibles
- **Hito 2026-11-09:** fase de diseño procedimental D1–D6 concluida; código legado aislado en `legacy/`; raíz refactorizada para D4; ejecución D4 completada
- **Hito 2026-11-11:** cierre experimental D7: M0/M1/M2 redefinidos, `m = 0.5` definitivo, semillas `SeedSequence(42).spawn(2000)` y análisis pareado con Wilcoxon/Holm/Cliff
- **Hito 2026-11-11:** el equipo aprueba las cifras D7; se cierra la reproducibilidad con versiones exactas, comando único y manifiesto SHA-256 (D8)
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
| **D7** | Cierre experimental: M0 = Viterbi logarítmico nominal; M1 = baseline puntual `argmax_i B[i,O_t]`; M2 = Viterbi nominal sobre observaciones con `B(m=0.5)` definitiva; N = 2000 con `SeedSequence(42).spawn(2000)`; Macro-F1 con media/SD/mediana/RIC/IC P2.5–P97.5; Wilcoxon bilateral con Holm-Bonferroni y Delta de Cliff; criterios 1 y 2 definidos | Registrada y cerrada definitivamente | Instrucción y aprobación del equipo, 2026-11-11 |
| **D8** | Cierre de reproducibilidad: versiones exactas en `requirements.txt`, `outputs/MANIFEST.txt` con SHA-256, comando único `python scripts/reproduce.py`, Python 3.12.10 documentado | Registrada | Instrucción y aprobación del equipo, 2026-11-11 |

## Convenciones y parámetros fijados

- **Notación:** S = {s₁, s₂, s₃}; alfabeto de observación {Alta, Media, Baja}; orden de filas y columnas como en el material.
- **A, B y π:** se usan tal como aparecen en el caso; son matrices estocásticas válidas (filas y π suman 1).
- **π no es estacionaria:** π·A ≈ [0.46, 0.335, 0.205] ≠ π. Se trata como prior en t = 1, no como equilibrio. La estacionaria de A es ≈ [0.424, 0.348, 0.227].
- **Persistencia:** duración media en cada estado ≈ 1/(1 − pᵢᵢ) → 3.3, 2.0 y 2.5 pasos.
- **Supuesto ya incorporado en B:** más humedad ⇒ menos riesgo (RB concentra masa en Alta; RE en Baja). Es un supuesto del material, no evidencia.
- **Especificación técnica vigente de la comparación (D7):**
  - **M0** HMM nominal: Viterbi en espacio logarítmico con A, B y π.
  - **M1** baseline puntual sin HMM ni memoria temporal: `argmax_i B[i, O_t]`.
  - **M2** HMM nominal sobre observaciones generadas con `B(m) = (1 - m)B + mU`, `m = 0.5`, `U_ij = 1/3`; decodifica con la B nominal.
  - Los tres usan los mismos estados latentes y las mismas réplicas (diseño pareado). La comparación aísla la estructura del modelo, no la calidad de la estimación.
  - La especificación M0/M1 de D4 (umbral determinista y cadena observable con prior estacionario) queda como antecedente histórico y no debe citarse como vigente.
- **Tamaño del experimento:** T = 500 pasos, N = 2000 réplicas independientes con `np.random.SeedSequence(42).spawn(2000)`. La unidad independiente es la secuencia. El IC 95 % es percentil P2.5–P97.5 de las métricas por secuencia; la corrección por comparaciones múltiples es Holm-Bonferroni.
- **Cota teórica útil:** en t = 1, con π, el mejor clasificador que solo mira una observación acierta como máximo ≈ 0.67; los errores se concentran entre estados adyacentes.
- **Independencia:** la unidad independiente es la secuencia, no el paso de tiempo. Las métricas se calculan por secuencia y luego se agregan (promedio ± desviación / IC).
- **Estado de ejecución:** el experimento D7 se ejecutó el 2026-11-11 con T = 500, N = 2000 y `SeedSequence(42).spawn(2000)`. El equipo aprobó las cifras ese mismo día. Los resultados son simulados y están en `outputs/`; `outputs/MANIFEST.txt` registra sus hashes SHA-256. La secuencia de 5 observaciones del material sigue siendo solo demostrativa. La versión de 120 días está en `legacy/`.

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

### D7 — Cierre experimental (registrada 2026-11-11)

La instrucción del equipo reemplaza las definiciones de modelos de D4 y fija
el escenario con B alterada:

1. **M0:** Viterbi en espacio logarítmico con A, B y π nominales.
2. **M1:** baseline puntual sin memoria temporal,
   `S_hat_t = argmax_i B[i, O_t]`, evaluado sobre las observaciones nominales.
3. **M2:** Viterbi con A, B y π nominales sobre observaciones generadas con
   `B(m) = (1 - m)B + mU`, con `m = 0.5` definitivo y `U_ij = 1/3`.
4. **Semillas:** `np.random.SeedSequence(42).spawn(2000)`, una secuencia de
   semilla por réplica.
5. **Métricas:** Macro-F1 por secuencia con media, SD, mediana, RIC e IC
   percentil P2.5–P97.5; matriz de confusión normalizada agregada.
6. **Contrastes:** Wilcoxon bilateral pareado, alpha = 0.01, Holm-Bonferroni
   para M0 vs M1 y M0 vs M2, y Delta de Cliff.
7. **Criterio 1:** media Macro-F1(M0) − Media Macro-F1(M1) ≥ 0.05,
   p < 0.01 y |Delta de Cliff| ≥ 0.474.
8. **Criterio 2:** caída significativa de M2 respecto de M0 (p < 0.01)
   manteniendo Macro-F1(M2) > 0.333.

El historial D4 se conserva como antecedente; D7 es el protocolo vigente.

#### Cierre definitivo de D7 (aprobado 2026-11-11)

El equipo revisó las cifras ejecutadas en `outputs/` y las aprobó. Quedan
cerrados definitivamente los tres puntos siguientes:

- **(a) M1 como baseline puntual sin HMM.** M1 es exactamente
  `S_hat_t = argmax_i B[i, O_t]`, sin matriz A, sin π y sin memoria temporal.
  No se usará la definición anterior basada en la ley observable o en el prior
  estacionario.
- **(b) `m = 0.5` fijo en `B(m)`.** La emisión degradada es
  `B(m) = (1 - m)B + mU` con `m = 0.5` y `U_ij = 1/3`. El valor no es
  provisional y no se cambiará sin una nueva decisión registrada.
- **(c) Protocolo estadístico.** Wilcoxon bilateral pareado con
  Holm-Bonferroni para M0 vs M1 y M0 vs M2, alpha = 0.01, Delta de Cliff y los
  criterios 1 y 2 definidos en D7. Los criterios no se reinterpretan después de
  ver los resultados.

Resultado aprobado: Criterio 1 **NO CUMPLE** (M0 y M1 son indistinguibles:
diferencia media −0.000186, p Holm = 0.778, Δ Cliff = −0.006) y Criterio 2
**CUMPLE** (caída M0 − M2 = 0.161232, p Holm < 0.001, Macro-F1(M2) = 0.498924
> 0.333). Estas cifras son simuladas y no implican superioridad general del
HMM.

### Resuelto — legado de código y resultados

La versión de 120 días (humedad en porcentaje, focos de incendio, alertas de quema e índice de peligro) se trasladó a `legacy/` junto con su notebook, `src/`, pruebas y `outputs/`. Esos artefactos **no son resultados del protocolo actual**.

Documentación adoptada:

> La carpeta `legacy/` contiene una simulación exploratoria previa con variables continuas y reglas de negocio de incendios. El protocolo formal del artículo científico se implementa en la raíz bajo las especificaciones D1–D7.

La raíz quedó refactorizada para D4: HMM con Forward, Forward–Backward y Viterbi; simulación de secuencias sintéticas con T = 500 y N = 2000; comparación M0/M1/M2; macro-F1 por secuencia con agregación e IC por bootstrap. La ejecución del protocolo se registra en la sección siguiente.

### Notas de implementación (histórico; ver D7)

- **M1 (D4):** se implementó como HMM con A, B y la distribución estacionaria ξ de A. Esta definición fue reemplazada por D7: M1 es ahora el baseline puntual `argmax_i B[i, O_t]`, sin memoria temporal.
- **B alterada (D4):** el escenario usaba una mezcla provisional del 50 % con la distribución uniforme. D7 fija `m = 0.5` de forma definitiva.

### Resultados de la ejecución D4 (2026-11-09) — antecedente histórico

> Estos resultados corresponden al protocolo D4 anterior. Fueron reemplazados por el experimento D7 del 2026-11-11. Se conservan solo como historial; no deben citarse como resultados vigentes.

Ejecución: `python main.py --save outputs/protocolo_d4_resumen.json`, con T = 500, N = 2000, semilla maestra 20261109 y dos escenarios. Artefactos: `outputs/protocolo_d4_resumen.json`, `.csv`, `.md`, `outputs/protocolo_d4_metricas.png` y `outputs/protocolo_d4_ejecucion.log`.

**Escenario base**

| Modelo | Macro-F1 (media [IC 95 %]) | Recall s3 | Exactitud |
|---|---:|---:|---:|
| M0 | 0.6608 [0.6599, 0.6618] | 0.6996 [0.6976, 0.7015] | 0.6650 [0.6641, 0.6660] |
| M1 | 0.6749 [0.6738, 0.6760] | 0.6691 [0.6667, 0.6714] | 0.6828 [0.6817, 0.6838] |
| M2 | 0.6749 [0.6738, 0.6759] | 0.6691 [0.6666, 0.6715] | 0.6828 [0.6818, 0.6839] |

**Escenario con B alterada**

| Modelo | Macro-F1 (media [IC 95 %]) | Recall s3 | Exactitud |
|---|---:|---:|---:|
| M0 | 0.4912 [0.4902, 0.4922] | 0.5163 [0.5142, 0.5184] | 0.4991 [0.4982, 0.5001] |
| M1 | 0.4966 [0.4953, 0.4979] | 0.3999 [0.3970, 0.4029] | 0.5236 [0.5223, 0.5248] |
| M2 | 0.4965 [0.4952, 0.4977] | 0.3996 [0.3968, 0.4025] | 0.5236 [0.5224, 0.5248] |

Observaciones descriptivas, sin convertirlas en superioridad general:

- En el escenario base, M1 y M2 superan a M0 en macro-F1 y exactitud, pero el recall de `s3` es mayor en M0.
- M1 y M2 coinciden hasta la cuarta cifra decimal; es consistente con que solo difieren en el prior inicial (ξ frente a π) y T es largo.
- Con B alterada, las tres variantes bajan de forma marcada. M1 y M2 mejoran apenas la macro-F1 de M0, pero pierden recall de `s3` respecto de M0.
- Las cifras son simuladas y dependen de la B alterada de D4 (histórica). No se afirma validez ecológica ni superioridad del HMM.

## Próximo paso

D1–D8 están cerradas. El experimento vigente (D7) se ejecutó el 2026-11-11 con T = 500, N = 2000, `SeedSequence(42).spawn(2000)` y `m = 0.5`, y el equipo aprobó sus cifras. Los artefactos están en `outputs/experimento_hmm_resumen.*`, `outputs/experimento_hmm_comparativa.png` y `outputs/MANIFEST.txt`.

El manuscrito de **anteproyecto** todavía contiene las tablas y la figura del protocolo D4 anterior; **no se ha tocado** en esta fase. Con la aprobación ya registrada, el siguiente paso es actualizar el manuscrito con D7, recompilar el PDF y verificar cada cifra contra `outputs/`. Después se decidirá si se mantiene la etiqueta `anteproyecto` o se avanza a `final`.

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
| 2026-11-09 | Ejecución D4 | Correr T=500/N=2000, semilla 20261109, escenario base y B alterada | Pruebas de la raíz y del legado; resultados guardados y regenerables | **Ejecución completada; sin nueva decisión científica** | `outputs/protocolo_d4_resumen.json`; `.csv`; `.md`; `.png`; `.log` |
| 2026-11-09 | Manuscrito de anteproyecto | Redactar el manuscrito con resultados D4, limitaciones y declaración de IA | Cada cifra trazada a `outputs/`; referencias marcadas como pendientes | **Borrador de anteproyecto redactado; sin aprobación final** | `manuscrito_anteproyecto.md` |
| 2026-11-09 | Autoría | Registrar los nombres de los integrantes | Coinciden con el grupo de trabajo 11 | **Autores registrados** | Mensaje del equipo; `manuscrito_anteproyecto.md` |
| 2026-11-09 | Referencias | Verificar Rabiner (1989) y Baum et al. (1970) | Comprobadas por el equipo | **Referencias verificadas** | Mensaje del equipo; `manuscrito_anteproyecto.md` |
| 2026-11-09 | Declaración de uso de IA | Revisar y aprobar la declaración | Aprobada por el grupo de trabajo 11 | **Declaración de IA aprobada** | Mensaje del equipo; `manuscrito_anteproyecto.md` |
| 2026-11-09 | Conversión a LaTeX | Convertir el manuscrito y ajustarlo a la plantilla | Estructura, tablas, figura y bibliografía revisadas | **Conversión a LaTeX realizada** | `manuscrito_anteproyecto.tex` |
| 2026-11-09 | Compilación del PDF | Instalar Tectonic 0.17.0 y compilar el manuscrito | Compilación sin errores; PDF de 8 páginas revisado visualmente | **PDF generado** | `manuscrito_anteproyecto.pdf` |
| 2026-11-11 | Cierre experimental D7 | Redefinir M0/M1/M2, fijar `m=0.5`, usar `SeedSequence(42).spawn(2000)` y añadir Wilcoxon/Holm/Cliff | Pruebas unitarias y ejecución completa; artefactos en `outputs/` | **D7 registrada; experimento ejecutado; sin cambio de manuscrito todavía** | `src/simulation.py`; `tests/test_protocol.py`; `outputs/experimento_hmm_resumen.json` |
| 2026-11-11 | Aprobación de cifras D7 | Presentar el resumen exacto de métricas, contrastes y criterios | Cifras verificadas contra `outputs/experimento_hmm_resumen.json` | **Cifras aprobadas; D7 cerrada definitivamente (M1 puntual, m=0.5, Wilcoxon/Holm/Cliff)** | Mensaje del equipo |
| 2026-11-11 | Reproducibilidad | Fijar versiones exactas, comando único y manifiesto SHA-256 | Repetición determinista: mismos archivos y hashes; `15 passed` | **D8 registrada** | `requirements.txt`; `scripts/reproduce.py`; `outputs/MANIFEST.txt` |

## Cómo retomar

Abrir una sesión en `AE2_HMM` y usar un mensaje como:

> Retomamos el proyecto AE2_HMM. Lee `.agents/skills/articulo-hmm/SKILL.md`, `materiales/caso_riesgo_de_incendio_forestal.md` y `decisiones.md`. D1–D8 están cerradas, las cifras D7 están aprobadas y el experimento es reproducible con `python scripts/reproduce.py`. El entregable sigue siendo anteproyecto. No registres aprobaciones que no expresemos. Primero confirma el estado leyendo la bitácora y luego propón el siguiente paso.
