
# Simulación de Yahtzee con Montecarlo - El Azar en el Silicio

Este repositorio contiene la solución al proyecto de simulación estocástica utilizando el juego de Yahtzee. El proyecto aplica el método de Montecarlo para la toma de decisiones y evalúa la Ley de los Grandes Números.

## Estructura del Proyecto
* `simulacion_01.ipynb`: Notebook base con el motor de Montecarlo para calcular el Valor Esperado (EV) de 32 máscaras de bloqueo posibles.
* `simulacion_02_dados_cargados.ipynb`: (Fase 2) Modificación del código para incluir dados con sesgo (el número 6 tiene un 30% de probabilidad).

## Fases del Proyecto
1. **USA (Analiza):** El código original evalúa la toma decisiones lanzando simulaciones futuras, utilizando el modelo montecarlo. Se analiza la convergencia de los datos usando 10, 1,000 y 100,000 iteraciones.
2. **MODIFICA (Interviene):** Se altera el generador pseudoaleatorio (`random.randint`) para simular "dados cargados" y se observa el impacto en las combinaciones macroscópicas.
3. **CREA (Propone):** Se calcula el Valor Esperado (EV) para decidir si arriesgarse a lanzar 2 dados o conservar el puntaje actual.

## Resultados Principales
* La simulación demuestra que a mayor cantidad de iteraciones (100,000), el Valor Esperado converge a un valor estable (~17.28), comprobando empíricamente la Ley de los Grandes Números.
* La tecnica Montecarlo demuestra ser superior a la selección aleatoria de categorías.

## Ejecución
Abrir los archivos `.ipynb` en Google Colab y ejecutar todas las celdas en orden.
