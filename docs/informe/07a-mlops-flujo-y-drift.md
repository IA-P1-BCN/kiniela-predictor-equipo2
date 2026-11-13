# 7a. MLOps: versiones, promoción y data drift

**Quién:** Mariana · **Issues:** #16, #14 · **Estado:** esquema (el texto largo va con la #16)

## Cubrir

- Qué se guarda de un modelo (`version`, `predict`, `model_card.json`) y cómo se promociona a `models/kiniela_model.joblib` ([contrato](../model-contract.md)).
- Cómo se detecta drift: PSI, umbral 0,20, comando `python -m kiniela.monitoring.drift` ([docs/drift.md](../drift.md)).
- Qué hacer si salta la alerta (revisar lote, pipeline, reentrenar).
- Relación con 7b: el feedback no se documenta aquí.
