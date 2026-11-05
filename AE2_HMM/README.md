# AE2_HMM

Sistema de evaluación de riesgo de incendio forestal con un Modelo Oculto de Markov (HMM).

## Ejecución principal: Jupyter Notebook

El proyecto se ejecuta en el notebook **`AE2_HMM.ipynb`**, que contiene la simulación, la decodificación de Viterbi, las métricas, las tablas y los gráficos.

### 1. Crear un entorno virtual limpio

```powershell
python -m venv .venv
```

### 2. Activarlo (Windows PowerShell)

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Instalar las dependencias

```powershell
pip install -r requirements.txt
```

### 4. Registrar el kernel del entorno (opcional, recomendado)

```powershell
python -m ipykernel install --user --name ae2-hmm --display-name "Python (AE2 HMM)"
```

### 5. Abrir Jupyter y ejecutar el notebook

```powershell
jupyter notebook AE2_HMM.ipynb
```

También puede abrirse con JupyterLab o VS Code seleccionando el kernel del `.venv`.
Ejecute las celdas en orden con **Run All**. Los resultados se guardan en `outputs/`.

## Ejecución alternativa por consola

```powershell
python main.py
```

## Pruebas

```powershell
python -m pytest -q
```

## Estructura

```text
/
├── AE2_HMM.ipynb          # Notebook principal
├── src/
│   ├── hmm_model.py       # Matrices A, B, pi, Viterbi y forward-backward
│   ├── simulation.py      # Simulación Monte Carlo y métricas
│   └── utils.py           # Gráficos, tablas y reporte
├── tests/test_hmm.py      # Pruebas con pytest
├── main.py                # Punto de entrada alternativo
├── requirements.txt
└── outputs/               # Figuras y CSV generados
```
