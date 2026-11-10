# Kiniela Predictor — Equipo 2

Clasificación multiclase del tipo de resultado de un partido de fútbol para una kiniela. El modelo distingue seis situaciones, no solo local, empate o visitante.

**Repositorio**: https://github.com/IA-P1-BCN/kiniela-predictor-equipo2  
**Organización**: [IA-P1-BCN](https://github.com/IA-P1-BCN)

Esta versión es la base del proyecto. No incluye dataset ni modelo entrenado.

## Clases

| Clase | Significado |
| --- | --- |
| 0 | Victoria local clara |
| 1 | Victoria local ajustada |
| 2 | Empate |
| 3 | Victoria visitante ajustada |
| 4 | Victoria visitante clara |
| 5 | Partido de muchos goles (4+ goles) |

El umbral entre victoria clara y ajustada, y la precedencia de la clase 5, se cierran en la issue de etiquetado antes de entrenar.

## Equipo

| Persona | Rol |
| --- | --- |
| Anna | Scrum Master y Data & EDA Lead |
| Cala | Modeling Lead |
| Eva | App & Backend Lead |
| Mariana | Product Owner y MLOps & Neural Networks Lead |

La asignación está en [docs/ASIGNACION_TAREAS.md](docs/ASIGNACION_TAREAS.md). El backlog, en [docs/ISSUES.md](docs/ISSUES.md).

## Tecnologías

- Python 3.12
- pandas y NumPy para los datos
- scikit-learn, XGBoost y LightGBM para los modelos tabulares
- Streamlit para la aplicación
- Docker para empaquetar la app
- pytest para los tests

La red neuronal se añade en la issue correspondiente, cuando el baseline ya sea comparable.

## Estructura

```text
app/streamlit_app.py          Aplicación
src/kiniela/                  Código reutilizable
  config.py                   Clases y semilla
  data/                       Carga y variable objetivo
  features/                   Feature engineering
  models/                     Entrenamiento y predicción
  monitoring/                 Data drift
notebooks/                    EDA, features y modelado
data/raw/                     Datos de origen (no se versionan)
data/processed/               Dataset de modelado (no se versiona)
models/                       Artefactos entrenados (no se versionan)
tests/                        Tests
docs/                         Backlog, tareas y dailies
```

## Puesta en marcha

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest
streamlit run app/streamlit_app.py
```

La pantalla abre las seis clases. El botón de predicción permanece desactivado hasta que haya un modelo en `models/`.

## Docker

```bash
docker build -t kiniela-predictor .
docker run --rm -p 8501:8501 kiniela-predictor
```

La app queda en http://localhost:8501.

## Tests

```bash
pytest
```

Hoy cubren el catálogo de clases, la validación de goles y la elección de la clase más probable. El etiquetado completo sigue pendiente de la regla de negocio.

## Documentación de trabajo

- [Issues](docs/ISSUES.md)
- [Asignación de tareas](docs/ASIGNACION_TAREAS.md)
- [Plantilla de daily](docs/DAILY_TEMPLATE.md)
- Plantilla de GitHub: `.github/ISSUE_TEMPLATE/tarea.md`
