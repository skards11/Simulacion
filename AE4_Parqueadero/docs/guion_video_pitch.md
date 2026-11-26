# Guion del video pitch — AE4 Parqueaderos

**Objetivo:** sustentar en 3–4 minutos la decisión del Centro Comercial
Supercentro: ¿la operación actual de tres cajeros con filas independientes es
suficiente o hay que cambiarla?

**Duración objetivo:** 3:45 (rango 3:30–4:00).
**Texto:** ~570 palabras habladas a 150–155 palabras por minuto.
**Formato:** cámara para el expositor y pantalla compartida con las figuras de
`outputs/figuras/`. No leer el documento ni el código.
**Reparto:** tres intervenciones consecutivas, sin intercalar, en este orden:

1. **Oscar** — apertura, contexto y pregunta (0:00–1:00).
2. **Anderson** — modelo, validación y resultados de los puntos A y B (1:00–2:30).
3. **Kevin** — escenarios, decisión y cierre (2:30–3:55).

**Consejo de grabación:** cada integrante graba su bloque completo en una sola
toma, mirando a cámara y con la figura correcta en pantalla. Si se graba por
separado, unir los tres bloques con corte seco y mantener el mismo tamaño de
letra.

---

## 0:00–1:00 — Apertura, contexto y pregunta · Oscar

**Visual:** título del trabajo + `fig_sistema.png` (tres filas, tres cajeros) +
tabla de tipos de usuario.

> Buenas tardes. Somos Oscar De la Pava, Anderson Ospina y Kevin Valencia.
> Hoy resolvemos una decisión real de operación: el Centro Comercial Supercentro
> cobra el parqueadero en **tres cajeros**, cada uno con su propia fila. La
> administración quiere saber si esa operación es suficiente o si debe invertir
> en más cajeros. Lo respondemos con simulación de eventos discretos, no con
> intuición.
>
> Los usuarios llegan de cuatro tipos: **25 % rápidos, 20 % normales, 27.5 %
> lentos y 27.5 % muy lentos**. Sus tiempos entre llegadas son exponenciales con
> media de 3, 3, 5 y 7 minutos, y sus tiempos de servicio de 1, 3, 4 y 6
> minutos. La jornada es de **720 minutos**, doce horas.
>
> Con esos datos, la carga del sistema es de **0.774 erlangs**. Repartida entre
> tres cajeros, cada uno trabaja al **26 %**. El sistema es estable y sobra
> capacidad. Entonces la pregunta no es “¿cuántos cajeros faltan?”, sino
> **“¿por qué los usuarios esperan?”**.

**Idea que debe quedar:** hay una decisión de negocio concreta, sobra capacidad y
el problema parece estar en la organización de las filas.

---

## 1:00–2:30 — Modelo, validación y resultados A–B · Anderson

**Visual:** `fig_calibracion.png`, `fig_validacion.png`, `fig_cajeros.png` y
`fig_tipos.png`, en ese orden.

> Para responder construimos un simulador en Python con reloj de eventos. En cada
> réplica se sortea el tipo de usuario y luego el tiempo hasta la siguiente
> llegada; el servicio es exponencial según el tipo. Modelamos tres cajeros con
> fila FIFO propia y sin cambio de fila, la operación actual; al cerrar, el
> sistema se drena.
>
> El experimento final tiene **32 réplicas** y semilla **42**. Descartamos los
> primeros **102 minutos** porque son transitorios: al inicio el sistema está
> vacío y la espera se ve artificialmente baja.
>
> Validamos contra la teoría: servicio a menos del **2.5 %** de lo nominal,
> llegadas al **0.6 %**, errores frente a M/M/1 y M/G/1 inferiores al **3.5 %**
> y nueve pruebas superadas.
>
> Los tres cajeros tienen tiempos promedio de **3.52, 3.53 y 3.56 minutos**. La
> diferencia máxima es de **2.8 segundos** y Friedman da **p = 0.804**: no hay
> un “cajero lento”.
>
> La demanda observada fue **25.5, 20.1, 26.7 y 27.6 por ciento**, casi la del
> enunciado; chi-cuadrado da **p = 0.653**. Un dato interesante: los **rápidos**
> esperan **2.01 minutos** y los **muy lentos** **1.20**. No es un error: la
> asignación aleatoria hace que un rápido quede detrás de un servicio largo
> mientras otro cajero se desocupa. Ese es el síntoma.

**Idea que debe quedar:** el modelo es confiable, los cajeros son iguales y la
demanda es correcta; el problema está en cómo se reparten los usuarios.

---

## 2:30–3:55 — Escenarios, decisión y cierre · Kevin

**Visual:** `fig_escenarios.png` resaltando la configuración actual y la
propuesta; al final, diapositiva con **Wq 1.61 → 0.08**, **P(>5) 12 % → 0.2 %**
y **0 cajeros nuevos**.

> Comparamos diez escenarios. La operación actual cumple cuatro de cinco
> criterios: espera en cola **1.61 minutos**, tiempo en el sistema **5.15** y
> utilización **30 %**. Pero el **12 %** espera más de cinco minutos y el máximo
> es **10 %**. Por ahí falla.
>
> La mejor alternativa no cuesta nada: **mantener los tres cajeros y compartir
> una sola fila**. La espera en cola baja a **0.08 minutos**, un **95 %** menos;
> la del sistema a **3.61**; y quienes esperan más de cinco minutos pasan de
> **12 % a 0.2 %**.
>
> Un cuarto cajero también cumple, pero cuesta personal y funciona peor que la
> fila única. Especializar es el peor escenario: **3.59 minutos**, porque
> concentra a los lentos en un solo cajero.
>
> En conclusión: sobra capacidad y falla la política de filas. Recomendamos
> **una fila única atendida por los tres cajeros**. Con el mismo personal
> logramos una espera promedio de **cinco segundos** y casi eliminamos las
> esperas largas.
>
> Si no se puede implementar, la política de “cajero libre o cola más corta”
> reduce la espera a **0.20 minutos** y también cumple. El código, los datos y
> las figuras permiten reproducir el estudio con una sola instrucción. Gracias.

**Idea que debe quedar:** una recomendación clara, cuantificada, de bajo costo y
con plan alternativo.

---

## Anexo: mapa de bloques y cifras

| Tiempo | Bloque | Expositor | Cifra que debe decir |
|---|---|---|---|
| 0:00–1:00 | Apertura, contexto y pregunta | Oscar | 3 cajeros; 25/20/27.5/27.5; 0.774 erlangs |
| 1:00–2:30 | Modelo, V&V y resultados A–B | Anderson | 32 réplicas; corte 102 min; Friedman p = 0.804; chi² p = 0.653 |
| 2:30–3:55 | Escenarios, decisión y cierre | Kevin | Wq 1.61 → 0.08; P(>5) 12 % → 0.2 %; 0 cajeros nuevos |

## Anexo: preguntas probables del jurado

| Pregunta | Respuesta corta |
|---|---|
| ¿Por qué 32 réplicas y no 30? | La fórmula del error relativo del IC 95 % con 30 daba 10.3 %; 32 lo baja del 10 %. |
| ¿Por qué 102 minutos de calentamiento? | Promedio móvil de 60 min sobre N(t): el primer bloque tiene 0.60 usuarios y el estado estable 1.19. |
| ¿El modelo es válido si el servicio no es exponencial? | Se validó también con M/G/1 (error ≤ 3.4 %) y con Erlang C para fila única (error 1 %). |
| ¿Por qué no 2 cajeros con fila única? | Sí cumple y es la opción más económica (Wq 0.73), pero los tres cajeros ya existen; no hay ahorro inmediato. |
| ¿Por qué la fila única mejora tanto? | Elimina el desbalance: el siguiente usuario siempre va al primer cajero que se desocupa. |
| ¿Qué pasa en horas pico? | No se modelaron; es una limitación. El análisis de sensibilidad sugiere que la fila única seguiría siendo superior. |
