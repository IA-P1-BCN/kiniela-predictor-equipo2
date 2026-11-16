# Operación de modelos (MLOps)

Cómo se versiona un modelo, cómo entra en la app, qué pasa con el feedback y qué hacer si hay data drift. Una persona del equipo puede seguir este flujo sin explicación oral. Cubre la issue #16. El A/B y la promoción automática son la #37 ([docs/ab-testing.md](ab-testing.md)).

```text
entrenar (#5–#7, #13)
        │
        ▼
models/candidate_model.joblib  +  candidate_model_card.json
        │  comprobar el contrato
        │  (docs/model-contract.md)
        ▼
python -m kiniela.models.promote     ←  esto es promocionar (#37)
        │
        ▼
models/kiniela_model.joblib  +  model_card.json
        │  estos DOS van en git (excepción #35: Render construye desde el repo)
        ▼
la app carga load_predictor()
        │
        ├─ predicción + version ──► base de datos ──► feedback
        │                                              │
        │                    python -m kiniela.storage.export
        │                                              ▼
        │                         data/raw/feedback/labelled_matches.csv
        │                                              │
        └─ lote nuevo ──► python -m kiniela.monitoring.drift
                          (referencia = CSV de entrenamiento)
```

## 1. Versionar y promocionar

### Qué se guarda

| Archivo | Qué es | ¿En git? |
| --- | --- | --- |
| `models/<nombre>-<AAAA-MM-DD>.joblib` | Artefacto de entrenamiento (baseline, red…) | No |
| `models/candidate_model.joblib` + `candidate_model_card.json` | Candidato del A/B | Sí, cuando se prueba en Render |
| `models/kiniela_model.joblib` + `model_card.json` | **El** modelo que carga la app y su ficha | **Sí.** Excepción de la #35: Render construye la imagen desde el repo; si no están en git, no llegan a producción |
| `models/archive/<versión>/` | Modelo sustituido | Sí, si se quiere poder volver atrás |

El resto de `models/` sigue en `.gitignore`. Solo el promocionado, el candidato y las fichas son la excepción.

El objeto en `kiniela_model.joblib` tiene que cumplir el protocolo `Predictor`: atributo `version` (texto, por ejemplo `lgbm-2026-11-20`) y `predict(home_team, away_team) → 6 probabilidades`. Si no, `load_predictor()` falla. Detalle: [docs/model-contract.md](model-contract.md).

La clase del objeto tiene que vivir en `src/kiniela/`. `joblib` guarda la ruta de importación; un notebook no sirve.

### Cómo se promociona

No se copia el archivo a mano. El script aplica la regla de la #37 (F1 macro, gap < 0,05, suficiente feedback) y, si el candidato gana, mueve el actual a `archive/` y deja el candidato como `kiniela_model.joblib` / `model_card.json`.

1. Entrenar y validar con el mismo `StratifiedKFold` y `RANDOM_STATE` (`src/kiniela/config.py`), sobre las **8 features** de Anna (`FEATURE_COLUMNS` en `src/kiniela/features/engineering.py`).
2. Guardar el candidato como `models/candidate_model.joblib` y su ficha `candidate_model_card.json` (`f1_macro`, `overfitting_gap`, `version`).
3. Comprobar el contrato en local (`load_predictor` + `predicted_class`).
4. Opcional: A/B en la app con `AB_CANDIDATE_SHARE` ([docs/ab-testing.md](ab-testing.md)).
5. Decisión en seco, y promoción:

   ```bash
   PYTHONPATH=src python -m kiniela.models.promote --dry-run
   PYTHONPATH=src python -m kiniela.models.promote
   ```

6. **Commit de** `kiniela_model.joblib` **y** `model_card.json`, PR a `dev`, deploy en Render.

Hasta que exista ese archivo en el repo, la app usa el **modelo de prueba** (`ReferencePredictor`: frecuencias del dataset) y lo avisa en pantalla. No es un fallo: es el contrato.

Detalle de la regla y de los umbrales: Eva, [sección 7b](informe/07b-mlops-feedback-ab.md) y [docs/ab-testing.md](ab-testing.md).

## 2. Feedback y reentrenamiento

1. La persona predice un partido en la app.
2. La app guarda fecha, equipos, clase predicha, seis probabilidades y `model_version`.
3. Si dice si acertó y cuál fue la clase real, eso queda ligado a la predicción ([docs/database.md](database.md)).
4. `python -m kiniela.storage.export` saca solo las filas **con clase real** a `data/raw/feedback/labelled_matches.csv`, sin duplicar `prediction_id` ([docs/retraining.md](retraining.md)).
5. Esas filas se unen al histórico, se recalculan las 8 features **solo con partidos anteriores**, se entrena y se compara con el modelo actual.
6. Si el candidato cumple la regla de `promote`, se promociona (paso 1). Si no, se deja el modelo que ya está.

Un «falló» sin clase real no sirve para entrenar. Las credenciales (`DATABASE_URL`) salen de `.env` o del panel de Render, nunca del repo.

## 3. Monitoreo y data drift

Comparar el CSV de **entrenamiento** (referencia) con un **lote nuevo** que tenga las mismas 8 features de modelado:

```bash
PYTHONPATH=src python -m kiniela.monitoring.drift \
  --reference data/processed/premier_league_with_features_and_target.csv \
  --current data/processed/nuevo_lote.csv
```

Método: **PSI**, 10 bins de cuantiles de la referencia. Umbral: una feature tiene drift si `PSI >= 0.20`; el lote, si **alguna** feature lo supera. Código de salida `1` si hay drift, `0` si no. Detalle: [docs/drift.md](drift.md).

### Si salta la alerta

1. Mirar qué features tienen `YES`. ¿El lote es la misma competición y los mismos nombres de equipo?
2. Comprobar el pipeline: nulos, columnas cambiadas, temporada distinta, features calculadas con el partido actual (fuga).
3. Si el cambio es real, revisar el acierto en el historial de la app (por `model_version`).
4. Reentrenar con datos nuevos (paso 2) y promocionar solo si `promote` lo permite.
5. Si el lote está mal generado, no se promociona nada: se corrige el CSV y se vuelve a medir.

No hace falta un cron todavía. El comando se lanza cuando hay un lote nuevo (otra jornada, otro export) o antes de promocionar.

## Comandos

| Qué | Comando |
| --- | --- |
| Tests | `pytest` |
| Drift | `PYTHONPATH=src python -m kiniela.monitoring.drift --reference … --current …` |
| Export de etiquetas | `python -m kiniela.storage.export` |
| Promocionar | `python -m kiniela.models.promote` (`--dry-run` primero) |
| App | `streamlit run app/streamlit_app.py` |
