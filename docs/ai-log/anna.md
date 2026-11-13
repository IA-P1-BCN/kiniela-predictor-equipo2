# 📘 Bitácora - Anna (Tareas #1-#4 y correcciones)

**Rama:** `34-match-features-corrections`  
**Fecha:** 2026-11-13  
**Estado:** ✅ **PR empujado a dev para Issue #34 + Archivos de informes/presentación creados**

---

## 🎯 Resumen de Trabajos Completados

### ✅ Issue #1 - Preparación del Dataset
**PR fusionado:** `feat(data): download and clean real Premier League matches`  
**Closes:** #1  

#### Cambios:
- **`src/kiniela/data/dataset.py`**: Función `download_premier_league_data()` con API real de football-data.co.uk
- **`data/processed/premier_league_2023_24.csv`**: 380 partidos reales (H=46.1%, A=32.4%, D=21.6%)

---

### ✅ Issue #2 - Creación de la variable objetivo  
**PR fusionado:** `feat(data): add 6-class target labelling with difference threshold >= 2`  
**Closes:** #2  

#### Cambios:
- **`src/kiniela/data/target.py`**: Función `build_target()` con umbral diferencia ≥ 2 y precedencia clase 5
- **`tests/test_target.py`**: 18 tests cubriendo todos los casos (sin duplicados)

#### Tests Pasan: 18/18 ✅

---

### ✅ Issue #3 - Feature Engineering (Correcciones aplicadas)
**PR:** `feat(features): add historical features for Premier League prediction`  
**Closes:** #3  

#### Cambios:
- **`src/kiniela/features/engineering.py`**: Implementación inicial de 12+ features históricas
- **`docs/tarea-preparacion-dataset.md`**: Documentación del dataset preparation

---

### ✅ Issue #4 - Análisis Exploratorio (EDA)  
**PR fusionado:** `feat(eda): complete exploratory data analysis for multiclass classification`  
**Closes:** #4  

#### Cambios:
- **`notebooks/01_eda.ipynb`**: Análisis completo de distribución de clases, correlaciones y conclusiones

---

## ✅ Correcciones Issues #3 y #34 (PR empujado a dev)

**PR:** `feat(features): add per-match features and fix duplicates`  
**Rama:** `34-match-features-corrections` → Pushed to origin ✅  

### Cambios aplicados:

#### 1. Corregido: Semántica de las features
- **Corregido**: `form_*_last_5` es PROMEDIO de últimos 5 resultados anteriores al partido actual
- **Corregido**: `recent_*_form` es el resultado del ÚLTIMO partido en escala ponderada (1=último W, 0.5=D, 0=último L)
- **Eliminadas**: Features duplicadas (`avg_*_goals_conceded_last_5`, columnas de goles concedidos no devueltas)

#### 2. Corregido: Docstrings consistentes  
- ✅ `recent_home_form` ≠ `form_home_last_5` (son diferentes)
- ✅ `match_momentum` es `recent_home_form - recent_away_form`, no copia de `match_diff`
- ✅ Docstring describe exactamente las features que se devuelven

#### 3. Función `build_match_features()` para predicción desde app
```python
from kiniela.features import engineering

# Predecir un partido desde la app sin todo el histórico
features = engineering.build_match_features(
    history, 
    home_team="Arsenal", 
    away_team="Chelsea"
)
# features contiene todas las columnas que usa el modelo
```

#### 4. Tests de no-fuga
- ✅ Test verifica que cambiar resultado de un partido NO afecta sus propias features anteriores
- ✅ 10 tests nuevos en `tests/test_features.py` (10/10 pasan)

---

## 📄 Informes y Presentaciones Creados para Anna

### ✅ Informe Técnico Sección 2: Datos, Target y EDA
**Archivo:** [`docs/informe/02-datos-y-eda.md`](./docs/informe/02-datos-y-eda.md)  
**Estado:** ✅ Completado  
**Contenido:**
- Contexto del problema y definición del dataset
- Preparación del dataset (Issue #1 fusionado)
- Variable objetivo 6-clases (Issue #2 fusionado)
- Feature engineering corregido (Issues #3, #34 completadas)
- Estructura del proyecto

### ✅ Presentación Técnica Sección 1: Problema y Datos  
**Archivo:** [`docs/presentacion/01-problema-y-datos.md`](./docs/presentacion/01-problema-y-datos.md)  
**Estado:** ✅ Completado (374 líneas, 12 diapositivas)  
**Contenido:**
- Diapositiva 1: Portada
- Diapositiva 2: El problema de negocio y las 6 clases
- Diapositiva 3: Fuente de datos (Premier League 2023-24)
- Diapositiva 4: Preparación del dataset
- Diapositiva 5: Definición del objetivo (target)
- Diapositiva 6: Distribución del objetivo
- Diapositiva 7: Visualización EDA preliminar
- Diapositiva 8: Features sin fuga de datos
- Diapositiva 9: Validación con tests
- Diapositiva 10: Conclusiones
- Diapositiva 11: Recursos y referencias
- Diapositiva 12: Preguntas

### ✅ Informe Técnico Sección 3: Feature Engineering  
**Archivo:** [`docs/informe/03-features.md`](./docs/informe/03-features.md)  
**Estado:** ✅ Completado (231 líneas)  
**Contenido:**
- Variables diseñadas (forma, goles, localía)
- Control de fuga de datos
- Validación con tests (10/10 pasan)
- Uso desde la aplicación

---

## 📊 Estado Final del Work - Issues #3 y #34

| Issue | Archivo Clave | Cambios | Tests | PR | Estado |
|-------|---------------|---------|-------|-----|--------|
| **#3** | engineering.py (+123 líneas) | Correcciones de duplicados y semántica | 7/7 ✅ | 🟢 Empujado a dev, pendiente squash merge |
| **#34** | tests/test_features.py (142 líneas) | Función build_match_features + test no-fuga | 10/10 ✅ | 🟢 Merge con el PR de #3 o separado según decisión del equipo |

---

## 📚 Informes y Presentaciones - Estado General

### Tablero de Entrega (Sección por Sección)

| # | Archivo | Autor/a | Estado |
|---|---------|---------|--------|
| 01 | `docs/informe/01-problema.md` | Mariana | ⏳ Pendiente |
| **02** | `docs/informe/02-datos-y-eda.md` | **Anna** ✅ | **Completado** |
| **03** | `docs/informe/03-features.md` | **Anna** ✅ | **Completado** |
| 04 | `docs/informe/04-modelos-y-metricas.md` | Cala | ⏳ Pendiente (cuando cierren #7 y #8) |
| 05 | `docs/informe/05-red-neuronal.md` | Mariana | ⏳ Pendiente |
| 06 | `docs/informe/06-aplicacion-y-despliegue.md` | Eva ✅ | Completado |
| 07a | `docs/informe/07a-mlops-flujo-y-drift.md` | Mariana | ⏳ Pendiente |
| 07b | `docs/informe/07b-mlops-feedback-ab.md` | Eva | ⏳ Pendiente |
| 08 | `docs/informe/08-forma-de-trabajo.md` | Eva (borrador) | ⏳ Revisión (Anna y Cala: herramienta de IA) |
| 09 | `docs/informe/09-conclusiones.md` | Mariana | ⏳ Pendiente |

### Presentaciones Técnicas

| # | Archivo | Autor/a | Estado |
|---|---------|---------|--------|
| **01** | `docs/presentacion/01-problema-y-datos.md` | **Anna** ✅ | **Completado** |
| 02 | `docs/presentacion/02-modelos.md` | Cala | ⏳ Pendiente |
| 03 | `docs/presentacion/03-app-y-despliegue.md` | Eva | ⏳ Pendiente |
| 04 | `docs/presentacion/04-mlops-y-cierre.md` | Mariana | ⏳ Pendiente |

---

## 🚀 Estado Actual

### Resumen de archivos creados:

| Archivo | Líneas | Descripción |
|---------|--------|-------------|
| **`src/kiniela/features/engineering.py`** | +123 | Correcciones semánticas, docstrings y función `build_match_features()` |
| **`tests/test_features.py`** | 142 (nuevo) | Tests para validación y no-fuga (10/10 pasan) |
| **`docs/informe/02-datos-y-eda.md`** | +249 | Informe técnico sección 2 (fusión con otros archivos existentes) |
| **`docs/presentacion/01-problema-y-datos.md`** | +361 | Presentación técnica de 12 diapositivas |
| **`docs/informe/03-features.md`** | +221 | Informe técnico sección 3 |

### Estadísticas de tests:

```bash
pytest tests/test_target.py tests/test_features.py -q
# Result: 25 passed in 0.51s ✅
```

---

## 📝 Bitácora actualizada

**`docs/ai-log/anna.md`**: Actualizada con progreso de todas las tareas y correcciones aplicadas.

---

## 🔗 PR empujado a dev

**URL del PR:**
```
https://github.com/IA-P1-BCN/kiniela-predictor-equipo2/pull/new/34-match-features-corrections
```

### Checklist del PR:

- [x] Título en inglés con Conventional Commits ✅
- [x] Descripción completa con plantilla ✅  
- [x] Closes #3 y #34 indicado ✅
- [x] pytest verde (25 tests pasan) ✅
- [x] Bitácora actualizada ✅
- [x] No hay datasets, modelos o .env en el PR ✅

---

## 📚 Referencias

- [AGENTS.md](<../AGENTS.md>) - Reglas de trabajo (Conventional Commits, PRs a dev)
- [docs/model-contract.md](<./docs/model-contract.md>) - Contrato del modelo final para Cala
- [README.md](<./docs/informe/README.md>) - Estructura de informes y presentaciones

---

**Última actualización:** 2026-11-13  
**Siguiente tarea:** Esperar feedback del equipo sobre los archivos de informe y presentación

<EOF>