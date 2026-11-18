# Presentación técnica · Modelos y métricas

**Presenta:** Carla · **Duración:** unos 3–4 minutos · Detalle y cifras en la [sección 4 del informe](../informe/04-modelos-y-metricas.md)

Cinco diapositivas. Las cifras salen de la ficha del modelo ([`models/model_card.json`](../../models/model_card.json)) y del recálculo de 16/11/2026 con 8 features recogido en la [sección 5](../informe/05-red-neuronal.md). No se mezclan las de una temporada con las del modelo final de nueve.

## Diapositiva 1 · Una sola regla para comparar

- **Qué se ve:** `StratifiedKFold(5, shuffle=True, random_state=42)` en grande; debajo, las cuatro filas «reference · random_forest · xgboost · lightgbm» y la red neuronal, todas bajo la misma llave. Un recuadro: «F1 macro decide · accuracy se reporta».
- **Qué se dice:** «Fijamos la semilla 42 y cinco folds estratificados antes de entrenar nada, y `stratified_cv()` es el único sitio donde se construye. Así los números de los cinco modelos son comparables de verdad. La clase 5 es casi un tercio de los partidos, así que el fold estratificado mantiene las proporciones y F1 macro pesa igual las seis clases; la accuracy la enseñamos para ver el efecto de la clase mayoritaria, no para elegir.»
- **Captura o diagrama:** el bloque de código de `config.py` con `RANDOM_STATE` y `CV_N_SPLITS`, o un esquema simple con la llave compartida.

## Diapositiva 2 · La accuracy engaña

- **Qué se ve:** tabla de la comparación de una temporada (2023-24, 359 partidos, 8 features):

  | Modelo | Accuracy | F1 macro |
  | --- | --- | --- |
  | reference (mayoritaria) | **0,443** | 0,102 |
  | random_forest | 0,228 | **0,180** |
  | xgboost | 0,262 | 0,177 |
  | lightgbm | 0,248 | 0,166 |

  La celda de 0,443 en rojo y la de 0,180 en verde.
- **Qué se dice:** «Si siempre acertáramos la clase 5, tendríamos un 44 % de aciertos en esa temporada y ganaríamos en accuracy. Por eso esa columna no decide. En F1 macro, que obliga a mirar las seis clases, la referencia cae a 0,102 y los modelos entrenados la superan. Random Forest queda primero con 0,180, seguido muy de cerca por XGBoost con 0,177: menos de la desviación de los folds, así que esa diferencia no decide nada por sí sola.»
- **Captura o diagrama:** la tabla; si cabe, una barra apilada con el 43,7 % de clase 5 de 2023-24 (sección 2.3).

## Diapositiva 3 · Qué acierta cada modelo

- **Qué se ve:** F1 por clase 0–5 de la misma tabla: reference `0 0 0 0 0 0,61`, random_forest `0,26 0,09 0,15 0,11 0,12 0,36`, xgboost `0,22 0,14 0,11 0,11 0,06 0,43`.
- **Qué se dice:** «La referencia solo puntúa en la clase 5. Los árboles reparten: Random Forest llega a 0,26 en victoria local clara y XGBoost a 0,43 en muchos goles. Ninguno arregla la clase 4, la más escasa, y las clases 2 y 3 siguen flojas. Es el límite de los datos y de las 8 features, no un fallo del entrenamiento. En el run original de la issue #6 eligimos XGBoost como candidato; al recalcular con las features definitivas la diferencia con Random Forest es de 0,003, dentro del ruido.»
- **Captura o diagrama:** la tabla de F1 por clase con la columna 4 marcada.

## Diapositiva 4 · De memorizar a generalizar

- **Qué se ve:** tabla antes/después de la rejilla de hiperparámetros (#7), ya con 9 temporadas:

  | | F1 macro validación | F1 macro train | Gap |
  | --- | --- | --- | --- |
  | Antes (default #6) | 0,180 | 0,685 | 0,5050 |
  | Después (rejilla) | 0,172 | 0,222 | **0,0496** |

  Línea de corte en 0,05. Al lado: «648 combinaciones · gap medido con F1 macro · estrictamente < 0,05».
- **Qué se dice:** «Con los parámetros por defecto el modelo sacaba 0,685 en train y 0,180 en validación: se lo sabía de memoria. Buscamos en una rejilla de 648 combinaciones y solo admitimos las que bajaban de 0,05 de diferencia en F1 macro. La elegida pierde un poco de F1, de 0,180 a 0,172, pero baja el gap de 0,505 a 0,0496. Preferimos un modelo algo peor que podamos defender, y si ninguna combinación cumple, el código falla en lugar de colarlo.»
- **Captura o diagrama:** dos barras de gap antes/después con la línea de 0,05.

## Diapositiva 5 · Lo que se entrega y sus límites

- **Qué se ve:** ficha del modelo final `tuned-xgb-2026-11-16`: 9 temporadas, 3.235 partidos útiles de 3.420, F1 macro **0,172 ± 0,012**, accuracy 0,179, gap 0,0496. Debajo, la referencia con las mismas temporadas: F1 macro 0,080. Al lado, dos cifras del [informe de métricas](../metrics-report.md): confusión más frecuente, clase 5 → clase 4 en 288 partidos; feature más importante, `avg_away_goals_last_5`.
- **Qué se dice:** «El modelo que usa la app es este XGBoost ajustado: duplica el F1 macro de la referencia con las mismas nueve temporadas y cumple el límite de overfitting. La tabla de la diapositiva 2 es de una sola temporada y sirve para comparar modelos; no es la cifra del modelo final. Ya cerramos la #8 con métricas fuera de fold: la clase 1 es la que más se pierde, la 4 es la que más se predice en falso, y la forma del visitante es la variable con más peso. La matriz completa y los ejemplos están en el informe.»
- **Captura o diagrama:** recorte de `models/model_card.json` con `metrics`, `before_tuning` y `training_data`, o un recorte de la matriz del informe.
