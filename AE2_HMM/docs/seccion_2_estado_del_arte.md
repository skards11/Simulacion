# 2. Estado del arte

> **Nota de trazabilidad.** Esta sección se construyó exclusivamente a partir de `docs/referencias/fuentes_hmm.md` (fichas de los ocho artículos recientes/base) y de las dos referencias clásicas ya verificadas del proyecto (Rabiner, 1989; Baum, Petrie, Soules y Weiss, 1970). Ningún dato bibliográfico se completó con fuentes externas. Todo campo que no aparece explícitamente en esas fichas se marca como `[NO VERIFICADO]`, incluidos los DOI, los rangos de páginas y las ubicaciones exactas (página/sección) cuando la ficha solo consigna marcadores internos de cita.

## 2.1 Revisión sistemática breve

**Fundamentos.** El marco canónico de los modelos ocultos de Markov (HMM) quedó sistematizado por Rabiner [1], quien formuló los tres problemas clásicos —evaluación, decodificación y aprendizaje— y sus soluciones algorítmicas: Forward–Backward, Viterbi y Baum–Welch. Este trabajo es una revisión metodológica con aplicaciones en reconocimiento de voz y no reporta métricas empíricas propias. La base estadística de la reestimación tipo EM que conocemos como Baum–Welch fue establecida por Baum, Petrie, Soules y Weiss [2], cuyo aporte es teórico (convergencia de la técnica de maximización) y no incluye evaluación clasificatoria. Ambos constituyen el sustrato conceptual de cualquier estudio aplicado posterior, pero ninguno ofrece evidencia comparativa sobre el valor de la estructura temporal frente a reglas de decisión simples.

**Aplicaciones ambientales.** Wanjala, Makokha y Khamala [3] aplicaron un HMM multivariado con emisiones gaussianas a propiedades ópticas de aerosoles y variables climáticas en Kenia (2000–2022), con estimación EM, selección por BIC y decodificación de Viterbi; el modelo de cinco estados (BIC = 1380) identificó anomalías en el 5.08 % de los meses. Grammenos [4] modeló la ocurrencia diaria de lluvia en Ceará (Brasil) con HMM de emisiones Bernoulli, comparando especificaciones homogéneas y no homogéneas mediante AIC/BIC; el mejor ajuste incorporó una covariable climática en el proceso de observación (BIC = 24700.55). En ambos casos el HMM se **entrena** con los mismos datos que luego se evalúan y las métricas son heterogéneas (BIC/AIC), lo que impide aislar el efecto de la estructura de Markov.

**Incertidumbre, robustez y reproducibilidad.** Nicosia [5] abordó la incertidumbre de trayectoria mediante los "tubos tropicales de Viterbi", que delimitan el conjunto de rutas casi óptimas en tiempo O(TK²); lo validó en seis escenarios simulados y en trayectorias GPS/acústicas reales de murciélagos, con enriquecimientos de 2.25 y 0.27 para forrajeo y desplazamiento robustos. Pouzo, Psaradakis y Sola [6] demostraron por vía asintótica y por simulación Monte Carlo que los parámetros de la ecuación observable se estiman consistentemente por QML incluso si se ignora la cadena de Markov, siempre que los regímenes sean estacionarios y las covariables estrictamente exógenas. Ambos problematizan la inferencia, pero ninguno compara reglas de decodificación bajo parámetros fijos en un problema ordinal controlado.

**Aplicaciones híbridas, industria, salud y análisis secuencial.** Tran et al. [7] combinaron un HMM gaussiano de tres estados con una red LSTM de doble rama y atención para clasificar el cumplimiento normativo de calidad del agua costera en Vietnam, reportando 74.87 % de exactitud y 64.11 % de F1. Li, Qian y Wang [8] acoplaron un HMM izquierda-derecha con mezclas gaussianas a una regresión FS-LSSVR para pronosticar la vida útil remanente en el benchmark C-MAPSS, con reconocimiento de condición entre 77.69 % y 100.00 % y mejoras en MAPE, BIAS y convergencia frente a ANN. Deb, Pandey y Pakray [9] propusieron un HMM cuántico (QHMM) para etiquetado gramatical, con codificación de emisiones en estados cuánticos y mediciones parciales; reportan un F1 superior al HMM clásico, aunque la ficha consultada solo cubre las páginas iniciales hasta la Sección 2.2, por lo que el detalle numérico no puede verificarse aquí. Wang et al. [10] introdujeron StageGuard, una capa de inferencia estructurada con decodificador de Viterbi semi-Markoviano y restricciones fisiológicas para la estadificación del sueño, que reduce la tasa de violación de transiciones de 3.6–12.3 % a 0.1–0.8 % sin sacrificar exactitud. Estos trabajos confirman la madurez aplicada del formalismo, pero también su dependencia de arquitecturas híbridas y de entrenamiento supervisado o no supervisado sobre datos reales.

**Síntesis.** La literatura analizada cubre dominios muy diversos (clima, hidrología, agua, industria, sueño, lingüística, movimiento animal y econometría), con predominio de HMM continuos de emisiones gaussianas y de esquemas de estimación EM/Baum–Welch seguidos de decodificación de Viterbi. Las métricas son dispares (BIC/AIC, exactitud/F1, RMSE/Score, MAPE, tasas de violación de transiciones, enriquecimiento) y casi nunca se reporta la distribución completa de resultados por réplica. Solo los trabajos de corte metodológico [1], [2], [5] y [6] abordan explícitamente los fundamentos, la incertidumbre o la robustez del algoritmo; ninguno de los diez estudios compara la decodificación de un HMM con \(A\), \(B\) y \(\pi\) fijos contra baselines simples en un escenario ordinal con secuencias pareadas.

## 2.2 Fichas técnicas de los diez estudios

### [1] Rabiner (1989) — Tutorial canónico de HMM

1. **Cita IEEE:** L. R. Rabiner, "A tutorial on hidden Markov models and selected applications in speech recognition," *Proceedings of the IEEE*, vol. 77, no. 2, pp. 257–286, Feb. 1989.
2. **Año:** 1989.
3. **Base/Revista:** *Proceedings of the IEEE*, vol. 77, no. 2.
4. **DOI:** `[NO VERIFICADO]`.
5. **Dominio de aplicación:** Reconocimiento de voz (artículo de revisión metodológica).
6. **Tipo de HMM:** Discreto (marco general; el tutorial cubre también formulaciones continuas).
7. **Algoritmo de inferencia/entrenamiento:** Forward–Backward, Viterbi y Baum–Welch para los tres problemas canónicos (evaluación, decodificación y aprendizaje).
8. **Métricas reportadas:** Ninguna métrica empírica propia (revisión; "sin métricas propias").
9. **Naturaleza de datos:** No aplica (revisión conceptual y algorítmica).
10. **Página/sección de respaldo:** pp. 257–286 (título, resumen y cuerpo del tutorial). Ubicación interna de la ficha: `[NO VERIFICADO]` (la ficha no consigna marcadores de cita para esta entrada).

### [2] Baum, Petrie, Soules y Weiss (1970) — Técnica de maximización

1. **Cita IEEE:** L. E. Baum, T. Petrie, G. Soules, and N. Weiss, "A maximization technique occurring in the statistical analysis of probabilistic functions of Markov chains," *The Annals of Mathematical Statistics*, vol. 41, no. 1, pp. 164–171, 1970.
2. **Año:** 1970.
3. **Base/Revista:** *The Annals of Mathematical Statistics*, vol. 41, no. 1.
4. **DOI:** `[NO VERIFICADO]`.
5. **Dominio de aplicación:** Teoría estadística de cadenas de Markov.
6. **Tipo de HMM:** Discreto (formulación teórica).
7. **Algoritmo de inferencia/entrenamiento:** Técnica de maximización que fundamenta la reestimación EM conocida como Baum–Welch.
8. **Métricas reportadas:** Resultado de convergencia teórica; sin métricas de clasificación.
9. **Naturaleza de datos:** Teoría (sin datos empíricos).
10. **Página/sección de respaldo:** pp. 164–171. Ubicación interna de la ficha: `[NO VERIFICADO]`.

### [3] Wanjala, Makokha y Khamala (2025) — Anomalías aerosol-clima en Kenia

1. **Cita IEEE:** D. W. Wanjala, J. W. Makokha, and G. W. Khamala, "Anomaly detection in selected aerosol optical properties and associated climate variables using a multivariate hidden Markov model: A case study over Kenya," *Open Access Library Journal*, vol. 12, art. e14160, 2025.
2. **Año:** 2025.
3. **Base/Revista:** *Open Access Library Journal*, vol. 12, artículo e14160 (rango de páginas: `[NO VERIFICADO]`).
4. **DOI:** `[NO VERIFICADO]`.
5. **Dominio de aplicación:** Detección de anomalías espacio-temporales en propiedades ópticas de aerosoles (AOD, SSA, AE) y variables climáticas (SAT, tasa de lluvia) en Kenia, 2000–2022.
6. **Tipo de HMM:** Continuo (HMM multivariado con emisiones gaussianas; MHMM).
7. **Algoritmo de inferencia/entrenamiento:** EM (paquete R `depmixS4`), selección de estados por BIC y decodificación con Viterbi.
8. **Métricas reportadas:** BIC = 1380 para el modelo óptimo de 5 estados; 5.08 % de meses clasificados como anómalos; caracterización de estados extremos (AOD hasta 0.40, SSA = 0.81, SAT = 27.6 °C, lluvia = 44.7 mm/mes, SPEI = −1.85).
9. **Naturaleza de datos:** Reales (series mensuales satelitales MODIS, MERRA-2 y TRMM, 2000–2022, validadas con conteos de incendios MODIS y SPEI).
10. **Página/sección de respaldo:** `[NO VERIFICADO]` (la ficha no reporta páginas ni secciones); respaldo localizado por marcadores internos `[cite: 17, 20, 21, 22, 23, 24, 29, 31]`.

### [4] Grammenos (2025) — Ocurrencia de lluvia con HMM homogéneos y no homogéneos

1. **Cita IEEE:** K. Grammenos, "Hidden Markov models and their application in modeling rainfall occurrence," M.S. thesis, Athens University of Economics and Business, 2025.
2. **Año:** 2025.
3. **Base/Revista:** Tesis de Maestría, Athens University of Economics and Business.
4. **DOI:** `[NO VERIFICADO]`.
5. **Dominio de aplicación:** Ocurrencia diaria de lluvia multisitio en el noreste de Brasil (Ceará) y efecto de anomalías climáticas de gran escala.
6. **Tipo de HMM:** Discreto (emisiones Bernoulli por estación bajo independencia condicional).
7. **Algoritmo de inferencia/entrenamiento:** HMM multivariado homogéneo (HHMM), HMM no homogéneo (NHMM) con regresión logística multinomial en las transiciones, covariables en el proceso de observación y modelado por secuencias estacionales independientes; estimación EM/Baum–Welch, selección AIC/BIC y decodificación Viterbi.
8. **Métricas reportadas:** BIC = 24752.58 (HHMM de 4 estados); mejor ajuste con covariable GCM en observación: AIC = 24382.59, BIC = 24700.55; secuencias estacionales independientes: BIC = 24719.46.
9. **Naturaleza de datos:** Reales (10 estaciones, febrero–abril, 90 días/año durante 24 años, T = 2,160 días) más una covariable simulada por el GCM ECHAM 4.5.
10. **Página/sección de respaldo:** `[NO VERIFICADO]` (la ficha no reporta páginas ni secciones); respaldo localizado por marcadores internos `[cite: 76, 88, 115, 119, 120, 124, 125, 127, 130, 131, 132, 136, 141, 143, 146, 150]`.

### [5] Nicosia (2026) — Tubos tropicales de Viterbi

1. **Cita IEEE:** A. Nicosia, "Tropical Viterbi tubes for decoding uncertainty in hidden Markov models," arXiv:2606.17181v1, 2026.
2. **Año:** 2026.
3. **Base/Revista:** arXiv:2606.17181v1 (enviado a *The Annals of Applied Statistics*).
4. **DOI:** `[NO VERIFICADO]`.
5. **Dominio de aplicación:** Cuantificación de incertidumbre de trayectoria completa en HMM; caso aplicado de movimiento animal (murciélagos pescadores, *Myotis vivesi*).
6. **Tipo de HMM:** Continuo (2 estados: forrajeo vs. desplazamiento, con longitud de paso y ángulo de giro).
7. **Algoritmo de inferencia/entrenamiento:** Decodificación de Viterbi más "tubo tropical" definido por tolerancia \(\epsilon \ge 0\) en escala log-odds posterior; recursiones forward–backward en álgebra max-plus con coste O(TK²).
8. **Métricas reportadas:** Validación en 6 escenarios simulados; a tolerancia \(\eta = 0.005\): 28.2 % forrajeo robusto (enriquecimiento 2.25), 17.9 % ambiguo y 53.9 % desplazamiento robusto (enriquecimiento 0.27); 7 viajes y 5,271 ubicaciones reales.
9. **Naturaleza de datos:** Ambos (simulados y reales GPS/acústicos).
10. **Página/sección de respaldo:** `[NO VERIFICADO]` (la ficha no reporta páginas ni secciones); respaldo localizado por marcadores internos `[cite: 37, 38, 41, 42, 43, 52, 55, 56, 57, 60, 61, 64, 67]`.

### [6] Pouzo, Psaradakis y Sola (2025) — Robustez de mezclas ante regímenes HMM

1. **Cita IEEE:** D. Pouzo, Z. Psaradakis, and M. Sola, "On the robustness of mixture models in the presence of hidden Markov regimes with covariate-dependent transition probabilities," *Econometric Theory*, vol. 41, pp. 1229–1243, 2025.
2. **Año:** 2025.
3. **Base/Revista:** *Econometric Theory*, vol. 41, pp. 1229–1243.
4. **DOI:** `[NO VERIFICADO]`.
5. **Dominio de aplicación:** Econometría; estimación de modelos de mezclas finitas cuando el proceso generador es un HMM con transiciones dependientes de covariables.
6. **Tipo de HMM:** Híbrido en el sentido de regímenes discretos de Markov con transiciones dependientes de covariables (no semi-Markoviano); el modelo estimado es una mezcla finita con regímenes i.i.d.
7. **Algoritmo de inferencia/entrenamiento:** Cuasi-máxima verosimilitud (QML), análisis asintótico, divergencia de Kullback–Leibler, identificabilidad vía función característica, estimador *sandwich* para la covarianza y simulaciones Monte Carlo.
8. **Métricas reportadas:** Consistencia y normalidad asintótica de \(\mu^*\), \(\gamma^*\) y \(\sigma^*\) (Teorema 1); evaluación de sesgo por Monte Carlo con \(T \in \{200, 800, 1600, 3200\}\).
9. **Naturaleza de datos:** Simulados (Monte Carlo) y desarrollo teórico; sin datos reales.
10. **Página/sección de respaldo:** pp. 1229–1243 (rango del artículo); página/sección específica: `[NO VERIFICADO]`; respaldo localizado por marcadores internos `[cite: 157, 158, 162, 163, 164, 165, 166, 167, 168, 170]`.

### [7] Tran et al. (2026) — Arquitectura híbrida HMM-LSTM con atención

1. **Cita IEEE:** H. T. Tran, G. T. Tran, H. T. Tran, N. M. Nguyen, and T. M. Phan, "Integrating hidden Markov models and attention-based LSTM framework for regulation compliance in coastal water quality assessment: A case study in Vietnam," Preprints.org, 202605.1728.v1, 2026.
2. **Año:** 2026.
3. **Base/Revista:** Preprints.org, 202605.1728.v1 (preprint; rango de páginas: `[NO VERIFICADO]`).
4. **DOI:** `[NO VERIFICADO]`.
5. **Dominio de aplicación:** Clasificación del cumplimiento normativo de calidad del agua costera en Vietnam (QCVN 10:2023/BTNMT: clases A2 Buena, B1 Moderada, B2 Pobre).
6. **Tipo de HMM:** Continuo (HMM gaussiano de 3 estados) acoplado a una red LSTM de doble rama con atención (arquitectura híbrida).
7. **Algoritmo de inferencia/entrenamiento:** Baum–Welch para el HMM; estados decodificados por Viterbi (*one-hot*) y probabilidades de transición concatenadas con las variables físicas; entrenamiento de la LSTM con atención Bahdanau y partición cronológica 70/15/15.
8. **Métricas reportadas:** Exactitud 74.87 % y F1 64.11 %; HMM solo 44.10 %, LSTM sin atención 68.20 %, ARIMA 70.77 %; *lead time* de 1 a 3 días; *recall* de la clase "Pobre" 14 % con 67 % de precisión; desbalance 75/15/10 (ratio 7.5:1).
9. **Naturaleza de datos:** Reales (1,305 mediciones diarias, 2020–2023, estación Sao Mai–Ben Dinh, Ho Chi Minh City; 5 variables: TSS, pH, TPH, coliformes totales y DO).
10. **Página/sección de respaldo:** `[NO VERIFICADO]` (la ficha no reporta páginas ni secciones); respaldo localizado por marcadores internos `[cite: 173, 174, 175, 176, 177, 178, 179, 181, 182, 183, 184]`.

### [8] Li, Qian y Wang (2013) — Pronóstico de fallas con MG-HMM y FS-LSSVR

1. **Cita IEEE:** X. Li, J. Qian, and G. Wang, "Fault prognostic based on hybrid method of state judgment and regression," *Advances in Mechanical Engineering*, vol. 2013, art. 149562, 2013.
2. **Año:** 2013.
3. **Base/Revista:** *Advances in Mechanical Engineering*, vol. 2013, artículo 149562 (rango de páginas: `[NO VERIFICADO]`).
4. **DOI:** `[NO VERIFICADO]`.
5. **Dominio de aplicación:** Gestión de salud de maquinaria (CBM/PHM); estimación de vida útil remanente (RUL) y diagnóstico de condiciones operativas.
6. **Tipo de HMM:** Continuo (HMM izquierda-derecha con mezclas gaussianas, LR-MG-HMM, 5 estados y 2 componentes) combinado con regresión FS-LSSVR (arquitectura híbrida).
7. **Algoritmo de inferencia/entrenamiento:** Baum–Welch/EM para el HMM; reconocimiento de condición por máxima verosimilitud y extracción de índices de salud con las variables forward \(\alpha_t(i)\); FS-LSSVR con aproximación de Nyström y selección de subconjuntos por entropía cuadrática de Rényi.
8. **Métricas reportadas:** Reconocimiento de condición 99.06 % (FD001), 77.69 % (FD002), 100.00 % (FD003) y 99.87 % (FD004); RUL: MAPE 0.38–0.47 vs. 0.43–0.49 (ANN), BIAS 0.27–0.55 vs. 0.36–0.70, \(MA\alpha\) 0.27–0.37 vs. 0.23–0.29 y convergencia \(C\) 5779.59–11066.95 vs. 6745.52–11270.31.
9. **Naturaleza de datos:** Reales (benchmark de motores turbofán NASA C-MAPSS, subconjuntos FD001–FD004; 26 variables).
10. **Página/sección de respaldo:** `[NO VERIFICADO]` (la ficha no reporta páginas ni secciones); respaldo localizado por marcadores internos `[cite: 315, 317, 318, 319, 321, 322, 323]`.

### [9] Deb, Pandey y Pakray (2026) — Modelo oculto de Markov cuántico

1. **Cita IEEE:** B. Deb, S. Pandey, and P. Pakray, "Quantum hidden Markov model for sequential analysis," *Evolutionary Intelligence*, vol. 19, art. 90, 2026.
2. **Año:** 2026.
3. **Base/Revista:** *Evolutionary Intelligence*, vol. 19, artículo 90 (rango de páginas: `[NO VERIFICADO]`).
4. **DOI:** `[NO VERIFICADO]`.
5. **Dominio de aplicación:** Análisis secuencial; etiquetado gramatical (POS tagging) en inglés y datos bilingües inglés–hindi (*code-mixed*).
6. **Tipo de HMM:** Discreto (QHMM: probabilidades de emisión codificadas en estados cuánticos; matrices de transición convertidas en operadores cuánticos).
7. **Algoritmo de inferencia/entrenamiento:** Codificación de emisiones en superposición de qubits, ortonormalización de Gram–Schmidt para las transiciones y mediciones parciales (*mid-circuit measurement*) con registro *ancilla* como memoria entre pasos temporales; comparación con HMM clásico y Viterbi.
8. **Métricas reportadas:** F1-superior al HMM clásico (valor numérico: `[NO VERIFICADO]`, la ficha no lo reporta); se mencionan exactitud, precisión y *recall* sin cifras.
9. **Naturaleza de datos:** Reales (corpus en inglés y datos bilingües inglés–hindi).
10. **Página/sección de respaldo:** Sección 2.2 (límite del archivo consultado: "solo contenía las páginas iniciales hasta la sección 2.2"); resto de páginas/secciones: `[NO VERIFICADO]`; respaldo localizado por marcadores internos `[cite: 188, 189, 190]`.

### [10] Wang et al. (2026) — StageGuard: estadificación del sueño

1. **Cita IEEE:** J. Wang, Y. Wang, H. Wu, J. Gao, S. Xu, and D. Zou, "StageGuard: Physiologically constrained sleep staging," in *Proc. 32nd ACM SIGKDD Conf. Knowledge Discovery and Data Mining (KDD '26)*, vol. 2, pp. 12267–12278, 2026.
2. **Año:** 2026.
3. **Base/Revista:** *Proceedings of the 32nd ACM SIGKDD Conference on Knowledge Discovery and Data Mining (KDD '26)*, vol. 2, pp. 12267–12278.
4. **DOI:** `[NO VERIFICADO]`.
5. **Dominio de aplicación:** Estadificación del sueño con restricciones fisiológicas; reducción de hipnogramas inválidos en modelos de *deep learning*.
6. **Tipo de HMM:** Semi-Markoviano (decodificador de Viterbi con espacio de estados aumentado por duración \(\tilde{\mathcal{S}} = \{(s,d)\}\), \(D_{max}=10\), duraciones mínimas \(d_{min}(s)\)).
7. **Algoritmo de inferencia/entrenamiento:** Capa de inferencia estructurada agnóstica al *backbone*: regularización de transiciones raras (\(\mathcal{L} = \mathcal{L}_{CE} + \lambda \mathcal{L}_{trans}\), \(\lambda = 0.5\)), módulo de calidad de señal (SQI, \(\beta_t \in [0,1]\)) y decodificación exacta de Viterbi semi-Markoviano con penalización anti-*flip-flop* (\(\gamma=2.0\), \(k=5\)).
8. **Métricas reportadas:** TVR reducida de 3.6–12.3 % a 0.1–0.8 % (anotadores expertos: 2.1 %); FI reducido 56–62 %; exactitud hasta +3.6 a +4.8 pp en SLEEPBRL; sobrecosto <2 ms por sujeto (+6.5 % en U-Sleep); MAE de estadísticas del sueño reducido 59–79 % (latencia REM de 21.3 a 8.7 min); recuperación de diferencias entre subgrupos clínicos (OSA y edad).
9. **Naturaleza de datos:** Reales (4 datasets: AccuSleep EEG/EMG en ratones, Sleep-Accel, SHHS y SLEEPBRL; validación LOSO sobre 6 *backbones*).
10. **Página/sección de respaldo:** pp. 12267–12278 (rango del artículo); página/sección específica: `[NO VERIFICADO]`; respaldo localizado por marcadores internos `[cite: 325, 326, 327, 328, 329, 330, 331, 332, 333]`.

## 2.3 Tabla comparativa de trabajos previos

| Ref. | Estudio | Dominio | Tipo de HMM | Inferencia / entrenamiento | Datos | Métricas clave |
|---|---|---|---|---|---|---|
| [1] | Rabiner (1989) | Voz / ASR (revisión) | Discreto (marco general) | Forward–Backward, Viterbi, Baum–Welch | No aplica | Sin métricas propias |
| [2] | Baum et al. (1970) | Teoría estadística | Discreto | EM / Baum–Welch | Teoría | Convergencia teórica |
| [3] | Wanjala et al. (2025) | Aerosoles y clima (Kenia) | Continuo (gaussiano multivariado) | EM, BIC, Viterbi | Reales 2000–2022 | BIC = 1380; 5.08 % meses anómalos |
| [4] | Grammenos (2025) | Lluvia (Ceará, Brasil) | Discreto (Bernoulli) | EM/Baum–Welch, AIC/BIC, Viterbi | Reales + covariable GCM | BIC = 24700.55 (mejor); AIC = 24382.59 |
| [5] | Nicosia (2026) | Movimiento animal / incertidumbre | Continuo (2 estados) | Viterbi + tubo tropical (max-plus O(TK²)) | Ambos (simulación + GPS/audio) | Enriquecimiento 2.25 / 0.27; 28.2 % / 17.9 % / 53.9 % |
| [6] | Pouzo et al. (2025) | Econometría / robustez | Híbrido (regímenes discretos con transiciones dependientes de covariables) | QML asintótico y Monte Carlo | Simulados (teoría) | Consistencia y normalidad asintótica; T ∈ {200, 800, 1600, 3200} |
| [7] | Tran et al. (2026) | Calidad de agua (Vietnam) | Continuo (gaussiano 3 estados) + LSTM | Baum–Welch, Viterbi, LSTM con atención | Reales (1,305) | Exactitud 74.87 %; F1 64.11 % |
| [8] | Li et al. (2013) | RUL / PHM (C-MAPSS) | Continuo (LR-MG-HMM) + FS-LSSVR | Baum–Welch/EM, forward, regresión | Reales (FD001–FD004) | Condición 77.69–100 %; MAPE 0.38–0.47; BIAS 0.27–0.55 |
| [9] | Deb et al. (2026) | POS tagging / QHMM | Discreto (cuántico) | QHMM, mediciones parciales, Viterbi clásico | Reales (inglés e inglés–hindi) | F1 superior al HMM clásico (sin cifra) |
| [10] | Wang et al. (2026) | Estadificación del sueño | Semi-Markoviano | Viterbi semi-Markoviano + DL con restricciones | Reales (4 datasets, LOSO) | TVR 0.1–0.8 %; FI −56 a −62 %; MAE −59 a −79 % |

**Lectura de la tabla.** Se observa una clara concentración en HMM continuos con emisiones gaussianas y en el ciclo "EM/Baum–Welch → Viterbi" ([3], [7], [8]); los HMM discretos aparecen en aplicaciones con observaciones categóricas o binarias ([4], [9]) y solo un trabajo emplea un formalismo semi-Markoviano ([10]). La naturaleza de los datos es mayoritariamente real ([3], [4], [7], [8], [9], [10]); los estudios con componente simulada ([5], [6]) la usan para validar propiedades metodológicas, no para comparar reglas de decodificación. Las métricas no son conmensurables entre estudios, lo que refuerza la necesidad de un protocolo común de evaluación.

## 2.4 Vacío identificado en la literatura y justificación del estudio D5a

La revisión muestra tres patrones convergentes. Primero, **los trabajos aplicados entrenan y evalúan sobre los mismos datos** (o sobre datos reales sin un contraste pareado contra baselines), de modo que el efecto de la estructura temporal del HMM queda confundido con el de la estimación de parámetros ([3], [4], [7], [8], [10]). Segundo, **las métricas son heterogéneas** —BIC/AIC, exactitud/F1, MAPE/BIAS, tasas de violación de transiciones, enriquecimiento— y rara vez se reporta la distribución completa de los resultados por réplica ([3]–[10]). Tercero, **solo los trabajos metodológicos** ([1], [2], [5], [6]) discuten fundamentos, incertidumbre o robustez, pero ninguno aborda la comparación controlada de reglas de decodificación con parámetros fijos en un escenario ordinal de pocos estados.

En consecuencia, el vacío que justifica el estudio **D5a** es acotado y verificable: *no existe evidencia controlada sobre si la estructura temporal de un HMM, con \(A\), \(B\) y \(\pi\) fijos, mejora la decodificación frente a reglas simples cuando las observaciones son ordinales, el número de estados es pequeño y las secuencias se evalúan de forma pareada*. Los estudios aplicados no permiten aislar ese efecto porque confunden modelo y aprendizaje; los estudios metodológicos no lo abordan porque su objeto es la incertidumbre ([5]), la robustez asintótica ([6]) o la exposición algorítmica ([1], [2]). D5a cubre exactamente esa brecha mediante inferencia con parámetros fijos, comparación contra baselines simples y reporte de resultados por secuencia y por réplica, sin introducir entrenamiento (Baum–Welch queda explícitamente fuera del núcleo y solo se contemplaría como extensión D5b).

## Referencias

[1] L. R. Rabiner, "A tutorial on hidden Markov models and selected applications in speech recognition," *Proceedings of the IEEE*, vol. 77, no. 2, pp. 257–286, Feb. 1989. DOI: `[NO VERIFICADO]`.

[2] L. E. Baum, T. Petrie, G. Soules, and N. Weiss, "A maximization technique occurring in the statistical analysis of probabilistic functions of Markov chains," *The Annals of Mathematical Statistics*, vol. 41, no. 1, pp. 164–171, 1970. DOI: `[NO VERIFICADO]`.

[3] D. W. Wanjala, J. W. Makokha, and G. W. Khamala, "Anomaly detection in selected aerosol optical properties and associated climate variables using a multivariate hidden Markov model: A case study over Kenya," *Open Access Library Journal*, vol. 12, art. e14160, 2025. DOI: `[NO VERIFICADO]`.

[4] K. Grammenos, "Hidden Markov models and their application in modeling rainfall occurrence," M.S. thesis, Athens University of Economics and Business, 2025. DOI: `[NO VERIFICADO]`.

[5] A. Nicosia, "Tropical Viterbi tubes for decoding uncertainty in hidden Markov models," arXiv:2606.17181v1, 2026. DOI: `[NO VERIFICADO]`.

[6] D. Pouzo, Z. Psaradakis, and M. Sola, "On the robustness of mixture models in the presence of hidden Markov regimes with covariate-dependent transition probabilities," *Econometric Theory*, vol. 41, pp. 1229–1243, 2025. DOI: `[NO VERIFICADO]`.

[7] H. T. Tran, G. T. Tran, H. T. Tran, N. M. Nguyen, and T. M. Phan, "Integrating hidden Markov models and attention-based LSTM framework for regulation compliance in coastal water quality assessment: A case study in Vietnam," Preprints.org, 202605.1728.v1, 2026. DOI: `[NO VERIFICADO]`.

[8] X. Li, J. Qian, and G. Wang, "Fault prognostic based on hybrid method of state judgment and regression," *Advances in Mechanical Engineering*, vol. 2013, art. 149562, 2013. DOI: `[NO VERIFICADO]`.

[9] B. Deb, S. Pandey, and P. Pakray, "Quantum hidden Markov model for sequential analysis," *Evolutionary Intelligence*, vol. 19, art. 90, 2026. DOI: `[NO VERIFICADO]`.

[10] J. Wang, Y. Wang, H. Wu, J. Gao, S. Xu, and D. Zou, "StageGuard: Physiologically constrained sleep staging," in *Proc. 32nd ACM SIGKDD Conf. Knowledge Discovery and Data Mining (KDD '26)*, vol. 2, pp. 12267–12278, 2026. DOI: `[NO VERIFICADO]`.
