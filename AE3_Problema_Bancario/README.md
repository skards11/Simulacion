# AE3 — Problema bancario

Simulación de eventos discretos del desempeño de los cajeros del **Banco de
Colombia** para operaciones de retiro y consignación/pago. El laboratorio pide
al menos 10 réplicas de un día de 8 horas, comparar configuraciones de cajas y
decidir cuántas cajas deberían ser exclusivas para retiros y cuántas para pagos.

> **Aviso:** todas las cifras de este proyecto son simuladas. No provienen de
> datos reales del banco. Los supuestos y criterios de decisión están
> documentados para que puedan defenderse en el informe.

## Inicio rápido

```powershell
# DESDE LA CARPETA AE3_Problema_Bancario
python -m pytest -q
python main.py --replicas 30 --duration 480 --seed 42
python scripts/build_report_assets.py
```

O todo en un solo comando:

```powershell
python scripts/reproduce.py
```

Los resultados quedan en `outputs/`. El resumen listo para citar está en
[`outputs/resumen_ejecucion.md`](outputs/resumen_ejecucion.md).

## Modelo implementado

- **Llegadas:** se sortea primero la acción (70 % retiro, 30 % pago), luego el
  tipo de usuario con las probabilidades de la Tabla 2 y finalmente el tiempo
  entre llegadas con una exponencial cuya media depende del tipo (Tabla 1).
- **Servicio:** tiempo exponencial con media según acción y tipo (Tabla 1).
- **Cajeros:** cada caja es un servidor M/M/1 independiente con cola FIFO
  propia.
- **Asignación:** entre las cajas que pueden atender la acción, se elige una
  libre al azar; si todas están ocupadas, se elige la cola más corta con
  desempate aleatorio. Así se evita favorecer siempre al cajero 0.
- **Cierre:** se generan llegadas hasta el minuto 480 y luego se drena el
  sistema. Todos los clientes que alcanzaron a llegar terminan su servicio,
  aunque el reloj supere las 8 horas.
- **Diseño pareado:** dentro de una réplica, todas las configuraciones reciben
  exactamente las mismas llegadas, tipos y tiempos de servicio. Solo cambia la
  asignación a cajeros. Esto reduce el ruido y permite comparar configuraciones
  de forma justa.

### Configuraciones evaluadas

| Clave | Configuración | Cajas |
|---|---|---:|
| `mixto_3` | 3 cajas mixtas (situación actual) | 3 |
| `retiro_1_pago_2` | 1 caja de retiros + 2 de pagos | 3 |
| `retiro_2_pago_1` | 2 cajas de retiros + 1 de pagos | 3 |
| `mixto_4` | 4 cajas mixtas | 4 |
| `retiro_2_pago_2` | 2 cajas de retiros + 2 de pagos | 4 |
| `retiro_3_pago_1` | 3 cajas de retiros + 1 de pagos | 4 |
| `retiro_1_pago_3` | 1 caja de retiros + 3 de pagos | 4 |

La carga ofrecida total es de **1.334 servidores**. Con 3 cajas la utilización
teórica global es 44.5 %; con 4 cajas, 33.3 %. Todas las configuraciones son
estables (`rho < 1`), pero las especializadas pueden dejar un grupo con una
utilización muy alta y esperas largas.

## Resultados principales (30 réplicas, semilla 42)

| Configuración | Cajas | Espera prom. (min) | Espera retiros | Espera pagos | P90 | Util. máx. | ¿Cumple criterios? |
|---|---:|---:|---:|---:|---:|---:|:---:|
| 4 cajas mixtas | 4 | 0.21 | 0.21 | 0.22 | 0.02 | 36.5 % | Sí |
| 2 retiros + 2 pagos | 4 | 0.66 | 0.57 | 0.86 | 1.69 | 38.2 % | Sí |
| **3 cajas mixtas (actual)** | **3** | **0.78** | **0.84** | **0.66** | **2.09** | **46.9 %** | **Sí** |
| 3 retiros + 1 pago | 4 | 2.66 | 0.09 | 8.53 | 10.19 | 61.9 % | No |
| 2 retiros + 1 pago | 3 | 2.98 | 0.55 | 8.53 | 11.27 | 61.9 % | No |
| 1 retiro + 3 pagos | 4 | 3.94 | 5.55 | 0.16 | 13.67 | 66.0 % | No |
| 1 retiro + 2 pagos | 3 | 4.16 | 5.55 | 0.89 | 14.05 | 66.0 % | No |

**Lectura:** la configuración actual de 3 cajas mixtas cumple los criterios de
servicio y no requiere un cuarto cajero. Las configuraciones exclusivas
mejoran un tipo de operación a costa de castigar fuertemente el otro: con
2 retiros + 1 pago, la espera de pagos sube a 8.53 min; con 1 retiro + 2 pagos,
la espera de retiros sube a 5.55 min. Por eso la recomendación costo-efectiva
es **mantener 3 cajas mixtas (0 exclusivas de retiro y 0 exclusivas de pago)**.
Si el banco exige especializar las 3 cajas existentes, la opción más balanceada
es 1 retiro + 2 pagos, pero no cumple todos los criterios. Si está dispuesto a
crear una cuarta caja y especializar, la mejor opción es 2 retiros + 2 pagos.

Estas cifras se regeneran con `python scripts/reproduce.py` y se explican en
[`outputs/resumen_ejecucion.md`](outputs/resumen_ejecucion.md).

`outputs/clientes.csv` es la salida cruda por cliente (~8 MB). No se versiona
por tamaño: se regenera con el mismo comando. Por eso su hash puede aparecer en
`outputs/MANIFEST.txt` aunque el archivo no esté en un clon limpio.

## Estructura

```text
AE3_Problema_Bancario/
├── main.py                          # Ejecuta el experimento y guarda CSV/JSON crudos
├── src/
│   ├── bank_simulation.py           # Datos, motor de eventos y métricas
│   ├── analysis.py                  # Resúmenes, IC 95 %, tablas de los 5 puntos
│   └── __init__.py
├── scripts/
│   ├── build_report_assets.py       # Tablas derivadas, figuras 300 dpi y resumen MD
│   └── reproduce.py                 # pytest + simulación + tablas + manifiesto SHA-256
├── tests/
│   └── test_simulation.py           # 12 pruebas del modelo y la reproducibilidad
├── outputs/
│   ├── resumen_ejecucion.md         # Resumen con cifras para el documento
│   ├── punto1_cajeros.csv
│   ├── punto2_usuarios_tipo.csv
│   ├── punto3_replicas.csv
│   ├── punto3_minimos.csv
│   ├── punto4_criterios.csv
│   ├── punto4_comparacion.csv
│   ├── punto5_configuracion.csv
│   ├── decisiones.json
│   ├── figuras/                     # 6 figuras a 300 dpi
│   └── MANIFEST.txt                 # SHA-256 de los artefactos (tras reproduce.py)
├── docs/
│   ├── guia_documento.md            # Guía paso a paso para elaborar el informe
│   ├── guion_video_pitch.md         # Guion y tiempos del video de 3 minutos
│   └── plantilla_documento.md       # Esqueleto para copiar a Word
├── requirements.txt
├── pytest.ini
└── README.md
```

## Entregables del laboratorio

El enunciado pide un documento con introducción, metodología, resultados y
conclusiones, además del código, los datos en CSV, un video de sustentación
y el repositorio en GitHub. La guía detallada está en
[`docs/guia_documento.md`](docs/guia_documento.md) e incluye:

- estructura sección por sección y qué archivo de `outputs/` usar en cada punto;
- cómo redactar los cinco puntos solicitados sin copiar código;
- criterios de decisión y análisis de sensibilidad;
- mapeo contra la rúbrica de 100 puntos;
- guion del video pitch de 3 minutos y checklist del repositorio;
- lista de verificación antes de entregar.

El esqueleto editable está en
[`docs/plantilla_documento.md`](docs/plantilla_documento.md) y el guion del
video en [`docs/guion_video_pitch.md`](docs/guion_video_pitch.md).

## Métricas calculadas

- Tiempo promedio, desviación estándar, mediana, P50, P90, P95 y máximo de
  espera.
- Tiempo promedio de servicio y de permanencia en el sistema.
- `Lq` y `L` por integración temporal durante las 8 horas.
- Utilización promedio y máxima por caja.
- Fracción de clientes con espera > 5, > 10 y > 15 minutos.
- Conteos por acción y tipo de usuario por réplica.
- Intervalos de confianza del 95 % con t de Student para las réplicas.
- Criterios de servicio: espera promedio ≤ 5 min, P90 ≤ 10 min, fracción con
  espera > 10 min ≤ 10 % y utilización máxima ≤ 85 %.

Los criterios son supuestos documentables; si el curso o el banco fija otros,
se cambian en `SLA_DEFAULT` de `src/bank_simulation.py` y se regeneran las
tablas.

## Reproducibilidad

- Semilla maestra: `42`.
- `np.random.SeedSequence(42).spawn(30)`; cada réplica se divide en tres
  secuencias hijas: llegadas, servicios y despacho.
- Misma réplica ⇒ mismas llegadas y mismos servicios en todas las
  configuraciones.
- El comando `python scripts/reproduce.py` ejecuta pruebas, simulación, tablas
  y escribe `outputs/MANIFEST.txt` con el SHA-256 de cada artefacto.

## Pruebas

```powershell
python -m pytest -q
```

Salida esperada: `12 passed`.

## Limitaciones

- No se modelan abandono de cola, prioridades, horarios pico ni cajeros
  electrónicos; el enunciado pide cajas M/M/1 independientes.
- Los tiempos son exponenciales con las medias del enunciado; no se ajustaron
  distribuciones empíricas.
- La asignación a la cola más corta es una política operativa razonable, pero
  no la única posible.
- Las cifras son de una simulación didáctica y no deben presentarse como
  diagnóstico real del banco.
