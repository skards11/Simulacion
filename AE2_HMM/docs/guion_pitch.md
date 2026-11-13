# Guion del Video Pitch — AE2_HMM

**Duración objetivo:** 2:30 min (150 s) · **Formato:** MP4, 1920×1080, 16:9 horizontal, H.264 + AAC.
**Ritmo de lectura:** ~130 palabras/minuto. **Cifras:** verificadas contra `outputs/experimento_hmm_resumen.json` y el PDF final.

| Integrante | Bloque | Tema | Ventana | Duración |
|---|---|---|---|---|
| Oscar Alonso De la Pava Suarez | 1 | Gancho | 0:00–0:13 | 13 s |
| Oscar Alonso De la Pava Suarez | 2 | Motivación e impacto | 0:13–0:32 | 19 s |
| Oscar Alonso De la Pava Suarez | 3 | Solución propuesta | 0:32–0:51 | 19 s |
| Anderson Jesus Ospina Cardona | 4 | Metodología y diseño | 0:51–1:15 | 24 s |
| Anderson Jesus Ospina Cardona | 5 | Resultado clave | 1:15–1:42 | 27 s |
| Kevin Andrés Valencia Daza | 6 | Aporte científico | 1:42–2:08 | 26 s |
| Kevin Andrés Valencia Daza | 7 | Cierre | 2:08–2:30 | 22 s |

---

## INTEGRANTE 1 — Contexto y modelo (0:00–0:51)

### Bloque 1 — Gancho (0:00–0:13)

> Imaginen un bosque donde solo podemos medir la humedad: alta, media o baja. El riesgo real —bajo, moderado o extremo— permanece oculto. ¿Podemos inferirlo con matemáticas?

*[Cámara del presentador, plano medio. Fondo: imagen de bosque con transición a iconos de humedad. Rótulo inferior: “Riesgo oculto → ¿inferible?”.]*

### Bloque 2 — Motivación e impacto (0:13–0:32)

> Antes de llevar un modelo así a una alerta real, necesitamos saber cuánto depende de sus supuestos. Un modelo que parece acertado puede fallar en silencio si sus observaciones pierden calidad. Medir esa sensibilidad es tan importante como medir el acierto.

*[Screencast breve de `outputs/fig_metricas_300dpi.png` con zoom al eje macro-F1; luego corte a cámara. Rótulo: “Sensibilidad antes que despliegue”.]*

### Bloque 3 — Solución propuesta (0:32–0:51)

> Proponemos un HMM discreto: lambda igual a S, V, A, B y pi. Tres estados ocultos de riesgo, tres observaciones ordinales de humedad, matriz de transición A, matriz de emisión B y prior pi. Decodificamos con Viterbi en espacio logarítmico para evitar desbordamientos numéricos.

*[Diagrama animado del HMM: estados RB–RM–RE, flechas A, emisiones B hacia Alta–Media–Baja, vector pi. Cierre con el Algoritmo 1 del manuscrito resaltando `log`. Duración total del bloque: 19 s.]*

---

## INTEGRANTE 2 — Experimento y resultados (0:51–1:42)

### Bloque 4 — Metodología y diseño experimental (0:51–1:15)

> En una frase: simulamos un HMM con parámetros fijos y comparamos tres reglas pareadas. Generamos dos mil secuencias, cada una de quinientos pasos: M0 decodifica con Viterbi nominal, M1 clasifica cada paso solo con B, sin memoria, y M2 usa Viterbi sobre observaciones degradadas con m igual a cero punto cinco.

*[Cámara + screencast de VS Code mostrando `src/simulation.py` (constantes `DEFAULT_T`, `DEFAULT_N`, `ALTERED_MIXING`). Inserto del diagrama de flujo F1–F7 (Figura 1). Rótulo: “T = 500 · N = 2000 · pareado”.]*

### Bloque 5 — Resultado clave (1:15–1:42)

> Bajo B nominal, M0 y M1 son estadísticamente indistinguibles: macro-F1 de 0.6602 frente a 0.6603, con p igual a 0.778 y delta de Cliff de menos 0.006. En cambio, M2 cae a 0.4989: una diferencia de 0.1612, p menor que 0.001 y delta de Cliff de 1.0. Las dos mil secuencias favorecen a M0. No hay empates.

*[Gráfica de barras a 300 dpi (`fig_metricas_300dpi.png`) con las tres medias y sus IC. Luego Tabla 4 resaltando la fila M0 vs. M2. Señalizar la fuente en pantalla: “Datos simulados — outputs/”.]*

---

## INTEGRANTE 3 — Aporte y cierre (1:42–2:30)

### Bloque 6 — Aporte científico (1:42–2:08)

> El aporte no es que el HMM gane, sino demostrar cuándo no gana. Con Wilcoxon pareado, Holm–Bonferroni y delta de Cliff separamos señal de azar. Y todo es reproducible: código, semillas, hashes SHA-256 y auditoría de las sesenta y seis cifras. Cualquiera puede repetir el experimento y obtener los mismos números.

*[Screencast de `docs/auditoria_final.md` desplazándose por la tabla de verificación; corte a `outputs/MANIFEST.txt` con los hashes. Rótulo: “66 cifras auditadas · 15 pruebas”.]*

### Bloque 7 — Cierre (2:08–2:30)

> Respondiendo: el riesgo se representa con un HMM discreto; los parámetros influyen de forma jerárquica, con B dominando; y el modelo es reproducible pero sensible a la calidad de las emisiones. El alcance es simulado: no afirmamos predicción de incendios reales. El siguiente paso es estimar A, B y pi con Baum–Welch sobre datos meteorológicos reales. Gracias.

*[Cámara del presentador a plano medio, cierre con tarjeta final: título del trabajo, los tres nombres, correos institucionales y URL del repositorio. Fundido a negro.]*

---

## Notas de producción

- **Reparto:** Oscar abre (bloques 1–3), Anderson conduce el experimento (4–5), Kevin cierra (6–7).
- **Ritmo:** leer a ~130 palabras/minuto; ensayar con cronómetro y dejar 2 s de aire entre bloques.
- **Cifras exactas:** no redondear en voz alta más allá de lo escrito; las cifras provienen de `outputs/experimento_hmm_resumen.json`.
- **Rotulación obligatoria:** todo gráfico de resultados debe mostrar “Datos simulados”.
- **Exportación:** MP4 H.264, 1080p, 16:9, audio 48 kHz; nombre sugerido `AE2_HMM_pitch_v1.0.mp4`.
- **Enlace:** al publicar el video, reemplazar `[INSERTAR_URL_VIDEO_PITCH]` en `README.md`.
