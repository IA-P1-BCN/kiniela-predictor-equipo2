# Base de datos: predicciones y feedback

La app guarda cada predicción y el feedback de la persona usuaria. Sirve para tres cosas: consultar el historial, medir cuánto acierta el modelo en producción y reunir datos para reentrenarlo.

El código está en `src/kiniela/storage/`:

| Archivo | Qué hace |
| --- | --- |
| `database.py` | Conexión: elige la base de datos con `DATABASE_URL` |
| `models.py` | Las dos tablas |
| `repository.py` | Guardar y consultar: `save_prediction`, `save_feedback`, `list_history`, `feedback_stats` |

## Qué base de datos se usa

Se elige con la variable de entorno `DATABASE_URL`. No hay credenciales en el código ni en el repositorio.

| Entorno | `DATABASE_URL` | Base de datos |
| --- | --- | --- |
| Local, tests y Docker | sin definir | SQLite en `data/kiniela.db` (ignorado por git) |
| Producción | cadena de conexión de Neon | PostgreSQL en [Neon](https://neon.tech), plan gratuito |

- Para usar otra base de datos en local, copia `.env.example` a `.env` y rellena `DATABASE_URL`. Con Docker: `docker run --env-file .env ...`.
- Neon da URLs que empiezan por `postgresql://`; el código las adapta al driver `psycopg` que instala el proyecto.
- Neon apaga la base de datos cuando no se usa. `pool_pre_ping` reconecta solo en la primera petición.
- En Docker sin `DATABASE_URL`, la base SQLite vive dentro del contenedor y **se pierde al borrarlo**. Por eso en producción siempre se usa Neon.

Las tablas se crean solas al arrancar (`init_db`). Si el esquema cambia más adelante, habrá que añadir migraciones.

## Esquema

```text
predictions                                   feedback
─────────────────────────────────────         ──────────────────────────────────────
id               entero, PK                   id              entero, PK
created_at       fecha y hora (UTC)           prediction_id   FK → predictions.id, único
model_version    texto                        created_at      fecha y hora (UTC)
home_team        texto                        is_correct      booleano
away_team        texto                        actual_class    entero 0-5, opcional
inputs           JSON                         comment         texto, opcional
predicted_class  entero 0-5
prob_0 … prob_5  decimal
```

### `predictions`

Una fila por predicción.

| Columna | Por qué |
| --- | --- |
| `model_version` | Qué modelo hizo la predicción. Permite comparar versiones (A/B testing) y vigilar cada una por separado |
| `inputs` | Las features que recibió el modelo, en JSON. Así el conjunto de features (#3) puede cambiar sin tocar la tabla |
| `predicted_class` | Clase con mayor probabilidad. No se escribe a mano: se calcula a partir de las probabilidades |
| `prob_0` … `prob_5` | Una columna por clase, en lugar de un JSON, para poder filtrar y agregar en SQL (por ejemplo, la confianza media por clase) |

Restricción: `predicted_class` entre 0 y 5.

### `feedback`

Como mucho una fila por predicción.

| Columna | Por qué |
| --- | --- |
| `is_correct` | Lo mínimo que puede decir la persona usuaria: ¿acertó? |
| `actual_class` | La clase real, si se conoce el resultado. Es la etiqueta que se usará para reentrenar |
| `comment` | Comentario libre, de 1.000 caracteres como máximo |

Restricciones:

- `actual_class` entre 0 y 5, o vacío.
- `prediction_id` único: una predicción no puede tener dos veredictos.
- Si se borra una predicción, se borra su feedback.
- Si se indica `actual_class`, tiene que cuadrar con `is_correct`. Esto lo comprueba `save_feedback`.

## Métricas en tiempo real

`feedback_stats(session, model_version=None)` devuelve:

| Clave | Significado |
| --- | --- |
| `predictions` | Predicciones hechas |
| `with_feedback` | Cuántas tienen feedback |
| `correct` | Cuántas acertaron, según el feedback |
| `accuracy` | `correct / with_feedback`, o `None` si todavía no hay feedback |

Con `model_version` se calculan solo para ese modelo.

## Ejemplo

```python
from kiniela.storage import get_engine, init_db, session_scope, save_prediction, save_feedback

engine = get_engine()   # lee DATABASE_URL
init_db(engine)

with session_scope(engine) as session:   # confirma al salir; si hay error, deshace
    prediction = save_prediction(
        session,
        home_team="Arsenal",
        away_team="Chelsea",
        inputs={"home_form": 2.1, "away_form": 1.4},
        probabilities=[0.1, 0.5, 0.1, 0.1, 0.1, 0.1],
        model_version="v1",
    )

with session_scope(engine) as session:
    save_feedback(session, prediction.id, is_correct=False, actual_class=2)
```

## Consultas útiles

```sql
-- Acierto por versión de modelo
SELECT p.model_version, COUNT(f.id) AS con_feedback, AVG(CASE WHEN f.is_correct THEN 1.0 ELSE 0 END) AS accuracy
FROM predictions p JOIN feedback f ON f.prediction_id = p.id
GROUP BY p.model_version;

-- Ejemplos etiquetados para reentrenar
SELECT p.inputs, f.actual_class
FROM predictions p JOIN feedback f ON f.prediction_id = p.id
WHERE f.actual_class IS NOT NULL;
```
