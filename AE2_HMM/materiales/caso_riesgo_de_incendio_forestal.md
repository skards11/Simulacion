# Caso didáctico: evaluación de riesgo de incendio forestal

Un entorno forestal registra niveles ambientales de humedad alta, media y baja. Explorar si un HMM permite inferir estados supuestos de riesgo de incendio (Riesgo Bajo, Riesgo Moderado, Riesgo Extremo). No se aporta un dataset sensorizado real. La humedad por sí sola no demuestra directamente el nivel de riesgo en el terreno.

Observaciones ilustrativas: Humedad Alta, Humedad Alta, Humedad Media, Humedad Baja, Humedad Baja.

Parámetros hipotéticos para una simulación (no estimados de un ecosistema real):
$A = \begin{bmatrix} 0.70 & 0.25 & 0.05 \\ 0.30 & 0.50 & 0.20 \\ 0.10 & 0.30 & 0.60 \end{bmatrix}$

$B = \begin{bmatrix} 0.70 & 0.25 & 0.05 \\ 0.20 & 0.60 & 0.20 \\ 0.05 & 0.25 & 0.70 \end{bmatrix}$

$\pi = [0.50, 0.30, 0.20]$

$A$: filas/columnas Riesgo Bajo, Riesgo Moderado, Riesgo Extremo. $B$: filas Riesgo Bajo, Riesgo Moderado, Riesgo Extremo; columnas Humedad Alta, Humedad Media, Humedad Baja.

Tareas: formular pregunta, justificar HMM, proponer método sencillo de comparación, datos, métrica y experimento controlado. Distinguir decodificación con parámetros conocidos de entrenamiento. No inventar hallazgos, fuentes ni cifras.