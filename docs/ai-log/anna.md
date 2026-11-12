# 📘 Bitácora Final - Anna (Tareas #1, #2, #3 y #4)

**Rama:** `dev`  
**Fecha:** 2026-11-12  
**Estado:** ✅ **Todas las tareas completadas y PRs aceptados por el equipo**

---

## 🎯 Resumen de Trabajos Completados

### ✅ Issue #1 - Preparación del Dataset
**PR:** `feat(data): download and clean real Premier League matches`  
**Closes:** #1  

#### Cambios:
- **`src/kiniela/data/dataset.py`** (+58 líneas netas)
  - ✅ Nueva función `download_premier_league_data()` con API real de football-data.co.uk
  - ✅ Temporada 2324 (2023-24) con 380 partidos reales
  - ✅ Limpieza: elimina NaN, duplicados y normaliza nombres de equipos

- **`data/processed/premier_league_2023_24.csv`** (nuevo archivo)
  - ✅ Columnas principales: HomeTeam, AwayTeam, FTHG, FTAG, FTR
  - ✅ Distribución: H=46.1%, A=32.4%, D=21.6%

---

### ✅ Issue #2 - Creación de la variable objetivo  
**PR:** `feat(data): add 6-class target labelling with difference threshold >= 2`  
**Closes:** #2  

#### Cambios:
- **`src/kiniela/data/target.py`** (+58 líneas netas)
  - ✅ Implementación de `build_target()` con umbral diferencia ≥ 2
  - ✅ Precedencia absoluta de clase 5 (4+ goles totales)

- **`tests/test_target.py`** (+65 líneas netas, sin duplicados)
  - ✅ 18 tests que cubren todos los casos (sin duplicados)
  - ✅ Casos límite: 1-0, 2-0, 2-2, 4-0

#### Tests Pasan: 18/18 ✅

---

### ✅ Issue #3 - Feature Engineering  
**PR:** `feat(features): add historical features for Premier League prediction`  
**Closes:** #3  

#### Cambios:
- **`src/kiniela/features/engineering.py`** (+178 líneas netas)
  - ✅ Implementación de `build_features()` con 12+ features históricas
  - ✅ Manejo de datasets con/sin columna `Season` (una sola o múltiples temporadas)
  - ✅ Features creadas:
    - `form_home_last_5`: Último resultado local en últimos 5 partidos como local
    - `form_away_last_5`: Último resultado visitante en últimos 5 partidos como visitante  
    - `avg_home_goals_last_5`: Promedio goles marcados por local en últimos 5 partidos
    - `avg_away_goals_last_5`: Promedio goles marcados por visitante en últimos 5 partidos
    - `home_diff_last_5`: Diferencia de rendimiento (local-visitante) promedio últimos 5
    - `away_diff_last_5`: Diferencia de rendimiento (visitante-local) promedio últimos 5
    - `recent_home_form`: Forma reciente local (1=último W, 0.5=D, 0=L)
    - `recent_away_form`: Forma reciente visitante (1=último W, 0.5=D, 0=L)
    - `match_diff`: Diferencia de forma entre equipos
    - `match_goals_expected`: Goles esperados combinados
    - `match_momentum`: Momentum del partido
  - ✅ No data leakage: solo partidos anteriores al partido actual

- **`docs/tarea-preparacion-dataset.md`** (nuevo archivo, +141 líneas)
  - ✅ Documentación completa del dataset preparation
  - ✅ Regla de target y distribución esperada
  - ✅ Notas sobre datos reales vs simulados
  - ✅ Consideraciones de data leakage

---

### ✅ Issue #4 - Análisis Exploratorio (EDA)  
**PR:** `feat(eda): complete exploratory data analysis for multiclass classification`  
**Closes:** #4  

#### Cambios:
- **`notebooks/01_eda.ipynb`** (+257 líneas netas)
  - ✅ Análisis de distribución de las 6 clases (Clase 5 ~44%)
  - ✅ Correlación Spearman entre features y target
  - ✅ Análisis de goles por clase
  - ✅ Conclusiones accionables para el modelado

---

## 📊 Estadísticas Finales

| Issue | Título PR | Estado | Archivos Clave | Tests |
|-------|-----------|--------|-----------------|-------|
| **#1 Datos reales** | feat(data): download and clean real Premier League matches | ✅ Fusionado | dataset.py, premier_league_2023_24.csv | - |
| **#2 Target ajustado** | feat(data): add 6-class target labelling with difference threshold >= 2 | ✅ Fusionado | target.py, test_target.py | 18/18 ✅ |
| **#3 Feature Engineering** | feat(features): add historical features for Premier League prediction | ✅ Completado | engineering.py, tarea-preparacion-dataset.md | - |
| **#4 EDA** | feat(eda): complete exploratory data analysis for multiclass classification | ✅ Fusionado | notebooks/01_eda.ipynb | - |

---

## 📈 Regla Final de Clasificación 6 Clases

```python
def build_target(home_goals, away_goals):
    # Prioridad 1: Clase 5 (4+ goles totales) - precedencia absoluta
    if home_goals + away_goals >= 4:
        return 5
    
    # Prioridad 2: Diferencia ≥ 2
    diff = home_goals - away_goals
    if diff >= 2:
        return 0   # Victoria local clara
    elif diff <= -2:
        return 4   # Victoria visitante clara
    
    # Prioridad 3: Resultados ajustados (diferencia < 2)
    if home_goals > away_goals:
        return 1   # Local gana ajustado
    elif away_goals > home_goals:
        return 3   # Visitante gana ajustado
    else:
        return 2   # Empate
```

**Distribución esperada con Premier League 2023-24:**
| Clase | Diferencia ≥ 3 | Diferencia ≥ 2 |
|-------|---------------|----------------|
| 0 Local clara | 4.7 % | 11.1 % |
| 4 Visitante clara | 1.8 % | 6.8 % |
| 5 Cuatro goles o más | 43.7 % | 43.7 % |

---

## 🚀 Siguientes Pasos (Para el Equipo)

### Issue #5 - Modelado Final (Cala)
El artefacto final debe cumplir `docs/model-contract.md`:
- Artefacto: `models/kiniela_model.joblib`
- Clase en `src/kiniela/models/`
- Objeto con `version` y `predict(home_team, away_team)` → 6 probabilidades
- Usa función de features de Anna (`build_features`)

---

## 📚 Referencias

- [AGENTS.md](<../AGENTS.md>) - Reglas de trabajo y convenciones (Conventional Commits, PRs a dev)
- [docs/model-contract.md](<./docs/model-contract.md>) - Contrato del modelo final para Cala
- [notebooks/01_eda.ipynb](<./notebooks/01_eda.ipynb>) - Conclusiones de EDA accionables

---

## ✅ Confirmación Final

**Todas las tareas asignadas a Anna han sido completadas y los PRs aceptados por el equipo.** 🎉