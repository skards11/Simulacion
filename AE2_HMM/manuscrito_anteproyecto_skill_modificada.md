# Decodificación con modelos ocultos de Markov frente a una regla de humedad en un caso didáctico de riesgo de incendio forestal: anteproyecto con trazabilidad y decisiones pendientes

**Producto:** anteproyecto provisional  
**Skill aplicada:** `.agents/skills/articulo-hmm/skill_modificada.md`  
**Insumos usados:** `materiales/caso_riesgo_de_incendio_forestal.md` y `materiales/plantilla_articulo.pdf`  
**Fecha:** 2026-11-09  
**Autoría propuesta:** Oscar Alonso De la Pava Suarez, Anderson Jesus Ospina Cardona, Kevin Andrés Valencia Daza — *pendiente de confirmación en esta versión*  
**Estado de aprobación:** **ninguna decisión, autoría, referencia o declaración de esta versión ha sido aprobada por el equipo.**  
**Declaración de uso de IA:** propuesta, no aprobada (ver §10)

> **Nota de alcance.** Este producto se construye únicamente con la solicitud inicial y los materiales iniciales. No reutiliza el manuscrito previo, sus tablas ni sus cifras. La ejecución D4 que existe en el repositorio se menciona solo como evidencia disponible no incorporada (§6.3), porque no forma parte de los insumos de esta versión y no fue auditada aquí.

---

## Resumen

Este anteproyecto estudia, con fines exclusivamente didácticos, si un modelo oculto de Markov (HMM) aporta alguna ventaja de decodificación frente a una regla simple de humedad en el caso de riesgo de incendio forestal del material del curso. El caso no aporta datos sensorizados reales, no define los estados como variables físicas y advierte que la humedad por sí sola no demuestra el riesgo en el terreno. Por tanto, el problema se delimita como un ejercicio de formalización y comparación controlada, no como un estudio ecológico.

Se proponen dos preguntas evaluables. La primera compara la decodificación del HMM con parámetros fijos frente a un umbral determinista sobre la humedad actual, usando macro-F1, recall de la clase extrema y exactitud sobre secuencias sintéticas pareadas. La segunda repite la comparación cuando la matriz de emisión se acerca a la uniforme, para observar cuánto depende el resultado de la separabilidad de las observaciones. El diseño previsto es pareado, con la secuencia como unidad independiente, métricas agregadas por secuencia e intervalos de confianza por bootstrap.

**No se reportan resultados porque el experimento no se ejecutó en esta versión.** El producto incluye la formalización, las razones para usar y para descartar el HMM, el protocolo experimental, una tabla vacía de resultados, la trazabilidad de cada afirmación extraída y una lista explícita de decisiones pendientes. Las referencias se presentan como candidatas, no como verificadas. No se atribuye ninguna aprobación al equipo.

**Palabras clave:** modelos ocultos de Markov, decodificación, Viterbi, Forward–Backward, macro-F1, simulación, trazabilidad.

---

## 1. Problema y alcance

### 1.1 Hechos verificados en el material

Los siguientes elementos se extraen directamente del caso y se usan como hechos de partida, no como resultados:

- El entorno registra niveles ambientales de humedad **alta, media y baja** (caso, línea 3).
- Se explora si un HMM permite inferir estados supuestos de **Riesgo Bajo, Riesgo Moderado y Riesgo Extremo** (caso, línea 3).
- **No se aporta un dataset sensorizado real** (caso, línea 3).
- La humedad por sí sola **no demuestra directamente** el nivel de riesgo en el terreno (caso, línea 3).
- Se ofrecen cinco observaciones ilustrativas: Alta, Alta, Media, Baja, Baja (caso, línea 5).
- Los parámetros A, B y π son **hipotéticos** y no fueron estimados de un ecosistema real (caso, líneas 7–12).
- En A, las filas y columnas corresponden a Riesgo Bajo, Moderado y Extremo; en B, las filas son esos estados y las columnas son Humedad Alta, Media y Baja (caso, línea 14).
- Las tareas solicitadas son formular pregunta, justificar el HMM, proponer un método sencillo de comparación, datos, métrica y experimento controlado; distinguir decodificación con parámetros conocidos de entrenamiento; y no inventar hallazgos, fuentes ni cifras (caso, línea 16).

La plantilla del curso se usa solo como referencia de estructura y secciones (plantilla, pp. 1–8). Sus cifras y escenarios pertenecen a otro ejercicio y **no se trasladan** a este anteproyecto.

### 1.2 Supuestos de trabajo (no aprobados)

Estos supuestos permiten avanzar, pero no se registran como decisiones del equipo:

1. Los estados `s1`, `s2` y `s3` se tratan como **etiquetas puras**, sin definición física; “Riesgo Bajo/Moderado/Extremo” funciona como alias mnemónico.
2. La humedad es **ordinal**: Alta > Media > Baja. No se inventan porcentajes ni umbrales numéricos.
3. Un paso es una **ocasión de observación**, sin unidad física. “Día” solo sería una convención editorial.
4. A, B y π se usan **tal como aparecen** en el caso, como generador de secuencias sintéticas.
5. La relación “más humedad, menos riesgo” está incorporada en B por el material; es un supuesto didáctico, no evidencia de campo.

### 1.3 Inferencias a partir de las matrices

Estas afirmaciones no están escritas en el caso; se derivan de sus matrices y se marcan como inferencias:

- π no es la distribución estacionaria de A. El cálculo da πA ≈ [0.460, 0.335, 0.205], distinto de π = [0.50, 0.30, 0.20].
- La distribución estacionaria de A es aproximadamente ξ ≈ [0.424, 0.348, 0.227].
- Las duraciones medias aproximadas en cada estado son 3.33, 2.00 y 2.50 pasos, a partir de 1/(1 − aᵢᵢ).
- El mapeo determinista de M0 sobre las columnas de B es Alta → s1, Media → s2, Baja → s3, porque cada columna tiene un máximo distinto.
- En t = 1, el clasificador que solo mira una observación y usa π y B tiene un límite teórico cercano a 0.67; no se usa como resultado, solo como cota de referencia.

### 1.4 Incertidumbres

- No hay datos reales ni etiquetas reales de riesgo.
- No hay definición física de los estados ni unidad de tiempo.
- No hay revisión de literatura ejecutada en esta versión.
- No hay resultados experimentales ejecutados en esta versión.
- No se conoce la sensibilidad del diseño al valor de mezcla de la B alterada.
- No se puede afirmar validez ecológica, capacidad predictiva ni superioridad general del HMM.

### 1.5 Razones para usar un HMM

1. **Estructura temporal explícita:** el HMM representa persistencia y transiciones entre regímenes latentes, algo que una regla sobre la humedad actual no modela.
2. **Inferencia probabilística:** Forward–Backward produce posteriores marginales y Viterbi produce una ruta; ambas son comparables con una línea base simple.
3. **Separación conceptual:** permite distinguir evaluación, decodificación y aprendizaje, que es justamente lo que pide el caso.
4. **Comparación controlada:** con A, B y π fijos se puede aislar el efecto de la estructura del modelo sin confundirlo con la calidad de la estimación.
5. **Reproducibilidad:** al ser un modelo discreto y pequeño, es posible registrar matrices, semillas y código con bajo costo computacional.

### 1.6 Razones para descartar o cuestionar el HMM

1. **No hay datos reales:** sin observaciones de campo, el HMM no puede validarse ecológicamente; solo puede simularse.
2. **B ya codifica la relación humedad–riesgo:** si el objetivo se reduce a asignar la humedad actual a un estado, M0 puede ser suficiente y más transparente.
3. **Riesgo de sobreajuste conceptual:** añadir estados latentes, transiciones y un prior puede dar apariencia de sofisticación sin mejorar la decisión.
4. **Parámetros “oráculo”:** si A, B y π se fijan, el ejercicio evalúa decodificación, no aprendizaje; no demuestra que el HMM sea útil en un problema real.
5. **Supuestos fuertes:** Markov de primer orden, estacionariedad, emisiones discretas y estados como etiquetas puras no están justificados por el material.
6. **Costo interpretativo:** un resultado agregado mejor puede ocultar un peor recall de la clase extrema, que suele ser la más relevante.
7. **Alternativa más simple:** una regla ordinal o una cadena observable pueden explicar gran parte del comportamiento sin estados latentes.

La conclusión provisional es que el HMM **es pertinente como objeto de estudio didáctico**, pero **no está justificado como solución superior** antes de compararlo y de reportar incertidumbre.

### 1.7 Alternativas de alcance

| Alternativa | Alcance | Ventaja | Límite | Estado |
|---|---|---|---|---|
| A. Decodificación con A, B y π fijos | Forward, Forward–Backward y Viterbi; comparación con M0 y M1 | Aísla la estructura del modelo; es reproducible | No evalúa aprendizaje; no valida ecología | **Propuesta principal** |
| B. Añadir Baum–Welch | Estimar A, B y π con EM | Permite estudiar aprendizaje | Requiere partición, inicializaciones y alineación; excede el caso | Pendiente de autorización |
| C. Usar datos reales | Validación externa | Mayor pertinencia aplicada | No hay dataset disponible | No viable con estos materiales |
| D. Solo regla simple | M0 ordinal, sin HMM | Máxima transparencia | No responde si el HMM aporta algo | Línea base obligatoria |

La alternativa A se propone porque responde al caso sin inventar datos. La D no se descarta: se incorpora como baseline.

---

## 2. Preguntas y objetivos

### 2.1 Preguntas investigables

**P1. Con A, B y π fijos, ¿la decodificación del HMM (M2) mejora la macro-F1 y el recall de la clase extrema frente a una regla determinista sobre la humedad actual (M0) en secuencias sintéticas pareadas?**

- **Comparación:** M0 frente a M2, con las mismas observaciones y los mismos estados verdaderos simulados.
- **Criterio de evaluación:** diferencia de medias por secuencia en macro-F1, recall de `s3` y exactitud, con IC 95 % por bootstrap de secuencias. No se afirmará superioridad si el intervalo de la diferencia incluye 0 o si el resultado depende del escenario.
- **Evidencia necesaria:** secuencias, etiquetas simuladas, matrices fijas, semillas y salidas reproducibles.

**P2. ¿Cómo cambia esa comparación cuando la matriz de emisión B se acerca a la uniforme, reduciendo la separabilidad entre estados?**

- **Comparación:** el mismo par M0/M2 en escenario base y en escenario con B alterada, con el mismo T, N y semillas.
- **Criterio de evaluación:** cambio en macro-F1, recall de `s3` y exactitud; se reportará también la pérdida o ganancia absoluta y su IC.
- **Condición:** el valor de mezcla debe fijarse antes de ejecutar y registrarse; en esta versión se propone m = 0.5 como valor provisional, no aprobado.

No se plantea una tercera pregunta de aprendizaje porque Baum–Welch queda fuera del alcance propuesto.

### 2.2 Objetivo general

Formular, implementar y evaluar de forma reproducible una comparación de decodificación entre un HMM didáctico de tres estados y una regla simple de humedad, sin afirmar validez ecológica ni superioridad general.

### 2.3 Objetivos específicos

1. Formalizar el HMM con S = {s1, s2, s3}, V = {Alta, Media, Baja}, A, B y π fijos, y explicar Forward, Forward–Backward y Viterbi sin confundirlos con el aprendizaje.
2. Diseñar un experimento pareado con T = 500, N = 2000 y semillas independientes por secuencia, que compare M0, M1 y M2 con macro-F1, recall de `s3` y exactitud, agregadas por secuencia.
3. Ejecutar, si el equipo lo autoriza, un escenario secundario con B alterada y reportar los cambios con incertidumbre.

### 2.4 Lo que este anteproyecto no responde

- No responde si el HMM es mejor en incendios reales.
- No responde si los estados latentes existen en el ecosistema.
- No responde si A, B y π son correctos.
- No responde si Baum–Welch recupera los parámetros.
- No responde si el modelo es publicable en un venue Q1.

---

## 3. Estado del arte

### 3.1 Protocolo de búsqueda propuesto

No se ejecutó una búsqueda bibliográfica en esta versión y no se declara acceso a bases indexadas. El protocolo queda preparado para que el equipo lo apruebe y lo ejecute:

| Elemento | Propuesta | Estado |
|---|---|---|
| Bases | Scopus, Web of Science, IEEE Xplore | Acceso no verificado |
| Cadena 1 | `"hidden Markov model" AND ("decoding" OR "Viterbi") AND ("baseline" OR "comparison")` | No ejecutada |
| Cadena 2 | `"hidden Markov model" AND ("emission matrix" OR "sensitivity") AND ("synthetic" OR "simulation")` | No ejecutada |
| Ventana | 1989–2026, con clásicos anteriores por búsqueda inversa | No ejecutada |
| Criterios de inclusión | Artículo original, HMM discreto o comparable, métricas de decodificación, suficiente detalle metodológico | Pendiente de aprobación |
| Criterios de exclusión | Revisiones sin datos, aplicaciones sin métricas, duplicados, textos no accesibles | Pendiente de aprobación |
| Registro | Base, cadena, fecha, filtros, resultados y deduplicación | Pendiente |
| Extracción | Pregunta, modelo, datos, métricas, resultado, límite y página/sección | Pendiente |
| Verificación | Comprobar que la cita existe y que la afirmación aparece en la página indicada | Pendiente |

### 3.2 Referencias candidatas

| Referencia | Ubicación en la plantilla | Estado en esta versión | Uso previsto |
|---|---|---|---|
| L. R. Rabiner, “A tutorial on hidden Markov models and selected applications in speech recognition,” *Proceedings of the IEEE*, 77(2), 257–286, 1989. | Plantilla, p. 7, referencia [1] | **Candidata; no verificada en esta versión** | Contexto de los tres problemas clásicos |
| L. E. Baum, T. Petrie, G. Soules y N. Weiss, “A maximization technique occurring in the statistical analysis of probabilistic functions of Markov chains,” *The Annals of Mathematical Statistics*, 41(1), 164–171, 1970. | Plantilla, p. 7, referencia [2] | **Candidata; no verificada en esta versión** | Contexto del aprendizaje por EM |

No se incluyen otras referencias porque no fueron consultadas ni verificadas. La plantilla menciona otras fuentes en su Tabla 1 (p. 3), pero **no se usan** aquí: no se dispone de los originales ni de sus páginas.

### 3.3 Vacío que motiva el ejercicio

El vacío no se plantea como un hueco de la literatura, porque no se hizo una revisión sistemática. Se plantea como una **necesidad docente y metodológica**: separar la inferencia con parámetros conocidos del aprendizaje, evitar fuga de información, comparar contra una línea base simple y reportar incertidumbre. La plantilla insiste en reproducibilidad y rigor (plantilla, pp. 1–2), pero sus propios resultados pertenecen a otro diseño; este anteproyecto no los adopta.

---

## 4. Marco teórico

### 4.1 Definición del HMM

Un HMM discreto se especifica como λ = (S, V, A, B, π), donde:

- S = {s1, s2, s3} es el conjunto de estados latentes.
- V = {Alta, Media, Baja} es el alfabeto de observaciones.
- A = [aᵢⱼ] es la matriz de transición, con aᵢⱼ = P(Sₜ = sⱼ | Sₜ₋₁ = sᵢ) y filas que suman 1.
- B = [bᵢ(k)] es la matriz de emisión, con bᵢ(k) = P(Oₜ = vₖ | Sₜ = sᵢ) y filas que suman 1.
- π = [πᵢ] es la distribución inicial en t = 1, con πᵢ = P(S₁ = sᵢ) y suma 1.

Las matrices del caso son:

```text
A = [[0.70, 0.25, 0.05],
     [0.30, 0.50, 0.20],
     [0.10, 0.30, 0.60]]

B = [[0.70, 0.25, 0.05],
     [0.20, 0.60, 0.20],
     [0.05, 0.25, 0.70]]

π = [0.50, 0.30, 0.20]
```

Estas matrices son hipotéticas y se usan como generador, no como estimación de un ecosistema real (caso, líneas 7–12).

### 4.2 Los tres problemas clásicos y el alcance

1. **Evaluación:** calcular P(O₁:T | λ) con Forward.
2. **Decodificación:** obtener la ruta más probable con Viterbi o las posteriores marginales con Forward–Backward.
3. **Aprendizaje:** estimar A, B y π con Baum–Welch.

Este anteproyecto se limita a **evaluación y decodificación con A, B y π fijos**. No implementa ni evalúa Baum–Welch. La distinción es importante porque un buen resultado de decodificación con parámetros “oráculo” no demuestra que el modelo pueda aprenderse de datos.

### 4.3 Parámetros fijados frente a parámetros aprendidos

| Parámetro | Estado en este anteproyecto | Origen | Implicación |
|---|---|---|---|
| A | Fijado | Caso, líneas 8–14 | No se estima; se usa como generador y como modelo |
| B | Fijado | Caso, líneas 10–14 | No se estima; se usa como generador y como modelo |
| π | Fijado | Caso, línea 12 | Prior inicial en t = 1; no es estacionario |
| m (mezcla de B alterada) | Provisional | Propuesta de esta versión | Debe fijarse antes de ejecutar |
| Semillas | Fijadas por diseño | Propuesta | Deben registrarse por secuencia |
| Baum–Welch | No usado | Fuera de alcance | No hay parámetros aprendidos |

### 4.4 Modelos comparados

- **M0 — regla determinista sin HMM:** asigna a cada observación el estado con mayor probabilidad en B. Con las matrices del caso: Alta → s1, Media → s2, Baja → s3. Es la línea base simple que exige el diseño experimental.
- **M1 — cadena observable con prior estacionario:** usa A, B y la distribución estacionaria ξ de A en lugar de π. Se incluye como referencia intermedia para separar el efecto de la estructura observable del efecto del prior inicial.
- **M2 — HMM completo:** usa A, B y π. La regla principal es el argmax de la posterior marginal de Forward–Backward; Viterbi se conserva como análisis de sensibilidad.

M0 no usa estados latentes; M1 y M2 sí. Los tres reciben las mismas observaciones y se evalúan contra los mismos estados simulados.

### 4.5 Métricas y disponibilidad de etiquetas

- **Macro-F1:** promedio no ponderado del F1 de las tres clases. Es la métrica principal porque no deja que la clase mayoritaria domine.
- **Recall de `s3`:** proporción de pasos con estado verdadero `s3` identificados como `s3`. Es secundaria, pero relevante porque la clase extrema suele ser la de mayor interés.
- **Exactitud:** proporción de pasos correctamente clasificados. Es secundaria y puede ocultar desbalances.

**Comprobación de etiquetas:** en este caso no existen etiquetas reales de riesgo. Las únicas etiquetas verdaderas posibles son las generadas por la simulación. Por tanto, macro-F1, recall y exactitud se calcularán **únicamente sobre secuencias sintéticas** y no se reportarán como validación en datos de campo. Esta condición se cumple antes de proponer cualquier métrica supervisada.

---

## 5. Metodología

### 5.1 Datos

No se usan datos reales. Para cada secuencia sintética se generan estados latentes a partir de π y A, y observaciones a partir de B. Las cinco observaciones del caso (Alta, Alta, Media, Baja, Baja) son solo ilustrativas y no constituyen un dataset de evaluación.

### 5.2 Diseño experimental previsto

- **Diseño pareado:** M0, M1 y M2 reciben exactamente las mismas observaciones y se comparan contra los mismos estados latentes.
- **Tamaño propuesto:** T = 500 pasos por secuencia; N = 2000 secuencias.
- **Semillas:** una semilla maestra y una semilla distinta por secuencia, derivada y registrada. No se reinicia la misma semilla en réplicas supuestamente independientes.
- **Unidad independiente:** la secuencia, no el paso de tiempo. Las métricas se calculan por secuencia y luego se agregan.
- **Agregación:** media, desviación estándar e IC 95 % por bootstrap de secuencias (1000 réplicas propuestas).
- **Escenarios:** base y B alterada. Ambos comparten T, N, semilla maestra y reglas de decisión.

Estos valores son una **propuesta de protocolo**, no una ejecución. No se reportan como resultados.

### 5.3 Reglas de decisión

- **M0:** ŝₜ = argmaxᵢ Bᵢ,Oₜ.
- **M1:** HMM con A, B y ξ; ŝₜ = argmaxᵢ P(Sₜ = sᵢ | O₁:T).
- **M2:** HMM con A, B y π; misma regla de posterior marginal. La ruta de Viterbi se conserva como sensibilidad.

### 5.4 Escenario con B alterada

La B alterada se construiría mezclando cada fila de B con la distribución uniforme:

```text
B_alt = (1 − m) B + m (1/3)
```

con m = 0.5 **provisional**. Al aumentar m, las emisiones se vuelven menos separables. El valor de m no está aprobado y debe fijarse antes de ejecutar; si el equipo no lo fija, el escenario debe reportarse como exploratorio y no como confirmatorio.

### 5.5 Prevención de fuga de información

- Las etiquetas verdaderas se usan **solo para evaluar**, nunca para elegir el modelo, calibrar el prior ni seleccionar semillas.
- M0, M1 y M2 no se ajustan con las etiquetas.
- No se selecciona el mejor modelo mirando el conjunto de prueba.
- No se reutilizan secuencias entre réplicas.
- Las matrices A y B se mantienen fijas en todos los modelos; cualquier cambio se declara como escenario.

### 5.6 Fases metodológicas

| Fase | Actividad | Responsable propuesto | Evidencia | Estado |
|---|---|---|---|---|
| F1 | Protocolo y alcance | Equipo | Este documento | Propuesta |
| F2 | Materiales del caso | Equipo / IA | Caso y plantilla leídos | Hecho |
| F3 | Formalización del HMM | IA, revisión del equipo | §4 | Propuesta |
| F4 | Implementación y pruebas | Equipo / IA | Código y pruebas | Pendiente |
| F5 | Simulación pareada | Equipo | `outputs/` | Pendiente en esta versión |
| F6 | Métricas e intervalos | Equipo | Tabla y figura | Pendiente |
| F7 | Revisión y aprobación | Equipo | Bitácora | Pendiente |

La tabla distingue acciones mecánicas de decisiones científicas. Ninguna fila se registra como aprobada por el equipo.

### 5.7 Reproducibilidad prevista

Si se autoriza la ejecución, el protocolo debería registrar:

- Versión de Python y dependencias.
- Semilla maestra y semillas por secuencia.
- Comando exacto de ejecución.
- Matrices A, B, π y m usados.
- Salidas crudas, tabla agregada y figura.
- Fecha, duración y cualquier advertencia.

No se afirma que estos artefactos existan en esta versión.

---

## 6. Resultados

### 6.1 Estado de la evidencia

**No hay resultados ejecutados en esta versión.** No se reportan cifras porque no se ejecutó el protocolo con los insumos de este anteproyecto. Tampoco se copian las cifras de la plantilla ni las del manuscrito previo: pertenecen a otros diseños y no fueron auditadas aquí.

### 6.2 Tabla vacía de resultados

| Modelo | Macro-F1 media | IC 95 % | Recall `s3` media | IC 95 % | Exactitud media | IC 95 % |
|---|---:|---:|---:|---:|---:|---:|
| M0 | — | — | — | — | — | — |
| M1 | — | — | — | — | — | — |
| M2 | — | — | — | — | — | — |

| Escenario | Modelo | n secuencias | Media macro-F1 | Diferencia vs M0 | IC 95 % de la diferencia |
|---|---|---:|---:|---:|---:|
| Base | M0 | — | — | — | — |
| Base | M2 | — | — | — | — |
| B alterada | M0 | — | — | — | — |
| B alterada | M2 | — | — | — | — |

### 6.3 Evidencia disponible no incorporada

El repositorio contiene una ejecución D4 previa con resultados en `outputs/`. Esa evidencia **no se incorpora** a este producto porque:

1. No forma parte de los materiales iniciales de esta solicitud.
2. Depende de decisiones y supuestos que no se revalidan en esta versión.
3. Su valor de mezcla para B alterada es provisional.
4. No fue auditada en esta sesión.

Si el equipo autoriza su reutilización, debería añadirse como anexo con la trazabilidad completa a `outputs/protocolo_d4_resumen.json`.

### 6.4 Plan de presentación si se ejecuta

- Tabla por escenario con media, desviación e IC por bootstrap de secuencias.
- Figura con macro-F1, recall de `s3` y exactitud por modelo.
- Distribución por secuencia, no solo el promedio.
- Tabla de diferencias pareadas M2 − M0 y M2 − M1.
- Registro de semillas y comandos.
- Declaración explícita de que las cifras son simuladas.

---

## 7. Discusión

### 7.1 Lo que se puede discutir sin resultados

Sin resultados, la discusión se limita al diseño:

- La comparación es informativa solo si M0 es una línea base realmente simple y M2 no recibe información adicional.
- M1 y M2 comparten A y B; si solo cambia el prior, la diferencia puede ser pequeña con T largo.
- La macro-F1 puede mejorar mientras el recall de `s3` empeora; la conclusión depende de la métrica.
- El escenario con B alterada es una prueba de estrés, no una condición real.
- La disponibilidad de etiquetas simuladas permite calcular F1, pero no valida el modelo en campo.

### 7.2 Amenazas a la validez

- **Validez de constructo:** los estados son etiquetas puras; “riesgo” no es una variable física medida.
- **Validez interna:** el prior π no es estacionario; M1 y M2 pueden diferir por ese detalle y no por la estructura latente.
- **Validez externa:** no hay datos reales ni población definida.
- **Validez de conclusión:** sin ejecución no hay inferencia estadística; con ejecución, los IC son descriptivos y no sustituyen pruebas de hipótesis.
- **Sesgo de métrica:** la exactitud y la macro-F1 pueden ocultar el comportamiento de la clase extrema.

### 7.3 Explicaciones alternativas si aparecen diferencias

Si M2 supera a M0, podría deberse a la persistencia temporal, al uso del prior o a la suavización de Forward–Backward, no necesariamente a una “mejor comprensión” del riesgo. Si M0 supera a M2, podría deberse a que B ya contiene la señal útil y el HMM añade ruido. Si M1 y M2 coinciden, el prior inicial sería irrelevante con T largo. Ninguna de estas explicaciones se afirma como resultado.

### 7.4 Límites de la plantilla

La plantilla es una guía de estructura y redacción (plantilla, pp. 1–2), no una garantía de aceptación editorial ni un estándar Q1 automático. Sus tablas y cifras (plantilla, pp. 5–7) corresponden a otro ejercicio y no se reutilizan.

---

## 8. Conclusiones provisionales

**Sobre P1.** No puede responderse todavía: no se ejecutó el experimento. El anteproyecto deja la comparación definida, con métricas, unidad de análisis y criterio de decisión.

**Sobre P2.** No puede responderse todavía: el escenario con B alterada requiere fijar m y ejecutar el protocolo. El valor m = 0.5 es solo una propuesta.

**Conclusión metodológica.** El HMM puede formalizarse con S, V, A, B y π sin inventar porcentajes de humedad ni definiciones físicas. También es posible diseñar una comparación controlada contra una regla simple. Lo que no es posible, con estos materiales, es afirmar que el HMM sea superior o ecológicamente válido.

**Trabajo futuro:** ejecutar el protocolo, auditar las salidas, añadir pruebas de hipótesis y tamaños de efecto, completar la búsqueda bibliográfica, verificar las referencias y, solo si se obtienen datos adecuados, explorar una validación externa.

---

## 9. Limitaciones

- Los resultados no existen en esta versión; el documento es un anteproyecto.
- No hay datos reales ni etiquetas reales.
- Los estados son etiquetas puras; “riesgo” es un alias didáctico.
- La humedad es ordinal; no se usan porcentajes.
- A, B y π son hipotéticos y fijos; no se estimaron.
- M1 y M2 comparten A y B; la comparación no aísla una línea base completamente distinta.
- El valor de m para B alterada es provisional.
- No hay revisión sistemática ni referencias verificadas en esta versión.
- La plantilla no garantiza calidad Q1 ni aceptación editorial.
- No se atribuye ninguna aprobación al equipo.

---

## 10. Declaración de uso de IA

Se utilizó un asistente de programación basado en IA (OpenCode) para organizar el protocolo, proponer la estructura, redactar el borrador y preparar las tablas de trazabilidad. Las decisiones científicas, la autoría, las referencias y esta declaración **no están aprobadas por el equipo en esta versión**. Cualquier uso final requiere revisión y aprobación explícita del grupo de trabajo.

---

## 11. Referencias

**Referencias candidatas, no verificadas en esta versión:**

1. L. R. Rabiner, “A tutorial on hidden Markov models and selected applications in speech recognition,” *Proceedings of the IEEE*, vol. 77, no. 2, pp. 257–286, 1989. Citada en la plantilla, p. 7, referencia [1].
2. L. E. Baum, T. Petrie, G. Soules y N. Weiss, “A maximization technique occurring in the statistical analysis of probabilistic functions of Markov chains,” *The Annals of Mathematical Statistics*, vol. 41, no. 1, pp. 164–171, 1970. Citada en la plantilla, p. 7, referencia [2].

**Materiales internos:**

3. Caso didáctico “Evaluación de riesgo de incendio forestal,” `materiales/caso_riesgo_de_incendio_forestal.md`. Documento interno, no publicado.
4. Plantilla de artículo Q1 del curso, `materiales/plantilla_articulo.pdf`. Documento interno, no publicado.

No se incluyen otras referencias porque no fueron consultadas ni verificadas.

---

## Anexo A. Trazabilidad de afirmaciones

| Afirmación | Fuente | Ubicación | Tipo |
|---|---|---|---|
| El entorno registra humedad alta, media y baja | Caso | Línea 3 | Hecho |
| Se exploran estados de riesgo Bajo, Moderado y Extremo | Caso | Línea 3 | Hecho |
| No hay dataset sensorizado real | Caso | Línea 3 | Hecho |
| La humedad sola no demuestra el riesgo | Caso | Línea 3 | Hecho |
| Observaciones ilustrativas Alta, Alta, Media, Baja, Baja | Caso | Línea 5 | Hecho |
| A, B y π son hipotéticos | Caso | Líneas 7–12 | Hecho |
| Filas/columnas de A y B | Caso | Línea 14 | Hecho |
| Tareas del caso | Caso | Línea 16 | Hecho |
| πA ≈ [0.460, 0.335, 0.205] | Cálculo propio | — | Inferencia |
| ξ ≈ [0.424, 0.348, 0.227] | Cálculo propio | — | Inferencia |
| Duraciones 3.33, 2.00 y 2.50 | Cálculo propio | — | Inferencia |
| M0: Alta→s1, Media→s2, Baja→s3 | Cálculo sobre B | — | Inferencia |
| Estructura de resumen, secciones y tablas | Plantilla | pp. 1–8 | Referencia estructural |
| Tres problemas clásicos | Plantilla | p. 4, §3.4 | Referencia estructural |
| Fases F1–F7 | Plantilla | p. 5, Tabla 2 | Referencia estructural |
| Rabiner y Baum como candidatas | Plantilla | p. 7, referencias [1] y [2] | Referencia no verificada |
| Cifras de la plantilla | Plantilla | pp. 1, 6–7 | No aplicables a este caso |

---

## Anexo B. Bitácora de decisiones pendientes

| Fecha | Consulta | Propuesta | Verificación | Decisión humana | Justificación | Evidencia |
|---|---|---|---|---|---|---|
| 2026-11-09 | Problema y alcance | Ejercicio didáctico, sin validez ecológica | Coherente con el caso | **Pendiente** | El material no aporta datos reales | Caso, línea 3 |
| 2026-11-09 | Semántica de estados | Etiquetas puras; “riesgo” como alias | Coherente con el caso | **Pendiente** | Evita inventar definiciones físicas | Caso, línea 3 |
| 2026-11-09 | Humedad | Escala ordinal Alta/Media/Baja | Coherente con el caso | **Pendiente** | No hay porcentajes en el material | Caso, líneas 3–14 |
| 2026-11-09 | Parámetros | A, B y π fijos | Matrices válidas | **Pendiente** | El caso las ofrece como hipotéticas | Caso, líneas 7–12 |
| 2026-11-09 | Preguntas | P1 y P2 con comparación y criterio | Verificables si se ejecuta | **Pendiente** | Responden al caso sin inventar resultados | §2 |
| 2026-11-09 | Comparación | M0, M1 y M2 | Baseline sin HMM incluida | **Pendiente** | Permite aislar el aporte del HMM | §4.4 |
| 2026-11-09 | Métricas | Macro-F1, recall s3, exactitud | Etiquetas solo sintéticas | **Pendiente** | No hay etiquetas reales | §4.5 |
| 2026-11-09 | Tamaño | T = 500, N = 2000 | Propuesta reproducible | **Pendiente** | Equilibra costo y precisión | §5.2 |
| 2026-11-09 | B alterada | m = 0.5 | Provisional | **Pendiente** | Prueba de estrés, no condición real | §5.4 |
| 2026-11-09 | Referencias | Rabiner y Baum como candidatas | No verificadas aquí | **Pendiente** | No se inventan citas | §11 |
| 2026-11-09 | Autoría | Nombres propuestos | No aprobada | **Pendiente** | No se atribuye aprobación | Portada |
| 2026-11-09 | Declaración de IA | OpenCode como asistente | No aprobada | **Pendiente** | Requiere revisión del equipo | §10 |

---

## Anexo C. Pendientes científicos priorizados

1. **C1 — Aprobar o rechazar el alcance:** decidir si el ejercicio se limita a decodificación con parámetros fijos o si se añade aprendizaje.
2. **C2 — Fijar el valor de m:** sin un valor aprobado, el escenario con B alterada es exploratorio.
3. **C3 — Ejecutar el protocolo:** generar secuencias, correr M0/M1/M2, guardar semillas y salidas.
4. **C4 — Auditar las salidas:** verificar que cada cifra provenga de una ejecución y que la agregación sea por secuencia.
5. **C5 — Completar la búsqueda bibliográfica:** ejecutar el protocolo de §3.1 y verificar cada cita con página o sección.
6. **C6 — Revisar la plantilla:** comprobar que la estructura cumple los requisitos del curso sin copiar sus cifras.
7. **C7 — Aprobar autoría y declaración de IA:** solo después de revisar el texto.

## Anexo D. Siguiente paso

La IA puede continuar con acciones mecánicas: preparar el esqueleto de código, las tablas vacías y el registro de semillas. **No debe registrar aprobaciones, ejecutar el protocolo ni reportar resultados hasta que el equipo lo autorice expresamente.**
