# Revisión de la skill `articulo-hmm-diseno-experimental`

**Objeto revisado:** `.agents/skills/articulo-hmm/articulo-hmm-diseno-experimental.md`
**Contexto:** sección de Diseño experimental del artículo del proyecto AE2_HMM.
**Fecha de revisión:** 2026-11-11.

## 0. Alcance y método

Se leyeron, sin modificar:

- `.agents/skills/articulo-hmm/articulo-hmm-diseno-experimental.md` (skill objeto de revisión).
- `.agents/skills/articulo-hmm/SKILL.md` y `skill_modificada.md` (marco general).
- `decisiones.md` (D1–D6 y notas de implementación).
- `manuscrito_anteproyecto.md`, sección 4.1–4.5.
- `src/simulation.py`, `tests/test_protocol.py` y `outputs/protocolo_d4_resumen.md`.

**No se hizo:** ejecutar el protocolo, recalcular métricas, consultar fuentes externas, generar figuras ni registrar aprobaciones. Los artefactos de `outputs/` se citan solo como evidencia documental existente; no se auditaron numéricamente en esta revisión.

**Criterio de revisión:** ¿el procedimiento obliga a detectar omisiones de diseño y a reconocer evidencia faltante, sin convertir lo provisional en conclusión? Las propuestas se presentan para decisión del equipo; no se aplicaron a la skill.

---

## 1. Veredicto breve

La skill **sí detecta las omisiones gruesas** que motivaron su creación: falta de baseline, uso de métricas supervisadas sin etiquetas, confusión entre parámetros fijos y aprendidos, semillas repetidas, ausencia de dispersión, falta de razones para descartar el HMM y desalineación con el código.

Pero **no detecta omisiones finas** que afectan la validez de la sección:

- no verifica que el baseline sea comparable en información y esfuerzo;
- no exige análisis pareado aunque el diseño sea pareado;
- no exige preespecificar el resultado primario ni controlar comparaciones múltiples;
- no distingue evidencia ausente, parcial, no trazable, contradictoria o provisional;
- no impide que un parámetro no aprobado (por ejemplo, la mezcla de la B alterada) sostenga afirmaciones definitivas;
- no define cómo comprobar la alineación protocolo–código–artefacto;
- no exige declarar desviaciones, corridas fallidas ni resultados no reportados.

**Riesgo principal:** un protocolo puede “pasar” la checklist de la skill y aun así producir una sección que parezca más concluyente de lo que la evidencia permite.

---

## 2. Lo que la skill ya hace bien

| Criterio actual | Qué obliga a hacer | Evidencia en el proyecto |
|---|---|---|
| Baseline sin HMM (criterio 1) | Incluir una referencia simple de contraste | M0 está definido y ejecutado |
| Métricas y etiquetas (criterio 2) | Comprobar etiquetas antes de proponer exactitud o Macro-F1 | Las etiquetas son simuladas y se usan solo para evaluar |
| Reproducibilidad y control (criterio 3) | Separar parámetros fijados de perturbados o aprendidos | D5a fija A, B y π; D5b queda fuera del núcleo |
| Independencia estocástica (criterio 4) | Semillas independientes y estadísticos de dispersión | Una semilla por secuencia; IC por bootstrap |
| Pertinencia (criterio 5) | Razones para usar y para descartar el HMM | El manuscrito reconoce límites y no afirma superioridad general |
| Alineación con el código (criterio 6) | Evitar supuestos de versiones legado | `legacy/` está separado; la raíz implementa D4 |
| Falta de evidencia | No inventar; marcar pendientes; tablas vacías; reportar conflicto código–protocolo | El manuscrito rotula cifras como simuladas y deja `m = 0.5` como provisional |

También acierta en el formato: separar hechos, supuestos e incertidumbres; listar decisiones pendientes; exigir bitácora; y reservar al equipo las decisiones científicas.

---

## 3. Decisiones humanas explícitas que deben conservarse

Esta revisión **no propone cambiar** ninguna de las siguientes decisiones. Cualquier ajuste que las altere requeriría una decisión nueva del equipo.

| ID | Decisión registrada | Implicación para la skill |
|---|---|---|
| D1 | Ejercicio didáctico, sin validez ecológica ni datos de campo | La skill no debe sugerir datos reales ni conclusions aplicadas |
| D2 | Escenarios hipotéticos; A, B y π como generador; toda cifra es simulada | No presentar resultados como evidencia empírica |
| D3.1 | Estados como etiquetas puras; los nombres de riesgo son alias | No exigir una definición física de los estados |
| D3.2 | Humedad ordinal; sin porcentajes ni umbrales inventados | No introducir cortes numéricos |
| D3.3 | Un paso es una ocasión de observación | Aceptar la decisión delegada y registrada; no reinterpretarla |
| D3.4 | Constructo “regímenes latentes asociados a humedad” | Mantener la formulación honesta |
| D3.5 | K = 3; π es prior inicial, no estacionaria; A, B y π fijos | No convertir π en distribución estacionaria |
| D4 | M0, M1 y M2; macro-F1 principal; recall de `s3` y exactitud secundarias; diseño pareado; T = 500; N = 2000; B alterada como escenario secundario | La skill puede exigir más rigor, pero no cambiar métricas ni parámetros |
| D5a | Solo decodificación con parámetros fijos; Baum–Welch fuera del núcleo | D5b solo si el equipo lo activa expresamente |
| D6.1 | Aprobador y revisor: grupo de trabajo 11 | No atribuir aprobaciones a otras personas |
| D6.2 | Alcance limitado: simulado y didáctico; sin validez ecológica ni superioridad general | La skill debe impedir conclusiones que excedan ese alcance |
| D6.3 | Aprobación por registro en bitácora, fecha, versión y etiqueta Git | La skill no debe aceptar aprobación por silencio |
| D6.4 | Entregable `anteproyecto`; `final` solo al completar la checklist | Las propuestas no autorizan el cierre `final` |
| D6.5 | Legado aislado en `legacy/` | La skill debe impedir mezclar artefactos legado |

**Elementos que siguen abiertos y que la skill debería detectar como tales:**

- La definición de M1: `decisiones.md` indica que, si el equipo quería otra definición, debe pronunciarse antes de reportar resultados.
- El valor de mezcla de la B alterada: `PROVISIONAL_ALTERED_MIXING = 0.5` está marcado como provisional y no aprobado.

La skill actual menciona “aprobar las perturbaciones”, pero no obliga a marcar los resultados que dependen de un valor aún no aprobado. Esa es una omisión relevante.

---

## 4. Omisiones que el procedimiento no detecta

### 4.1 Diseño y comparación

1. **Confusión entre modelos y escenarios.** La línea 16 llama “escenarios (M0, M1, M2)” a lo que en el proyecto son *modelos*; los escenarios son base y B alterada. Esto puede llevar a una tabla o a una decisión mal planteada.
2. **Comparación no equitativa.** Exige un baseline sin HMM, pero no exige documentar si baseline y HMM reciben la misma información, el mismo presupuesto de ajuste y el mismo tratamiento de parámetros “oráculo”.
3. **Diseño pareado sin análisis pareado.** El criterio 3 habla de aislar cambios, pero no exige comparar diferencias por secuencia ni usar intervalos de confianza de la diferencia. Dos IC marginales solapados no prueban ausencia de diferencia, y dos IC no solapados no siempre prueban superioridad.
4. **Resultado primario no preespecificado.** La skill pide métricas, pero no exige declarar antes de ejecutar cuál es la métrica principal, la dirección esperada y el criterio de éxito. Sin eso, la elección posterior de la métrica favorable es posible.
5. **Comparaciones múltiples.** No exige declarar cuántos modelos, escenarios y métricas se comparan, ni distinguir análisis confirmatorios de exploratorios.
6. **Tamaño de muestra sin justificación.** Pide T y N, pero no un piloto, una desviación esperada o un efecto mínimo detectable.
7. **Escenarios sin matriz de control.** No exige una tabla que diga, para cada escenario, qué factor cambia, qué se mantiene fijo y qué efecto se espera.
8. **Perturbación no aprobada.** No exige que un valor provisional quede fuera del resumen, las conclusiones o la etiqueta `final`.

### 4.2 Etiquetas y evidencia

9. **“Etiquetas reales” es ambiguo.** En simulación, las etiquetas verdaderas son reales *dentro del modelo*, no observaciones de campo. La skill debería distinguir etiquetas reales, proxy y simuladas, y exigir su procedencia.
10. **Fuga de etiquetas.** Prohíbe usar etiquetas de prueba para seleccionar modelos, pero no exige una comprobación explícita de que las etiquetas no entraron en el ajuste, la inicialización, la selección de escenarios ni la elección de métricas.
11. **Sin etiquetas, no hay alternativa.** Prohíbe exactitud y Macro-F1, pero no propone métricas no supervisadas o diagnósticos (por ejemplo, verosimilitud en held-out, entropía posterior, estabilidad de decodificación o acuerdo entre métodos) para que el equipo decida.
12. **Evidencia parcial no reconocida.** La skill solo contempla “no hay simulaciones”. No dice qué hacer si hay algunas corridas, algunos escenarios o algunas métricas, pero no todas.
13. **Evidencia no trazable.** No exige verificar que cada cifra del borrador provenga de un artefacto identificable.
14. **Evidencia contradictoria.** No contempla que la bitácora, el código y el manuscrito digan cosas distintas.

### 4.3 Reproducibilidad y cierre

15. **Semillas sin procedencia completa.** Pide semillas independientes, pero no exige registrar la semilla maestra, la derivación, la semilla del bootstrap ni la relación entre escenarios pareados.
16. **Entorno no documentado.** No exige versión de Python, dependencias, sistema, comando exacto, duración ni hash/commit.
17. **Alineación con el código sin procedimiento.** El criterio 6 dice “verificar”, pero no indica cómo: matriz protocolo–función–prueba–artefacto, reproducción de una celda, revisión de valores por defecto.
18. **Legado sin regla de exclusión de resultados.** El criterio 6 habla de supuestos legado, pero no prohíbe mezclar cifras o figuras de `legacy/` con las del protocolo vigente.
19. **D5b sin condiciones explícitas.** La skill menciona D5b como opción, pero no incorpora en esta sección las condiciones de partición, inicializaciones, alineación de estados y convergencia.
20. **“Detener el cierre” es ambiguo.** No queda claro si se detiene solo la etiqueta `final` y las conclusiones, o también el borrador provisional.
21. **Sin registro de desviaciones y corridas fallidas.** No exige declarar qué se cambió respecto del protocolo, qué corridas no convergieron o qué resultados no se reportan.
22. **Sin taxonomía de amenazas.** Pide “alcance y amenazas a la validez”, pero no distingue validez interna, externa, de constructo, de conclusión estadística y computacional.

---

## 5. Evidencia faltante: qué reconoce y qué no

| Situación | Respuesta actual de la skill | ¿Suficiente? | Propuesta |
|---|---|---|---|
| No hay etiquetas de referencia | Prohíbe métricas supervisadas | Parcial: no ofrece alternativas ni exige procedencia | Marcar `[SIN ETIQUETAS]`, proponer métricas no supervisadas y exigir decisión del equipo |
| No hay baseline elegido | Lo menciona como pendiente y pide 2 alternativas | Sí, pero sin criterio de comparabilidad | Añadir paridad de información y presupuesto |
| No hay simulaciones | Tablas vacías y rótulo “Anteproyecto / Pendiente de ejecución” | Sí | Mantener |
| Hay simulaciones parciales | No lo contempla | No | Rótulo `[EVIDENCIA PARCIAL]`; no completar celdas faltantes |
| El artefacto existe pero no es trazable | No lo contempla | No | Rótulo `[NO TRAZABLE]`; no usar la cifra |
| El código y el protocolo discrepan | Reportar y detener el cierre | Sí, pero “detener” es ambiguo | Detener solo afirmaciones y cierre; continuar borrador con `[CONFLICTO]` |
| La bitácora falta o se contradice | No lo contempla | No | No inferir aprobaciones; listar decisión requerida |
| Un parámetro es provisional | Solo pide aprobación de perturbaciones | No | Rótulo `[PROVISIONAL NO APROBADO]`; excluir de resumen y conclusiones |
| No hay plantilla editorial | Estructura estándar sin inventar requisitos | Sí | Mantener |
| No hay referencias verificadas | Lo cubre la skill general, no esta sección | Parcial | Remitir explícitamente a la skill general y marcar `[NO VERIFICADO]` |
| No hay recursos de cómputo | No lo contempla | No | Declarar imposibilidad y no simular una ejecución |

---

## 6. Ajustes propuestos para decisión del equipo

Las propuestas están ordenadas por prioridad. Ninguna cambia D1–D6; varias solo hacen explícito lo que el proyecto ya practica.

### P1. Convertir las entradas en una compuerta con estados

**Dónde:** reemplazar o ampliar “Entradas necesarias” (líneas 11–16).

**Texto propuesto:**

> Antes de redactar, clasificar cada entrada como `confirmada`, `parcial`, `ausente` o `contradictoria`, indicando fuente. Son bloqueantes: pregunta y alcance, especificación formal, régimen D5a/D5b, etiquetas de referencia, T/N/semillas, baseline, métrica principal y criterio de éxito. Si una entrada bloqueante no está confirmada, no cerrar la sección: entregar borrador provisional y listar la decisión requerida.

**Por qué:** la skill actual enumera entradas, pero no distingue “existe” de “fue validada”. Esto evita que una entrada supuesta se trate como hecho.

**Efecto:** no altera D1–D6; obliga a declarar el estado real de cada insumo.

### P2. Separar modelos de escenarios

**Dónde:** línea 16.

**Texto propuesto:**

> Parámetros de simulación: longitud T, réplicas Monte Carlo N, semillas y escenarios (por ejemplo, base y perturbado). Los modelos comparados (M0, M1, M2) se especifican aparte de los escenarios.

**Por qué:** evita tablas y decisiones conceptualmente mezcladas.

### P3. Protocolo de evidencia faltante con rótulos obligatorios

**Dónde:** reemplazar “Qué hacer si falta evidencia” (líneas 45–49).

**Texto propuesto:**

> Clasificar toda ausencia como: `[SIN EVIDENCIA]`, `[EVIDENCIA PARCIAL]`, `[NO TRAZABLE]`, `[CONFLICTO]` o `[PROVISIONAL NO APROBADO]`. Para cada caso: (a) describir qué falta; (b) indicar qué afirmación queda bloqueada; (c) ofrecer dos alternativas concretas; (d) asignar la decisión al equipo. No completar celdas, no extrapolar de otros escenarios y no convertir un valor provisional en conclusión.

**Por qué:** la regla actual es correcta pero estrecha; solo cubre parámetros, ausencia total de simulaciones y conflicto de código.

**Efecto:** aplica de inmediato a la mezcla `m = 0.5` y a la definición abierta de M1.

### P4. Estados de decisión y prohibición de aprobación por silencio

**Dónde:** ampliar “Decisiones reservadas al grupo de trabajo” (líneas 26–32).

**Texto propuesto:**

> Toda decisión se registra como `propuesta`, `delegada`, `registrada`, `provisional` o `rechazada`, con fecha, responsable y evidencia. El silencio, la ausencia de objeciones o el uso de la skill no equivalen a aprobación. Una decisión delegada se respeta como tal, pero no se presenta como aprobación plena del equipo. Si la bitácora falta o se contradice, no inferir aprobaciones.

**Por qué:** la skill general ya lo dice, pero esta sección no lo reitera y el proyecto tiene una decisión delegada (D3.3) y varios elementos provisionales.

**Efecto:** preserva D3.3 y D6.3 sin reabrirlos.

### P5. Exigir comparabilidad del baseline

**Dónde:** ampliar criterio 1 (línea 19).

**Texto propuesto:**

> Documentar para el baseline y para el HMM: información de entrada, parámetros fijados o estimados, presupuesto de ajuste, criterio de selección y costo computacional. Si ambos usan parámetros “oráculo”, declararlo. Si el baseline es más débil por información y no por estructura, la comparación no aísla la contribución del HMM.

**Por qué:** un baseline débil puede producir una mejora aparente que no se debe al modelo.

### P6. Exigir análisis pareado y preespecificación

**Dónde:** ampliar criterios 3 y 4 (líneas 21–22).

**Texto propuesto:**

> Declarar antes de ejecutar la métrica principal, la dirección esperada y el criterio de éxito. Comparar modelos con las mismas secuencias y semillas; reportar la diferencia pareada por secuencia con su intervalo de confianza. No inferir diferencias a partir del solapamiento de intervalos marginales. Si hay varias métricas, escenarios o modelos, distinguir análisis confirmatorios de exploratorios y declarar si se aplica corrección por comparaciones múltiples.

**Por qué:** el proyecto ya usa diseño pareado, pero la skill no exige el análisis correspondiente. Esto es una omisión de método, no un cambio de D4.

**Efecto:** si el equipo quisiera añadir un análisis pareado al manuscrito, sería un análisis nuevo y debería registrarse; esta revisión no lo calcula.

### P7. Exigir procedencia y no fuga de etiquetas

**Dónde:** ampliar criterio 2 (línea 20).

**Texto propuesto:**

> Distinguir etiquetas reales, proxy y simuladas. Para etiquetas simuladas, documentar el generador y aclarar que son verdad de referencia solo dentro de la simulación. Verificar que las etiquetas no se usaron para ajustar, inicializar, seleccionar escenarios ni elegir métricas. Sin etiquetas de referencia, prohibir métricas supervisadas y proponer alternativas no supervisadas o diagnósticas para decisión del equipo.

**Por qué:** “etiquetas reales” puede leerse como etiquetas de campo, lo que contradice D1–D2.

### P8. Matriz de escenarios y control de perturbaciones

**Dónde:** ampliar criterio 3 y la tabla de salida (línea 38).

**Texto propuesto:**

> Presentar una tabla con: escenario, factor modificado, factores mantenidos fijos, efecto esperado, estado de aprobación y artefacto de resultados. Cambiar un factor a la vez salvo que se justifique un diseño factorial. Todo valor de perturbación no aprobado se marca `[PROVISIONAL NO APROBADO]` y no puede sostener el resumen, las conclusiones ni la etiqueta `final`.

**Por qué:** el escenario con B alterada depende de `m = 0.5`, que el propio proyecto declara provisional.

### P9. Reproducibilidad y alineación con el código como verificación, no como intención

**Dónde:** ampliar criterio 6 (línea 24) y “Formato de salida” (líneas 34–43).

**Texto propuesto:**

> Mantener una matriz de trazabilidad: elemento del protocolo → función o archivo → prueba → artefacto de salida. Reproducir al menos una cifra resumen desde los artefactos y comparar. Registrar commit o etiqueta, versión de Python, dependencias, comando, semillas, duración y fecha. Excluir explícitamente cifras y figuras de `legacy/`. Si la reproducción falla, aplicar `[CONFLICTO]` y no cerrar.

**Por qué:** “verificar que el diseño corresponda al código” es correcto, pero no operativo. Esta propuesta lo convierte en una comprobación repetible.

### P10. Ampliar la salida con lo que no se puede afirmar

**Dónde:** ampliar “Formato de salida” (líneas 34–43).

**Texto propuesto:** añadir cuatro apartados:

> 5. **Evidencia faltante y afirmaciones bloqueadas:** lista de lo que no se puede afirmar y por qué.
> 6. **Desviaciones y corridas no reportadas:** cambios respecto del protocolo, corridas fallidas o no convergentes y resultados omitidos.
> 7. **Amenazas a la validez:** interna, externa, de constructo, de conclusión estadística y computacional.
> 8. **Trazabilidad:** cada cifra o tabla del borrador con su artefacto de origen.

**Por qué:** la salida actual puede quedar limpia aunque falte evidencia; estos apartados hacen visible el hueco.

### P11. Precisar el significado de “detener el cierre”

**Dónde:** última viñeta de “Qué hacer si falta evidencia” (línea 49).

**Texto propuesto:**

> Detener la etiqueta `final`, el resumen y las conclusiones, pero continuar el borrador provisional marcando el conflicto. No silenciar el conflicto ni resolverlo por inferencia.

**Por qué:** evita que la regla de seguridad bloquee toda la redacción o, al contrario, que se cierre con un conflicto abierto.

### P12. Bloque condicional para D5b

**Dónde:** añadir después del criterio 3 o como anexo.

**Texto propuesto:**

> Si D5b se activa: partición por secuencia; inicializaciones múltiples seleccionadas por validación, nunca por prueba; alineación de estados antes de comparar; error de Frobenius en A y B; log-verosimilitud; tolerancia; semillas; y reporte de corridas no convergentes. D5b permanece desactivado salvo decisión expresa.

**Por qué:** la skill menciona D5b, pero no traslada sus condiciones a esta sección. D5a sigue siendo el núcleo.

### P13. Pruebas de autoauditoría de la skill

**Dónde:** anexo de la skill o documento de validación.

**Propuesta:** probar la skill con casos hipotéticos y verificar que se comporta así:

| Caso de prueba | Respuesta esperada |
|---|---|
| No hay etiquetas de referencia | No proponer exactitud ni Macro-F1; marcar `[SIN ETIQUETAS]` y ofrecer alternativas |
| No hay baseline elegido | No inventar uno; marcar pendiente y ofrecer dos opciones |
| Un parámetro es provisional | Marcar `[PROVISIONAL NO APROBADO]`; excluirlo de conclusiones |
| El código contradice la bitácora | Reportar `[CONFLICTO]`; no cerrar |
| Solo hay resultados parciales | Reportar solo lo disponible; no completar celdas |
| Dos IC marginales se solapan | No afirmar ausencia de diferencia sin análisis pareado |
| La bitácora no existe | No atribuir aprobaciones |

Estas pruebas no generan resultados científicos; solo verifican el comportamiento de la skill.

---

## 7. Cambios mínimos recomendados

Si el equipo prefiere no reescribir la skill completa, el conjunto mínimo para cerrar las brechas más graves sería:

1. **P1** (compuerta de entradas).
2. **P3** (rótulos de evidencia faltante y regla de provisionalidad).
3. **P5** (comparabilidad del baseline).
4. **P6** (preespecificación y análisis pareado).
5. **P10** (salida con evidencia faltante, desviaciones y trazabilidad).

Los demás ajustes son deseables, pero no bloquean una revisión honesta de la sección.

---

## 8. Decisiones que se solicitan al equipo

No se registra ninguna aprobación en esta revisión. El equipo decide:

1. ¿Aprueba la compuerta de entradas con estados y entradas bloqueantes (P1)?
2. ¿Aprueba los rótulos de evidencia faltante y la regla de que un valor provisional no sostiene conclusiones (P3)?
3. ¿Aprueba exigir comparabilidad explícita del baseline (P5)?
4. ¿Aprueba exigir preespecificación y análisis pareado (P6)?
5. ¿Aprueba ampliar la salida con evidencia faltante, desviaciones y trazabilidad (P10)?
6. ¿Autoriza modificar la skill, o prefiere mantener estas propuestas como documento de revisión?
7. ¿Confirma la definición vigente de M1 y el valor de mezcla de la B alterada, o los deja como pendientes?
8. ¿Desea añadir al manuscrito un análisis pareado de los resultados ya existentes? En caso afirmativo, sería un análisis nuevo que debería ejecutarse y registrarse; esta revisión no lo calculó.

---

## 9. Lo que esta revisión no hace

- No modifica `.agents/skills/articulo-hmm/articulo-hmm-diseno-experimental.md`.
- No ejecuta el protocolo ni recalcula métricas.
- No verifica numéricamente `outputs/`.
- No busca ni cita fuentes externas.
- No registra aprobaciones del equipo.
- No declara que la sección sea `final` ni que la skill esté aprobada.
