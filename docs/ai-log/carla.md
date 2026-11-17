# Bitácora de IA · Carla

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
  - Tras la revisión automática del PR: `train_baseline()` ya no imprime nada; el informe lo renderiza `format_report()` como texto puro y solo `main()` lo escribe en consola, con un test nuevo que lo comprueba. Docstring de `_cross_validate` con `X` (features) e `y` (etiquetas).
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

### #6 Modelos ensemble (XGBoost y LightGBM)

- **Fecha:** 2026-11-12
- **Herramienta y modelo:** OpenCode, MiMo-V2.6-Flash.
- **Prompt clave:** «crea la rama y ahora me toca hacer esto», con el texto de la issue #6 (entrenar y comparar XGBoost y LightGBM).
- **Qué generó el agente:**
  - `src/kiniela/models/ensembles.py`: `compare_models()` entrena la referencia, el Random Forest de la #5, XGBoost y LightGBM con el **mismo** `stratified_cv()` y los mismos datos preparados, y devuelve `ModelComparison` con accuracy, F1 macro y **F1 por clase** de los cuatro modelos.
  - `choose_candidate()` elige por mayor F1 macro (el accuracy solo desempata) y la razón queda escrita en la salida.
  - En `train.py`: `FoldScores` pasa a guardar F1 por clase, y lo que era privado se vuelve público (`prepare_xy`, `cross_validate_model`, `build_forest`, `build_reference`) para que #6 lo reutilice en vez de duplicarlo.
  - XGBoost se equilibra con `sample_weight` calculado **solo con las etiquetas del fold de entrenamiento** (no tiene `class_weight`); LightGBM con `class_weight="balanced"` y `deterministic=True, n_jobs=1` para que sea reproducible.
  - 10 tests nuevos → **100 en verde**, entre ellos la reproducibilidad de los dos ensembles y que el RF de la comparación da exactamente los mismos números que el baseline de la #5.
- **Aceptado:**
  - Candidato **XGBoost**: mayor F1 macro (0.166 frente a 0.162 del RF y 0.137 de LightGBM) y mejor accuracy de los entrenados (0.254). Justificación: el F1 macro reparte el peso por igual entre las 6 clases, mientras que el accuracy solo premia acertar la clase 5, que es el 46% de los partidos.
  - Incluir también la referencia de la #5 en la tabla, para ver contra qué barra se juega.
  - Un test que garantiza que la comparación reproduce el baseline de la #5 cifra a cifra.
- **Rechazado o cambiado, y por qué:**
  - Tuning de hiperparámetros: fuera de alcance, es la #7. Aquí solo parámetros fijos y semilla.
  - Guardar los modelos entrenados: no lo pide la issue; lo decidirán #7 y #8.
- **Errores o alucinaciones del agente y cómo se corrigieron:**
  - Al crear la rama con `git checkout -b 6-ensemble-models origin/dev`, git la configuró para hacer *push* a `origin/dev`; se le quitó el upstream antes de subirla, para que un `push` sin argumentos no pudiera tocar `dev`.
  - XGBoost no admite `class_weight` como sklearn: sin el ajuste por `sample_weight` la comparación habría sido injusta (el RF y LightGBM sí se equilibraban).
- **Revisión humana:** pendiente en el PR. Puntos a mirar: que el candidato se justifique con F1 macro y no con accuracy, que los dos ensembles usen el mismo esquema que la #5, y que la semilla esté en todos los modelos.

### #7 Optimización y control de overfitting (XGBoost)

- **Fecha:** 2026-11-13
- **Herramienta y modelo:** OpenCode, MiMo-V2.6-Flash.
- **Prompt clave:** «crea la rama y mírame esto pero no lo subas, déjame los archivos allí», con el texto de la issue #7 (optimizar hiperparámetros y garantizar overfitting inferior al 5%).
- **Qué generó el agente:**
  - `src/kiniela/models/tuning.py`: `tune_model()` con búsqueda en **rejilla** (grid, 648 combinaciones) sobre `SEARCH_SPACE` documentado en el docstring — `max_depth` 1/2, `n_estimators` 25/100/300, `learning_rate` 0.01/0.03/0.1, `min_child_weight` 1/5/20, `reg_lambda` 10/100/500, `subsample` y `colsample_bytree` 0.7/1.0 —, con el mismo `stratified_cv()` y los mismos `sample_weight` balanceados por fold que la #6.
  - Métrica del gap **declarada**: `GAP_METRIC = "f1_macro"`; el gap es `|mean(train f1_macro) - mean(validation f1_macro)|` calculado por folds (`FoldScores.f1_macro_gap`) y el umbral `GAP_THRESHOLD = 0.05` es estricto, como pide la issue.
  - Selección: mayor F1 macro de validación **solo entre las combinaciones con gap < 0.05**; el accuracy solo desempata (misma regla que la #6); si ninguna combinación es viable lanza `ValueError` en vez de devolver un modelo sobreajustado en silencio.
  - En `train.py`: `FoldScores` gana `train_f1_macro` (se puntúa en cada fold de entrenamiento dentro de `cross_validate_model`), para que #8 reutilice el mismo gap.
  - En `ensembles.py`: `build_xgboost(**overrides)` extraído, para que los defaults de #6 y el punto de partida de la búsqueda sean la misma definición.
  - Artefacto `models/tuned_xgboost.joblib` (`TunedXGBoost`) con los hiperparámetros finales y el gap **dentro** del modelo, nunca en `kiniela_model.joblib` (guard como en #5); informe `format_tuning()` puro, solo `main()` imprime.
  - 14 tests nuevos → **137 en verde**. El CSV real y el `.joblib` siguen en `.gitignore`.
- **Aceptado:**
  - **Tabla gap antes/después** (datos reales, esquema fijo, seed 42): antes `0.958 train / 0.166 val → gap 0.792`; después `0.148 / 0.104 → gap 0.044 < 0.05`. De 648 combinaciones, **15 son viables**.
  - **Hiperparámetros finales registrados con el modelo**: `max_depth=1, n_estimators=25, learning_rate=0.1, min_child_weight=20, reg_lambda=100, subsample=1.0, colsample_bytree=1.0` (dentro del artefacto y en la salida del informe).
  - **Grid en lugar de Optuna**: sin dependencias nuevas, el espacio queda descrito en el docstring y el resultado es reproducible y revisable en el diff.
  - El gap se mide con **F1 macro**, la misma métrica que eligió al candidato en #6, no con accuracy.
- **Rechazado o cambiado, y por qué:**
  - Optuna o búsqueda aleatoria: la issue admite grid y el espacio es pequeño; además Optuna metería una dependencia nueva solo por comodidad.
  - **Trade-off honesto que hay que defender en el PR**: cumplir el gap < 0.05 cuesta métrica. El XGBoost por defecto de #6 tenía el mejor F1 (0.166) pero un gap de 0.792 (se memoriza el train); el mejor viable baja a **0.104 de F1 con gap 0.044**, de la altura de la referencia (0.102). La mejor combinación sin restricción (0.165) tiene gap 0.141 y queda fuera. Con una sola temporada y features débiles es un problema de datos, no del código; el accuracy también baja (0.254 → 0.114) y queda en la tabla para #8.
  - Tunear LightGBM o el Random Forest: la #6 eligió XGBoost como candidato, la búsqueda es solo sobre él.
- **Errores o alucinaciones del agente y cómo se corrigieron:**
  - El primer test del límite «gap exactamente 0.05» falló por aritmética de coma flotante (`0.5 - 0.45 = 0.0499…` era `< 0.05` y el combo entraba como viable); corregido usando el propio `GAP_THRESHOLD` como valor de train, cuya resta da exactamente `0.05`.
  - La rejilla pequeña de los tests no era viable en el dataset sintético (hasta un solo stump daba gap 0.095): se cambió a `min_child_weight` 1/100, donde el combo regularizado colapsa a predicción casi constante (gap 0) y el sobreajustado queda fuera — justo el comportamiento que el test debe probar.
  - El test de la CLI tardaba 6 minutos: sin argumento de espacio, `main()` ejecutaba las 648 combinaciones completas; se parchea `SEARCH_SPACE` en ese test para que solo corra la rejilla pequeña.
- **Revisión humana:** pendiente en el PR. Puntos a mirar: que el gap declarado sea F1 macro y estrictamente menor que 0.05, que la tabla compare antes/después con el mismo esquema y solo cambien los hiperparámetros, que los parámetros finales viajen dentro del artefacto, y que el trade-off de F1 quede claro para el informe de #8.

### #17 Informe y presentación: modelos y métricas

- **Fecha:** 2026-11-17
- **Herramienta y modelo:** OpenCode, Big Pickle.
- **Prompt clave:** «en mi proyecto de kiniela mirame porque no me instala el npm» y «haz una rama y arreglame lo mio soy carla», con los criterios de aceptación de las issues #5 y #6 y el aviso de mi compañera de que mi parte «solo tiene el esquema, sin texto ni cifras».
- **Qué generó el agente:**
  - Rama `17-models-metrics-section` desde `origin/dev`, sin upstream (un `push` sin argumentos no puede tocar `dev`).
  - `docs/informe/04-modelos-y-metricas.md`: sección completa con el esquema fijo (#5), la comparación reference/RF/XGB/LGBM de 16/11 con 8 features (#5/#6), la rejilla y el antes/después del gap (#7), el modelo final `tuned-xgb-2026-11-16` (#66) y el hueco marcado de #8.
  - `docs/presentacion/02-modelos.md`: 5 diapositivas con título, qué se ve, qué se dice (30–45 s) y captura, con las mismas cifras.
  - Esta entrada en mi bitácora.
- **Aceptado:**
  - Cifras solo de fuentes del repo: `models/model_card.json` para el modelo final (F1 macro 0,1719 ± 0,0118, accuracy 0,1787, gap 0,0496, 3.235 filas de 3.420) y la tabla de 8 features de la sección 5 para la comparación de una temporada (reference 0,443/0,102, RF 0,228/0,180, XGB 0,262/0,177, LGBM 0,248/0,166).
  - Separar explícitamente la comparación de una temporada del modelo final de nueve: no se mezclan sus números.
  - Decir que la elección entre RF (0,180) y XGB (0,177) en la tabla de 8 features está dentro de la desviación; el modelo entregado es el XGBoost ajustado de #66 porque cumple el gap.
  - Marcar como «pendiente de cifra (#8)» la matriz de confusión, la feature importance, el F1 por clase del modelo final y el análisis de errores, como permite el README del informe.
- **Rechazado o cambiado, y por qué:**
  - No añadir `package.json`, `npm install` ni archivos de Node: este repo es Python (requirements + Streamlit). El error de npm venía de la política de ejecución de PowerShell en su máquina (`npm.ps1` bloqueado), no del proyecto; además `python` no está en el PATH de esa consola. No era un cambio de repositorio.
  - No rellenar el informe con el F1 por clase de la comparación de una temporada ni con el `score_multiclass()` de la #15: no son las métricas del modelo final de 9 temporadas.
  - No tocar los archivos de Anna, Eva ni Mariana (README del informe y de la presentación incluidos): cada persona edita solo su sección.
- **Errores o alucinaciones del agente y cómo se corrigieron:**
  - No pude leer la imagen que adjuntó (el modelo no admite imágenes); pedí el texto y él llegó en el mensaje siguiente con los criterios de #5 y #6. No inventé nada a partir de la captura.
  - El primer borrador decía «esa es la cambio» y la diapositiva 2 llevaba «no Decide»; corregido antes de dejar los archivos.
  - No hice commit, push ni PR: los cambios quedan en la rama para que yo revise el diff antes de subirlos.
- **Revisión humana:** pendiente. Puntos a mirar: que las cifras coincidan con `model_card.json` y con la sección 5, y que el guion no contradiga el informe ni la parte de Eva.

### #8 Informe de métricas completas

- **Fecha:** 2026-11-17
- **Herramienta y modelo:** OpenCode, Big Pickle.
- **Prompt clave:** «vale, ahora haz otra rama y añade esto», con los criterios de aceptación de la #8 (accuracy, precision/recall/F1 por clase, matriz, importance, confusiones y ejemplos).
- **Qué generó el agente:**
  - Rama `8-metrics-report` desde `origin/dev`, sin upstream.
  - `src/kiniela/models/report.py`: `build_report()` reconstruye el dataset desde el `MatchPredictor` guardado y puntúa con predicciones fuera de fold del `StratifiedKFold` fijo, con los hiperparámetros de la ficha y pesos de clase por fold; `format_report()` es puro y `main()` escribe el Markdown.
  - `docs/metrics-report.md`: accuracy 0,1787, precision/recall/F1 de las 6 clases, matriz etiquetada, 5 confusiones con 10 partidos reales, importance de las 8 features y límites.
  - `tests/test_report.py`: 3 tests, los 3 en verde.
  - Enlace en el README y actualización de la sección 4 del informe y de la diapositiva 5 del guion, que dejan de estar pendientes.
- **Aceptado:**
  - Medir fuera de fold y no puntuar el entrenamiento con el modelo final: la accuracy reproduce la de la ficha (0,1786707882534776), así que la reconstrucción del dataset es correcta.
  - Explicar que el F1 macro agregado (0,175) y el de la ficha (0,1719) son dos formas de agregar el mismo esquema, no dos modelos.
  - Cifras del informe: clase 1 peor recuperada (recall 0,098), clase 4 menos fiable (precision 0,122), confusión 5→4 en 288 partidos y `avg_away_goals_last_5` como feature con más gain (0,2187).
- **Rechazado o cambiado, y por qué:**
  - No rellenar la matriz con predicciones del modelo entrenado sobre todas las filas: habría inflado las métricas y no cumpliría el criterio de evaluación honesta.
  - No tocar los AI logs de las demás ni las secciones del informe de Anna, Eva o Mariana.
  - No hice commit, push ni PR: los cambios quedan en la rama para que Carla revise el diff antes de subirlos.
- **Errores o alucinaciones del agente y cómo se corrigieron:**
  - El primer `pytest` completo se quedó sin respuesta después de 10 minutos en este entorno; al repetirlo pasaron las 234 pruebas en 2:55, y cada archivo de tests también pasó por separado.
  - El primer borrador de los tests usaba una matriz 3x3 con un bucle de 6 clases y un dataset sintético sin columnas de partido; corregido con `matrix.shape` y columnas `Date`/equipos/goles.
  - Las primeras cifras salían con separador decimal inglés y fechas con hora; corregido en `format_report()` y en `_examples()`.
- **Revisión humana:** pendiente. Puntos a mirar: que la matriz y el F1 por clase salgan de fuera de fold y que el informe enlazado tenga los seis criterios. La suite completa (234 tests) pasa en 2:55.
