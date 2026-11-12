# Bitácora de IA · Cala

| Herramienta | Modelo | Coste | Alcance |
| --- | --- | --- | --- |
| OpenCode | MiMo-V2.6-Flash | — | Mis tareas: modelado (#5 baseline, #6 ensembles, #7 optimización, #8 informe). El agente redacta el código, los tests y estas entradas; yo decido, reviso el diff y apruebo el push y el PR |

## Entradas

### #5 Modelo baseline (Random Forest + StratifiedKFold)

- **Fecha:** 2026-11-12
- **Herramienta y modelo:** OpenCode, MiMo-V2.6-Flash.
- **Prompt clave:** El texto de la issue #5 («Entrenar un modelo baseline (Random Forest o Logistic Regression) con StratifiedKFold») más las dudas que fui planteando: «¿cuál es mejor o más fácil para este proyecto?», «¿hay algo de estos dos en el proyecto?» y «mira si falta algo de lo mío» cuando llegaron los archivos nuevos de Anna.
- **Qué generó el agente:**
  - `src/kiniela/models/train.py`: `train_baseline()` con `RandomForestClassifier(class_weight="balanced")`, el baseline de referencia (`DummyClassifier` de clase mayoritaria) evaluado en los mismos folds, `stratified_cv()` como único punto donde se construye el `StratifiedKFold(n_splits=5, shuffle=True, random_state=42)`, informe con accuracy y F1 macro (media ± desviación) y guardado del artefacto con joblib.
  - `CV_N_SPLITS = 5` junto a `RANDOM_STATE` en `config.py`, para que #6 y #13 reutilicen el mismo esquema sin divergir.
  - `tests/test_train.py`: 13 tests con dataset sintético (esquema fijo, reproducibilidad, exclusión de columnas con fuga, artefacto guardado, CLI, errores) → 90 tests en verde.
  - CLI re-ejecutable: `PYTHONPATH=src python -m kiniela.models.train --dataset ... --model ...`.
  - Ante el bloqueo de la #3 (Anna), implementación completa esperando su dataset, validada al llegar: rama rebasada sobre `dev` y prueba real con `premier_league_with_features_and_target.csv`.
- **Aceptado:**
  - **Random Forest** en lugar de Logistic Regression: el `target` se define con reglas no lineales (umbral ≥ 2, precedencia de la clase 5), no hace falta escalar y es comparable después con XGBoost/LightGBM (#6). Lo decidí yo con la comparativa del agente delante.
  - Esquema fijo en `config.py` y documentado en el docstring, no en un notebook.
  - Columnas anti-fuga (`NON_FEATURE_COLUMNS`): del output de Anna se excluyen `FTHG`, `FTAG`, `FTR` y el resto de datos post-partido; el modelo entrena con 11 features.
  - Guardar el baseline en `models/baseline_rf.joblib`, nunca en `kiniela_model.joblib` (la app solo carga objetos `Predictor` y fallaría con un `TypeError`); con un guard que lo impide.
- **Rechazado o cambiado, y por qué:**
  - Entrenar con las cuotas (`B365H`…) como features mínimas mientras no existía la #3: preferí esperar a las features de Anna antes que mezclar alcances entre issues.
  - La primera versión **fallaba con los NaN** que `build_features()` deja en las primeras jornadas (no hay historial). Cambiado a descartar esas filas **y contarlas en el informe** (`359 rows, 21 dropped without history`), no esconderlas.
  - El símbolo `±` en la salida: se rompía en la consola de Windows (`UnicodeEncodeError`), cambiado a `+/-`.
- **Errores o alucinaciones del agente y cómo se corrigieron:**
  - Al principio dio por hecho que el dataset de modelado ya existía y propuso usarlo; al comprobarlo en el repo vio que `build_features()` seguía en `NotImplementedError` y paró a preguntar. Fue el acierto de la sesión: si habría entrenado a ciegas con el CSV crudo, habría metido `FTHG`/`FTAG` como features y el modelo habría hecho trampa.
  - Resultado real que hay que defender en el PR: el RF gana al baseline en F1 macro (0.162 vs 0.102) pero **pierde en accuracy** (0.209 vs 0.443), porque con una sola temporada «predecir siempre clase 5» da el 44% gratis. El agente probó 6 variantes (RF con/sin `class_weight`, profundidad, `min_leaf`, Logistic Regression) y ninguna le gana al dummy en accuracy: es un problema de datos (una temporada, features débiles), no del código. Dejamos el RF balanced, el mejor en F1 macro, y el gap queda documentado para #6/#7.
  - Aviso encontrado por el agente, no suyo: `build_features()` de Anna truena en consolas Windows (`print` con `⚠️`), se evita con `PYTHONUTF8=1`. Y el CSV final de la #3 no lo genera ningún código: lo he generado yo en local para validar (está en `.gitignore`, no se commitea).
- **Revisión humana:** pendiente en el PR. Puntos a mirar: que el informe refleje las dos métricas con la semilla y el esquema fijos, que ninguna columna con fuga entra al modelo, y que `dev` no recibe nada sin los checks en verde.
