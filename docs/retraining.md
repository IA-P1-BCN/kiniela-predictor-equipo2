# Datos para reentrenar

Cada vez que alguien usa la app y dice cuál fue la **clase real** de un partido, tenemos un partido etiquetado nuevo. Este pipeline los saca de la base de datos para añadirlos al entrenamiento. Cubre el requisito del nivel medio del briefing: *pipeline de recolección de datos nuevos para reentrenamiento futuro*.

```text
App (feedback con clase real) ──► base de datos ──► export ──► data/raw/feedback/labelled_matches.csv
                                  (Neon o SQLite)               │
                                                                ▼
                         histórico + partidos nuevos ──► features (#3, #34) ──► entrenamiento (#5–#7)
```

## Ejecutarlo

```bash
python -m kiniela.storage.export                                  # todo lo nuevo
python -m kiniela.storage.export --since 2026-11-01               # solo desde una fecha (UTC)
python -m kiniela.storage.export --model-version reference-class-frequencies
python -m kiniela.storage.export --output otra/ruta.csv
```

- Lee la base de datos de `DATABASE_URL`. Sin ella, usa el SQLite local (`data/kiniela.db`).
- Para exportar de **producción (Neon)**, define la variable solo en tu terminal. No la escribas en ningún archivo versionado ni la pases como argumento, porque quedaría en el historial:

  ```bash
  set -a; source .env; set +a      # .env tiene DATABASE_URL y está en .gitignore
  python -m kiniela.storage.export
  ```

- **Es incremental.** Las filas cuyo `prediction_id` ya está en el CSV no se vuelven a escribir, así que se puede lanzar cada día sin duplicar partidos.
- El CSV va a `data/raw/feedback/`, que no se versiona: los datos recogidos no acaban en git.

## Qué se exporta

Solo las predicciones con feedback **y** clase real. Un «falló» sin clase real no sirve para entrenar, porque no dice cuál era la respuesta correcta. Si la persona dice que acertó, la app guarda como clase real la clase predicha.

| Columna | Qué es |
| --- | --- |
| `prediction_id` | Identificador de la predicción; evita duplicados |
| `Date` | Día de la predicción (UTC) |
| `HomeTeam`, `AwayTeam` | Equipos, con los mismos nombres que el dataset histórico |
| `target` | **Clase real (0-5)**: la etiqueta para entrenar. Mismo nombre de columna que usa `kiniela.models.train` |
| `predicted_class` | Lo que dijo el modelo |
| `is_correct` | Si acertó |
| `model_version` | Qué modelo hizo la predicción |
| `feedback_at` | Cuándo se dio el feedback |

## Cómo se usa para reentrenar

1. Ejecutar el export.
2. Añadir las filas al histórico de partidos. Tienen `HomeTeam`, `AwayTeam` y `Date`, como el dataset de la #1.
3. Calcular las features con el feature engineering (#3, #34). Las features de un partido se calculan con los partidos anteriores, así que las filas nuevas siguen sin fuga de datos.
4. Entrenar y validar como en las #5–#7.
5. Si el modelo nuevo mejora, promocionarlo (#35 y #37).

`predicted_class`, `is_correct` y `model_version` no son features: sirven para analizar los errores y para comparar modelos (A/B testing, #37).

## Precauciones

- **Calidad de la etiqueta.** La clase real la escribe una persona. Antes de reentrenar, conviene cruzarla con el resultado real del partido cuando esté en football-data.co.uk.
- **Fecha.** `Date` es el día en que se hizo la predicción, no el del partido. Mientras la app no pida la fecha del partido, hay que revisarla antes de mezclar las filas con el histórico.
