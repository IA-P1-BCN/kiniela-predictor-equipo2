# 7a. MLOps: versiones, promoción y data drift

**Quién:** Mariana · **Issues:** #16, #14 · **Estado:** escrita (16/11/2026)

El procedimiento operativo, con comandos, está en [docs/mlops.md](../mlops.md). El A/B y la regla de sustitución los detalla Eva en la [sección 7b](07b-mlops-feedback-ab.md) y en [docs/ab-testing.md](../ab-testing.md).

## Qué se versiona

Cada entrenamiento produce un candidato (`candidate_model.joblib` + ficha). La app solo carga `models/kiniela_model.joblib` y `model_card.json`.

**Esos dos archivos van en git.** Es la excepción de la #35: Render construye la imagen desde el repositorio; si el modelo y la ficha no están versionados, no llegan a producción. El resto de artefactos de entrenamiento sigue fuera de git.

## Cómo se promociona

No se copia el archivo a mano. Se lanza:

```bash
PYTHONPATH=src python -m kiniela.models.promote --dry-run
PYTHONPATH=src python -m kiniela.models.promote
```

El script aplica la regla (F1 macro, gap < 0,05, feedback mínimo). Si el candidato gana, archiva el actual y deja el candidato como modelo de la app. Después hay que commitear `kiniela_model.joblib` y `model_card.json` y desplegar.

Hasta que existan en el repo, la app usa un modelo de prueba (frecuencias de clase) y lo dice en pantalla. Así Eva pudo desplegar sin esperar al modelo final.

El objeto tiene que cumplir el [contrato](../model-contract.md): `version` + `predict(local, visitante) → 6 probabilidades`.

## Drift

Antes de mezclar un lote nuevo con el entrenamiento se compara con PSI ([docs/drift.md](../drift.md)), sobre las **8 features** de Anna (#58 / #61):

- umbral **0,20** por feature;
- drift global si **alguna** feature lo supera;
- comando `python -m kiniela.monitoring.drift`.

Si salta: primero se mira si el lote está mal generado; si el cambio es real, se reentrena y solo se promociona si `promote` lo permite.
