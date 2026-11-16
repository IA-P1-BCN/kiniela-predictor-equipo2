# 5. Red neuronal

**Quién:** Mariana · **Issue:** #13 · **Estado:** escrita (16/11/2026) · Código: `src/kiniela/models/neural.py` (PR #41)

Las features de Anna cambiaron en las #58 y #61: ahora son **8 columnas**, y las anteriores estaban mal calculadas. Las cifras de abajo salen de un recálculo el 16/11/2026 sobre `data/processed/premier_league_2023_24.csv` (380 jornadas → 359 filas con historial, 21 sin él). No son las de 11 features.

## 5.1 Por qué una red, y por qué esta

El briefing pedía una red neuronal **multiclase** comparable con los ensembles, no una arquitectura nueva por moda. Carla ya tenía Random Forest, XGBoost y LightGBM con el mismo `StratifiedKFold` (`n_splits=5`, `shuffle=True`, `RANDOM_STATE=42`). La red tiene que medirse en esa regla; si no, la tabla miente.

Se eligió un **MLP de scikit-learn** (`MLPClassifier`) en lugar de TensorFlow o PyTorch: el runtime de la app ya lleva scikit-learn, no hace falta una dependencia nueva para predecir, y `clone` + `sample_weight` encajan con `cross_validate_model` de Carla.

## 5.2 Arquitectura y regularización

| Pieza | Valor | Por qué |
| --- | --- | --- |
| Entrada | 8 features (`FEATURE_COLUMNS` de Anna) | Mismas que el resto de modelos tras #58/#61 |
| Salidas | 6 (una por clase) | Misma `target` que el resto del proyecto |
| Capas ocultas | 32 y 16, ReLU | Tabular y pequeño; no es imagen |
| Escalado | `StandardScaler` **dentro** de cada fold | El scaler no ve el fold de test |
| L2 | `alpha = 1e-4` | Penaliza pesos grandes |
| Early stopping | 15 % del fold de train, para si 10 épocas no bajan la pérdida | Evita seguir entrenando cuando ya no generaliza |
| Desbalance | `sample_weight` por fold, como XGBoost | La clase 5 no puede comerse al resto |
| Semilla | `RANDOM_STATE` | Misma reproducibilidad que #5 y #6 |

La búsqueda de hiperparámetros de los árboles es la issue #7 de Carla. Aquí la arquitectura está **fija** a propósito: el entregable es la comparación, no un Optuna paralelo.

## 5.3 Cómo se compara (y de dónde salen las cifras)

```bash
PYTHONPATH=src python -m kiniela.models.neural \
  --dataset data/processed/premier_league_with_features_and_target.csv
```

El CSV de modelado no está en git: se arma con `build_features` + `build_target` sobre `premier_league_2023_24.csv` y se deja solo `FEATURE_COLUMNS` + `target`. Un run anterior, o uno con 11 columnas, no vale.

El informe imprime, para la referencia (mayoritaria), Random Forest, XGBoost, LightGBM y la red:

- accuracy media ± desviación en los 5 folds;
- F1 macro (la métrica con la que se elige candidato);
- F1 por clase 0–5;
- cuál es el **mejor ensemble** y el F1 de la red al lado.

### Tabla (16/11/2026 · 359 filas · 8 features · StratifiedKFold 5, seed 42)

| Modelo | Accuracy | F1 macro | F1 por clase (0–5) |
| --- | --- | --- | --- |
| reference (majority) | 0.443 ± 0.003 | 0.102 ± 0.001 | 0.00 0.00 0.00 0.00 0.00 0.61 |
| random_forest | 0.228 ± 0.060 | **0.180 ± 0.058** | 0.26 0.09 0.15 0.11 0.12 0.36 |
| xgboost | 0.262 ± 0.048 | 0.177 ± 0.041 | 0.22 0.14 0.11 0.11 0.06 0.43 |
| lightgbm | 0.248 ± 0.038 | 0.166 ± 0.049 | 0.19 0.04 0.08 0.14 0.12 0.42 |
| **neural_network** | 0.354 ± 0.034 | 0.129 ± 0.020 | 0.00 0.12 0.04 0.05 0.00 0.56 |
| mejor ensemble | **random_forest** (F1 macro 0.180) | la red queda a 0.129 | accuracy de la red 0.354 |

Los tests de `tests/test_neural.py` comprueban el esquema, la reproducibilidad y el texto del informe. No sustituyen este recálculo sobre el CSV real.

## 5.4 Lectura (mismo run)

La accuracy de la clase mayoritaria (0.443) gana a todos: la clase 5 es ~44 % de la temporada. F1 macro es la que cuenta. Ahí **gana Random Forest (0.180)**; la red se queda en **0.129**. El MLP acierta más que los árboles (0.354 vs 0.228) porque se pega a la clase 5 (F1 0.56) y casi no ve las clases 0 y 4 (F1 0.00). Eso no es un modelo mejor: es el mismo sesgo del dummy, un poco suavizado.

La red está para:

- cumplir el nivel experto del briefing con la **misma** validación;
- dejar por escrito L2 y early stopping;
- no vender una red que no se puede volver a entrenar.

El modelo que se promociona a la app **no** es esta red: sigue el de Carla vía `python -m kiniela.models.promote`, hoy el Random Forest de este run. La red queda como línea neuronal; con más temporadas se puede repetir el comando.

## 5.5 Límites

- Sin búsqueda de arquitectura: más capas o dropout serían otra issue.
- El early stopping usa un trozo del fold de train, no un conjunto extra de test.
- Hay que repetir el comando de 5.3 cada vez que cambien las features o el CSV.
- Hasta promocionar un `Predictor` con `python -m kiniela.models.promote` y commitear `kiniela_model.joblib`, la app usa el modelo de prueba y lo avisa (Eva, [sección 6](06-aplicacion-y-despliegue.md)).
