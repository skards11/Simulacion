# Skills & Reglas de Desarrollo: HMM Riesgo de Incendio Forestal (Local Windows)

## 1. Contexto del Dominio y Modelo Matemático
Sistema de evaluación de riesgo de incendio forestal con Modelo Oculto de Markov (HMM).

- **Estados Ocultos ($S$):** `Riesgo Bajo`, `Riesgo Moderado`, `Riesgo Extremo`
- **Observaciones ($O$):** `Hum. Alta`, `Hum. Media`, `Hum. Baja`
- **Algoritmos clave:** Generación de secuencias (Monte Carlo) y Algoritmo de Viterbi para decodificación.

---

## 2. Entorno de Ejecución (Windows Local)
- El proyecto corre directamente en Windows con Python 3.11+.
- La ejecución principal es en **Jupyter Notebook**: `AE2_HMM.ipynb`.
- Usar el entorno virtual `.venv` del proyecto.
- Dependencias registradas en `requirements.txt` (incluye `jupyter` e `ipykernel`).
- `main.py` se mantiene como ejecución alternativa por consola.

---

## 3. Estructura del Proyecto
```text
/
├── .venv/
├── AE2_HMM.ipynb          # Notebook principal de ejecución
├── src/
│   ├── __init__.py
│   ├── hmm_model.py       # Definición de matrices A, B, pi y validación estocástica
│   ├── simulation.py      # Simulación Monte Carlo y Viterbi
│   └── utils.py           # Gráficos y tablas de resultados
├── tests/
│   └── test_hmm.py        # Pruebas con pytest
├── main.py                # Punto de entrada
├── requirements.txt
└── OPENCODE.md