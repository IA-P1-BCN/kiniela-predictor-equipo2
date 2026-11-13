# Operación de modelos (MLOps)

Cómo se versiona un modelo, cómo entra en la app, qué pasa con el feedback y qué hacer si hay data drift. Una persona del equipo puede seguir este flujo sin explicación oral. Cubre la issue #16. El detalle de Eva (export y A/B) está enlazado, no duplicado.

```text
entrenar (#5–#7, #13)
        │
        ▼
models/<nombre>-<fecha>.joblib     +  models/model_card.json
        │  comprobar el contrato
        │  (docs/model-contract.md)
        ▼
copiar a models/kiniela_model.joblib     ←  esto es promocionar
        │
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
| `models/<nombre>-<AAAA-MM-DD>.joblib` | Artefacto entrenado (baseline, LightGBM, red…) | No. `models/*` está en `.gitignore` salvo `.gitkeep` |
| `models/model_card.json` | Versión, fecha, métricas, features y `RANDOM_STATE` | No (viaja con el modelo en Docker) |
| `models/kiniela_model.joblib` | **El** modelo que carga la app | No. Solo entra en la imagen Docker |

El objeto en `kiniela_model.joblib` tiene que cumplir el protocolo `Predictor`: atributo `version` (texto, por ejemplo `lgbm-2026-11-20`) y `predict(home_team, away_team) → 6 probabilidades`. Si no, `load_predictor()` falla. Detalle: [docs/model-contract.md](model-contract.md).

La clase del objeto tiene que vivir en `src/kiniela/`. `joblib` guarda la ruta de importación; un notebook no sirve.

### Cómo se promociona

1. Entrenar y validar con el mismo `StratifiedKFold` y `RANDOM_STATE` (`src/kiniela/config.py`).
2. Guardar el artefacto en un path **que no sea** `kiniela_model.joblib` (el baseline ya se niega a pisar ese archivo).
3. Comprobar el contrato en local:

   ```python
   from kiniela.models.predict import load_predictor, predicted_class
   predictor = load_predictor("models/candidato.joblib")
   predicted_class(predictor.predict("arsenal", "chelsea"))
   ```

4. Escribir `models/model_card.json` con versión, fecha, accuracy, F1 macro, F1 por clase, lista de features y semilla.
5. Copiar el candidato a `models/kiniela_model.joblib`.
6. Arrancar la app y hacer una predicción. En el historial tiene que aparecer la `version` nueva.
7. Desplegar (Render reconstruye la imagen; solo esos dos archivos de `models/` entran, ver `.dockerignore`).

Hasta que exista ese archivo, la app usa el **modelo de prueba** (`ReferencePredictor`: frecuencias del dataset) y lo avisa en pantalla. No es un fallo: es el contrato.

La sustitución automática entre dos modelos en producción es la issue #37 (Eva, sección 7b). Mientras tanto, promocionar es copiar el archivo a propósito.

## 2. Feedback y reentrenamiento

1. La persona predice un partido en la app.
2. La app guarda fecha, equipos, clase predicha, seis probabilidades y `model_version`.
3. Si dice si acertó y cuál fue la clase real, eso queda ligado a la predicción ([docs/database.md](database.md)).
4. `python -m kiniela.storage.export` saca solo las filas **con clase real** a `data/raw/feedback/labelled_matches.csv`, sin duplicar `prediction_id` ([docs/retraining.md](retraining.md)).
5. Esas filas se unen al histórico, se recalculan features **solo con partidos anteriores**, se entrena y se compara con el modelo actual.
6. Si mejora en F1 macro con el mismo esquema de validación, se promociona (paso 1). Si no, se deja el modelo que ya está.

Un «falló» sin clase real no sirve para entrenar. Las credenciales (`DATABASE_URL`) salen de `.env` o del panel de Render, nunca del repo.

## 3. Monitoreo y data drift

Comparar el CSV de **entrenamiento** (referencia) con un **lote nuevo** que tenga las mismas features de modelado:

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
4. Reentrenar con datos nuevos (paso 2) y promocionar solo si el modelo nuevo gana.
5. Si el lote está mal generado, no se promociona nada: se corrige el CSV y se vuelve a medir.

No hace falta un cron todavía. El comando se lanza cuando hay un lote nuevo (otra jornada, otro export) o antes de promocionar.

## Comandos

| Qué | Comando |
| --- | --- |
| Tests | `pytest` |
| Drift | `PYTHONPATH=src python -m kiniela.monitoring.drift --reference … --current …` |
| Export de etiquetas | `python -m kiniela.storage.export` |
| App | `streamlit run app/streamlit_app.py` |
