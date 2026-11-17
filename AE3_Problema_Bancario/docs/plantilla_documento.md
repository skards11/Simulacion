# Plantilla del documento — Problema bancario AE3

> Copiar este archivo a Word (o a Google Docs) y reemplazar los textos entre
> corchetes. Borrar esta nota antes de entregar. Mantener el formato de
> portada, índice, numeración y títulos.

---

## Portada

**INSTITUCIÓN:** [Nombre de la institución]

**ASIGNATURA:** Simulación

**TÍTULO:** Solución de un problema bancario: simulación de cajas M/M/1

**INTEGRANTES:**

- [Nombre completo] — [correo institucional]
- [Nombre completo] — [correo institucional]
- [Nombre completo] — [correo institucional]

**DOCENTE:** [Nombre]

**FECHA:** [DD/MM/AAAA]

**CIUDAD:** [Ciudad]

**VERSIÓN:** v1.0

---

## Índice

[Generar automáticamente en Word: Referencias > Tabla de contenido.]

---

## Resumen ejecutivo

[Escribir máximo una página. Incluir: problema, método, hallazgo principal,
recomendación y cifra clave. No incluir tablas extensas.]

Ejemplo de apertura:

> El Banco de Colombia necesita decidir cómo distribuir sus tres cajas entre
> retiros y pagos. Se simuló un día de operación de 8 horas con 30 réplicas y
> un modelo M/M/1 por cajero. La configuración actual de 3 cajas mixtas
> cumple los criterios de servicio, con una espera promedio de [0.78] min y una
> utilización máxima de [46.9] %. Por tanto, se recomienda [mantener 3 cajas
> mixtas / crear una cuarta caja / especializar de la siguiente forma].

---

# 1. Introducción

## 1.1 Contexto y problema

[Describir el banco, las 3 cajas, la composición 70 % retiros / 30 % pagos,
las 8 horas de operación y la pregunta sobre cajas exclusivas. Cerrar con la
pregunta de decisión.]

## 1.2 Objetivos

**Objetivo general:** [Evaluar configuraciones de cajas para reducir la espera
y recomendar una asignación de cajas exclusivas/mixtas.]

**Objetivos específicos:**

1. [Simular al menos 10 réplicas de un día de 8 horas.]
2. [Identificar el cajero con menor y mayor tiempo promedio de atención.]
3. [Estimar el promedio de usuarios de cada tipo en el total de cajeros.]
4. [Determinar el total de usuarios por tipo en cada réplica.]
5. [Evaluar la necesidad de un cajero adicional.]
6. [Comparar configuraciones y recomendar cuántas cajas exclusivas destinar a
   pagos y cuántas a retiros.]

## 1.3 Alcance y preguntas de análisis

[Delimitar: cajas M/M/1, sin cajeros electrónicos, sin abandono, un día
representativo, siete configuraciones.]

Preguntas:

1. [¿Qué cajero tiene el menor y el mayor tiempo promedio de atención?]
2. [¿Cuántos usuarios de cada tipo atiende el sistema en promedio?]
3. [¿Cómo varía el total de usuarios por tipo entre réplicas?]
4. [¿Se necesita un cuarto cajero?]
5. [¿Cuántas cajas exclusivas para pagos y cuántas para retiros conviene
   tener?]

## 1.4 Justificación

[Explicar por qué la simulación es adecuada frente a una fórmula analítica
simple: mezcla de tipos, varias cajas, aleatoriedad y comparación de
escenarios.]

---

# 2. Marco teórico y metodología

## 2.1 Teoría de colas y modelo M/M/1

[Definir M/M/1, lambda, mu, rho, L, Lq, W, Wq y ley de Little. Incluir la
condición rho < 1. Aclarar que cada cajero se modela como M/M/1, pero la mezcla
de tipos de usuario se incorpora en la simulación.]

## 2.2 Datos del sistema y supuestos

[Insertar Tabla 1: tiempos de servicio y llegada. Insertar Tabla 2:
probabilidades de tipo de usuario.]

**Tabla 1.** Tiempos de servicio y de llegada por tipo de usuario.
*Fuente: enunciado del laboratorio.*

[Tabla]

**Tabla 2.** Probabilidades de los tipos de usuario.
*Fuente: enunciado del laboratorio.*

[Tabla]

**Tabla 3.** Supuestos de la simulación.

| Supuesto | Valor / decisión | Justificación |
|---|---|---|
| Composición de llegadas | [70 % retiros, 30 % pagos] | [Enunciado] |
| Tipo de usuario | [Probabilidades Tabla 2] | [Enunciado] |
| Tiempo entre llegadas | [Exponencial, media Tabla 1] | [Enunciado] |
| Tiempo de servicio | [Exponencial, media Tabla 1] | [Enunciado] |
| Cajas | [3 actual; 4 en ampliación] | [Pregunta del banco] |
| Asignación | [Caja libre al azar; si no, cola más corta] | [Política operativa] |
| Cierre | [Llegadas hasta 480 min; luego drenaje] | [Evitar truncar esperas] |
| Réplicas | [30; semilla 42] | [Supera el mínimo de 10] |

## 2.3 Diseño de la simulación

[Describir el flujo de eventos: llegada, asignación, servicio, fin de servicio,
registro. Explicar los números aleatorios comunes: todas las configuraciones
de una réplica usan los mismos clientes y servicios; solo cambia la asignación.
Explicar el drenaje después del minuto 480.]

## 2.4 Configuraciones evaluadas

**Tabla 4.** Configuraciones simuladas.

| Clave | Configuración | Cajas |
|---|---|---:|
| `mixto_3` | 3 cajas mixtas (actual) | 3 |
| `retiro_1_pago_2` | 1 retiro + 2 pagos | 3 |
| `retiro_2_pago_1` | 2 retiros + 1 pago | 3 |
| `mixto_4` | 4 cajas mixtas | 4 |
| `retiro_2_pago_2` | 2 retiros + 2 pagos | 4 |
| `retiro_3_pago_1` | 3 retiros + 1 pago | 4 |
| `retiro_1_pago_3` | 1 retiro + 3 pagos | 4 |

## 2.5 Métricas y criterios de decisión

[Definir espera promedio, P90, máximo, fracción > 10 min, tiempo de servicio,
tiempo en el sistema, Lq, L, utilización y conteos por tipo. Insertar Tabla 5
con los criterios.]

**Tabla 5.** Criterios de servicio usados para decidir.

| Criterio | Umbral |
|---|---:|
| Espera promedio global | ≤ 5 min |
| Espera promedio de retiros | ≤ 5 min |
| Espera promedio de pagos | ≤ 5 min |
| Espera promedio del peor tipo | ≤ 5 min |
| P90 de espera global | ≤ 10 min |
| P90 de espera de retiros | ≤ 10 min |
| P90 de espera de pagos | ≤ 10 min |
| Fracción con espera > 10 min | ≤ 10 % |
| Utilización máxima de una caja | ≤ 85 % |

[Justificar el número de réplicas: 30 supera el mínimo de 10 y da un IC 95 %
de la espera promedio de 0.59–0.97 min con 3 cajas mixtas.]

## 2.6 Herramientas y reproducibilidad

[Mencionar Python 3.12, NumPy, pandas, SciPy, Matplotlib, pruebas (12
passed), comando `python scripts/reproduce.py`, semilla 42 y manifiesto
SHA-256. No incluir capturas de código en el cuerpo.]

---

# 3. Resultados

> Para cada punto: pregunta, tabla/figura, lectura y respuesta directa. No
> pegar tablas sin interpretación.

## 3.1 Punto 1: cajero con menor y mayor tiempo de atención

**Tabla 6.** Desempeño por cajero en la configuración de 3 cajas mixtas.

| Cajero | Clientes | Servicio prom. (min) | IC 95 % | Espera prom. (min) | Sistema prom. (min) | Utilización |
|---:|---:|---:|---|---:|---:|---:|
| [0] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |
| [1] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |
| [2] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |

*Fuente: `outputs/punto1_cajeros.csv`.*

**Figura 1.** Tiempo promedio de servicio y de espera por cajero.
*Fuente: `outputs/figuras/fig_cajeros_configuracion_actual.png`.*

[Insertar figura]

[Interpretar: ¿quién tiene el menor y el mayor promedio? ¿La diferencia es
estadísticamente relevante o ruido muestral? Explicar que en la configuración
mixta la asignación es aleatoria y las distribuciones son iguales.]

**Respuesta del punto 1:** [El cajero [X] tuvo el menor tiempo promedio de
servicio ([ ] min) y el cajero [Y] el mayor ([ ] min). La diferencia es [ ] min
y los intervalos de confianza [se solapan / no se solapan], por lo que [no hay
evidencia de diferencia operativa / hay diferencia].]

## 3.2 Punto 2: promedio de usuarios de cada tipo

**Tabla 7.** Promedio de usuarios por tipo en el total de cajas.

| Tipo | Promedio por réplica | DE | IC 95 % | % del total | Promedio por cajero |
|---|---:|---:|---|---:|---:|
| Rápido | [ ] | [ ] | [ ] | [ ] | [ ] |
| Normal | [ ] | [ ] | [ ] | [ ] | [ ] |
| Lento | [ ] | [ ] | [ ] | [ ] | [ ] |
| Muy lento | [ ] | [ ] | [ ] | [ ] | [ ] |

*Fuente: `outputs/punto2_usuarios_tipo.csv`.*

[Interpretar qué tipo es más frecuente y cómo se relaciona con los tiempos de
servicio. Aclarar que “totalidad de cajeros” significa la suma de las tres
cajas por réplica.]

**Respuesta del punto 2:** [El tipo [X] es el más frecuente con [ ] usuarios
promedio por réplica ([ ] %), seguido de [Y] con [ ] ([ ] %).]

## 3.3 Punto 3: total de usuarios por tipo en cada réplica

**Tabla 8.** Réplica con menor cantidad de usuarios por tipo.

| Tipo | Réplica con mínimo | Mínimo | Promedio | Máximo |
|---|---:|---:|---:|---:|
| Rápido | [ ] | [ ] | [ ] | [ ] |
| Normal | [ ] | [ ] | [ ] | [ ] |
| Lento | [ ] | [ ] | [ ] | [ ] |
| Muy lento | [ ] | [ ] | [ ] | [ ] |

*Fuente: `outputs/punto3_minimos.csv`.*

La tabla completa de las [30] réplicas está en el Anexo A
(`outputs/punto3_replicas.csv`).

[Interpretar: no hay una única réplica con menos usuarios de todos los tipos;
el mínimo depende del tipo. Explicar que las llegadas son comunes entre
configuraciones, por lo que los conteos no cambian por asignación de cajas.]

**Respuesta del punto 3:** [La réplica [X] tuvo el mínimo de usuarios rápidos
([ ]) y normales ([ ]); la réplica [Y] el mínimo de lentos ([ ]); la réplica
[Z] el mínimo de muy lentos ([ ]).]

## 3.4 Punto 4: necesidad de un cajero adicional

**Tabla 9.** Comparación de 3 y 4 cajas mixtas.

| Métrica | 3 cajas mixtas | 4 cajas mixtas | Diferencia |
|---|---:|---:|---:|
| Espera promedio global (min) | [ ] | [ ] | [ ] |
| Espera retiros (min) | [ ] | [ ] | [ ] |
| Espera pagos (min) | [ ] | [ ] | [ ] |
| P90 (min) | [ ] | [ ] | [ ] |
| Fracción > 10 min | [ ] | [ ] | [ ] |
| Utilización máxima | [ ] | [ ] | [ ] |

*Fuente: `outputs/punto4_comparacion.csv`.*

**Figura 2.** Comparación de esperas entre 3 y 4 cajas mixtas.
*Fuente: `outputs/figuras/fig_punto4_comparacion.png`.*

[Insertar figura]

[Evaluar cada criterio de la Tabla 5 con 3 cajas. Indicar cuáles se cumplen y
cuáles no. Explicar si la cuarta caja es necesaria o solo mejora un resultado
que ya es aceptable.]

**Respuesta del punto 4:** [Con 3 cajas mixtas [se cumplen / no se cumplen]
los criterios: espera promedio [ ] min, P90 [ ] min, utilización máxima [ ] %.
Por tanto, [no se requiere / se requiere] crear un nuevo cajero.]

[Aclarar que “nuevo cajero” se interpreta como cajero/ventanilla atendido por
personal, no como cajero electrónico, porque el caso no incluye cajeros
automáticos.]

## 3.5 Punto 5: configuración óptima de cajas exclusivas

**Tabla 10.** Ranking de configuraciones.

| Puesto | Configuración | Cajas | Retiro | Pago | Mixtas | Espera prom. (min) | Espera retiro | Espera pago | P90 | Util. máx. | ¿Cumple? |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|:---:|
| [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |

*Fuente: `outputs/punto5_configuracion.csv`.*

**Figura 3.** Espera promedio por tipo de operación y configuración.
*Fuente: `outputs/figuras/fig_espera_por_accion.png`.*

[Insertar figura]

[Explicar el trade-off: 1R+2P mejora pagos pero castiga retiros; 2R+1P reduce
el promedio global pero castiga pagos; 2R+2P con 4 cajas es la mejor
especializada; 4 mixtas es el mejor desempeño absoluto pero implica una caja
adicional. Distinguir “mejor desempeño” de “recomendación costo-efectiva”.]

**Respuesta del punto 5:** [La recomendación es [configuración]: [X] cajas
exclusivas de retiro y [Y] de pago, con [Z] cajas mixtas. Justificación:
[espera promedio, cumplimiento de criterios, costo de cajas adicionales]. Si se
exige especializar las 3 cajas, la opción más balanceada es [1R+2P / 2R+1P],
pero [no cumple / cumple parcialmente].]

## 3.6 Análisis integrado y sensibilidad

[Conectar los cinco puntos. Mencionar que la demanda es ~198 usuarios/día y la
carga ofrecida 1.334 servidores. Explicar que la conclusión depende de los
criterios: si se exige espera ≤ 0.5 min, la cuarta caja mixta sí sería
necesaria; si se exige utilización ≤ 30 %, ni siquiera 4 cajas mixtas alcanzan
(36.5 %) y habría que evaluar 5. Mencionar que se puede repetir con 50 o 100
réplicas.]

---

# 4. Conclusiones y recomendaciones

## 4.1 Conclusiones

1. [Cajeros: no hay diferencia operativa real; las diferencias son ruido.]
2. [Usuarios por tipo: el normal es el más frecuente; el muy lento pesa por su
   tiempo de servicio.]
3. [Réplicas: el mínimo por tipo ocurre en réplicas distintas.]
4. [Cajero adicional: no se requiere con 3 cajas mixtas.]
5. [Configuración: mantener 3 cajas mixtas; si se especializa, explicar el
   trade-off.]

## 4.2 Recomendaciones para el banco

- [Mantener 3 cajas mixtas y monitorear la espera real.]
- [Evaluar una cuarta caja si la demanda crece o se endurecen los criterios.]
- [Si se especializa, comunicar el costo en espera del otro tipo de operación.]
- [Calibrar las medias con datos reales.]

---

# 5. Limitaciones y trabajo futuro

[No se modelan abandonos, prioridades, horarios pico ni cajeros electrónicos.
Los tiempos son exponenciales con medias del enunciado. La asignación es una
política posible. Se simula un día representativo. Trabajo futuro: validar con
datos reales, incluir costos de apertura y optimizar el costo total.]

---

# Referencias

[Usar el estilo solicitado por el curso (IEEE o APA). Ejemplos:]

1. [Autor. “Título del artículo o libro.” Editorial, año.]
2. [Documento del laboratorio: “Solución de un problema bancario”, S25 –
   Módulo 2, 2026.]
3. [Documentación de Python/NumPy/pandas/Matplotlib, año.]

---

# Anexos

## Anexo A. Tablas completas

- [Tabla A1: total de usuarios por tipo en cada réplica
  (`outputs/punto3_replicas.csv`).]
- [Tabla A2: métricas por cajero y réplica (`outputs/cajeros.csv`).]
- [Tabla A3: resumen por acción y tipo (`outputs/resumen_por_accion.csv`,
  `outputs/resumen_por_tipo.csv`).]

## Anexo B. Código y estructura del repositorio

[Incluir la estructura de carpetas y una breve descripción de `main.py`,
`src/bank_simulation.py`, `src/analysis.py`, `scripts/` y `tests/`. No pegar
todo el código; indicar el repositorio y las instrucciones de ejecución.]

```text
AE3_Problema_Bancario/
├── main.py
├── src/
├── scripts/
├── tests/
├── outputs/
├── docs/
└── requirements.txt
```

## Anexo C. Evidencia de reproducibilidad

- [Salida de `python -m pytest -q`: 12 passed.]
- [Comando `python scripts/reproduce.py`.]
- [Manifiesto SHA-256: `outputs/MANIFEST.txt`.]
- [Datos en CSV generados por el código: `outputs/`.]
- [Enlace del video: [URL].]
- [Enlace del repositorio: [URL].]

---

## Nota final

[Revisar la lista de verificación de `docs/guia_documento.md` antes de
exportar a PDF. Verificar que todas las cifras coincidan con `outputs/` y que
el nombre del archivo sea `Apellido_Nombre_problemaBancario.docx` o `.pdf`.]
