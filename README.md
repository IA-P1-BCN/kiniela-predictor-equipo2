# Kiniela Predictor — Equipo 2

Clasificación multiclase del tipo de resultado de un partido de fútbol para una kiniela. El modelo distingue seis situaciones, no solo local, empate o visitante.

**App desplegada**: https://kiniela-predictor.onrender.com  
**Repositorio**: https://github.com/IA-P1-BCN/kiniela-predictor-equipo2  
**Organización**: [IA-P1-BCN](https://github.com/IA-P1-BCN)  
**Tablero**: [GitHub Projects](https://github.com/orgs/IA-P1-BCN/projects/56)

Mientras no haya un modelo entrenado en `models/`, la app usa un modelo de prueba y lo avisa en pantalla.

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
app/                          Aplicación Streamlit
  streamlit_app.py            Entrada y navegación
  resources.py                Modelo, base de datos y equipos (en caché)
  views/                      Páginas: predecir e historial
src/kiniela/                  Código reutilizable
  config.py                   Clases y semilla
  data/                       Carga y variable objetivo
  features/                   Feature engineering
  models/                     Entrenamiento y predicción
  monitoring/                 Data drift
  storage/                    Predicciones y feedback (base de datos)
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
source .venv/bin/activate          # Windows (Git Bash): source .venv/Scripts/activate
pip install -r requirements-dev.txt
pytest
streamlit run app/streamlit_app.py
```

Las dependencias están en dos archivos:

| Archivo | Contenido | Quién lo usa |
| --- | --- | --- |
| `requirements.txt` | Lo que necesitan la app y el modelo para predecir | La imagen Docker y el despliegue |
| `requirements-dev.txt` | Lo anterior, más pytest, matplotlib, seaborn e ipykernel | Desarrollo local, notebooks y CI |

Una librería nueva va en `requirements.txt` solo si la app la necesita para predecir. Si no, va en `requirements-dev.txt`.

## Aplicación

```bash
streamlit run app/streamlit_app.py
```

Se abre en http://localhost:8501 y tiene dos páginas:

| Página | Qué hace |
| --- | --- |
| **Predecir** | Eliges el equipo local y el visitante (o un partido de ejemplo), y la app muestra la clase predicha con su nombre y las probabilidades de las 6 clases. La predicción se guarda, y después puedes decir si acertó y cuál fue la clase real |
| **Historial** | Las últimas 50 predicciones con su feedback, y el acierto según el feedback, para el modelo actual y para todos |

- Si eliges un equipo que falta, o el mismo equipo dos veces, la app muestra un mensaje y no predice.
- Si la base de datos falla, la predicción se muestra igualmente, con un aviso de que no se ha guardado.
- **Modelo de prueba.** Mientras no haya un modelo en `models/kiniela_model.joblib`, la app usa el reparto de clases observado en el dataset, igual para cualquier partido, y lo avisa en pantalla. El modelo real tiene que cumplir el [contrato del modelo](docs/model-contract.md).
- Los equipos salen del dataset de `data/processed/`. Si no está, como dentro de Docker, se usan los 20 equipos de la Premier 2023-24.

## Docker

```bash
docker build -t kiniela-predictor .
docker run --rm -p 8501:8501 --name kiniela kiniela-predictor
```

La app queda en http://localhost:8501.

| Comando | Para qué |
| --- | --- |
| `docker ps` | Ver si el contenedor está en marcha y si el healthcheck lo marca como `healthy` |
| `docker logs -f kiniela` | Ver los logs de la app |
| `docker stop kiniela` | Pararlo |
| `docker run --rm -p 8080:8080 -e PORT=8080 kiniela-predictor` | Cambiar el puerto, como hacen los servicios en la nube |

Detalles de la imagen:

- Parte de `python:3.12-slim` e instala solo `requirements.txt`.
- La app se ejecuta con un usuario sin privilegios, no como root.
- No incluye `.env`, datos, notebooks, tests ni entornos virtuales (ver `.dockerignore`). Los secretos se pasan al arrancar, con `-e` o `--env-file .env`.
- De `models/` solo entran el modelo promocionado (`kiniela_model.joblib`) y su ficha (`model_card.json`), si existen.

### Docker Compose (app + PostgreSQL)

Para probar en local igual que en producción, con PostgreSQL en vez de SQLite:

```bash
docker compose up --build      # http://localhost:8501
docker compose down            # parar (los datos se quedan)
```

## Despliegue

**URL pública:** https://kiniela-predictor.onrender.com (rama `dev`; si lleva un rato sin visitas, tarda alrededor de un minuto en despertar)

La app corre en Render (Docker, plan gratuito) y guarda las predicciones en PostgreSQL de Neon. Variables de entorno:

| Variable | Para qué | Dónde se define |
| --- | --- | --- |
| `DATABASE_URL` | Conexión a PostgreSQL (Neon) | Panel de Render; es secreta, nunca va en el repo |
| `PORT` | Puerto de la app | Lo pone Render |

Pasos, limitaciones del plan gratuito y cómo cambiar a `main`: [docs/deploy.md](docs/deploy.md).

## Base de datos

La app guarda cada predicción y el feedback de la persona usuaria.

- **En local** no hay que configurar nada: se usa SQLite en `data/kiniela.db`.
- **En producción** se usa PostgreSQL en Neon, con la variable `DATABASE_URL`. Las variables necesarias están en `.env.example`, sin valores reales.

El esquema y las métricas en tiempo real están en [docs/database.md](docs/database.md). Para sacar los partidos con su clase real y reentrenar: `python -m kiniela.storage.export` ([docs/retraining.md](docs/retraining.md)).

## Tests

```bash
pytest
```

Cubren el catálogo de clases, el etiquetado, la predicción, la base de datos y la app de punta a punta. La app se prueba con `AppTest` de Streamlit, sin navegador: predicción, entradas inválidas, feedback e historial.

## Documentación de trabajo

- [Issues](docs/ISSUES.md)
- [Asignación de tareas](docs/ASIGNACION_TAREAS.md)
- [Plantilla de daily](docs/DAILY_TEMPLATE.md)
- [Base de datos](docs/database.md)
- [Despliegue](docs/deploy.md)
- [Contrato del modelo](docs/model-contract.md)
- [Datos para reentrenar](docs/retraining.md)
- Plantilla de GitHub: `.github/ISSUE_TEMPLATE/tarea.md`
