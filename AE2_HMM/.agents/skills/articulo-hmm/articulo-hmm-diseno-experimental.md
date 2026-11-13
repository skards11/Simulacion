---
name: articulo-hmm-diseno-experimental
description: Diseña, audita y redacta la sección de Diseño experimental de un artículo sobre HMM con comparación baseline, control de parámetros fijados vs. aprendidos, auditoría de etiquetas y decisión humana.
---

# Diseño Experimental en Artículos sobre HMM

## Preparación
Leer las decisiones aprobadas del proyecto (problema, formalización de S, A, B, pi y régimen D5a/D5b) y el código disponible. Adaptar la redacción técnica a nivel de quinto semestre. Si falta plantilla editorial, usar estructura académica estándar sin inventar requisitos.

## Entradas necesarias
- Pregunta de investigación y alcance delimitado (D1–D2).
- Especificación formal del HMM: estados S, observaciones O, matrices A, B y vector pi (D3).
- Régimen experimental: decodificación con parámetros fijos (D5a) o entrenamiento (D5b).
- Naturaleza de las secuencias (sintéticas o reales) y existencia de etiquetas verdaderas.
- Parámetros de simulación: longitud T, réplicas Monte Carlo N, semillas y escenarios (M0, M1, M2).

## Criterios específicos de revisión
1. **Comparación (Baseline):** Incluir obligatoriamente un método sencillo sin HMM (ej. regla directa por observación o frecuencia) como referencia de contraste.
2. **Métricas y etiquetas:** Comprobar si existen etiquetas reales conocidas antes de proponer exactitud o Macro-F1. Prohibir métricas supervisadas si no hay etiquetas de referencia.
3. **Reproducibilidad y control:** Distinguir explícitamente los parámetros fijados a priori de los perturbados o aprendidos. Evitar factores confundidos aislando cambios entre escenarios.
4. **Independencia estocástica:** Verificar que las réplicas Monte Carlo (N) empleen semillas independientes (no reiniciar la misma semilla en cada corrida) y reporten estadísticos de dispersión.
5. **Pertinencia:** Exponer tanto las razones para emplear el HMM en el diseño como los escenarios donde debería descartarse.
6. **Alineación con el código:** Verificar que el diseño descrito corresponda al código vigente y no arrastre supuestos de versiones legado.

## Decisiones reservadas al grupo de trabajo
- Aprobar los escenarios experimentales y las perturbaciones aplicadas a las matrices (ej. B alterada).
- Seleccionar el método baseline sin HMM.
- Validar las métricas de evaluación y el criterio de éxito.
- Fijar los parámetros computacionales definitivos (T, N, esquema de semillas).
- Aprobar la declaración de alcance y amenazas a la validez.
- Autorizar el cierre como anteproyecto o el inicio de las corridas experimentales.

## Formato de salida
1. **Verificación de entradas:** Separación entre hechos confirmados, supuestos e incertidumbres.
2. **Borrador de la sección "Diseño experimental":**
   - Unidad de análisis y generación de datos (T, N).
   - Escenarios y control de parámetros (tabla comparativa M0, M1, M2).
   - Método de referencia (baseline sin HMM) y pertinencia del modelo.
   - Métricas de evaluación y protocolo estadístico.
   - Alcance y amenazas a la validez.
3. **Decisiones pendientes:** Lista numerada de puntos que el grupo debe aprobar.
4. **Bitácora:** Registro estructurado de consulta, propuesta, verificación, decisión humana y evidencia.

## Qué hacer si falta evidencia
- No inventar ejecuciones, métricas, semillas ni resultados.
- Si faltan parámetros (ej. valores de B alterada o el baseline), marcar `[PENDIENTE DE DECISIÓN HUMANA]` y ofrecer 2 alternativas concretas.
- Si no hay simulaciones ejecutadas, entregar el protocolo y tablas de resultados vacías, rotulando el producto como "Anteproyecto / Pendiente de ejecución".
- Si existe discrepancia entre el código del repositorio y el protocolo aprobado, reportar el conflicto y detener el cierre hasta que el grupo lo resuelva.