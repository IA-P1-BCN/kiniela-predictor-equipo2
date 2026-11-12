# 📘 Bitácora Final - Anna (Tareas #1, #2, #3 y #4)

**Rama:** `dev`  
**Fecha:** 2026-11-12  
**Estado:** ✅ Tareas #1, #2, #3 y #4 completadas

---

## 🎯 Resumen de Trabajos Completados

### ✅ Issue #1 - Preparación del Dataset
**Título:** `feat(data): download and clean real Premier League matches`  
**Closes:** #1  

#### Cambios:
- **`src/kiniela/data/dataset.py`** (+58 líneas netas)
  - ✅ Nueva función `download_premier_league_data()` con API real de football-data.co.uk
  - ✅ Temporada 2324 (2023-24) con 380 partidos reales
  - ✅ Limpieza: elimina NaN, duplicados y normaliza nombres de equipos

- **`data/processed/premier_league_2023_24.csv`** (nuevo archivo)
  - ✅ Columnas principales: HomeTeam, AwayTeam, FTHG, FTAG, FTR

---

### ✅ Issue #2 - Creación de la variable objetivo  
**Título:** `feat(data): add 6-class target labelling with difference threshold >= 2`  
**Closes:** #2  

#### Cambios:
- **`src/kiniela/data/target.py`** (+58 líneas netas)
  - ✅ Implementación de `build_target()` con umbral diferencia ≥ 2
  - ✅ Precedencia absoluta de clase 5 (4+ goles totales)

- **`tests/test_target.py`** (+65 líneas netas, sin duplicados)
  - ✅ 18 tests que cubren todos los casos (sin duplicados)

#### Tests Pasan: 18/18 ✅

---

### ✅ Issue #3 - Feature Engineering  
**Título:** `feat(features): add historical features for Premier League prediction`  
**Closes:** #3  

#### Cambios:
- **`src/kiniela/features/engineering.py`** (+178 líneas netas)
  - ✅ Implementación de `build_features()` con 12+ features históricas
  - ✅ Manejo de datasets con/sin columna `Season`

---

### ✅ Issue #4 - Análisis Exploratorio (EDA)  
**Título:** `feat(eda): complete exploratory data analysis for multiclass classification`  
**Closes:** #4  

#### Cambios:
- **`notebooks/01_eda.ipynb`** (+257 líneas netas)
  - ✅ Análisis de distribución de las 6 clases (Clase 5 ~44%)
  - ✅ Correlación Spearman entre features y target
  - ✅ Análisis de goles por clase

---

## 📊 Estadísticas Finales

| Issue | Título | Estado | Archivos Clave |
|-------|--------|--------|-----------------|
| **#1 Datos reales** | Download & clean dataset | ✅ Completado | dataset.py, premier_league_2023_24.csv |
| **#2 Target** | 6-class target labelling | ✅ Completado | target.py, test_target.py |
| **#3 Features** | Historical features | ✅ Completado | engineering.py, tarea-preparacion-dataset.md |
| **#4 EDA** | Exploratory data analysis | ✅ Completado | notebooks/01_eda.ipynb |

---

## 📚 Referencias

- [AGENTS.md](<../AGENTS.md>) - Reglas de trabajo y convenciones  
- [docs/ISSUES.md](<../ISSUES.md>) - Backlog completo del proyecto