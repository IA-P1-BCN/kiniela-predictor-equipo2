# 7a. MLOps: versiones, promoción y data drift

**Quién:** Mariana · **Issues:** #16, #14 · **Estado:** escrita (13/11/2026)

El procedimiento operativo, con comandos, está en [docs/mlops.md](../mlops.md). Aquí va el relato del informe.

## Qué se versiona

Cada entrenamiento produce un artefacto `.joblib` con fecha en el nombre y una **tarjeta** (`models/model_card.json`: versión, métricas, features, semilla). Eso no entra en git. La app no carga cualquiera de esos archivos: solo `models/kiniela_model.joblib`.

Promocionar es **copiar a propósito** el candidato a ese path, después de comprobar el [contrato](../model-contract.md): `version` + `predict(local, visitante) → 6 probabilidades`. Si el archivo no existe, la app usa un modelo de prueba (frecuencias de clase) y lo dice en pantalla. Así Eva pudo desplegar sin esperar al modelo final.

## Feedback → reentrenar

La app guarda cada predicción y, si la persona indica la clase real, esa etiqueta se exporta con `python -m kiniela.storage.export` ([docs/retraining.md](../retraining.md)). El CSV es incremental. Eva documenta el detalle y el A/B en la [sección 7b](07b-mlops-feedback-ab.md).

## Drift

Antes de mezclar un lote nuevo con el entrenamiento se compara con PSI ([docs/drift.md](../drift.md)):

- umbral **0,20** por feature;
- drift global si **alguna** feature lo supera;
- comando `python -m kiniela.monitoring.drift`.

Si salta: primero se mira si el lote está mal generado; si el cambio es real, se reentrena y solo se promociona si el F1 macro mejora con el mismo `StratifiedKFold`.
