# 5. Red neuronal

**Quién:** Mariana · **Issue:** #13 · **Estado:** escrita (13/11/2026) · Código: `src/kiniela/models/neural.py` (PR #41)

## 5.1 Por qué una red, y por qué esta

El briefing pedía una red neuronal **multiclase** comparable con los ensembles, no una arquitectura nueva por moda. Cala ya tenía Random Forest, XGBoost y LightGBM con el mismo `StratifiedKFold` (`n_splits=5`, `shuffle=True`, `RANDOM_STATE=42`). La red tiene que medirse en esa regla; si no, la tabla miente.

Se eligió un **MLP de scikit-learn** (`MLPClassifier`) en lugar de TensorFlow o PyTorch: el runtime de la app ya lleva scikit-learn, no hace falta una dependencia nueva para predecir, y `clone` + `sample_weight` encajan con `cross_validate_model` de Cala.

## 5.2 Arquitectura y regularización

| Pieza | Valor | Por qué |
| --- | --- | --- |
| Salidas | 6 (una por clase) | Misma `target` que el resto del proyecto |
| Capas ocultas | 32 y 16, ReLU | Tabular y pequeño; no es imagen |
| Escalado | `StandardScaler` **dentro** de cada fold | El scaler no ve el fold de test |
| L2 | `alpha = 1e-4` | Penaliza pesos grandes |
| Early stopping | 15 % del fold de train, para si 10 épocas no bajan la pérdida | Evita seguir entrenando cuando ya no generaliza |
| Desbalance | `sample_weight` por fold, como XGBoost | La clase 5 no puede comerse al resto |
| Semilla | `RANDOM_STATE` | Misma reproducibilidad que #5 y #6 |

La búsqueda de hiperparámetros de los árboles es la issue #7 de Cala. Aquí la arquitectura está **fija** a propósito: el entregable es la comparación, no un Optuna paralelo.

## 5.3 Cómo se compara

```bash
PYTHONPATH=src python -m kiniela.models.neural \
  --dataset data/processed/premier_league_with_features_and_target.csv
```

El informe imprime, para la referencia (mayoritaria), Random Forest, XGBoost, LightGBM y la red:

- accuracy media ± desviación en los 5 folds;
- F1 macro (la métrica con la que se elige candidato: pondera las seis clases igual);
- F1 por clase 0–5;
- cuál es el **mejor ensemble** y el F1 de la red al lado.

Los tests de `tests/test_neural.py` comprueban que la red usa el mismo esquema que `compare_models`, que es reproducible y que el texto del informe incluye early stopping y el mejor ensemble. No se copian aquí cifras de un run local: las oficiales son las de ese comando sobre el CSV de modelado de Anna, y van también a la [sección 4](04-modelos-y-metricas.md) de Cala.

## 5.4 Lectura prevista (sin adelantar al ensemble)

En un problema tabular con pocas filas y mucho desbalance, un MLP de este tamaño **no suele ganar** a LightGBM o XGBoost en F1 macro. La red está para:

- cumplir el nivel experto del briefing con la **misma** validación;
- dejar por escrito L2 y early stopping;
- no vender una red que no se puede volver a entrenar.

Si el F1 macro de la red queda por debajo del mejor ensemble, el modelo que se promociona a la app sigue siendo el de Cala ([contrato](../model-contract.md)). La red no se descarta: queda como línea de base neuronal para un dataset más grande.

## 5.5 Límites

- Sin búsqueda de arquitectura: más capas o dropout serían otra issue.
- El early stopping usa un trozo del fold de train, no un conjunto extra de test: no hay fuga del test, pero el fold de train «efectivo» es más pequeño.
- Hasta que exista `models/kiniela_model.joblib` con el `Predictor`, ni la red ni el ensemble están en producción; la app usa el modelo de prueba y lo avisa (Eva, [sección 6](06-aplicacion-y-despliegue.md)).
