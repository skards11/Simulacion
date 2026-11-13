# Ruta del anteproyecto a la versión final del artículo

**Proyecto:** AE2_HMM
**Fecha:** 2026-11-11
**Estado de partida:** anteproyecto con resultados D4 simulados, manuscrito en Markdown, LaTeX y PDF, autores y declaración de IA registrados.
**Actualización 2026-11-11:** D7 cerró M0/M1/M2, fijó `m = 0.5` y añadió Wilcoxon/Holm/Cliff. El experimento vigente ya se ejecutó; el manuscrito **todavía contiene los resultados D4** y es lo primero que debe actualizarse.
**Regla:** este documento no modifica la skill ni registra aprobaciones. Las propuestas de mejora de la skill quedan en `revision_skill_diseno_experimental.md`.

---

## 1. Resumen ejecutivo

El proyecto ya tiene lo más costoso: problema delimitado, formalización, código, protocolo ejecutado, resultados simulados, tablas, figura y manuscrito compilado. Para pasar a `final` no falta “escribir más”, sino **cerrar evidencia y decisiones**:

1. **Literatura:** la sección 2 sigue siendo provisional; no hay búsqueda sistemática ejecutada, tabla comparativa ni vacío de investigación sustentado.
2. **Decisiones abiertas:** D7 cerró M0/M1/M2, `m = 0.5` y el análisis pareado; el manuscrito aún no refleja ese cierre.
3. **Estadística:** el experimento D7 ya incluye Wilcoxon, Holm-Bonferroni, Delta de Cliff y criterios; falta trasladarlo al manuscrito.
4. **Plantilla:** faltan elementos que la plantilla del curso muestra: correos, tabla de fases con entregables, diagrama de flujo, pseudocódigo, anexo de presentación oral y URL del repositorio.
5. **Reproducibilidad:** el código es reproducible: `requirements.txt` tiene versiones exactas, existe `outputs/MANIFEST.txt` y el comando único `python scripts/reproduce.py`. Falta declarar commit/versión en el manuscrito y regenerarlo con los nuevos artefactos.
6. **Cierre editorial:** el título y el resumen siguen diciendo “anteproyecto”; falta revisar formato, referencias, figuras y declaraciones según el destino real.

**Conclusión:** el experimento ya está cerrado en código y artefactos, pero el manuscrito todavía reporta D4. Para llegar a `final` primero debe actualizarse el manuscrito con D7 y después completarse la literatura, la plantilla y la verificación editorial. Cambiar solo la etiqueta de `anteproyecto` a `final` no sería suficiente ni honesto.

---

## 2. Lo que ya está listo

| Elemento | Evidencia | Estado |
|---|---|---|
| Problema y alcance didáctico | D1–D3; secciones 1 y 3 del manuscrito | Listo |
| Formalización del HMM | Sección 3; `src/hmm_model.py` | Listo |
| Comparación M0/M1/M2 | `src/simulation.py`; secciones 3.4 y 4.3 | Listo, salvo definición de M1 |
| Protocolo ejecutado | `outputs/protocolo_d4_resumen.json`; T = 500, N = 2000, semilla 20261109 | Listo |
| Resultados simulados | `outputs/protocolo_d4_resumen.csv` y `.md` | Listo como cifras simuladas |
| Figura de métricas | `outputs/protocolo_d4_metricas.png` | Listo, falta revisión editorial |
| Pruebas automatizadas | `tests/test_protocol.py` | Listo; deben reejecutarse al cierre |
| Manuscrito | `.md`, `.tex`, `.pdf` | Listo como anteproyecto |
| Autores y declaración de IA | Manuscrito y bitácora | Registrado |
| Referencias clásicas | Rabiner (1989) y Baum et al. (1970) | Verificadas por el equipo |

---

## 3. Bloqueantes antes de declarar `final`

### B1. Decidir el destino editorial real

**Situación:** el manuscrito usa una plantilla genérica en LaTeX y menciona “plantilla de artículo Q1” del curso. La plantilla disponible es una guía de redacción, no necesariamente las normas de una revista.

**Falta:**

- Decidir si el entregable final es para el curso, para una revista concreta o para ambos.
- Si es para una revista, leer sus instrucciones reales de autores y no asumir requisitos.
- Ajustar estructura, extensión, formato de referencias, figuras y declaraciones a ese destino.

**No hacer:** afirmar que el artículo cumple “Q1” solo por usar la plantilla del curso.

### B2. Cerrar la definición de M1 — resuelto por D7

**Situación:** D7 reemplazó M1 por el baseline puntual sin memoria temporal, `argmax_i B[i, O_t]`, evaluado sobre las observaciones nominales.

**Falta:** actualizar el manuscrito, que todavía describe M1 como HMM con prior estacionario.

**Impacto:** la comparación M0/M1 cambia de interpretación; el manuscrito debe reflejar la nueva definición.

### B3. Fijar el valor de la B alterada — resuelto por D7

**Situación:** D7 fijó `m = 0.5` de forma definitiva; M2 decodifica con la B nominal.

**Falta:** actualizar el manuscrito, que todavía presenta `m = 0.5` como provisional.

**Impacto:** el escenario con B alterada ya puede reportarse como escenario definido, sin llamarlo provisional.

### B4. Decidir el tratamiento estadístico — resuelto por D7

**Situación:** D7 fijó Wilcoxon bilateral pareado, Holm-Bonferroni, Delta de Cliff y dos criterios de éxito. Los resultados D7 ya están calculados.

**Falta:** trasladar al manuscrito las nuevas métricas, contrastes, criterios y matrices de confusión; retirar la afirmación de que no se hicieron pruebas formales.

**Regla:** no reinterpretar los criterios después de ver los resultados. Los criterios ya quedaron definidos en D7.

### B5. Ejecutar la revisión de literatura

**Situación:** la sección 2 declara explícitamente que no se hizo revisión sistemática y solo incluye dos referencias clásicas verificadas.

**Falta:**

- Protocolo de búsqueda: bases, cadenas, fechas, criterios de inclusión y exclusión.
- Registro de búsqueda y deduplicación.
- Cribado y extracción.
- Tabla comparativa de trabajos previos, similar a la Tabla 1 de la plantilla.
- Síntesis crítica y vacío de investigación.
- Verificación de cada cita y, si se afirma algo extraído, página o sección.

**No hacer:** agregar referencias “probables” o “conocidas” sin verificarlas. Si no se ejecuta la búsqueda, el artículo final debe declararlo como limitación, pero entonces no puede presentar un estado del arte cerrado.

### B6. Completar metadatos y artefactos de entrega

**Situación:** el manuscrito tiene autores, grupo, institución, docente y fecha. La plantilla muestra correos electrónicos, afiliaciones numeradas y autor de correspondencia.

**Falta:**

- Correos institucionales de los autores y del docente, si se autoriza publicarlos.
- Afiliaciones y autor de correspondencia.
- URL del repositorio o declaración de disponibilidad.
- Licencia del código y de los datos, si aplica.
- Confirmar si se mantienen tres estudiantes o si se incorpora un cuarto autor; la plantilla muestra cuatro, pero no se debe inventar un autor.

### B7. Actualizar documentos internos — parcialmente resuelto

**Situación:** `OPENCODE.md` y `README.md` ya se actualizaron al experimento D7. `decisiones.md` registra D7 y marca los resultados D4 como históricos.

**Falta:**

- Actualizar el manuscrito, que sigue describiendo D4.
- Verificar que no queden referencias a `PROVISIONAL_ALTERED_MIXING` ni a la M1 con prior estacionario.
- Verificar que `legacy/` no se mezcle con resultados del experimento vigente.

---

## 4. Trabajo para completar el manuscrito

### 4.1 Estructura frente a la plantilla del curso

| Elemento de la plantilla | Estado actual | Qué falta |
|---|---|---|
| Título, autores, afiliaciones, correos | Parcial | Correos, afiliaciones, autor de correspondencia |
| Resumen y palabras clave | Listo | Quitar “anteproyecto”; ajustar si cambian resultados |
| Introducción con P1–P3 | Listo | Revisar redacción final |
| Estado del arte con Tabla 1 | Falta | Búsqueda real, tabla comparativa y vacío |
| Marco teórico | Listo | Revisión de notación y ecuaciones |
| Metodología con siete fases | Parcial | Tabla de fases con entregables parciales/finales |
| Diagrama de flujo experimental | Falta | Figura de flujo |
| Pseudocódigo | Falta | Listado de Viterbi o Forward–Backward |
| Diseño experimental y entorno | Parcial | Versiones fijadas, sistema, comando, commit |
| Resultados con tabla estadística | Parcial | SD, mínimo, máximo, IC; matriz de confusión si se decide |
| Discusión | Parcial | Conectar con literatura verificada |
| Conclusiones y trabajo futuro | Parcial | Ajustar a evidencia final y decisiones cerradas |
| Referencias | Parcial | Más literatura verificada o declarar límite |
| Anexo de repositorio | Parcial | URL, estructura, licencia, instrucciones |
| Anexo de presentación oral | Falta | Guión de 2–3 minutos |

### 4.2 Título, resumen y etiquetas

- Cambiar “anteproyecto reproducible” por una denominación de artículo final.
- Sustituir “Este anteproyecto estudia…” por “Este artículo estudia…” solo cuando el equipo apruebe el cierre.
- Actualizar “El aporte del anteproyecto…” y “manuscrito de anteproyecto”.
- Mantener la advertencia de que las cifras son simuladas y no tienen validez ecológica.
- No eliminar la etiqueta `anteproyecto` del repositorio hasta que la checklist final esté completa y aprobada.

### 4.3 Resultados y discusión

**Ya calculado por D7:** media, SD, mediana, RIC, IC percentil, matrices de confusión, Wilcoxon/Holm, Delta de Cliff y criterios.

**Falta en el manuscrito:**

- Reemplazar las tablas y la figura D4 por los artefactos D7.
- Reportar mínimo y máximo si se adopta el formato de la plantilla.
- Añadir precisión y recall por clase a partir de la matriz de confusión.
- Declarar que no se hicieron análisis de sensibilidad a T, N, semilla o decodificador, si no se ejecutan.
- Revisar expresiones como “M1 y M2 son prácticamente indistinguibles”; en D7 la comparación es M0 vs M1 y M0 vs M2.
- Revisar “mejora” para que no sugiera causalidad ni superioridad general.
- Conectar la discusión con literatura verificada; hoy no hay contraste bibliográfico real.

### 4.4 Referencias

- Mantener solo referencias verificadas.
- Añadir página o sección cuando se atribuya una afirmación concreta a una fuente.
- Si no se completa la revisión sistemática, declararlo en limitaciones y no presentar la sección 2 como cerrada.
- Revisar el estilo de citas y la correspondencia entre texto, tabla y bibliografía.

### 4.5 Figuras y tablas

- Verificar resolución, legibilidad y pies de figura.
- Asegurar que cada tabla y figura tenga llamada en el texto.
- Verificar que las cifras de las tablas coincidan con `outputs/experimento_hmm_metricas.csv` y `outputs/experimento_hmm_confusion.csv`.
- Regenerar tablas y figura desde el JSON después de cualquier cambio.
- No usar figuras de `legacy/`.

---

## 5. Reproducibilidad y calidad

| Elemento | Estado | Acción para el cierre |
|---|---|---|
| Código y pruebas | Listo | Ejecutar `python -m pytest -q` |
| Ejecución completa | Listo | Volver a ejecutar si cambia algún parámetro |
| Semillas | Registradas en JSON | Documentar derivación en el manuscrito |
| Dependencias | Fijadas con versiones exactas | Reinstalar y verificar en entorno limpio |
| Versión de Python | Declarada en README y OPENCODE (3.12.10) | Añadir versión usada al manuscrito |
| Commit o etiqueta | No declarado | Añadir commit y tag del cierre |
| Comando de reproducción | `python scripts/reproduce.py` verificado | Verificar en entorno limpio |
| Artefactos | Existentes con `MANIFEST.txt` SHA-256 | Regenerar si cambia algún parámetro |
| Figura | Generada | Regenerar y revisar |
| PDF | Compilado | Recompilar al final y revisar página por página |
| Documentación interna | Parcial | Corregir `OPENCODE.md` y contradicciones |

**Prueba de cierre recomendada:** en un entorno limpio, instalar dependencias, ejecutar pruebas, ejecutar el protocolo y regenerar tablas y figura. Comparar al menos una cifra de cada tabla con el artefacto. Si algo no coincide, no cerrar.

---

## 6. Checklist de la bitácora para pasar a `final`

La lista de `decisiones.md` dice que `final` requiere:

| Requisito | Estado actual | Qué falta |
|---|---|---|
| Protocolo con parámetros y semillas | Listo | Documentar derivación de semillas en el manuscrito |
| Código reproducible y versiones | Listo en el repositorio | Declarar commit/tag y versión de Python en el manuscrito |
| Cada cifra trazable a una ejecución | Documentado | Verificar numéricamente contra `outputs/` y el manifiesto |
| Tablas y figuras generadas por código | Documentado | Regenerar y revisar |
| Referencias verificadas o marcadas | Parcial | Completar búsqueda o declarar límite |
| Limitaciones y declaración de IA | Listo | Actualizar si cambia el alcance |
| Pendientes explícitos sin invención | Listo | Mantener |

---

## 7. Secuencia recomendada

### Etapa 1 — Decisiones y evidencia (cerrada por D7)

1. M1: cerrado por D7 (baseline puntual).
2. `m = 0.5`: cerrado por D7.
3. Análisis pareado, Wilcoxon/Holm/Cliff y criterios: cerrado por D7.
4. Destino editorial y plantilla real: pendiente.
5. Cuarto autor: pendiente, sin inventarlo.

### Etapa 2 — Literatura y manuscrito

6. Ejecutar la búsqueda bibliográfica y registrar el protocolo.
7. Construir la tabla comparativa y el vacío de investigación.
8. Añadir diagrama de flujo, pseudocódigo y tabla de fases con entregables.
9. Completar metadatos, correos, repositorio y declaraciones.
10. Actualizar título, resumen, resultados, discusión y conclusiones con D7.

### Etapa 3 — Verificación y cierre

11. Fijar dependencias y versión de Python.
12. Reejecutar pruebas y experimento si hubo cambios.
13. Regenerar tablas y figura.
14. Recompilar el PDF y revisar contra la plantilla.
15. Verificar cada cifra contra `outputs/experimento_hmm_*`.
16. Revisar documentación interna y referencias al protocolo D4.
17. Registrar la aprobación final en `decisiones.md`.
18. Crear la etiqueta `final` solo si toda la checklist está completa.

---

## 8. Decisiones que debe tomar el equipo

1. ¿El destino es el curso, una revista concreta o ambos?
2. ¿Se aprueba el cierre D7 y se actualiza el manuscrito con sus resultados?
3. ¿Se añade un análisis de sensibilidad al decodificador, a T, a N o a la semilla?
4. ¿Se completa la revisión sistemática o se declara como limitación?
5. ¿Se incorpora un cuarto autor o se adapta la plantilla a tres?
6. ¿Se autoriza publicar correos y URL del repositorio?
7. ¿Se autoriza el cambio de etiqueta a `final` después de la verificación?

---

## 9. Lo que no se debe hacer para “llegar a final”

- No cambiar la etiqueta sin completar la checklist.
- No inventar referencias, resultados, semillas, ejecuciones ni requisitos de revista.
- No presentar `m = 0.5` como aprobado si el equipo no lo aprueba.
- No afirmar superioridad del HMM ni validez ecológica.
- No mezclar cifras o figuras de `legacy/`.
- No añadir pruebas estadísticas sin ejecutarlas y registrarlas.
- No declarar “Q1” por usar una plantilla.
- No afirmar que la revisión de literatura está hecha si sigue pendiente.
