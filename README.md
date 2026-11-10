# Kiniela Predictor — Equipo 2 🏆

Clasificación multiclase del tipo de resultado de un partido de fútbol para una kiniela. El modelo distingue seis situaciones, no solo local, empate o visitante.

**Repositorio**: https://github.com/IA-P1-BCN/kiniela-predictor-equipo2  
**Organización**: [IA-P1-BCN](https://github.com/IA-P1-BCN)

## 📊 Estado Actual

### ✅ Issue #1: Preparación del Dataset - **EN PROGRESO**
**Asignado a**: Anna (Data & EDA Lead)  
**Progreso**: Archivos creados y documentados ⏳ Lista para ejecutar el script de descarga

| Archivo | Estado | Ubicación |
|---------|--------|-----------|
| `docs/tarea-preparacion-dataset.md` | ✅ Creado | Instrucciones completas |
| `src/preparacion_dataset.py` | ✅ Creado | Script de descarga y limpieza |
| `notebooks/01_preparacion_dataset.ipynb` | ✅ Creado | Notebook interactivo |
| `data/raw/` | ⏳ Pendiente | Para datos crudos descargados |
| `data/processed/` | ⏳ Pendiente | Para dataset limpio final |

**Cómo continuar**:
```bash
# 1. Activar entorno virtual (si no existe)
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 2. Instalar requisitos
pip install -r requirements.txt

# 3. Ejecutar script de preparación del dataset
python src/preparacion_dataset.py
```

**Resultado esperado**: Dataset de ~1,400-1,700 partidos de Premier League (2015-2024) listo en `data/processed/premier_league.csv`

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

## Equipo 👥

| Persona | Rol | Épicas |
| --- | --- | --- |
| Anna | Scrum Master + Data & EDA Lead | **📊 Datos, Feature Engineering y EDA** (Issues #1-#4) |
| Cala | Modeling Lead | Modelado, optimización y métricas (Issues #5-#8) |
| Eva | App & Backend Lead | Streamlit, Docker, base de datos y despliegue (Issues #9-#12) |
| Mariana | Product Owner + MLOps & Neural Networks Lead | Red neuronal, data drift, tests y MLOps (Issues #13-#16) |

La asignación está en [docs/ASIGNACION_TAREAS.md](docs/ASIGNACION_TAREAS.md). El backlog completo, en [docs/ISSUES.md](docs/ISSUES.md).  
📝 **Resumen Issue #1**: Ver [docs/RESUMEN_ISSUE_1.md](docs/RESUMEN_ISSUE_1.md)

## Tecnologías 🛠️

- Python 3.12
- pandas y NumPy para los datos
- scikit-learn, XGBoost y LightGBM para los modelos tabulares
- Streamlit para la aplicación
- Docker para empaquetar la app
- pytest para los tests

La red neuronal se añade en la issue correspondiente, cuando el baseline ya sea comparable.

## Estructura 📁

```text
kiniela-predictor-equipo2/
├── app/streamlit_app.py          # Aplicación Streamlit
├── src/
│   ├── preparacion_dataset.py    # Script Issue #1 (nuevo ✅)
│   └── kiniela/                  # Código reutilizable (en desarrollo)
│       ├── config.py             # Clases y semilla
│       ├── data/                 # Carga y variable objetivo
│       ├── features/             # Feature engineering
│       ├── models/               # Entrenamiento y predicción
│       └── monitoring/           # Data drift
├── notebooks/
│   ├── 01_preparacion_dataset.ipynb  # EDA Issue #1 (nuevo ✅)
│   ├── 02_features.ipynb     # Feature engineering
│   └── 03_modelado.ipynb     # Modelado
├── data/
│   ├── raw/           # Datos de origen (no se versionan)
│   └── processed/     # Dataset de modelado (no se versiona)
├── models/            # Artefactos entrenados (no se versionan)
├── tests/             # Tests
├── docs/              # Backlog, tareas y dailies
│   ├── ASIGNACION_TAREAS.md
│   ├── ISSUES.md
│   ├── DAILY_TEMPLATE.md
│   └── RESUMEN_ISSUE_1.md      # Resumen Issue #1 (nuevo ✅)
├── .gitignore
├── Dockerfile
├── pytest.ini
└── requirements.txt
```

## 📋 Backlog de Issues

| # | Título | Asignado a | Épica | Estado |
|---|--------|-----------|-------|--------|
| 1 | **Preparación del Dataset** | **Anna** | Datos | 🟠 En Progreso (archivos creados) |
| 2 | Creación de la variable objetivo | Anna | Datos | ⏳ Depende de #1 |
| 3 | Feature engineering | Anna | Datos | ⏳ Depende de #1, #2 |
| 4 | Análisis exploratorio (EDA) | Anna | EDA | ⏳ Depende de #2, #3 |
| 5 | Modelo baseline | Cala | Modelado | ⏳ Depende de #2, #3 |
| 6 | Modelos ensemble | Cala | Modelado | ⏳ Depende de #5 |
| 7 | Optimización y control de overfitting | Cala | Modelado | ⏳ Depende de #6 |
| 8 | Informe de métricas | Cala | Métricas | ⏳ Depende de #7 |
| 9 | Aplicación Streamlit | Eva | App | ⏳ Depende de #8 |
| 10 | Dockerización | Eva | DevOps | ⏳ Depende de #9 |
| 11 | Base de datos y feedback | Eva | Datos/App | ⏳ Depende de #9 |
| 12 | Despliegue | Eva | DevOps | ⏳ Depende de #10, #11 |
| 13 | Red neuronal | Mariana | MLOps | ⏳ Depende de #5, #6 |
| 14 | Monitoreo de data drift | Mariana | MLOps | ⏳ Depende de #3 |
| 15 | Tests unitarios | Mariana | Testing | ⏳ Depende de #2, #8 |
| 16 | Documentación MLOps | Mariana | MLOps | ⏳ Depende de #11, #13-#15 |
| 17 | Documentación y presentaciones | Todo el equipo | Docs | ⏳ Depende de #8, #12, #16 |
| 18 | Gestión del proyecto | Anna (Scrum Master) | Gestión | 🔴 Activa |

## Puesta en marcha 🚀

### Configuración inicial
```bash
# 1. Crear entorno virtual
python -m venv .venv

# 2. Activar entorno
source .venv/bin/activate        # Mac/Linux
# o
.venv\Scripts\activate            # Windows

# 3. Instalar requisitos
pip install -r requirements.txt

# 4. Verificar instalación
python -c "import pandas; print(pandas.__version__)"
```

### Ejecutar Issue #1 (Preparación del Dataset)
```bash
# Descargar y limpiar datos de Premier League
python src/preparacion_dataset.py
```

### Ejecutar Tests
```bash
pytest
```

### Lanzar Aplicación Streamlit
```bash
streamlit run app/streamlit_app.py
```
La app queda en http://localhost:8501. El botón de predicción permanece desactivado hasta que haya un modelo en `models/`.

## Docker 🐳

```bash
docker build -t kiniela-predictor .
docker run --rm -p 8501:8501 kiniela-predictor
```

La app queda en http://localhost:8501.

## Documentación de trabajo 📚

- [Issues](docs/ISSUES.md) - Backlog completo con criterios de aceptación
- [Asignación de tareas](docs/ASIGNACION_TAREAS.md) - Roles y responsabilidades del equipo
- [Plantilla de daily](docs/DAILY_TEMPLATE.md) - Formato para dailies
- [Resumen Issue #1](docs/RESUMEN_ISSUE_1.md) - Estado actual y siguientes pasos

**Plantilla de GitHub**: `.github/ISSUE_TEMPLATE/tarea.md`

## 📈 Próximos Hitos

- ✅ **Hito 1**: Preparación del dataset (archivos creados, lista para ejecutar)
- ⏳ **Hito 2**: Creación de variable objetivo con 6 clases Kiniela
- ⏳ **Hito 3**: Feature engineering y EDA completo
- ⏳ **Hito 4**: Modelo baseline entrenado

---

<div align="center">
  <strong>🏆 Equipo Kiniela Predictor - Factoria Madrid x IA-P1-BCN</strong>
</div>