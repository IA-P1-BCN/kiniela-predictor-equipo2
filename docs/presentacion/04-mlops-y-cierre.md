# Presentación técnica · MLOps, red neuronal y cierre

**Presenta:** Mariana · **Duración:** unos 4 minutos · **6 diapositivas** · Detalle en las secciones 5, 7a y 9 del informe

---

## 1. La red, en las mismas reglas que los árboles

**Se ve:** MLP 32-16, 6 salidas, «mismo StratifiedKFold, misma semilla».

**Se dice:** «La red no tiene ligas aparte. Es un MLP de scikit-learn, con L2 y early stopping, medido con los mismos cinco folds que Random Forest, XGBoost y LightGBM. Si gana, se promociona; si no, el de Cala sigue siendo el candidato y la red queda como línea neuronal.»

**Dato:** `python -m kiniela.models.neural --dataset …`

## 2. Tabla (un recuadro)

**Se ve:** tres filas: mejor ensemble · red · dummy mayoritario. Columnas: accuracy y F1 macro.

**Se dice:** «Estas dos cifras salen del mismo CSV de modelado. F1 macro es la que decide, porque el acierto global premia la clase 5.»

**Hueco:** pegar las cifras del comando cuando Cala y el run oficial coincidan.

## 3. Contrato y promoción

**Se ve:** enchufe `Predictor`: `version` + 6 probabilidades → `models/kiniela_model.joblib`.

**Se dice:** «La app no importa un notebook. Carga un objeto con versión y predict. Promocionar es copiar ese objeto al path que ella lee. Si el archivo no está, usa frecuencias de clase y lo dice en pantalla. Por eso Eva pudo desplegar antes de que existiera el modelo final.»

## 4. Drift

**Se ve:** PSI ≥ 0,20 = drift; comando `python -m kiniela.monitoring.drift`.

**Se dice:** «Antes de mezclar un lote nuevo, comparamos las features con las del entrenamiento. Si alguna se mueve demasiado, paramos: o el CSV está mal, o hay que reentrenar. No hay un cron todavía; se lanza cuando hay jornada nueva o antes de promocionar.»

## 5. Feedback → reentrenar

**Se ve:** una flecha: app → clase real → export → features sin fuga → entrenar → promocionar si mejora.

**Se dice:** «Eva tiene el detalle. Yo me quedo con la regla: sin clase real no se entrena, y no se promociona un modelo que no gane en F1 macro con el mismo esquema.»

## 6. Cierre

**Se ve:** «Usable hoy · comparable · honesto con los límites».

**Se dice:** «Tenemos producto en la web, modelos medidos igual y un procedimiento para no mentirnos cuando los datos cambien. Lo que no tenemos es el marcador exacto ni un modelo final enchufado: ese es el siguiente merge, no una promesa de negocio.»
