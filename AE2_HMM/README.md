# AE2_HMM — protocolo D4

Comparación didáctica de decodificación con un Modelo Oculto de Markov (HMM)
de tres estados latentes y tres observaciones ordinales de humedad.

**Estado:** anteproyecto. Las decisiones D1–D6 están registradas en
`decisiones.md` y el protocolo D4 ya se ejecutó. Los resultados están en
`outputs/protocolo_d4_resumen.*`; todas las cifras son simuladas.

## Aviso sobre el código legado

> La carpeta `legacy/` contiene una simulación exploratoria previa con variables continuas y reglas de negocio de incendios. El protocolo formal del artículo científico se implementa en la raíz bajo las especificaciones D1–D6.

El código de la raíz no usa porcentajes de humedad, focos de incendio ni
alertas de quema. Esos artefactos se conservan únicamente como historia del
proyecto en `legacy/`.

## Estructura

```text
/
├── main.py                 # Ejecutor del protocolo D4
├── src/
│   ├── hmm_model.py        # HMM, Forward, Forward–Backward y Viterbi
│   ├── simulation.py       # M0/M1/M2, métricas y experimento D4
│   └── __init__.py
├── tests/
│   └── test_protocol.py    # Pruebas del protocolo
├── scripts/
│   └── report_d4.py        # Tablas y figura desde el JSON
├── outputs/                # Resultados simulados del protocolo D4
├── legacy/                 # Simulación exploratoria anterior (120 días)
├── materiales/             # Caso didáctico y plantilla
├── manuscrito_anteproyecto.md
└── decisiones.md           # Bitácora de decisiones D1–D6
```

## Manuscrito

Borrador de anteproyecto: `manuscrito_anteproyecto.md`. Incluye resultados simulados, limitaciones, declaración de uso de IA y referencias marcadas como pendientes de verificación.

## Instalación

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Pruebas

```powershell
python -m pytest -q
```

## Ejecución del protocolo

Prueba de humo (rápida, no es un resultado del protocolo):

```powershell
python main.py --quick
```

Protocolo completo D4 (`T = 500`, `N = 2000`):

```powershell
python main.py
```

Opciones útiles:

```powershell
python main.py --T 500 --N 2000 --seed 20261109 --bootstrap 1000
python main.py --decoder viterbi
python main.py --save outputs/protocolo_d4_resumen.json
```

El protocolo completo puede tardar varios minutos. El escenario secundario
usa una B alterada por mezcla con la distribución uniforme; el valor de
mezcla es **provisional** (`PROVISIONAL_ALTERED_MIXING = 0.5`) y debe
registrarse antes de reportar ese escenario.

Para generar tablas CSV/Markdown y la figura de métricas a partir del JSON:

```powershell
python scripts/report_d4.py --input outputs/protocolo_d4_resumen.json
```

## Diseño del experimento

- **Unidad independiente:** la secuencia, no el paso de tiempo.
- **Diseño pareado:** M0, M1 y M2 reciben las mismas observaciones y se
  comparan contra los mismos estados latentes.
- **M0:** umbral determinista sobre la humedad actual.
- **M1:** baseline con la ley observable exacta y prior estacionario de A.
- **M2:** HMM completo con A, B y π.
- **Métrica principal:** macro-F1 por secuencia, agregada con media,
  desviación estándar e IC por bootstrap de secuencias.
- **Métricas secundarias:** recall de `s3` y exactitud.
- **Semillas:** una semilla distinta por secuencia, derivada de una semilla
  maestra y registrada en el resultado.

## Limitaciones

- Los estados `s1`, `s2`, `s3` son etiquetas puras, no variables físicas.
- La humedad es ordinal; no se usan porcentajes ni umbrales inventados.
- No se afirma validez ecológica ni superioridad general del HMM.
- Los resultados del escenario con B alterada dependen del valor de mezcla
  que se apruebe.
