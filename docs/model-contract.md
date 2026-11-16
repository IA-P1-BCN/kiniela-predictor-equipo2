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

El modelo final es `MatchPredictor` ([`src/kiniela/models/final.py`](../src/kiniela/models/final.py), #35). Guarda el XGBoost entrenado y el histórico de partidos jugados, y en cada predicción calcula las features con `build_match_features`, **la misma función del entrenamiento** (#34).

La clase tiene que estar en `src/kiniela/`. `joblib` guarda la ruta de importación del objeto y no lo podría cargar si la clase está definida en un notebook, o si se guarda desde un script lanzado con `python -m` sin cuidado (quedaría como `__main__`). `final.py` lo evita y lo comprueba un test.

## El modelo final (#35)

Se entrena y se guarda con un comando, desde la raíz del repo:

```bash
PYTHONPATH=src python -m kiniela.models.final            # descarga 2015-16 a 2023-24
PYTHONPATH=src python -m kiniela.models.final --matches data/raw/<archivo>.csv
```

1. Descarga las 9 temporadas con la función de datos de la #1, les añade la columna `Season` y deja una copia en `data/raw/` (no se versiona).
2. Calcula las features (#3, #34) y el `target` (#2).
3. Vuelve a lanzar la búsqueda de hiperparámetros de la #7 (`tune_model`: mismo `StratifiedKFold`, `RANDOM_STATE` y gap < 0,05), así los hiperparámetros siempre corresponden a las features actuales.
4. Escribe `models/kiniela_model.joblib` y `models/model_card.json`.

**Por qué 9 temporadas:** con solo 2023-24 (359 partidos útiles), únicamente 2 de 648 combinaciones cumplían el gap, y la elegida no superaba al modelo de prueba (F1 macro 0,095 frente a 0,102). Con 2015-16 a 2023-24 (3.235 partidos útiles) lo cumplen 496 y el F1 macro dobla al del modelo de prueba. Las cifras exactas están en la ficha.

El modelo solo acepta los equipos de la **última temporada**: un equipo descendido no tiene historial en ella y su predicción no tendría sentido.

**Excepción documentada:** `kiniela_model.joblib` y `model_card.json` sí se versionan (ver `.gitignore`), porque Render construye la imagen Docker desde el repo. El resto de `models/` no.

## Cómo comprobarlo

```python
from kiniela.models.predict import load_predictor, predicted_class

predictor = load_predictor()            # carga models/kiniela_model.joblib
probabilities = predictor.predict("arsenal", "chelsea")
predicted_class(probabilities)          # falla si no son 6 probabilidades válidas
```

`tests/test_predict.py` comprueba el contrato con un modelo guardado y con un objeto que no lo cumple. `tests/test_final.py` comprueba el modelo final: el contrato, que usa las features del entrenamiento, la ficha y el artefacto versionado en `models/`.

## Junto al modelo

- `models/model_card.json`: versión, fecha, métricas de validación, features y `RANDOM_STATE`. Lo usará la documentación MLOps (#16). La regla de promoción lee `version`, `metrics.f1_macro` y `metrics.overfitting_gap` ([A/B testing](ab-testing.md)).
- Un modelo **candidato** para A/B testing usa el mismo contrato, con los nombres `candidate_model.joblib` y `candidate_model_card.json`.
- Solo estos dos archivos entran en la imagen Docker (ver `.dockerignore`).
