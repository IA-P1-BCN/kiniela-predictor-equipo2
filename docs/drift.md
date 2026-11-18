# Data drift

Compara las features de modelado del **conjunto de referencia** (los datos de entrenamiento) con un **lote nuevo**. Cubre la issue #14.

## Método y umbral

El detector usa el **Population Stability Index (PSI)** de cada feature numérica, con 10 intervalos definidos por los cuantiles del conjunto de referencia. La media y la desviación de cada feature se imprimen como contexto; **no** deciden el aviso.

| PSI | Lectura |
| --- | --- |
| < 0.10 | Sin cambio material |
| 0.10 – 0.20 | Cambio leve, vigilar |
| ≥ **0.20** | Drift |

- **Por feature:** hay drift si `PSI >= 0.20`.
- **Global:** hay drift si **alguna** feature supera ese umbral.

Los umbrales viven en `src/kiniela/monitoring/drift.py` (`PSI_DRIFT_THRESHOLD`).

## Cómo ejecutarlo

Desde la raíz del repositorio, con el entorno virtual activo:

```bash
PYTHONPATH=src python -m kiniela.monitoring.drift \
  --reference data/processed/premier_league_with_features_and_target.csv \
  --current data/processed/nuevo_lote.csv
```

- `--reference`: CSV de entrenamiento, el mismo que usan las issues #5–#13 (features numéricas de la #3).
- `--current`: lote nuevo con **las mismas columnas** de features.

El proceso imprime una tabla con PSI, media de referencia, media actual y el aviso global. El código de salida es `0` si no hay drift y `1` si lo hay, para poder usarlo en un script o en CI.

Desde Python:

```python
from kiniela.monitoring import compute_drift, format_drift_report

report = compute_drift("data/processed/train.csv", "data/processed/nuevo.csv")
print(format_drift_report(report, "train.csv", "nuevo.csv"))
print(report.drifted, report.to_dict())
```

## Qué hacer si salta el aviso

1. Mirar qué features tienen `YES` y si el lote nuevo es comparable (misma competición, mismos nombres de equipos).
2. Confirmar que no hay un error de pipeline (nulos, columnas cambiadas, temporada distinta).
3. Si el cambio es real, revisar métricas del modelo y, si hace falta, reentrenar con [docs/retraining.md](retraining.md).

El flujo de versiones y de alerta queda descrito en la documentación MLOps (#16).
