# Legacy — simulación exploratoria previa

Esta carpeta conserva la versión de 120 días con humedad continua (0–100 %),
focos de incendio simulados, alertas de quema e índice de peligro 0–100.

> La carpeta `legacy/` contiene una simulación exploratoria previa con variables continuas y reglas de negocio de incendios. El protocolo formal del artículo científico se implementa en la raíz bajo las especificaciones D1–D6.

**No es el protocolo del artículo y no produce resultados del protocolo.**
Los archivos se mantienen para trazabilidad histórica; no deben citarse como
evidencia de D4.

## Contenido

- `main.py`: simulación operativa de 120 días.
- `AE2_HMM_legacy.ipynb`: notebook de esa misma versión.
- `src/`: copia congelada del modelo y la simulación exploratoria.
- `tests/test_hmm.py`: pruebas de la versión anterior.
- `outputs/`: figuras y CSV generados por la versión anterior.

## Ejecución (solo histórica)

Desde esta carpeta:

```powershell
cd legacy
python main.py
python -m pytest -q tests
```

La versión legacy usa porcentajes de humedad y reglas de negocio que chocan
con D3.2, D3.3 y D4. No se debe mezclar con el código de la raíz.
