# Guía para elaborar el documento — Problema bancario (AE3)

Esta guía acompaña el código de `AE3_Problema_Bancario` y explica **cómo
convertir los resultados simulados en el documento de entrega** que pide la
actividad 2-M3: introducción, metodología, resultados y conclusiones, más
video de sustentación y repositorio en GitHub.

> **Regla de oro:** ninguna cifra del documento debe escribirse “a mano” sin
> poder rastrearla hasta un archivo de `outputs/`. Cada tabla y cada figura de
> esta guía indica su archivo fuente.

**Contenido de esta guía**

1. Qué debe contener la entrega
2. Antes de escribir: preparar la evidencia
3. Estructura recomendada del documento
4. Portada, índice y resumen ejecutivo
5. Introducción
6. Marco teórico y metodología
7. Resultados: los cinco puntos
8. Conclusiones y recomendaciones
9. Video de sustentación
10. Repositorio en GitHub
11. Mapeo contra la rúbrica
12. Lista de verificación antes de entregar
13. Apéndice: comandos y archivos
14. Cifras de referencia de la corrida actual

---

## 1. Qué debe contener la entrega

Según el enunciado del laboratorio y la rúbrica del módulo, la entrega tiene
cuatro componentes:

| Componente | Qué es | Dónde está la evidencia |
|---|---|---|
| **Documento** | Informe con introducción, metodología, resultados y conclusiones. | `docs/plantilla_documento.md` como esqueleto. |
| **Código y datos** | Simulación funcional, comentada y reproducible, con las tablas CSV y figuras que sustentan el informe. | `main.py`, `src/`, `tests/`, `scripts/`, `outputs/` y `outputs/figuras/`. |
| **Video** | Sustentación del problema, modelo, resultados y conclusiones. | Guion de 3 minutos en `docs/guion_video_pitch.md`. |
| **Repositorio** | Código, README, instrucciones y evidencias. | Checklist de la sección 10. |

Los datos se entregan como **CSV generados por el código Python**; no se
requiere crear ni adjuntar un archivo de Excel.

### Formato del documento

El laboratorio pide:

- Nombre del archivo: `Apellido_Nombre_problemaBancario.doc` (o `.docx`/`.pdf`).
- Portada, índice y numeración de páginas.
- Formato Word o PDF.
- Archivos adicionales: datos en CSV y código Python (no se requiere Excel).
- Al menos **10 réplicas independientes**; este proyecto usa **30** por defecto.

**Recomendación de extensión:** 12 a 18 páginas de cuerpo, sin contar portada,
índice, referencias ni anexos. Un documento demasiado corto suele omitir el
análisis; uno demasiado largo repite tablas que pueden ir en anexos.

---

## 2. Antes de escribir: preparar la evidencia

Ejecutar desde la carpeta `AE3_Problema_Bancario`:

```powershell
python scripts/reproduce.py
```

Ese comando ejecuta las pruebas, la simulación, las tablas y figuras, y
regenera el manifiesto. Si se prefiere correr paso a paso:

```powershell
python -m pytest -q
python main.py --replicas 30 --duration 480 --seed 42
python scripts/build_report_assets.py
```

> El manifiesto `outputs/MANIFEST.txt` **solo** lo genera
> `python scripts/reproduce.py`; los tres comandos sueltos no lo actualizan.

Esto produce:

- `outputs/resumen_ejecucion.md`: resumen con las cifras principales.
- `outputs/punto1_cajeros.csv` a `outputs/punto5_configuracion.csv`: tablas de
  los cinco puntos.
- `outputs/figuras/`: seis figuras a 300 dpi.
- `outputs/decisiones.json`: decisión del cajero adicional y recomendación
  final.
- `outputs/MANIFEST.txt`: hashes de todos los artefactos (se genera con
  `python scripts/reproduce.py`).

Antes de redactar, responder en una hoja aparte:

1. ¿Cuál es la pregunta del banco? (configuración de cajas para reducir esperas).
2. ¿Cuáles son los cinco puntos que califica la rúbrica?
3. ¿Qué decisión tomó el equipo y con qué criterios?
4. ¿Qué cifras exactas sustentan esa decisión?
5. ¿Qué limitaciones tiene el modelo?

Si el equipo cambia el número de réplicas, la semilla o los criterios de
servicio, debe volver a ejecutar todo y actualizar las cifras. No mezclar
tablas de corridas distintas.

---

## 3. Estructura recomendada del documento

```text
Portada
Índice
Resumen ejecutivo (opcional, 1 página)
1. Introducción
   1.1 Contexto y problema
   1.2 Objetivos
   1.3 Alcance y preguntas de análisis
   1.4 Justificación
2. Marco teórico y metodología
   2.1 Teoría de colas y modelo M/M/1
   2.2 Datos del sistema y supuestos
   2.3 Diseño de la simulación
   2.4 Configuraciones evaluadas
   2.5 Métricas y criterios de decisión
   2.6 Herramientas y reproducibilidad
3. Resultados
   3.1 Punto 1: cajero con menor y mayor tiempo de atención
   3.2 Punto 2: promedio de usuarios por tipo
   3.3 Punto 3: total de usuarios por tipo en cada réplica
   3.4 Punto 4: necesidad de un cajero adicional
   3.5 Punto 5: configuración óptima de cajas
   3.6 Análisis integrado y sensibilidad
4. Conclusiones y recomendaciones
5. Limitaciones y trabajo futuro
Referencias
Anexos
   A. Tablas completas
   B. Código y estructura del repositorio
   C. Evidencia de reproducibilidad
```

Cada capítulo debe responder una pregunta, no solo describir archivos.

---

## 4. Portada, índice y resumen ejecutivo

### Portada

Incluir:

- Nombre de la institución y asignatura.
- Título: “Solución de un problema bancario: simulación de cajas M/M/1”.
- Nombres completos de los integrantes y correos institucionales.
- Nombre del docente.
- Fecha de entrega.
- Ciudad.
- Versión del documento (por ejemplo, `v1.0`).

### Índice

Generarlo automáticamente en Word (`Referencias > Tabla de contenido`) después
de aplicar estilos de título. Verificar que los números de página coincidan.

### Resumen ejecutivo (recomendado)

Máximo una página. Debe contener:

- Problema: 3 cajas, 70 % retiros y 30 % pagos, 8 horas/día.
- Método: simulación de eventos discretos con 30 réplicas y modelo M/M/1 por
  cajero.
- Hallazgo principal: la configuración actual de 3 cajas mixtas cumple los
  criterios y no requiere un cuarto cajero.
- Recomendación: 0 cajas exclusivas de retiro y 0 de pago; mantener 3 cajas
  mixtas. Si se exige especializar, explicar el costo en espera.
- Cifra clave: espera promedio global de 0.78 min y utilización máxima de
  46.9 % con 3 cajas mixtas.

No incluir tablas extensas en el resumen.

---

## 5. Introducción

### 5.1 Contexto y problema

Describir en 3–4 párrafos:

- El Banco de Colombia no cuenta con cajeros electrónicos y quiere optimizar
  sus cajas para pagos y retiros.
- Hay 3 cajas para ambas operaciones, 70 % de usuarios hacen retiros y 30 %
  pagos/consignaciones.
- La operación es de 8 horas diarias y se asume que un día es representativo.
- La pregunta: ¿una caja exclusiva para retiros y dos para pagos, o
  viceversa?, y ¿se necesita una cuarta caja?

**No** empezar con la historia de la teoría de colas. Empezar con la decisión
que debe tomar el banco.

### 5.2 Objetivos

Redactar un objetivo general y objetivos específicos medibles:

- **General:** evaluar configuraciones de cajas para minimizar la espera de los
  usuarios y recomendar una asignación de cajas exclusivas/mixtas.
- **Específicos:**
  1. Simular al menos 10 réplicas de un día de 8 horas.
  2. Identificar el cajero con menor y mayor tiempo promedio de atención.
  3. Estimar el promedio de usuarios de cada tipo en el total de cajeros.
  4. Determinar el total de usuarios por tipo en cada réplica.
  5. Evaluar si se requiere un cajero adicional con criterios de espera.
  6. Comparar configuraciones y recomendar cuántas cajas exclusivas destinar a
     pagos y cuántas a retiros.

### 5.3 Alcance y preguntas de análisis

Delimitar:

- Se modelan cajas M/M/1 independientes, sin cajeros electrónicos, sin
  abandono de cola y sin horarios pico.
- Se simula un día y se replica para estimar variabilidad.
- Se comparan siete configuraciones (tres de 3 cajas y cuatro de 4 cajas).

Preguntas que el documento debe responder explícitamente:

1. ¿Qué cajero tiene el menor y el mayor tiempo promedio de atención?
2. ¿Cuántos usuarios de cada tipo atiende el sistema en promedio?
3. ¿Cómo varía el total de usuarios por tipo entre réplicas y en qué réplica
   hay menos usuarios de cada tipo?
4. ¿Se necesita un cuarto cajero?
5. ¿Cuántas cajas exclusivas para pagos y cuántas para retiros conviene tener?

### 5.4 Justificación

Explicar por qué la simulación es adecuada: el sistema tiene llegadas y
servicios aleatorios, interacción entre colas y varias configuraciones; una
fórmula analítica M/M/1 simple no captura la mezcla de tipos de usuario ni la
asignación a cajas.

---

## 6. Marco teórico y metodología

### 6.1 Teoría de colas y modelo M/M/1

Incluir solo lo necesario:

- Notación de Kendall: M/M/1 (llegadas Poisson, servicio exponencial, un
  servidor).
- Fórmulas: `rho = lambda / mu`, `L = rho/(1-rho)`, `Lq = rho^2/(1-rho)`,
  `W = 1/(mu-lambda)`, `Wq = rho/(mu-lambda)`.
- Ley de Little: `L = lambda W`, `Lq = lambda Wq`.
- Condición de estabilidad: `rho < 1`.

**Cuidado:** en este laboratorio cada cajero atiende una mezcla de tipos de
usuario, por lo que el sistema completo no es un M/M/1 puro. Se usa M/M/1 como
modelo de cada servidor y la simulación incorpora la mezcla real. Escribir esta
precisión suma rigor; no ocultarla.

### 6.2 Datos del sistema y supuestos

Reproducir las Tablas 1 y 2 del enunciado (tiempos de servicio, tiempos de
llegada y probabilidades). Agregar una tabla de supuestos:

| Supuesto | Valor / decisión | Justificación |
|---|---|---|
| Composición de llegadas | 70 % retiros, 30 % pagos | Enunciado. |
| Tipo de usuario | Probabilidades condicionales de la Tabla 2 | Enunciado. |
| Tiempo entre llegadas | Exponencial; la media depende de la acción y del tipo del cliente que llega (Tabla 1) | Enunciado. |
| Tiempo de servicio | Exponencial; la media depende de la acción y del tipo de cliente (Tabla 1) | Enunciado. |
| Número de cajas | 3 en la situación actual; 4 en escenarios de ampliación | Pregunta del banco. |
| Asignación | Caja libre al azar; si todas ocupadas, cola más corta | Política operativa documentada. |
| Cierre | Llegadas hasta el minuto 480; luego se drena el sistema | Evitar truncar esperas. |
| Réplicas | 30, semilla maestra 42 | Supera el mínimo de 10 y permite IC. |

Si el equipo decide otra política de asignación (por ejemplo, cola única
compartida), debe justificarlo y volver a simular. No cambiar la política solo
para obtener cifras más favorables.

### 6.3 Diseño de la simulación

Describir el flujo:

1. Generar la acción (retiro/pago) y el tipo de usuario.
2. Generar el tiempo entre llegadas exponencial con la media que corresponde a
   esa acción y ese tipo (Tabla 1).
3. Generar el tiempo de servicio exponencial del cliente.
4. Asignar el cliente a una caja elegible.
5. Registrar llegada, inicio y fin de servicio.
6. Repetir hasta el minuto 480 y drenar.
7. Repetir 30 veces con semillas independientes.

Explicar el **diseño de números aleatorios comunes**: todas las configuraciones
de una misma réplica reciben los mismos clientes y servicios; solo cambia la
asignación. Esto hace que las diferencias se deban a la configuración y no a
otra muestra. Es un argumento metodológico importante.

### 6.4 Configuraciones evaluadas

Incluir la tabla de la sección “Configuraciones evaluadas” del README. Explicar
por qué se incluyen 3 y 4 cajas:

- 3 cajas: situación actual, 1R+2P y 2R+1P.
- 4 cajas: mixta, 2R+2P, 3R+1P y 1R+3P, para evaluar el cajero adicional y la
  especialización.

### 6.5 Métricas y criterios de decisión

Definir antes de mostrar resultados:

- Espera promedio (`Wq`), P90, máximo y fracción con espera > 10 min.
- Tiempo de servicio promedio y tiempo en el sistema.
- `Lq`, `L`, utilización promedio y máxima.
- Conteos por tipo y por acción.
- Intervalo de confianza del 95 % para la media de cada métrica.

Criterios usados en el código (se pueden cambiar, pero deben declararse):

| Criterio | Umbral |
|---|---:|
| Espera promedio global | ≤ 5 min |
| Espera promedio de retiros | ≤ 5 min |
| Espera promedio de pagos | ≤ 5 min |
| Espera promedio del peor tipo de usuario | ≤ 5 min |
| P90 de espera global | ≤ 10 min |
| P90 de espera de retiros | ≤ 10 min |
| P90 de espera de pagos | ≤ 10 min |
| Fracción con espera > 10 min | ≤ 10 % |
| Utilización máxima de una caja | ≤ 85 % |

El código evalúa estos nueve criterios; `punto4_criterios.csv` reporta un
criterio por fila para cada escenario. Si el documento omite los P90 por
operación, la tabla no coincidirá con la evidencia.

Las métricas de “peor tipo” y “peor operación” se calculan por réplica (máximo
entre tipos o acciones) y luego se promedian. Son cotas conservadoras, no el
máximo de los promedios; conviene definirlas así si se citan.

**¿Por qué 30 réplicas?** El mínimo del enunciado es 10. Con 30 réplicas, el
IC 95 % de la espera promedio con 3 cajas mixtas es **0.59–0.97 min**
(semiamplitud 0.19 min); el del P90 es **1.38–2.79 min**, y el de la
utilización máxima, **45.3–48.5 %**. Esa precisión es suficiente para decidir,
y por eso se documenta el número de réplicas (la rúbrica lo pide en “Manejo y
organización de la información”).

**No inventar criterios después de ver los resultados.** Si el equipo usa
otros, justificarlos con una norma de servicio, una política del banco o una
decisión del curso.

### 6.6 Herramientas y reproducibilidad

Mencionar:

- Python 3.12, NumPy, pandas, SciPy y Matplotlib.
- Código modular (`src/bank_simulation.py`, `src/analysis.py`).
- Pruebas: `python -m pytest -q` (12 pruebas).
- Reproducción: `python scripts/reproduce.py`.
- Semilla maestra y esquema de `SeedSequence`.
- Manifiesto SHA-256 en `outputs/MANIFEST.txt`.

No incluir capturas de pantalla del código en el cuerpo; el código va en anexo
o en el repositorio.

---

## 7. Resultados: los cinco puntos

Para cada punto usar la misma estructura:

1. **Pregunta:** qué se quiere responder.
2. **Tabla o figura:** con número, título y fuente.
3. **Lectura:** qué muestran los datos.
4. **Respuesta:** una frase directa.

No basta con pegar la tabla; la rúbrica evalúa el análisis.

### 7.1 Punto 1: cajero con menor y mayor tiempo de atención

**Fuente:** `outputs/punto1_cajeros.csv` y
`outputs/figuras/fig_cajeros_configuracion_actual.png`.

**Qué mostrar:** para la configuración actual de 3 cajas mixtas, una tabla con:

- Cajero.
- Clientes atendidos.
- Tiempo promedio de servicio (min).
- IC 95 % del tiempo de servicio.
- Tiempo promedio de espera.
- Tiempo promedio en el sistema.
- Utilización.

**Resultado de referencia (30 réplicas, semilla 42):**

| Cajero | Clientes | Servicio prom. (min) | IC 95 % servicio | Espera prom. (min) | Sistema prom. (min) | Utilización |
|---:|---:|---:|---|---:|---:|---:|
| 0 | 66.23 | 3.16 | 3.00 – 3.33 | 0.85 | 4.01 | 42.8 % |
| 1 | 66.47 | 3.20 | 2.98 – 3.42 | 0.82 | 4.02 | 43.3 % |
| 2 | 65.37 | 3.23 | 3.05 – 3.42 | 0.72 | 3.95 | 43.1 % |

**Interpretación correcta:** los tres cajeros usan las mismas distribuciones
de servicio y la asignación es aleatoria entre cajas libres. Por eso las
diferencias de 0.07 min son ruido muestral, no una diferencia real de
productividad. El cajero 0 tiene el menor promedio y el cajero 2 el mayor en
esta corrida, pero no se puede concluir que uno sea “mejor” que otro.

**Error frecuente:** decir “el cajero 2 es el más lento porque atiende usuarios
más lentos”. En la configuración mixta la asignación es aleatoria; la
composición de tipos por cajero es similar. Si se analiza una configuración
especializada, ahí sí la diferencia es sistemática porque el cajero atiende
solo un tipo de acción.

**Cómo redactarlo:**

> En la configuración de 3 cajas mixtas, el cajero 0 presentó el menor tiempo
> promedio de servicio (3.16 min) y el cajero 2 el mayor (3.23 min). La
> diferencia es inferior a 0.1 min y los intervalos de confianza se solapan,
> por lo que no hay evidencia de una diferencia operativa entre cajeros. La
> asignación aleatoria entre cajas libres distribuye la carga de forma
> equilibrada (42.8 %, 43.3 % y 43.1 % de utilización).

### 7.2 Punto 2: promedio de usuarios de cada tipo en la totalidad de cajeros

**Fuente:** `outputs/punto2_usuarios_tipo.csv` y
`outputs/figuras/fig_conteos_por_tipo.png`.

**Qué mostrar:** promedio por réplica de usuarios de cada tipo (rápido, normal,
lento, muy lento), sumando las tres cajas, con desviación estándar, IC 95 %,
porcentaje del total y promedio por cajero.

**Resultado de referencia:**

| Tipo | Promedio por réplica | DE | IC 95 % | % | Promedio por cajero |
|---|---:|---:|---:|---:|---:|
| Rápido | 38.23 | 8.73 | 34.97 – 41.49 | 19.3 % | 12.74 |
| Normal | 67.70 | 8.13 | 64.66 – 70.74 | 34.2 % | 22.57 |
| Lento | 40.47 | 6.44 | 38.06 – 42.87 | 20.4 % | 13.49 |
| Muy lento | 51.67 | 6.23 | 49.34 – 53.99 | 26.1 % | 17.22 |

**Interpretación:** el tipo “normal” es el más frecuente (34.2 %), seguido de
“muy lento” (26.1 %). Esto importa porque “muy lento” tiene tiempos de servicio
altos (4 min en retiro y 7 min en pago) y explica por qué la mezcla de usuarios
no se comporta como un M/M/1 simple.

**Aclaración de interpretación:** “en la totalidad de cajeros” se interpreta
como el total atendido por las tres cajas en una réplica, dividido entre el
número de réplicas. Si el docente quiere el promedio por cajero, la última
columna lo reporta.

### 7.3 Punto 3: total de usuarios por tipo en cada réplica

**Fuentes:** `outputs/punto3_replicas.csv` (tabla completa),
`outputs/punto3_minimos.csv` (réplica con mínimo por tipo).

**Qué mostrar:**

- Una tabla de 30 filas (réplica × tipo) en el anexo, no en el cuerpo.
- En el cuerpo, una tabla resumen con la réplica que tuvo menos usuarios de
  cada tipo, el mínimo, el promedio y el máximo.

**Resultado de referencia:**

| Tipo | Réplica con mínimo | Mínimo | Promedio | Máximo |
|---|---:|---:|---:|---:|
| Rápido | 12 | 24 | 38.23 | 55 |
| Normal | 12 | 54 | 67.70 | 86 |
| Lento | 27 | 27 | 40.47 | 51 |
| Muy lento | 4 | 40 | 51.67 | 63 |

**Interpretación:** la réplica 12 tuvo la menor cantidad de usuarios rápidos y
normales; la réplica 27 la menor de lentos; la réplica 4 la menor de muy
lentos. No hay una única réplica “con menos usuarios de todos los tipos”; el
mínimo depende del tipo.

**Aclaración importante sobre “modelo”:** el enunciado dice “detalla el modelo
con menor cantidad de usuarios por tipo”. En este informe se interpreta
“modelo” como **réplica o corrida** del simulador, porque el número de llegadas
se genera una vez y se comparte entre configuraciones (números aleatorios
comunes). Por eso el conteo por tipo es idéntico entre configuraciones; lo que
cambia es la asignación a cajeros. Si el docente se refería a “configuración”,
explicar esta decisión metodológica en una nota al pie. No inventar diferencias
de conteo entre configuraciones que el modelo no produce.

**Cómo redactarlo:**

> El total de usuarios por tipo varió entre réplicas debido a la aleatoriedad
> de las llegadas. La réplica 12 registró el mínimo de usuarios rápidos (24) y
> normales (54); la réplica 27 el mínimo de lentos (27); y la réplica 4 el
> mínimo de muy lentos (40). Como todas las configuraciones comparten las
> mismas llegadas, estas cifras describen la demanda simulada y no dependen de
> la asignación de cajas.

### 7.4 Punto 4: ¿se necesita un cajero adicional?

**Fuentes:** `outputs/punto4_criterios.csv`,
`outputs/punto4_comparacion.csv`, `outputs/decisiones.json` y
`outputs/figuras/fig_punto4_comparacion.png`.

**Qué mostrar:**

1. Tabla de criterios con umbral, valor con 3 cajas y valor con 4 cajas.
2. Comparación de espera promedio, P90, utilización y fracción > 10 min.
3. Decisión explícita: sí o no se requiere un cuarto cajero.

**Resultado de referencia:** con 3 cajas mixtas se cumplen todos los criterios:

- Espera promedio global: 0.78 min (umbral 5 min).
- Espera de retiros: 0.84 min.
- Espera de pagos: 0.66 min.
- P90 global: 2.09 min (umbral 10 min).
- Fracción con espera > 10 min: 1.9 % (umbral 10 %).
- Utilización máxima: 46.9 % (umbral 85 %).

Con 4 cajas mixtas la espera baja a 0.21 min, pero **no se justifica** crear la
cuarta caja porque la configuración actual ya cumple. Ésta es la diferencia
entre “mejor desempeño” y “decisión costo-efectiva”.

**Cómo redactarlo:**

> Con 3 cajas mixtas se cumplen todos los criterios definidos: la espera
> promedio global es 0.78 min, el P90 es 2.09 min y la utilización máxima es
> 46.9 %. Aunque una cuarta caja reduce la espera a 0.21 min, no se requiere
> para la demanda simulada. Por tanto, **no se recomienda crear un nuevo
> cajero** en las condiciones actuales.

**Análisis de sensibilidad (recomendado):** la decisión depende de los
criterios. Si el banco exigiera una espera promedio ≤ 0.5 min, la cuarta caja
mixta sí sería necesaria (0.21 min). En cambio, un umbral de utilización máxima
≤ 30 % **no se alcanzaría ni con 4 cajas mixtas** (36.5 %), así que habría que
evaluar 5 cajas u otra política. También se puede repetir con 50 o 100 réplicas
para ver si la conclusión se mantiene.

### 7.5 Punto 5: configuración óptima de cajas exclusivas

**Fuentes:** `outputs/punto5_configuracion.csv`, `outputs/decisiones.json` y
`outputs/figuras/fig_espera_por_accion.png`.

**Qué mostrar:** ranking de las siete configuraciones con:

- Número de cajas y composición (retiro/pago/mixtas).
- Carga ofrecida (`rho`).
- Espera promedio global, de retiros y de pagos.
- P90, utilización máxima, fracción > 10 min.
- Si cumple o no los criterios.
- Columna que marque la configuración recomendada.

**Resultado de referencia:** la recomendación costo-efectiva es **3 cajas
mixtas: 0 exclusivas de retiro y 0 exclusivas de pago**. Cumple los criterios y
evita el costo de una cuarta caja.

**El trade-off que debe explicarse:**

- **1 retiro + 2 pagos:** los pagos esperan solo 0.89 min, pero los retiros
  esperan 5.55 min; el 70 % de los usuarios son retiros, así que se castiga a
  la mayoría.
- **2 retiros + 1 pago:** la espera promedio global baja a 2.98 min, pero los
  pagos esperan 8.53 min; se castiga a un grupo minoritario pero con servicio
  más largo.
- **2 retiros + 2 pagos (4 cajas):** es la mejor opción si se decide
  especializar y ampliar; espera global 0.66 min y espera de pagos 0.86 min
  (la más alta entre operaciones).
- **4 cajas mixtas:** mejor desempeño absoluto (0.21 min), pero implica una
  caja adicional que no es necesaria para cumplir los criterios.

> **Precisión sobre `max_mean_wait_accion`:** en `punto5_configuracion.csv`,
> 2R+2P reporta 1.06 min en ese campo. Es el promedio entre réplicas del
> máximo de las esperas medias por operación (en unas réplicas el peor es
> retiros y en otras pagos), no la espera media de pagos (0.86 min). Si se cita
> en el documento, definirlo así; si no, usar 0.86 min, que es la operación
> con mayor espera media.

**Cómo redactarlo:**

> La configuración de 3 cajas mixtas es la recomendación costo-efectiva:
> cumple todos los criterios de servicio, mantiene la espera promedio en
> 0.78 min y evita crear una cuarta caja. Si el banco exige especializar las
> tres cajas existentes, la opción más balanceada es 1 caja de retiros + 2 de
> pagos, pero no cumple el criterio de espera para retiros (5.55 min). Si está
> dispuesto a crear una cuarta caja y especializar, la mejor opción es 2 cajas
> de retiros + 2 de pagos (espera global 0.66 min; la espera más alta es la de
> pagos, 0.86 min). Por tanto, la respuesta a la pregunta del banco es: **0 cajas
> exclusivas para pagos y 0 para retiros; mantener las 3 cajas mixtas** en las
> condiciones actuales.

### 7.6 Análisis integrado y sensibilidad

Cerrar resultados con 2–3 párrafos que conecten los cinco puntos:

- La demanda total es de ~198 usuarios/día y la carga ofrecida es 1.334
  servidores; 3 cajas mixtas son suficientes.
- La variabilidad de llegadas explica las diferencias entre réplicas.
- La especialización no es gratuita: mejora un tipo de operación y empeora
  otro. La decisión depende de la prioridad del banco (equidad vs. eficiencia).
- La conclusión es robusta si se mantienen los supuestos; si cambian las
  tasas de llegada o los criterios, debe reevaluarse.

---

## 8. Conclusiones y recomendaciones

### 8.1 Conclusiones

Escribir una conclusión por cada punto, con cifra y respuesta:

1. **Cajeros:** en la configuración mixta no hay un cajero intrínsecamente más
   rápido; las diferencias (<0.1 min) son ruido muestral.
2. **Usuarios por tipo:** el tipo normal es el más frecuente (34.2 %), seguido
   de muy lento (26.1 %).
3. **Réplicas:** el mínimo por tipo ocurre en réplicas distintas; no hay una
   réplica con menos usuarios de todos los tipos.
4. **Cajero adicional:** no se requiere con 3 cajas mixtas; se cumplen todos
   los criterios.
5. **Configuración:** mantener 3 cajas mixtas (0 exclusivas de retiro y 0 de
   pago). Si se exige especializar, 1R+2P es la opción más balanceada con 3
   cajas, pero no cumple; con 4 cajas, 2R+2P es la mejor especializada.

### 8.2 Recomendaciones para el banco

- Mantener las 3 cajas mixtas y monitorear la espera real.
- Si la demanda crece o se endurecen los criterios, evaluar una cuarta caja
  mixta antes que especializar.
- Si se decide especializar, comunicar el trade-off: la especialización mejora
  un tipo de operación y perjudica el otro.
- Medir tiempos reales para calibrar las medias del modelo; las cifras de este
  informe son simuladas.

### 8.3 Limitaciones y trabajo futuro

Listar con honestidad:

- No se modelan abandonos, prioridades, horarios pico ni cajeros electrónicos.
- Los tiempos son exponenciales con medias del enunciado; no se ajustaron
  distribuciones empíricas.
- La asignación a la cola más corta es una política; podrían evaluarse cola
  única, prioridades o asignación por tipo.
- El modelo simula un día representativo; no captura estacionalidad semanal o
  mensual.
- Trabajo futuro: validar con datos reales, incluir costos de apertura de
  cajas, optimizar con un modelo de costo total (espera + operación).

---

## 9. Video de sustentación

La rúbrica asigna 10 puntos al video. Para esta entrega se preparó un **pitch
de 3 minutos** con texto, tiempos y apoyos visuales en
[`docs/guion_video_pitch.md`](guion_video_pitch.md). El enunciado no exige una
duración específica; 3 minutos son suficientes si se responden los cinco
puntos y se justifica la decisión.

### Estructura del pitch

| Tiempo | Bloque | Contenido |
|---:|---|---|
| 0:00–0:20 | Apertura | Pregunta del banco y objetivo. |
| 0:20–0:50 | Contexto | 3 cajas, 70/30, 8 horas, M/M/1. |
| 0:50–1:30 | Modelo | Eventos discretos, 30 réplicas, semilla 42, números comunes. |
| 1:30–2:15 | Resultados | Los cinco puntos con cifras clave. |
| 2:15–2:45 | Decisión | 3 cajas mixtas vs. especializar y costo de la cuarta caja. |
| 2:45–3:00 | Cierre | Limitaciones, conclusión y gracias. |

### Consejos

- Usar las figuras de `outputs/figuras/`; no leer el documento.
- Mostrar una sola tabla por punto; el resto va al anexo.
- Decir las cifras redondeadas (0.78 min, 46.9 %, 2.09 min P90).
- Practicar el tiempo; el video debe demostrar dominio, no memorización.
- Grabar en 1080p, audio claro, sin ruido de fondo.
- Subir a YouTube/Drive como “no listado” y pegar el enlace en el README y en
  la entrega.

---

## 10. Repositorio en GitHub

La rúbrica asigna 10 puntos al repositorio. Checklist:

- [ ] README con descripción, modelo, configuración, resultados y comandos.
- [ ] `requirements.txt` con versiones.
- [ ] Código en `src/` y `main.py` funcional.
- [ ] Pruebas en `tests/` y salida `12 passed`.
- [ ] `outputs/` con tablas, figuras y `resumen_ejecucion.md`.
- [ ] `docs/guia_documento.md` y `docs/plantilla_documento.md`.
- [ ] Instrucciones de reproducción (`python scripts/reproduce.py`).
- [ ] Enlace al video en el README.
- [ ] Sin credenciales, tokens ni datos personales.
- [ ] Historial de commits con mensajes claros.
- [ ] Tag o release `v1.0` para la entrega final.

**Importante:** no subir ni hacer `push` hasta que todo el equipo confirme la
versión final y el docente autorice el enlace. Antes de publicar, verificar que
`outputs/MANIFEST.txt` corresponda a la última corrida.

---

## 11. Mapeo contra la rúbrica (100 puntos)

| Criterio | Puntos | Dónde se cumple | Evidencia |
|---|---:|---|---|
| Modelado del sistema | 20 | Metodología y puntos 1–2 | `src/bank_simulation.py`, `punto1_cajeros.csv`, `punto2_usuarios_tipo.csv` |
| Manejo y organización de la información | 20 | Punto 3 y anexos | `punto3_replicas.csv`, `punto3_minimos.csv`, `conteos_tipo.csv` |
| Análisis del caso planteado | 20 | Puntos 4 y 5 | `punto4_criterios.csv`, `punto5_configuracion.csv`, `decisiones.json` |
| Puntualidad y entrega | 10 | Formato, portada, índice, nombre | Documento final |
| Implementación | 10 | Código funcional y comentado | `main.py`, `src/`, `tests/` |
| Video de sustentación | 10 | Guion y video | Enlace en README |
| Repositorio en GitHub | 10 | Checklist | README, outputs, release |

**Ojo con la redacción de la rúbrica:** en “Análisis del caso planteado” dice
“nuevo cajero **electrónico**”, pero el caso trata de cajas atendidas por
personal. En el documento hay que aclarar que se interpreta como **cajero o
ventanilla adicional**, y responder en esos términos; si se copia literalmente
“cajero electrónico” el lector puede pensar que se evaluó un cajero automático.

Para obtener el 100 %, no basta con que el código funcione: el documento debe
**interpretar** los resultados y **justificar** la decisión. Las tablas sin
análisis suelen bajar la calificación de “Análisis del caso planteado”.

---

## 12. Lista de verificación antes de entregar

### Contenido

- [ ] Respondí los cinco puntos con tabla/figura y frase de respuesta.
- [ ] Expliqué el modelo y los supuestos (70/30, exponenciales, M/M/1, 8 h).
- [ ] Reporté 30 réplicas, expliqué el esquema de semillas y justifiqué por qué
      ese número basta (IC 95 %).
- [ ] Incluí intervalos de confianza o al menos desviación estándar.
- [ ] Aclaré que “cajero adicional” significa ventanilla/cajero atendido por
      personal, no cajero electrónico.
- [ ] Los datos quedan en CSV y se regeneran con `python scripts/reproduce.py`.
- [ ] Justifiqué la decisión del cajero adicional con criterios explícitos.
- [ ] Expliqué el trade-off de las configuraciones exclusivas.
- [ ] Diferencié “mejor desempeño” de “recomendación costo-efectiva”.
- [ ] Incluí limitaciones y trabajo futuro.
- [ ] Las cifras del texto coinciden con `outputs/`.

### Formato

- [ ] Portada completa.
- [ ] Índice actualizado y con números de página.
- [ ] Numeración de páginas.
- [ ] Tablas y figuras numeradas con título y fuente.
- [ ] Unidades en todos los ejes y columnas.
- [ ] Ortografía y redacción revisadas.
- [ ] Nombre del archivo: `Apellido_Nombre_problemaBancario.docx` o `.pdf`.

### Evidencia

- [ ] Código ejecutable con `python main.py`.
- [ ] Pruebas en verde (`12 passed`).
- [ ] `outputs/` completo y `MANIFEST.txt`.
- [ ] Enlace del video.
- [ ] Repositorio accesible para el docente.
- [ ] No se subió nada a GitHub sin confirmación del equipo.

---

## 13. Apéndice: comandos y archivos de referencia

```powershell
# Desde AE3_Problema_Bancario
python -m pytest -q
python main.py --replicas 30 --duration 480 --seed 42
python scripts/build_report_assets.py
python scripts/reproduce.py
```

| Necesito... | Archivo |
|---|---|
| Cifras principales | `outputs/resumen_ejecucion.md` |
| Tabla del punto 1 | `outputs/punto1_cajeros.csv` |
| Tabla del punto 2 | `outputs/punto2_usuarios_tipo.csv` |
| Tabla del punto 3 | `outputs/punto3_replicas.csv` y `punto3_minimos.csv` |
| Criterios del punto 4 | `outputs/punto4_criterios.csv` |
| Comparación 3 vs 4 | `outputs/punto4_comparacion.csv` |
| Ranking del punto 5 | `outputs/punto5_configuracion.csv` |
| Decisión y recomendación | `outputs/decisiones.json` |
| Figuras | `outputs/figuras/` |
| Datos para entrega | CSV de `outputs/` (no se requiere Excel). |
| Detalle por cliente | `outputs/clientes.csv` (regenerable; no se versiona por tamaño). |
| Reproducibilidad | `outputs/MANIFEST.txt` |

---

## 14. Cifras de referencia de la corrida actual

Estas cifras provienen de 30 réplicas, 480 minutos y semilla 42. Sirven para
comparar, pero **deben regenerarse si cambia cualquier parámetro**.

- Media entre llegadas: 2.398 min.
- Media de servicio: 3.198 min.
- Carga ofrecida total: 1.334 servidores.
- Usuarios promedio por día: ~198.
- Mejor desempeño absoluto: 4 cajas mixtas (0.21 min de espera).
- Recomendación costo-efectiva: 3 cajas mixtas (0.78 min de espera, 46.9 % de
  utilización máxima).
- ¿Nuevo cajero?: no, con los criterios definidos.
- Mejor opción exclusiva con 3 cajas: 1 retiro + 2 pagos (4.16 min global;
  retiros 5.55 min; pagos 0.89 min), pero no cumple todos los criterios.
- Mejor opción exclusiva con 4 cajas: 2 retiros + 2 pagos (0.66 min global;
  espera de pagos 0.86 min, la más alta entre operaciones).
