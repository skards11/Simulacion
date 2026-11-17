# Guion del video pitch — Problema bancario AE3

**Objetivo:** sustentar en 3 minutos el problema, el modelo, la simulación,
los resultados y la recomendación, que es lo que evalúa la rúbrica del video.

**Duración objetivo:** 3:00 (máximo recomendado: 3:15).
**Texto:** ~480 palabras; a un ritmo de 160 palabras por minuto ocupa 3:00.
**Formato:** cámara para el expositor y pantalla compartida con las figuras de
`outputs/figuras/`. No leer el documento ni el código.

Si son varios integrantes, se pueden repartir los bloques: apertura y contexto
(integrante A), modelo (B), resultados (C) y decisión/cierre (D). No es
obligatorio que todos aparezcan, pero sí que el video demuestre dominio del
trabajo.

---

## 0:00–0:20 — Apertura

**Visual:** diapositiva con el título y la pregunta central.

> Buenos días. Somos **[nombres]** y hoy resolvemos una decisión concreta del
> Banco de Colombia: ¿debe dedicar una caja exclusiva a retiros y dos a pagos,
> o al revés? Y, sobre todo, ¿necesita abrir una cuarta caja? Para responderlo,
> simulamos un día completo de operación.

**Idea que debe quedar:** hay una decisión de negocio, no solo un ejercicio
de código.

---

## 0:20–0:50 — Contexto y objetivo

**Visual:** esquema de las 3 cajas, el 70/30 y los 480 minutos.

> El banco tiene tres cajas para retiros y pagos. El 70 % de los usuarios hace
> retiros y el 30 % pagos o consignaciones. Opera 8 horas diarias, 480 minutos,
> y no tiene cajeros electrónicos. Cada caja es un servidor M/M/1: llegadas
> Poisson, servicio exponencial y cola independiente. Los tiempos medios salen
> de las tablas del laboratorio y dependen del tipo de usuario: rápido, normal,
> lento y muy lento.

**Idea que debe quedar:** el sistema es estocástico y cada cajero tiene su
propia cola.

---

## 0:50–1:30 — Modelo y metodología

**Visual:** diagrama de flujo: llegada → asignación → servicio → fin; al lado,
la semilla 42 y “30 réplicas”.

> Implementamos un simulador de eventos discretos en Python. En cada réplica
> sorteamos la acción, el tipo de usuario y los tiempos de llegada y servicio.
> Si hay una caja libre, el cliente va a una al azar; si todas están ocupadas,
> elige la cola más corta. Generamos llegadas hasta el minuto 480 y dejamos que
> el sistema se vacíe para no truncar esperas. Corrimos 30 réplicas
> independientes con semilla 42. Usamos números aleatorios comunes: dentro de
> una réplica, todas las configuraciones reciben los mismos clientes y
> servicios; solo cambia la asignación. Así comparamos de forma justa.

**Idea que debe quedar:** el experimento es reproducible y las diferencias
entre configuraciones no se deben a muestras distintas.

---

## 1:30–2:15 — Resultados: los cinco puntos

**Visual:** tabla con las tres cifras clave y, si cabe, una figura del ranking.
Resaltar en color: 0.78 min, 2.09 min y 46.9 %.

> Con las tres cajas mixtas actuales, la espera promedio es 0.78 minutos, el
> percentil 90 es 2.09 y la utilización máxima 46.9 %. Se cumplen todos los
> criterios. En el punto 1, el cajero 0 tuvo el menor tiempo medio de atención,
> 3.16 minutos, y el cajero 2 el mayor, 3.23; la diferencia es ruido muestral.
> En el punto 2, el usuario normal es el más frecuente, con 34.2 %, seguido del
> muy lento, con 26.1 %. En el punto 3, el mínimo por tipo aparece en réplicas
> distintas: no hay una sola réplica con menos usuarios de todos los tipos. En
> el punto 4, una cuarta caja mixta baja la espera a 0.21 minutos, pero no es
> necesaria porque la configuración actual ya cumple. En el punto 5,
> especializar no mejora el resultado global: una caja de retiros y dos de
> pagos hace esperar 5.55 minutos a los retiros, que son la mayoría.

**Idea que debe quedar:** los cinco puntos están respondidos con cifras, no
solo con tablas.

---

## 2:15–2:45 — Decisión y recomendación

**Visual:** ranking de `punto5_configuracion.csv`; resaltar “3 cajas mixtas”.

> Por eso recomendamos mantener tres cajas mixtas: cero exclusivas de retiros y
> cero de pagos. Si el banco exigiera especializar las tres cajas, la opción
> más balanceada sería una de retiros y dos de pagos, pero no cumple los
> criterios. Si estuviera dispuesto a crear una cuarta caja y especializar, la
> mejor sería dos y dos, con 0.66 minutos de espera global. La decisión
> costo-efectiva sigue siendo no abrir una caja adicional.

**Idea que debe quedar:** se distingue “mejor desempeño” de “recomendación
costo-efectiva”.

---

## 2:45–3:00 — Limitaciones y cierre

**Visual:** diapositiva final con la conclusión y el repositorio.

> El modelo asume tiempos exponenciales, un día representativo y una política
> de asignación; como trabajo futuro, conviene calibrarlo con datos reales y
> evaluar horarios pico. En resumen: tres cajas mixtas cumplen el servicio y
> evitan un costo innecesario. Gracias.

**Idea que debe quedar:** hay conclusiones claras y límites reconocidos.

---

## Checklist antes de grabar

- [ ] El video dura entre 2:50 y 3:15.
- [ ] Se entienden las cifras: 0.78 min, 2.09 min, 46.9 %, 0.21 min y 5.55 min.
- [ ] Se responden los cinco puntos, aunque sea en una frase cada uno.
- [ ] Se explica el modelo M/M/1 y los supuestos sin leer diapositivas.
- [ ] Se distingue la recomendación costo-efectiva del mejor desempeño absoluto.
- [ ] Se mencionan las limitaciones y el trabajo futuro.
- [ ] Audio claro, buena luz y pantalla legible.
- [ ] El enlace del video queda en el README y en la entrega.

## Frases de respaldo (si falta tiempo)

- “La conclusión no cambia si se usan 50 réplicas: la espera se mantiene por
  debajo de 1 minuto.”
- “La cuarta caja mejora el indicador, pero no resuelve un problema que la
  configuración actual ya cumple.”
- “Especializar mejora una operación a costa de la otra; por eso no es
  automáticamente la mejor decisión.”
