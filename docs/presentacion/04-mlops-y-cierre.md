# Presentación técnica · MLOps, red neuronal y cierre

**Presenta:** Mariana · **Duración:** unos 4 minutos · **6 diapositivas** · Detalle en las secciones 5, 7a y 9 del informe

---

## 1. La red, en las mismas reglas que los árboles

**Se ve:** MLP 32-16, 6 salidas, «mismo StratifiedKFold, misma semilla».

**Se dice:** «La red no tiene ligas aparte. Es un MLP de scikit-learn, con L2 y early stopping, medido con los mismos cinco folds que Random Forest, XGBoost y LightGBM. Si gana, se promociona; si no, el de Carla sigue siendo el candidato y la red queda como línea neuronal.»

**Dato:** mismo comando, 8 features, 359 filas: RF F1 macro 0.180 · red 0.129 · dummy accuracy 0.443.

## 2. Tabla (un recuadro)

**Se ve:** tres filas: mejor ensemble · red · dummy mayoritario. Columnas: accuracy y F1 macro.

**Se dice:** «Estas dos cifras salen del mismo CSV de modelado. F1 macro es la que decide, porque el acierto global premia la clase 5.»

**Cifras del run (16/11):** mejor ensemble RF 0.180 F1 · red 0.129 F1 / 0.354 acc · dummy 0.443 acc / 0.102 F1.

## 3. Contrato y promoción

**Se ve:** enchufe `Predictor` y el comando `python -m kiniela.models.promote`.

**Se dice:** «La app no importa un notebook. Carga un objeto con versión y predict. Promocionar no es copiar a mano: el script de la #37 decide si el candidato gana y deja `kiniela_model.joblib` más su ficha. Esos dos van en git, porque Render construye desde el repo. Si no están, usa frecuencias de clase y lo dice en pantalla.»

## 4. Drift

**Se ve:** PSI ≥ 0,20 = drift; comando `python -m kiniela.monitoring.drift`.

**Se dice:** «Antes de mezclar un lote nuevo, comparamos las features con las del entrenamiento. Si alguna se mueve demasiado, paramos: o el CSV está mal, o hay que reentrenar. No hay un cron todavía; se lanza cuando hay jornada nueva o antes de promocionar.»

## 5. Feedback → reentrenar

**Se ve:** una flecha: app → clase real → export → features sin fuga → entrenar → promocionar si mejora.

**Se dice:** «Eva tiene el detalle. Yo me quedo con la regla: sin clase real no se entrena, y no se promociona un modelo que no gane en F1 macro con el mismo esquema.»

## 6. Cierre

**Se ve:** «Usable hoy · comparable · honesto con los límites».

**Se dice:** «Tenemos producto en la web, modelos medidos igual y un procedimiento para no mentirnos cuando los datos cambien. Lo que no tenemos es el marcador exacto ni un modelo final enchufado: ese es el siguiente merge, no una promesa de negocio.»
