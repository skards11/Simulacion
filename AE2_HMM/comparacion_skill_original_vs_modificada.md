# Comparación de las dos respuestas al caso HMM

**Objeto de la comparación**

| Etiqueta | Producto | Skill aplicada | Estado |
|---|---|---|---|
| **R-A** | `manuscrito_anteproyecto.md` (+ `.tex` y `.pdf`) | `SKILL.md` original | Manuscrito completo con resultados D4, referencias verificadas y aprobaciones registradas |
| **R-B** | `manuscrito_anteproyecto_skill_modificada.md` | `skill_modificada.md` | Anteproyecto provisional, sin resultados y sin aprobaciones |

**Advertencia metodológica.** R-A no es solo la respuesta inicial: incorpora trabajo posterior (ejecución D4, LaTeX, PDF y aprobaciones del equipo). R-B se construyó deliberadamente solo con la solicitud y los materiales iniciales. Por tanto, la comparación no es estrictamente “misma etapa”. Se separan tres preguntas:

1. ¿Cuál es más **precisa** en lo que afirma?
2. ¿Cuál es más **pertinente** para el objetivo declarado?
3. ¿Cuál es más **trazable**?

---

## 1. Resumen ejecutivo

- **R-A es superior como producto final:** contiene resultados ejecutados, código reproducible, tablas, figura, LaTeX y PDF. Su trazabilidad empírica es fuerte.
- **R-B es superior como anteproyecto auditable:** cumple mejor los requisitos explícitos de la skill modificada, distingue hechos de inferencias, incluye razones para descartar el HMM y no atribuye aprobaciones.
- **Ninguna domina por completo.** R-A gana en completitud y evidencia; R-B gana en disciplina epistémica y trazabilidad documental.
- **La mejor versión futura no es elegir una, sino combinar:** la evidencia de R-A con la capa de auditoría de R-B.

---

## 2. Cumplimiento de requisitos comunes a ambas skills

| Requisito | R-A | R-B | Comentario |
|---|---|---|---|
| Dos preguntas investigables con comparación y criterio | **No** | **Sí** | R-A plantea tres preguntas (P1, P2, P3); ambas skills piden dos. |
| Protocolo y registro de búsqueda bibliográfica | **No** | **Parcial** | R-A solo declara la revisión como pendiente; R-B propone protocolo, pero no lo ejecuta. |
| No inventar referencias | **Sí** | **Sí** | R-A usa dos referencias verificadas por el equipo; R-B las marca como candidatas. |
| Formalización de S, V, A, B y π | **Sí** | **Sí** | Ambas son correctas y usan las matrices del caso. |
| Distinción Forward / Viterbi / aprendizaje | **Sí** | **Sí** | Ambas separan decodificación de Baum–Welch. |
| Distinción parámetros fijados / aprendidos | **Parcial** | **Sí** | R-A lo menciona como parámetros “oráculo”; R-B lo explicita en tabla. |
| Baseline sin HMM | **Sí** | **Sí** | Ambas incluyen M0. |
| Prevención de fuga de información | **Sí** | **Sí** | Ambas usan etiquetas solo para evaluar. |
| Resultados solo si son reales | **Sí** | **Sí** | R-A reporta ejecución real; R-B deja tabla vacía. |
| Tabla de siete etapas con responsable y evidencia | **Parcial** | **Sí** | R-A tiene fases F1–F7 con evidencia, pero sin responsable; R-B incluye responsable y estado. |
| Bitácora con decisión humana | **Parcial** | **Sí** | R-A remite a `decisiones.md`; R-B la incluye en el producto. |
| Declaración de aprobaciones | **Sí, pero dependiente del proyecto** | **No atribuye ninguna** | R-A registra aprobaciones reales del equipo; R-B evita esa dependencia. |
| Referencias verificadas o marcadas | **Sí** | **Sí** | R-A verificadas; R-B candidatas/no verificadas. |
| No afirmar validez ecológica | **Sí** | **Sí** | Ambas lo explicitan. |
| No afirmar superioridad general del HMM | **Sí** | **Sí** | R-A lo limita con resultados; R-B ni siquiera reporta resultados. |

**Lectura:** R-A cumple lo sustantivo, pero falla en dos requisitos formales que también estaban en la skill original: **dos preguntas** y **protocolo de búsqueda**. R-B cumple mejor el formato de entrega, aunque su cumplimiento es “en plan”, no “en ejecución”.

---

## 3. Requisitos añadidos por la skill modificada

| Requisito nuevo | R-A | R-B | Comentario |
|---|---|---|---|
| Razones para usar **y para descartar** el HMM | **Parcial** | **Sí** | R-A justifica a favor y advierte límites, pero no desarrolla un apartado de razones en contra. R-B lo hace explícito (§1.5–1.6). |
| Página o sección para cada afirmación extraída | **No** | **Sí** | R-A cita referencias, pero no indica página/sección de cada afirmación. R-B incluye Anexo A con línea/página. |
| Comprobar etiquetas antes de proponer exactitud/F1 | **Parcial** | **Sí** | R-A usa etiquetas simuladas correctamente, pero no lo declara como comprobación metodológica. R-B lo declara en §4.5. |
| Incluir método sencillo sin HMM | **Sí** | **Sí** | Ambas usan M0. |
| Resultados solo reales o tabla vacía | **Sí** | **Sí** | R-A tiene resultados reales; R-B tabla vacía. |
| Tabla de siete etapas con responsable | **Parcial** | **Sí** | R-A no asigna responsable. |
| Decisiones pendientes priorizadas | **Parcial** | **Sí** | R-A tiene limitaciones y trabajo futuro; R-B tiene C1–C7. |
| Siguiente paso explícito | **Parcial** | **Sí** | R-A lo menciona en conclusiones; R-B lo separa en Anexo D. |
| No atribuir aprobación al equipo | **No** | **Sí** | R-A registra aprobaciones; R-B declara que ninguna existe en esa versión. |

**Lectura:** la skill modificada cambia el centro de gravedad: de “producir un manuscrito completo” a “producir un anteproyecto auditable”. R-B sigue mejor ese cambio; R-A sigue mejor el objetivo de entrega final.

---

## 4. Comparación por dimensión

### 4.1 Precisión

| Subcriterio | R-A | R-B | Balance |
|---|---|---|---|
| Corrección formal y matemática | Alta | Alta | Empate. Ambas usan λ = (S, V, A, B, π), Forward, Viterbi y Baum–Welch correctamente. |
| Correspondencia cifras–ejecución | Alta | No aplica | R-A: cada cifra proviene de `outputs/protocolo_d4_resumen.json`; R-B no reporta cifras. |
| Manejo de referencias | Media | Alta | R-A usa dos referencias verificadas, pero sin página/sección por afirmación. R-B las marca como candidatas y ubica su origen en la plantilla. |
| Ausencia de afirmaciones no sustentadas | Alta | Alta | R-A evita superioridad del HMM; R-B evita cualquier resultado. |
| Claridad sobre límites | Alta | Alta | Ambas son explícitas. R-B es más conservadora. |
| Estado de aprobación | Dependiente del proyecto | Autocontenido | R-A necesita la bitácora externa para sostener sus aprobaciones; R-B no depende de aprobaciones. |

**Conclusión de precisión:** R-A es más precisa **empíricamente** porque sus cifras son verificables. R-B es más precisa **epistémicamente** porque distingue hecho, inferencia, recomendación e incertidumbre, y no presenta como verificado lo que no lo está.

**Matiz importante:** R-A no “inventa” sus aprobaciones; fueron expresadas por el equipo y están en `decisiones.md`. El problema es que esa cadena no es derivable de los materiales iniciales y hace que la respuesta dependa de contexto externo. R-B evita esa dependencia, pero paga con menor contenido.

### 4.2 Pertinencia

| Subcriterio | R-A | R-B | Balance |
|---|---|---|---|
| Cobertura de la solicitud inicial | Alta | Media | R-A entrega manuscrito, resultados, código, LaTeX y PDF. R-B entrega solo el anteproyecto y deja la ejecución pendiente. |
| Alineación con la skill aplicada | Media | Alta | R-A cumple la skill original en lo sustantivo, pero falla en dos preguntas y protocolo de búsqueda. R-B cumple casi todos los añadidos de la skill modificada. |
| Utilidad como entregable | Alta | Media | R-A está listo para revisión/entrega. R-B está listo para autorizar una ejecución. |
| Justificación y alcance | Media | Alta | R-A justifica a favor y reconoce límites; R-B añade razones en contra y alternativas de alcance. |
| Diseño de comparación | Alta | Alta | Ambas incluyen baseline, métricas, unidad de secuencia, semillas e IC. |
| Verificación de etiquetas | Parcial | Alta | R-A usa etiquetas simuladas sin problematizarlo; R-B lo declara como condición. |

**Conclusión de pertinencia:** R-A es más pertinente si el objetivo es **entregar un producto completo**. R-B es más pertinente si el objetivo es **decidir con rigor antes de ejecutar**. La solicitud inicial del caso pide “formular pregunta, justificar HMM, proponer método sencillo, datos, métrica y experimento controlado”; en ese sentido, R-B responde más directamente a la formulación, mientras R-A ya avanzó a la ejecución.

### 4.3 Trazabilidad

| Subcriterio | R-A | R-B | Balance |
|---|---|---|---|
| Afirmaciones → fuente | Media | Alta | R-A referencia el caso y sus artefactos, pero no indica página/sección para la literatura. R-B tiene Anexo A con línea/página y tipo de afirmación. |
| Decisiones → evidencia | Alta | Media | R-A registra D1–D6 con evidencia y bitácora. R-B deja todo pendiente, pero explícito. |
| Reproducibilidad | Alta | Media | R-A tiene código, pruebas, semillas, JSON/CSV/PNG y PDF. R-B tiene un plan, no una ejecución. |
| Referencias | Media | Media | R-A: verificadas por el equipo, pero solo dos y sin ubicación de cada afirmación. R-B: candidatas, no verificadas, con ubicación en la plantilla. |
| Auditoría y pendientes | Media | Alta | R-A tiene limitaciones y trabajo futuro; R-B tiene bitácora, pendientes C1–C7 y siguiente paso. |

**Conclusión de trazabilidad:** R-A gana en **trazabilidad empírica** (cifras, código, artefactos). R-B gana en **trazabilidad documental** (fuentes, afirmaciones, estado de cada decisión). Son complementarias.

---

## 5. Balance global

| Dimensión | R-A (skill original) | R-B (skill modificada) | Ganador |
|---|---|---|---|
| Precisión empírica | Alta: cifras verificadas contra JSON/CSV | No aplica: sin cifras | **R-A** |
| Precisión epistemológica | Media-alta: evita sobreafirmar, pero hereda aprobaciones | Alta: separa hecho/inferencia y marca estados | **R-B** |
| Pertinencia como producto final | Alta: manuscrito completo | Media: protocolo sin resultados | **R-A** |
| Pertinencia como anteproyecto auditable | Media: formato de manuscrito final | Alta: formato de decisión y pendientes | **R-B** |
| Trazabilidad empírica | Alta: código, semillas, salidas, PDF | Ausente: no hay ejecución | **R-A** |
| Trazabilidad documental | Media: sin página/sección por afirmación | Alta: Anexo A y bitácora | **R-B** |
| Cumplimiento de la skill aplicada | Media: falla en dos preguntas y búsqueda | Alta: cumple casi todos los añadidos | **R-B** |
| Completitud | Alta | Media-baja | **R-A** |

**Veredicto:** no hay un ganador absoluto. Hay dos perfiles:

- **R-A = producto completo de la etapa.** Mejor para entregar, revisar resultados y recompilar.
- **R-B = producto de control.** Mejor para decidir, auditar y evitar afirmaciones no sustentadas.

---

## 6. Hallazgos clave

1. **R-A es más completa, pero no más cumplida.** Entrega resultados y PDF, pero incumple requisitos formales que ya estaban en la skill original: dos preguntas y protocolo de búsqueda.
2. **R-B es más cumplida, pero no más completa.** Satisface la skill modificada, pero no responde empíricamente porque no ejecuta.
3. **Las trazabilidades son distintas.** R-A traza cifras a ejecuciones; R-B traza afirmaciones a líneas y páginas. Ninguna reemplaza a la otra.
4. **R-A depende de aprobaciones externas.** Sus afirmaciones de autoría, referencias e IA son válidas en el proyecto, pero no se sostienen solo con los materiales iniciales. R-B evita esa dependencia.
5. **R-B evita el riesgo de sobreinterpretar M1/M2.** R-A reporta correctamente que M1 y M2 son casi idénticos, pero un lector apresurado podría leerlo como validación del HMM. R-B ni siquiera llega a esa lectura porque no reporta resultados.
6. **Ninguna hizo una revisión sistemática real.** R-A la declara pendiente; R-B propone el protocolo. La diferencia es de formato, no de evidencia bibliográfica.
7. **Ambas aciertan en lo esencial:** no afirman validez ecológica, no inventan datos y no declaran superioridad general del HMM.

---

## 7. Riesgos de cada respuesta

**Riesgos de R-A**

- La completitud puede leerse como validación científica.
- Las aprobaciones registradas pueden confundirse con evidencia empírica.
- El estado del arte es demasiado delgado para un artículo Q1.
- Tres preguntas en lugar de dos dificultan la evaluación.
- No hay un apartado explícito de razones para descartar el HMM.

**Riesgos de R-B**

- Puede percibirse como una respuesta evasiva o incompleta.
- Excluye una ejecución disponible, lo que reduce su utilidad práctica.
- Las tablas vacías no demuestran nada por sí mismas.
- El exceso de pendientes puede bloquear la entrega si no se prioriza.
- No tiene PDF ni LaTeX, a diferencia de R-A.

---

## 8. Recomendación

### Si el objetivo es entregar

Usar **R-A** como base y añadirle la capa de auditoría de R-B:

1. Reducir a dos preguntas.
2. Añadir el apartado de razones para usar y descartar el HMM.
3. Incorporar el protocolo de búsqueda y el Anexo A de trazabilidad.
4. Añadir la tabla de parámetros fijados vs aprendidos.
5. Explicitar la comprobación de etiquetas.
6. Añadir la tabla de siete etapas con responsable y la bitácora de pendientes.
7. Mantener los resultados, pero con procedencia explícita a `outputs/`.

### Si el objetivo es decidir antes de ejecutar

Usar **R-B** como base y añadir, solo si el equipo lo autoriza, un anexo de resultados de R-A con procedencia y fecha. No mover el tag `anteproyecto` ni registrar aprobaciones nuevas.

### Lo que no conviene hacer

- Copiar las cifras de la plantilla.
- Presentar R-B como si ya tuviera resultados.
- Presentar R-A como si sus aprobaciones fueran derivables de los materiales iniciales.
- Declarar que una de las dos es “Q1” por usar la plantilla.

---

## 9. Evidencia usada en la comparación

- R-A: `manuscrito_anteproyecto.md`, `manuscrito_anteproyecto.tex`, `manuscrito_anteproyecto.pdf`, `outputs/protocolo_d4_resumen.json`, `decisiones.md`.
- R-B: `manuscrito_anteproyecto_skill_modificada.md`.
- Caso: `materiales/caso_riesgo_de_incendio_forestal.md`, líneas 3–16.
- Plantilla: `materiales/plantilla_articulo.pdf`, pp. 1–8, en especial p. 4 §3.4, p. 5 Tabla 2 y p. 7 referencias.
- Skills: `.agents/skills/articulo-hmm/SKILL.md` y `.agents/skills/articulo-hmm/skill_modificada.md`.
- Verificación numérica: `outputs/protocolo_d4_resumen.json` (base: T = 500, N = 2000, semilla maestra 20261109).

**Nota final:** esta comparación es una evaluación cualitativa de productos, no una prueba estadística ni una auditoría editorial. No atribuye aprobación del equipo a ninguna de las dos respuestas.
