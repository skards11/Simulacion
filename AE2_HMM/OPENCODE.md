# Reglas de desarrollo — AE2_HMM (protocolo D4)

## 1. Contexto

Comparación didáctica de decodificación con un HMM de tres estados latentes
(`s1`, `s2`, `s3`) y tres observaciones ordinales de humedad (`Alta`, `Media`,
`Baja`). Los estados son etiquetas puras (D3.1); la humedad es ordinal y no se
convierten a porcentajes (D3.2). Un paso es una ocasión de observación (D3.3).

El proyecto está en fase de **anteproyecto**: las decisiones D1–D6 están
registradas, pero no se han ejecutado los experimentos del protocolo.

## 2. Entorno

- Windows, Python 3.11+.
- Entorno virtual `.venv`.
- Dependencias en `requirements.txt`.
- Pruebas: `python -m pytest -q`.
- Protocolo: `python main.py --quick` (humo) o `python main.py` (completo).

## 3. Estructura

```text
/
├── main.py                 # Ejecutor del protocolo D4
├── src/
│   ├── hmm_model.py        # HMM, Forward, Forward–Backward, Viterbi
│   ├── simulation.py       # M0/M1/M2, macro-F1 y experimento D4
│   └── __init__.py
├── tests/test_protocol.py
├── outputs/                # Resultados del protocolo (vacío por ahora)
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
- M0, M1 y M2 deben recibir las mismas secuencias (diseño pareado).
- La unidad independiente es la secuencia; agregar métricas por secuencia.
- Registrar semillas y no reutilizar la misma semilla entre réplicas.
- Reportar macro-F1 como métrica principal; recall de `s3` y exactitud como
  secundarias.
- Rotular toda cifra como simulada. No afirmar validez ecológica ni
  superioridad general del HMM.

## 5. Legacy

`legacy/` es una copia congelada de la versión anterior. No se refactoriza
junto con la raíz ni se mezcla con el protocolo. Cualquier cambio histórico
debe documentarse en `decisiones.md`.
