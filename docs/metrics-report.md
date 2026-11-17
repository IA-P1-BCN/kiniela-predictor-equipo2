# Informe de métricas del modelo seleccionado

**Modelo:** `tuned-xgb-2026-11-16` · **Issue:** #8 · **Generado con** `python -m kiniela.models.report`

Las métricas usan **predicciones fuera de fold** con `StratifiedKFold(n_splits=5, shuffle=True, random_state=42)`: cada partido se puntúa con un modelo que no lo vio al entrenar. Se usa la misma rejilla de hiperparámetros y los mismos pesos por clase que en la ficha del modelo. Las métricas de entrenamiento se excluyen a propósito.

Datos: 3235 partidos con historial de 3420; 185 primeras jornadas descartadas por no tener features. Features: 8.

## Accuracy y métricas por clase

**Accuracy global: 0,1787** (17,9 % de los partidos bien clasificados).

| Clase | Support | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: |
| 0 · Victoria local clara | 397 | 0,162 | 0,338 | 0,219 |
| 1 · Victoria local ajustada | 560 | 0,148 | 0,098 | 0,118 |
| 2 · Empate | 559 | 0,178 | 0,152 | 0,164 |
| 3 · Victoria visitante ajustada | 445 | 0,208 | 0,142 | 0,168 |
| 4 · Victoria visitante clara | 245 | 0,122 | 0,453 | 0,192 |
| 5 · Partido de muchos goles (4+ goles) | 1029 | 0,378 | 0,126 | 0,189 |
| **Macro** | 3235 | 0,199 | 0,218 | **0,175** |

El F1 macro de esta tabla se calcula sobre todas las predicciones fuera de fold a la vez. La ficha del modelo da la media de los F1 de los 5 folds (0,1719); son dos agregaciones distintas del mismo esquema, no dos modelos.

## Matriz de confusión

Filas = clase real, columnas = clase predicha.

| Real \ Predicha | 0 | 1 | 2 | 3 | 4 | 5 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 0 · Victoria local clara | 134 | 53 | 55 | 18 | 84 | 53 |
| 1 · Victoria local ajustada | 166 | 55 | 103 | 54 | 123 | 59 |
| 2 · Empate | 124 | 80 | 85 | 49 | 160 | 61 |
| 3 · Victoria visitante ajustada | 91 | 52 | 68 | 63 | 145 | 26 |
| 4 · Victoria visitante clara | 44 | 21 | 28 | 26 | 111 | 15 |
| 5 · Partido de muchos goles (4+ goles) | 269 | 111 | 138 | 93 | 288 | 130 |

## Clases más confundidas y ejemplos

| Confusión | Partidos | % de la clase real |
| --- | ---: | ---: |
| 5 · Partido de muchos goles (4+ goles) → 4 · Victoria visitante clara | 288 | 28,0 % |
| 5 · Partido de muchos goles (4+ goles) → 0 · Victoria local clara | 269 | 26,1 % |
| 1 · Victoria local ajustada → 0 · Victoria local clara | 166 | 29,6 % |
| 2 · Empate → 4 · Victoria visitante clara | 160 | 28,6 % |
| 3 · Victoria visitante ajustada → 4 · Victoria visitante clara | 145 | 32,6 % |

Ejemplos reales de las confusiones más frecuentes:

| Fecha | Partido | Resultado | Clase real | Predicha |
| --- | --- | --- | --- | --- |
| 2015-08-29 | aston villa – sunderland | 2-2 | 5 · Partido de muchos goles (4+ goles) | 4 · Victoria visitante clara |
| 2015-09-12 | norwich – bournemouth | 3-1 | 5 · Partido de muchos goles (4+ goles) | 4 · Victoria visitante clara |
| 2015-09-20 | southampton – man united | 2-3 | 5 · Partido de muchos goles (4+ goles) | 0 · Victoria local clara |
| 2015-09-26 | west ham – norwich | 2-2 | 5 · Partido de muchos goles (4+ goles) | 0 · Victoria local clara |
| 2015-11-21 | chelsea – norwich | 1-0 | 1 · Victoria local ajustada | 0 · Victoria local clara |
| 2015-12-14 | leicester – chelsea | 2-1 | 1 · Victoria local ajustada | 0 · Victoria local clara |
| 2015-08-22 | sunderland – swansea | 1-1 | 2 · Empate | 4 · Victoria visitante clara |
| 2015-08-22 | norwich – stoke | 1-1 | 2 · Empate | 4 · Victoria visitante clara |
| 2015-08-29 | newcastle – arsenal | 0-1 | 3 · Victoria visitante ajustada | 4 · Victoria visitante clara |
| 2015-09-27 | watford – crystal palace | 0-1 | 3 · Victoria visitante ajustada | 4 · Victoria visitante clara |

### Lectura de errores

La clase 1 (Victoria local ajustada) es la que más se pierde: solo se recupera 9,8 % de sus partidos. La clase 4 (Victoria visitante clara) es la menos fiable cuando se predice: solo 12,2 % de esos pronósticos aciertan. El modelo cae con frecuencia en las victorias claras cuando no distingue entre el resto de clases.

## Feature importance

Importancia `gain` del modelo entrenado con todas las filas útiles (el que se sirve en la app):

| Feature | Gain |
| --- | ---: |
| `avg_away_goals_last_5` | 0,2187 |
| `match_diff` | 0,2172 |
| `away_diff_last_5` | 0,1170 |
| `avg_home_goals_last_5` | 0,1159 |
| `home_diff_last_5` | 0,1152 |
| `match_goals_expected` | 0,0871 |
| `form_home_last_5` | 0,0744 |
| `form_away_last_5` | 0,0545 |

## Límites

- La matriz y las métricas por clase son de validación fuera de fold, no de partidos futuros: retratan el rendimiento esperado sobre datos de la misma distribución (Premier League 2015-16 a 2023-24).
- Los ejemplos son partidos reales del histórico; no permiten explicar por qué el modelo se equivocó en cada uno, solo dónde se concentra el error.
- Solo hay 8 features de forma y goles, sin tiros, lesiones ni alineaciones.
