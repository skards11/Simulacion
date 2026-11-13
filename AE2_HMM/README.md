# AE2_HMM — experimento M0/M1/M2

Comparación didáctica de decodificación con un Modelo Oculto de Markov (HMM)
de tres estados latentes y tres observaciones ordinales de humedad.

**Estado:** versión final `v1.0-final`. Las decisiones D1–D8 están registradas
en `decisiones.md`. El equipo aprobó el 2026-11-11 las cifras del experimento
D7, ejecutado con T = 500, N = 2000 y
`np.random.SeedSequence(42).spawn(2000)`. Los resultados están en
`outputs/experimento_hmm_resumen.*`; todas las cifras son simuladas. El
artículo final es `manuscrito_final.tex` / `manuscrito_final.pdf` y su guion de
sustentación está en `docs/guion_pitch.md`.

## Aviso sobre el código legado

> La carpeta `legacy/` contiene una simulación exploratoria previa con variables continuas y reglas de negocio de incendios. El protocolo formal del artículo científico se implementa en la raíz bajo las especificaciones D1–D7.

El código de la raíz no usa porcentajes de humedad, focos de incendio ni
alertas de quema. Esos artefactos se conservan únicamente como historia del
proyecto en `legacy/`.

## Estructura

```text
/
├── main.py                     # Ejecutor del experimento M0/M1/M2
├── src/
│   ├── hmm_model.py            # HMM, Forward, Forward–Backward y Viterbi
│   ├── simulation.py           # M0/M1/M2, métricas y estadística
│   └── __init__.py
├── tests/
│   └── test_protocol.py        # 15 pruebas del experimento
├── scripts/
│   ├── report_d4.py            # Tablas y figura desde el JSON
│   ├── reproduce.py            # Reproducción completa + manifiesto SHA-256
│   ├── build_paper_assets.py   # Figuras 300 dpi, tabla resumen y hashes
│   └── audit_manuscript.py     # Auditoría de cifras, resumen y páginas
├── outputs/                    # Resultados simulados del experimento
│   └── MANIFEST.txt            # SHA-256 de los artefactos generados
├── docs/
│   ├── guion_pitch.md          # Guion del video de sustentación
│   ├── auditoria_final.md      # Tabla de verificación numérica
│   └── seccion_2_estado_del_arte.md
├── legacy/                     # Simulación exploratoria anterior (aislada)
├── materiales/                 # Caso didáctico y plantilla
├── manuscrito_final.tex        # Artículo final (fuente LaTeX)
├── manuscrito_final.pdf        # Artículo final compilado
└── decisiones.md               # Bitácora de decisiones D1–D8
```

## Manuscrito final

Artículo final en LaTeX (`manuscrito_final.tex`) y PDF (`manuscrito_final.pdf`),
con 18 páginas totales: 14 de cuerpo (sin contar Referencias ni Anexos), 10
referencias IEEE, figuras a 300 dpi y dos anexos (auditoría numérica y guion del
pitch). Todas las cifras provienen de `outputs/experimento_hmm_resumen.json` y
están rotuladas como simuladas.

Para recompilar el PDF sin una instalación completa de TeX:

```powershell
tectonic -X compile manuscrito_final.tex
```

Verificación automatizada de cifras, resumen y extensión:

```powershell
python scripts/audit_manuscript.py
```

## Video de Sustentación (Pitch)

**Duración:** 2:30 min · **Formato:** MP4, 1920×1080, 16:9 horizontal.
**Enlace:** [INSERTAR_URL_VIDEO_PITCH]

| Integrante | Rol en el pitch | Correo institucional |
|---|---|---|
| Oscar Alonso De la Pava Suarez | Bloques 1–3: contexto y modelo | oscar.delapava@est.iudigital.edu.co |
| Anderson Jesus Ospina Cardona | Bloques 4–5: experimento y resultados | anderson.ospina@est.iudigital.edu.co |
| Kevin Andrés Valencia Daza | Bloques 6–7: aporte y cierre | kevin.valencia@est.iudigital.edu.co |

El guion completo, con textos exactos, tiempos y notas de producción, está en
[`docs/guion_pitch.md`](docs/guion_pitch.md) y como Anexo B del manuscrito final.

## Entorno verificado

- **Sistema:** Windows (64 bits).
- **Python:** `3.12.10` (MSC v.1943 64 bit).
- **Dependencias:** versiones exactas fijadas en `requirements.txt`
  (`numpy==2.5.4`, `scipy==1.18.1`, `matplotlib==3.11.2`,
  `pandas==3.1.0`, `pytest==9.2.0`).

## Instalación

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Reproducción con un solo comando

```powershell
python scripts/reproduce.py
```

Ese comando ejecuta, en orden y sin intervención manual:

1. Las pruebas unitarias (`python -m pytest -q`).
2. El experimento completo con T = 500, N = 2000 y
   `np.random.SeedSequence(42).spawn(2000)`.
3. La generación de tablas CSV/Markdown y de la figura comparativa.
4. El manifiesto `outputs/MANIFEST.txt` con el SHA-256 de cada artefacto.

Salida esperada de las pruebas: `15 passed`. El experimento completo tarda
varios minutos. La ejecución es determinista: repetirla reproduce los mismos
archivos y los mismos hashes.

### Esquema de semillas

La semilla maestra es fija (`42`). Se usa una única llamada
`np.random.SeedSequence(42).spawn(2000)`; cada réplica recibe una secuencia de
semilla independiente y de ella deriva su propio generador. No se reutiliza la
misma semilla entre réplicas.

### Artefactos generados en `outputs/`

| Archivo | Contenido |
|---|---|
| `experimento_hmm_resumen.json` | Fuente completa: metadatos, métricas, contrastes, criterios, matrices de confusión y valores por secuencia. |
| `experimento_hmm_resumen.md` | Resumen legible de métricas, contrastes, criterios y matrices. |
| `experimento_hmm_metricas.csv` | Media, desviación estándar, mínimo, máximo, mediana, cuartiles, RIC e IC percentil por modelo y métrica. |
| `experimento_hmm_confusion.csv` | Matrices de confusión agregadas en conteos y proporciones por fila. |
| `experimento_hmm_comparaciones.csv` | Wilcoxon pareado, p crudo, p Holm y Delta de Cliff. |
| `experimento_hmm_comparativa.png` | Figura comparativa (300 dpi) con barras, cajas y matrices de confusión. |
| `fig_metricas_300dpi.png` | Figura 2 del manuscrito: macro-F1 por escenario con IC 95 % (300 dpi). |
| `fig_confusion_300dpi.png` | Figura 3 del manuscrito: matrices de confusión normalizadas (300 dpi). |
| `tabla_resumen_manuscrito.csv` | Tabla 3 del manuscrito: media, DE, mínimo, máximo e IC 95 % por escenario y métrica. |
| `auditoria_manuscrito.json` | Auditoría legible por máquina: 66 cifras, resumen, páginas, dpi y hashes. |
| `MANIFEST.txt` | Hashes SHA-256 de los artefactos anteriores. |

## Pruebas

```powershell
python -m pytest -q
```

## Ejecución por pasos (opcional)

```powershell
python main.py --save outputs/experimento_hmm_resumen.json
python scripts/report_d4.py --input outputs/experimento_hmm_resumen.json
```

El experimento completo puede tardar varios minutos. La B alterada usa
`m = 0.5` de forma definitiva; M2 decodifica con la matriz B nominal.

## Diseño del experimento

- **Unidad independiente:** la secuencia, no el paso de tiempo.
- **Diseño pareado:** M0, M1 y M2 usan las mismas réplicas y los mismos
  estados latentes.
- **M0:** Viterbi logarítmico con A, B y π nominales.
- **M1:** baseline puntual sin memoria temporal,
  `argmax_i B[i, O_t]`, sobre las observaciones nominales.
- **M2:** Viterbi nominal sobre observaciones generadas con
  `B(m) = (1 - m)B + mU`, con `m = 0.5`.
- **Métrica principal:** Macro-F1 por secuencia, agregada con media,
  desviación estándar, mediana, RIC e IC percentil 2.5–97.5.
- **Contrastes:** Wilcoxon bilateral pareado con corrección de
  Holm-Bonferroni y Delta de Cliff.
- **Semillas:** `np.random.SeedSequence(42).spawn(2000)`; cada réplica usa
  una secuencia de semilla independiente.

## Limitaciones

- Los estados son etiquetas didácticas, no variables físicas.
- La humedad es ordinal; no se usan porcentajes ni umbrales inventados.
- No se afirma validez ecológica ni superioridad general del HMM.
- La B alterada usa `m = 0.5`; el escenario es simulado y exploratorio.
