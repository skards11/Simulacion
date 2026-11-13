# Reglas de desarrollo — AE2_HMM (experimento M0/M1/M2)

## 1. Contexto

Comparación didáctica de decodificación con un HMM de tres estados latentes
(`Riesgo Bajo`, `Riesgo Moderado`, `Riesgo Extremo`) y tres observaciones
ordinales de humedad (`Humedad Alta`, `Humedad Media`, `Humedad Baja`). La
humedad es ordinal y no se convierte a porcentajes. Un paso es una ocasión de
observación.

El proyecto está en fase de **anteproyecto**: las decisiones D1–D8 están
registradas y el experimento vigente ya se ejecutó con resultados simulados,
aprobados por el equipo el 2026-11-11.

## 2. Entorno verificado

- Windows (64 bits), Python **3.12.10** (MSC v.1943 64 bit).
- Entorno virtual `.venv`.
- Dependencias con versiones exactas en `requirements.txt`:
  `numpy==2.5.4`, `scipy==1.18.1`, `matplotlib==3.11.2`,
  `pandas==3.1.0`, `pytest==9.2.0`.
- Pruebas: `python -m pytest -q` → `15 passed`.
- Reproducción completa: `python scripts/reproduce.py`.
- Humo: `python main.py --quick` (no genera cifras del protocolo).

## 3. Estructura

```text
/
├── main.py                 # Ejecutor del experimento M0/M1/M2
├── src/
│   ├── hmm_model.py        # HMM, Forward, Forward–Backward, Viterbi
│   ├── simulation.py       # M0/M1/M2, métricas y estadística
│   └── __init__.py
├── tests/test_protocol.py
├── scripts/report_d4.py    # Tablas y figura desde el JSON
├── scripts/reproduce.py    # Reproducción completa + manifiesto SHA-256
├── outputs/                # Resultados simulados del experimento
│   └── MANIFEST.txt        # SHA-256 de los artefactos generados
├── legacy/                 # Simulación exploratoria anterior (120 días)
│   ├── main.py
│   ├── AE2_HMM_legacy.ipynb
│   ├── src/
│   ├── tests/
│   └── outputs/
├── materiales/
├── decisiones.md
├── README.md
└── requirements.txt
```

## 4. Reglas del código de la raíz

- No usar porcentajes de humedad, focos de incendio, alertas de quema ni
  índices de peligro. Eso pertenece a `legacy/`.
- Mantener A, B y π fijos (D5a). No implementar Baum-Welch salvo que el equipo
  active expresamente el anexo D5b.
- M0 es Viterbi logarítmico con A, B y π nominales.
- M1 es el baseline puntual `argmax_i B[i, O_t]`, sin memoria temporal.
- M2 usa Viterbi nominal sobre observaciones generadas con
  `B(m) = (1 - m)B + mU`, con `m = 0.5` definitivo.
- M0, M1 y M2 deben usar las mismas réplicas y los mismos estados latentes.
- La unidad independiente es la secuencia; agregar métricas por secuencia.
- Usar `np.random.SeedSequence(42).spawn(N)` y no reutilizar la misma semilla
  entre réplicas.
- Reportar Macro-F1 como métrica principal, con media, SD, mediana, RIC e IC
  percentil 2.5–97.5.
- Reportar Wilcoxon bilateral pareado con Holm-Bonferroni y Delta de Cliff.
- Rotular toda cifra como simulada. No afirmar validez ecológica ni
  superioridad general del HMM.

## 5. Reproducibilidad

- **Comando único verificado:** `python scripts/reproduce.py`. Ejecuta pruebas,
  experimento completo, tablas/figura y manifiesto SHA-256.
- **Semillas:** `np.random.SeedSequence(42).spawn(2000)`; una secuencia de
  semilla independiente por réplica. No reiniciar ni reutilizar la semilla.
- **Determinismo:** repetir el comando reproduce los mismos archivos y hashes.
- **Artefactos en `outputs/`:**
  - `experimento_hmm_resumen.json` — fuente completa de resultados.
  - `experimento_hmm_resumen.md` — resumen legible.
  - `experimento_hmm_metricas.csv` — métricas agregadas (media, SD, mínimo,
    máximo, mediana, RIC e IC 95 %).
  - `experimento_hmm_confusion.csv` — matrices de confusión.
  - `experimento_hmm_comparaciones.csv` — Wilcoxon, Holm y Cliff.
  - `experimento_hmm_comparativa.png` — figura comparativa a 300 dpi.
  - `MANIFEST.txt` — hashes SHA-256 de los artefactos anteriores.
- No editar a mano los artefactos de `outputs/`; regenerarlos con el comando.

## 6. Legacy

`legacy/` es una copia congelada de la versión anterior. No se refactoriza
junto con la raíz ni se mezcla con el protocolo. Cualquier cambio histórico
debe documentarse en `decisiones.md`.
