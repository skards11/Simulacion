# AE4 — Solución de un problema de parqueaderos

Simulación de eventos discretos del cobro de parqueadero en el **Centro
Comercial Supercentro**. El sistema tiene tres cajeros, cada uno con su propia
fila FIFO, y cuatro tipos de usuario con tiempos de llegada y de servicio
exponenciales. El objetivo es decidir si la operación actual es suficiente o si
conviene cambiar la cantidad de cajeros o la política de filas.

**Asignatura:** Simulación — IUDigital
**Integrantes:** Oscar Alonso De la Pava Suarez, Anderson Jesus Ospina Cardona,
Kevin Andrés Valencia Daza

> Todas las cifras son **simuladas**. El enunciado entrega los parámetros; este
> repositorio construye, verifica, calibra y valida el modelo.

---

## Resultado principal

La configuración actual (3 cajeros, filas independientes) **no cumple** el
criterio de esperas largas: el **12.0 %** de los usuarios espera más de 5
minutos frente al máximo de 10 %.

La recomendación es **mantener los tres cajeros y compartir una sola fila**:

| Métrica | Actual (`indep_3`) | Propuesta (`unica_3`) | Cambio |
|---|---:|---:|---:|
| Espera en cola, Wq | 1.61 min | **0.08 min** | −95.2 % |
| Espera en el sistema, W | 5.15 min | **3.61 min** | −29.8 % |
| Cola promedio, Lq | 0.35 | **0.02** | −95.2 % |
| P(espera > 5 min) | 12.0 % | **0.2 %** | −98.3 % |
| Utilización máxima | 30.2 % | 29.4 % | — |
| Cajeros nuevos | — | **0** | — |

No requiere inversión: la mejora es organizativa. La validación contra M/M/1,
M/G/1 y Erlang C arroja errores inferiores al 3.5 %.

---

## Inicio rápido

Requisitos: Python 3.11 o superior (probado con 3.12.10).

```powershell
cd AE4_Parqueadero
python -m pip install -r requirements.txt

# Pruebas
python -m pytest -q

# Simulación + tablas + figuras + documento Word
python scripts/reproduce.py
```

Si se prefiere paso a paso:

```powershell
python main.py                            # 30 réplicas base, 720 min, semilla 42
python scripts/build_report_assets.py     # tablas, figuras y resumen
python scripts/build_docx.py              # documento Word
```

`main.py` corre primero una simulación piloto de 10 000 minutos para detectar el
calentamiento, estima cuántas réplicas se necesitan para un error relativo del
10 % y luego ejecuta el experimento definitivo. Los resultados quedan en
`outputs/`.

Opciones útiles:

```powershell
python main.py --quick                    # humo: 3 réplicas, 180 min
python main.py --replicas 40 --seed 7
python scripts/reproduce.py --skip-tests
```

---

## Estructura

```text
AE4_Parqueadero/
├── main.py                     # piloto, estimación de réplicas y experimento
├── src/
│   ├── parking_simulation.py   # modelo, escenarios, métricas, warm-up, V&V
│   └── analysis.py             # tablas y pruebas de los cinco puntos
├── scripts/
│   ├── build_report_assets.py  # tablas derivadas, 10 figuras y resumen
│   ├── build_docx.py           # Markdown -> Word (python-docx)
│   └── reproduce.py            # reproducción completa + MANIFEST SHA-256
├── tests/
│   └── test_simulation.py      # 31 pruebas automáticas
├── docs/
│   ├── documento_entrega.md    # documento de entrega (Markdown)
│   ├── documento_entrega.docx  # documento de entrega (Word)
│   └── guion_video_pitch.md    # guion del video, 3:45, tres expositores
├── outputs/                    # datos crudos, tablas, figuras y resumen
└── requirements.txt
```

---

## Modelo

- **Jornada:** 720 minutos (12 h). Se generan llegadas hasta el cierre y luego
  se drena el sistema.
- **Demanda:** 25 % rápidos, 20 % normales, 27.5 % lentos y 27.5 % muy lentos.
  En cada llegada se sortea el tipo y luego el tiempo hasta la siguiente llegada
  (exponencial de 3, 3, 5 y 7 min según el tipo).
- **Servicio:** exponencial de 1, 3, 4 y 6 min según el tipo.
- **Carga ofrecida:** 0.774 erlangs (0.258 por cajero con tres cajeros).
- **Política base:** tres servidores M/M/1 con fila FIFO propia; el usuario
  elige un cajero al azar y no cambia de fila.
- **Extensiones:** fila única (M/G/3), cola más corta, política adaptativa y
  especialización por tipo.
- **Números aleatorios comunes:** dentro de una réplica todos los escenarios
  reciben las mismas llegadas, tipos y servicios; solo cambia la política.
- **Semilla maestra:** 42. **Réplicas finales:** 32. **Calentamiento:** 102 min.

### Escenarios evaluados

| Clave | Cajeros | Política |
|---|---:|---|
| `indep_2` / `indep_3` / `indep_4` / `indep_5` | 2/3/4/5 | Filas independientes, elección aleatoria |
| `indep_3_corta` | 3 | Cola más corta al llegar |
| `indep_3_adaptativa` | 3 | Libre al azar; si todos ocupados, cola más corta |
| `unica_2` / `unica_3` / `unica_4` | 2/3/4 | Fila única compartida |
| `especializado_3` | 3 | 1 cajero para lentos + 2 para rápidos/normales |

### Criterios de decisión

| Criterio | Umbral |
|---|---:|
| Espera promedio en cola, Wq | ≤ 3 min |
| Espera promedio en el sistema, W | ≤ 8 min |
| Longitud promedio de la cola, Lq | ≤ 3 |
| Utilización máxima de un cajero | ≤ 85 % |
| Proporción con espera > 5 min | ≤ 10 % |

---

## Resultados por punto

| Punto | Pregunta | Hallazgo | Evidencia |
|---|---|---|---|
| A | ¿Cajero más rápido y más lento? | 3.5168 vs 3.5633 min; Friedman p = 0.804 (sin diferencias) | `punto1_cajeros.csv`, `fig_cajeros.png` |
| B | ¿Usuarios promedio por tipo? | 39.81 / 31.44 / 41.75 / 43.16 por réplica; χ² p = 0.653 | `punto2_tipos.csv`, `fig_tipos.png` |
| C | ¿Qué estrategia mejora el servicio? | Fila única con 3 cajeros: Wq 1.61 → 0.08 min | `punto3_comparacion.csv`, `fig_escenarios.png` |
| D | ¿El modelo es confiable? | 9/9 verificaciones; errores ≤ 3.5 % vs teoría | `punto4_*.csv`, `fig_validacion.png` |
| E | ¿Hay que eliminar el transitorio? | Corte en 102 min; sesgo inicial −0.51 % en N(t) | `punto5_antes_despues.csv`, `fig_antes_despues.png` |

La comparación completa de los diez escenarios está en
`outputs/punto3_comparacion.csv` y en la sección 3.3 del documento.

---

## Entregables

| Entregable | Archivo |
|---|---|
| Documento (Word) | `docs/documento_entrega.docx` |
| Documento (Markdown) | `docs/documento_entrega.md` |
| Guion del video (3:45, 3 expositores) | `docs/guion_video_pitch.md` |
| Resumen de la corrida | `outputs/resumen_ejecucion.md` |
| Tablas de los cinco puntos | `outputs/punto1_*.csv` … `outputs/punto5_*.csv` |
| Figuras (300 dpi) | `outputs/figuras/*.png` |
| Manifiesto de reproducibilidad | `outputs/MANIFEST.txt` |
| Código | `src/`, `main.py`, `scripts/` |
| Pruebas | `tests/test_simulation.py` |

El documento Word se genera con `python scripts/build_docx.py`. Incluye portada,
índice automático (actualizar con F9 en Word), 17 tablas, 10 figuras, numeración
de páginas y el anexo de código Python comentado. Si el aula virtual exige el
nombre `Apellido_Nombre_problemaParqueadero` o la extensión `.doc`, se renombra
o se guarda una copia desde Word al momento de entregar. El guion del video
reparte el contenido en tres bloques consecutivos: Oscar, Anderson y Kevin.

---

## Reproducibilidad

Todo el experimento depende de la semilla maestra. Con `--seed 42` (valor por
defecto) los resultados son idénticos en cualquier máquina:

```powershell
python scripts/reproduce.py
```

Ese comando ejecuta las pruebas, la simulación, las tablas, las figuras y el
documento, y escribe `outputs/MANIFEST.txt` con el SHA-256 de cada artefacto.
Para verificar que dos corridas coinciden:

```powershell
Get-Content outputs/MANIFEST.txt
```

Principales archivos de salida:

- `outputs/replicas.csv`: una fila por escenario y réplica con las métricas
  globales (32 × 10 = 320 filas).
- `outputs/cajeros.csv`: una fila por escenario, réplica y cajero.
- `outputs/clientes.csv`: una fila por usuario simulado (~50 000).
- `outputs/resultados.json`: metadatos, escenarios, criterios y teoría.
- `outputs/pilot_serie.csv`: serie N(t) de la corrida piloto de 10 000 min.
- `outputs/decisiones.json`: decisión recomendada y pruebas estadísticas.

---

## Mapeo con la rúbrica

| Criterio | Puntaje | Dónde se evidencia |
|---|---:|---|
| Análisis de resultados | 15 | Secciones 3.1–3.6; IC 95 %, percentiles y figuras |
| Medidas de tendencia central | 15 | Sección 3.1; IC 95 % y Friedman |
| Análisis de escenarios | 15 | Sección 3.3; 10 escenarios y decisión |
| Análisis del caso (V&V) | 15 | Sección 3.4; 9/9 pruebas, KS, M/M/1, M/G/1, Erlang C |
| Estado transitorio | 15 | Sección 3.5; corte de 102 min y comparación |
| Puntualidad | 5 | Fecha de entrega |
| Repositorio GitHub | 10 | Pendiente de publicación por decisión del equipo |
| Video | 10 | `docs/guion_video_pitch.md` |

---

## Limitaciones

- Los parámetros provienen del enunciado; no se ajustaron con datos reales.
- No se modelan picos horarios, deserción ni cambio de fila.
- No se incluyen costos salariales; la comparación de cajeros adicionales es
  cualitativa.
- La validación agregada usa la aproximación M/G/1 por cajero, no una solución
  exacta del sistema con llegadas marcadas por tipo.

---

## Estado del repositorio

El proyecto está completo y reproducible en local. **Aún no se ha publicado en
GitHub**; cuando el equipo lo decida, se debe subir la carpeta `AE4_Parqueadero`
con `outputs/` (excepto los archivos ignorados) y verificar que el README y las
rutas de las figuras sigan siendo válidos.
