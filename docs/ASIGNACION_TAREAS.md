# Asignación de tareas — Kiniela Predictor, Equipo 2

**Repositorio**: https://github.com/IA-P1-BCN/kiniela-predictor-equipo2  
**Product Owner**: Mariana  
**Scrum Master**: Anna

El detalle verificable de cada issue está en [ISSUES.md](ISSUES.md). Este documento reparte el trabajo y los entregables.

## Anna — Scrum Master y Data & EDA Lead

Datos, variable objetivo, features y análisis exploratorio. También mantiene el tablero y las dailies.

| Issue | Entregable |
| --- | --- |
| #1 Preparación del dataset | CSV limpio en `data/raw` y `data/processed`, con la fuente documentada |
| #2 Variable objetivo | `src/kiniela/data/target.py` con las 6 clases y la distribución comentada |
| #3 Feature engineering | `src/kiniela/features/engineering.py` sin fuga de datos del partido actual |
| #4 EDA | `notebooks/01_eda.ipynb` con clases, correlación y goles |
| #18 Gestión | Issues creadas en GitHub, tablero al día y dailies con [DAILY_TEMPLATE.md](DAILY_TEMPLATE.md) |

Antes de cerrar el etiquetado, Anna escribe el umbral entre victoria clara y ajustada, y si un partido de 4+ goles pasa siempre a la clase 5.

## Cala — Modeling Lead

Baseline, ensembles, control de overfitting y el informe de métricas.

| Issue | Entregable |
| --- | --- |
| #5 Modelo baseline | Entrenamiento en `src/kiniela/models/train.py` con `StratifiedKFold` y semilla fija |
| #6 Modelos ensemble | XGBoost y LightGBM comparados contra el baseline con el mismo esquema |
| #7 Optimización | Hiperparámetros finales y diferencia train/validación inferior a 0.05 |
| #8 Informe de métricas | Accuracy, precision/recall/F1 por clase, matriz de confusión, importancia y errores |

Cala no cambia el significado de `target`. Si el desbalance impide una métrica justa, lo documenta y lo habla con Anna y Mariana.

## Eva — App & Backend Lead

Aplicación, contenedor, persistencia del feedback y despliegue.

| Issue | Entregable |
| --- | --- |
| #9 Aplicación Streamlit | `app/streamlit_app.py` muestra la clase y las 6 probabilidades |
| #10 Dockerización | `Dockerfile` que construye y arranca la app |
| #11 Base de datos y feedback | Predicción guardada y feedback de la persona usuaria, sin credenciales en el repo |
| #12 Despliegue | URL pública enlazada en el `README.md` |

Eva parte del esqueleto actual. El botón de predicción permanece desactivado hasta que exista un modelo en `models/`.

## Mariana — Product Owner, MLOps y redes neuronales

Red neuronal, drift, tests y la documentación de operación. Coordina el cierre documental.

| Issue | Entregable |
| --- | --- |
| #13 Red neuronal | Red de 6 salidas comparada con el mejor ensemble, mismo esquema de validación |
| #14 Data drift | `src/kiniela/monitoring/drift.py` con umbral y informe |
| #15 Tests | Suite en `tests/` para datos, predicciones y métricas; `pytest` en verde |
| #16 Documentación MLOps | Flujo de versiones, feedback y monitoreo en `docs/` |
| #17 Documentación y presentaciones | Informe técnico, presentación de negocio y presentación técnica, con el resto del equipo |

## Orden de trabajo

1. Anna deja datos, `target` y features.
2. Cala entrena y compara modelos.
3. Eva publica la app cuando hay un modelo elegido.
4. Mariana añade la red, el drift y los tests sobre el código ya estable.
5. El equipo cierra informe y presentaciones.

## Acuerdos

- Cada persona trabaja en ramas propias y abre pull request. `main` queda para lo ya revisado.
- No se suben datasets grandes, modelos entrenados, `.env` ni credenciales.
- Una issue se cierra solo cuando se cumplen sus criterios de aceptación.
