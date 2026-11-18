# 4. Modelos, validación, optimización y métricas por clase

**Autora:** Carla · **Issues:** #5, #6, #7 y #8 · **Estado a 17/11/2026** · Modelo servido: `tuned-xgb-2026-11-16` ([ficha](../../models/model_card.json))

El objetivo era decidir un modelo para la kiniela con una regla de comparación que no cambiara en cada intento. La sección cuenta cómo se fijó esa regla (#5), qué pasó al comparar el baseline con los ensembles (#6), cómo se controló el sobreajuste (#7) y qué modelo se entregó finalmente (#66). Las cifras son las del repositorio: la ficha del modelo y el recálculo de 16/11/2026 recogido en la [sección 5](05-red-neuronal.md). Lo que todavía no está calculado se marca como pendiente, sin inventarlo.

## 4.1 Un solo esquema de validación para todos (#5)

Todos los modelos del proyecto —reference, Random Forest, XGBoost, LightGBM, la red de la sección 5 y el modelo final— se entrenan y validan con lo mismo:

| Pieza | Valor fijo | Dónde vive |
| --- | --- | --- |
| Particionador | `StratifiedKFold(n_splits=5, shuffle=True, random_state=42)` | `stratified_cv()` en [`train.py`](../../src/kiniela/models/train.py) |
| Semilla | `RANDOM_STATE = 42` | [`config.py`](../../src/kiniela/config.py) |
| Número de folds | `CV_N_SPLITS = 5` | [`config.py`](../../src/kiniela/config.py) |
| Referencia | `DummyClassifier(strategy="most_frequent")` | `build_reference()` en `train.py` |
| Métrica de decisión | F1 macro (accuracy también se reporta) | `cross_validate_model()` en `train.py` |

`stratified_cv()` es el único sitio donde se construye el particionador: #6, #7 y la red neuronal lo reutilizan en vez de crear el suyo. Eso es lo que hace que las tablas de abajo sean comparables entre sí. `StratifiedKFold` mantiene la proporción de las 6 clases en cada fold, imprescindible con una clase 5 que llega al 31,9 % de los partidos (ver [sección 2.3](02-datos-y-eda.md)).

El desbalance se trata igual en todos: Random Forest y LightGBM con `class_weight="balanced"`, XGBoost con `sample_weight` calculado **solo con las etiquetas del fold de entrenamiento** (no tiene `class_weight`). Así ningún modelo ve las clases del fold de validación al ponderar.

La semilla y el esquema quedan documentados en el docstring de `train.py` y en la ficha del modelo (`validation` en `model_card.json`).

## 4.2 Baseline y ensembles (#5 y #6)

Se compararon la referencia, el Random Forest equilibrado, XGBoost y LightGBM. La tabla es el recálculo del **16/11/2026** sobre la temporada 2023-24 (359 partidos con historial, 8 features definitivas) que se recoge en la [sección 5](05-red-neuronal.md); no son las cifras antiguas de 11 features:

| Modelo | Accuracy | F1 macro | F1 por clase (0–5) |
| --- | --- | --- | --- |
| reference (mayoritaria) | 0,443 ± 0,003 | 0,102 ± 0,001 | 0,00 0,00 0,00 0,00 0,00 0,61 |
| random_forest | 0,228 ± 0,060 | **0,180 ± 0,058** | 0,26 0,09 0,15 0,11 0,12 0,36 |
| xgboost | 0,262 ± 0,048 | 0,177 ± 0,041 | 0,22 0,14 0,11 0,11 0,06 0,43 |
| lightgbm | 0,248 ± 0,038 | 0,166 ± 0,049 | 0,19 0,04 0,08 0,14 0,12 0,42 |

**Por qué F1 macro y no accuracy.** La referencia gana en accuracy (0,443) porque siempre predice la clase 5, que en 2023-24 es el 43,7 % de los partidos. En F1 macro, que pesa igual las seis clases, queda en 0,102 y los modelos entrenados la superan. Por eso la métrica de decisión es F1 macro y la accuracy se muestra al lado, para que el engaño quede a la vista.

**Qué dicen los F1 por clase.** La referencia solo puntúa en la clase 5. Los árboles reparten mejor: Random Forest llega a 0,26 en la clase 0 y XGBoost a 0,43 en la 5. Ninguno destaca en la clase 4 (victoria visitante clara), la más escasa, y las clases 2 y 3 siguen débiles: es el efecto de tener pocos ejemplos y features que separan poco (sección 3.5).

**Candidato.** En el run original de #6 se eligió XGBoost por F1 macro. Al recalcular con las 8 features definitivas, Random Forest queda 0,180 y XGBoost 0,177: una diferencia de 0,003, mucho menor que la desviación de los folds (±0,058 y ±0,041). Esa diferencia no decide por sí sola; la decisión final se apoya en el modelo de 9 temporadas y en el guard de sobreajuste de #7 (4.3 y 4.4).

El código está en [`train.py`](../../src/kiniela/models/train.py) (#5) y [`ensembles.py`](../../src/kiniela/models/ensembles.py) (#6), con sus tests en `tests/test_train.py` y `tests/test_ensembles.py`. Ambos imprimen el informe accuracy, F1 macro y F1 por clase.

## 4.3 Optimización y control de overfitting (#7)

La búsqueda fue una **rejilla exhaustiva** sobre XGBoost, sin dependencias nuevas: 648 combinaciones del espacio documentado en [`tuning.py`](../../src/kiniela/models/tuning.py) (`max_depth` 1–2, `n_estimators` 25/100/300, `learning_rate` 0,01/0,03/0,1, `min_child_weight` 1/5/20, `reg_lambda` 10/100/500, `subsample` 0,7/1,0 y `colsample_bytree` 0,7/1,0). Se prefirió una rejilla a Optuna porque el espacio es pequeño, queda descrito en el código y el resultado es reproducible y revisable en el diff.

El **gap se mide con F1 macro**, la misma métrica que eligió candidato, y se declara en `GAP_METRIC`. Es `|F1 macro de train − F1 macro de validación|` y solo se admiten combinaciones con gap **estrictamente menor que 0,05** (`GAP_THRESHOLD`). Entre las viables gana la de mayor F1 macro de validación; la accuracy solo desempata. Si ninguna cumple, la búsqueda lanza un error en lugar de entregar un modelo sobreajustado sin avisar.

Antes y después, con las 9 temporadas del modelo final (ficha `model_card.json`):

| | F1 macro validación | F1 macro train | Gap |
| --- | --- | --- | --- |
| Antes (parámetros por defecto de #6) | 0,180 | 0,685 | 0,5050 |
| Después (mejor de la rejilla) | **0,172 ± 0,012** | 0,222 | **0,0496** |

Hiperparámetros finales, registrados dentro del artefacto: `max_depth=2`, `n_estimators=300`, `learning_rate=0,01`, `min_child_weight=20`, `reg_lambda=10`, `subsample=1,0`, `colsample_bytree=1,0`.

**Trade-off honesto.** Cumplir el criterio cuesta F1 macro (0,180 → 0,172), pero el modelo deja de memorizar el entrenamiento: el gap pasa de 0,505 a 0,0496, justo por debajo del límite. Con features débiles y clasificación difícil, ese es el cambio que permite entregar un modelo que generaliza.

## 4.4 Modelo final e informe de métricas (#8)

El modelo que sirve la app es el XGBoost ajustado, versionado `tuned-xgb-2026-11-16` en [`models/model_card.json`](../../models/model_card.json). Se entrena con 9 temporadas de Premier League (2015-16 a 2023-24): 3.420 partidos, de los que 3.235 tienen historial y 185 se descartan por ser primeras jornadas.

| Métrica del modelo final | Valor |
| --- | --- |
| F1 macro validación | 0,1719 ± 0,0118 |
| Accuracy validación | 0,1787 |
| F1 macro train | 0,2216 |
| Gap train/validación | 0,0496 (< 0,05) |
| Referencia con las mismas 9 temporadas | F1 macro 0,080 |

Frente a la referencia (0,080), el modelo final duplica el F1 macro. La accuracy de 0,179 no es un error de cálculo: con la clase 5 repartida por 9 temporadas, predecir siempre esa clase daría un 31,9 % de aciertos, y los modelos entrenados sacrifican accuracy para no ignorar las otras cinco clases.

El **[informe de métricas](../metrics-report.md)** (issue #8) está generado y se puede regenerar con `PYTHONPATH=src python -m kiniela.models.report` ([código](../../src/kiniela/models/report.py)). Usa predicciones **fuera de fold** del mismo `StratifiedKFold`: cada uno de los 3.235 partidos se puntúa con un modelo que no lo vio al entrenar, con los hiperparámetros de la ficha y pesos de clase calculados solo en el fold de entrenamiento. No son métricas de entrenamiento.

| Métrica del informe | Valor |
| --- | --- |
| Accuracy global | 0,1787 |
| F1 macro agregado (todas las predicciones) | 0,175 |
| F1 macro de la ficha (media de los 5 folds) | 0,1719 |
| Clase peor recuperada | 1 · Victoria local ajustada (recall 0,098) |
| Clase menos fiable al predecirla | 4 · Victoria visitante clara (precision 0,122) |
| Confusión más frecuente | 5 → 4: 288 partidos (28,0 % de la clase 5) |
| Feature más importante | `avg_away_goals_last_5` (gain 0,2187) |

El documento enlazado tiene la matriz de confusión con las 6 etiquetas, precision/recall/F1 por clase, las confusiones con ejemplos de partidos reales y la importance de las 8 features. El 0,175 y el 0,1719 son dos formas de agregar el mismo esquema (predicciones agrupadas frente a media de folds), no dos modelos distintos.

## 4.5 Cómo reproducirlo

Desde la raíz del repositorio, con el entorno virtual activo:

```bash
# Modelo final: descarga las 9 temporadas, reentrena y reescribe la ficha
PYTHONPATH=src python -m kiniela.models.final

# Comparación baseline vs ensembles (CSV de modelado, no versionado)
PYTHONPATH=src python -m kiniela.models.ensembles \
  --dataset data/processed/premier_league_with_features_and_target.csv

# Búsqueda de hiperparámetros y guard de overfitting
PYTHONPATH=src python -m kiniela.models.tuning \
  --dataset data/processed/premier_league_with_features_and_target.csv \
  --model models/tuned_xgboost.joblib
```

El CSV de modelado no está en git: `kiniela.models.final` lo genera a partir de los partidos descargados. Los tests de esta parte están en `tests/test_train.py`, `tests/test_ensembles.py`, `tests/test_tuning.py`, `tests/test_final.py` y `tests/test_metrics.py`.

## 4.6 Límites

- **La accuracy sola engaña.** La clase 5 es la más frecuente; por eso se decide con F1 macro.
- **Comparación de una temporada, entrega de nueve.** La tabla de 4.2 usa 359 partidos de 2023-24; el modelo final usa 3.235 de 9 temporadas. Son experimentos distintos y no se mezclan sus cifras.
- **Pocas features.** Ocho variables de forma y goles; no hay tiros, lesiones, alineaciones ni descanso.
- **Solo Premier League.** No hay datos de otras ligas ni de copas.
- **El informe de métricas es de validación, no de futuro.** La matriz y los ejemplos de 4.4 describen partidos ya jugados y fuera de fold; no explican por qué se acierta o se falla en cada partido nuevo.
