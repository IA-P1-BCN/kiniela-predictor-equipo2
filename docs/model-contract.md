# Contrato del modelo

Qué tiene que cumplir el modelo final para que la app lo use **sin cambiar su código**. Va dirigido a quien entrena y promociona el modelo (#5–#8 y #13) y a quien calcula las features (#3).

## Qué carga la app

Al arrancar, la app llama a `kiniela.models.predict.load_predictor()`:

1. Si existe `models/kiniela_model.joblib`, lo carga con `joblib.load`.
2. Si no existe, usa el **modelo de prueba** (`ReferencePredictor`): el reparto de clases del dataset, igual para cualquier partido.

## Qué tiene que tener el objeto guardado

El objeto que se guarda en `models/kiniela_model.joblib` tiene que cumplir el protocolo `Predictor` de `src/kiniela/models/predict.py`:

```python
class Predictor(Protocol):
    version: str

    def predict(self, home_team: str, away_team: str) -> list[float]:
        """Return the probability of each class, in class order (0-5)."""
```

| Elemento | Requisito |
| --- | --- |
| `version` | Texto que identifica el modelo, por ejemplo `"lgbm-2026-11-20"`. Se guarda con cada predicción para comparar versiones en el historial |
| `predict(home_team, away_team)` | Recibe los nombres tal y como salen en el dataset procesado (`"man city"`, `"arsenal"`…) y devuelve **6 probabilidades** en el orden de las clases 0 a 5, no negativas y que sumen 1 |
| Errores | Si un equipo no existe o la entrada no es válida, lanza `ValueError` con un mensaje claro. La app lo muestra sin romperse |

En la práctica, el objeto envuelve dos cosas:

- **El cálculo de las features del partido** (#3): forma reciente, goles y localía, a partir del histórico y usando solo partidos anteriores, para que no haya fuga de datos.
- **El modelo entrenado**, que debe exponer `predict_proba` con las clases en orden 0-5.

```python
# Sketch only: the class lives in src/kiniela/models/ so joblib can load it in the app
class MatchModel:
    def __init__(self, pipeline, history, version):
        self.pipeline, self.history, self.version = pipeline, history, version

    def predict(self, home_team, away_team):
        features = build_match_features(self.history, home_team, away_team)  # from #3
        return self.pipeline.predict_proba(features)[0].tolist()
```

La clase tiene que estar en `src/kiniela/`. `joblib` guarda la ruta de importación del objeto y no lo podría cargar si la clase está definida en un notebook.

## Cómo comprobarlo

```python
from kiniela.models.predict import load_predictor, predicted_class

predictor = load_predictor()            # carga models/kiniela_model.joblib
probabilities = predictor.predict("arsenal", "chelsea")
predicted_class(probabilities)          # falla si no son 6 probabilidades válidas
```

`tests/test_predict.py` comprueba el contrato con un modelo guardado y con un objeto que no lo cumple.

## Junto al modelo

- `models/model_card.json`: versión, fecha, métricas de validación, features y `RANDOM_STATE`. Lo usará la documentación MLOps (#16). La regla de promoción lee `version`, `metrics.f1_macro` y `metrics.overfitting_gap` ([A/B testing](ab-testing.md)).
- Un modelo **candidato** para A/B testing usa el mismo contrato, con los nombres `candidate_model.joblib` y `candidate_model_card.json`.
- Solo estos dos archivos entran en la imagen Docker (ver `.dockerignore`).
