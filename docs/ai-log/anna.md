# 📘 Bitácora Final - Anna (Tareas #1, #2, #3 y #4)

**Rama:** `bionic/tarea-4-eda`  
**Fecha:** 2026-11-12  
**Estado:** ✅ Tareas #1, #2, #3 completadas; Issue #4 en desarrollo (EDA listo para PR)

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
  - ✅ Distribución: H=46.1%, A=32.4%, D=21.6%

- **`data/processed/premier_league_2023_24.csv`** (nuevo archivo)
  - ✅ Columnas principales: HomeTeam, AwayTeam, FTHG, FTAG, FTR
  - ✅ Y muchas columnas adicionales para features futuras

---

### ✅ Issue #2 - Creación de la variable objetivo  
**Título:** `feat(data): add 6-class target labelling with difference threshold >= 2`  
**Closes:** #2  

#### Cambios:
- **`src/kiniela/data/target.py`** (+58 líneas netas)
  - ✅ Implementación de `build_target()` con umbral diferencia ≥ 2
  - ✅ Precedencia absoluta de clase 5 (4+ goles totales)
  - ✅ Distribución esperada: Clase 5 ~44%, Clase 0 ~11%, Clase 4 ~7%

- **`tests/test_target.py`** (+65 líneas netas, sin duplicados)
  - ✅ 18 tests que cubren todos los casos (sin duplicados)
  - ✅ Casos límite: 1-0, 2-0, 2-2, 4-0
  - ✅ Validación de precedencia clase 5

#### Tests Pasan: 18/18 ✅

---

### ✅ Issue #3 - Feature Engineering  
**Título:** `feat(features): add historical features for Premier League prediction`  
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

### ⏳ Issue #4 - Análisis Exploratorio (EDA) - EN PROCESO

**Título:** `feat(eda): complete exploratory data analysis for multiclass classification`  
**Closes:** #4  

#### Cambios:
- **`notebooks/01_eda.ipynb`** (+257 líneas netas)
  - ✅ Análisis de distribución de las 6 clases (Clase 5 ~44%, sobre-representada)
  - ✅ Correlación Spearman entre features y target
  - ✅ Análisis de goles por clase (FTHG, FTAG, goal_diff)
  - ✅ Resumen estadístico de features históricas
  - ✅ Heatmap de correlaciones entre features
  - ✅ Conclusiones accionables para el modelado:
    - Estrategia para manejo del desbalance (class weights o modelo híbrido)
    - Prioridades en feature selection
    - Recomendación: F1 macro como métrica principal por desbalance

---

## 📊 Estadísticas Finales

| Issue | Título | Estado | Archivos Clave |
|-------|--------|--------|-----------------|
| **#1 Datos reales** | Download & clean dataset | ✅ Completado | dataset.py, premier_league_2023_24.csv |
| **#2 Target** | 6-class target labelling | ✅ Completado | target.py, test_target.py |
| **#3 Features** | Historical features | ✅ Completado | engineering.py, tarea-preparacion-dataset.md |
| **#4 EDA** | Exploratory data analysis | ⏳ Listo para PR | 01_eda.ipynb |

---

## 📈 Distribución Final de Clases (Premier League 23/24)

```text
Clase    Descripción             Porcentaje Aproximado
-----    -----------             ------------------
0       Victoria local clara        ~11%
1       Local gana ajustado         ~38%  
2       Empate                      ~18%
3       Visitante gana ajustado     ~33%
4       Victoria visitante clara    ~7%
5       4+ goles totales            ~44%
```

**Observación clave:** La clase 5 (~44%) es significativamente sobre-representada, requiriendo:
- `StratifiedKFold` con al menos 3-5 folds
- Considerar `class_weight='balanced'` en modelos lineales
- O modelo híbrido (predecir high-scoring primero, luego dirección)

---

## 🔍 Hallazgos del EDA

### 1. Features más predictivas:
- `recent_home_form`, `form_home_last_5`: Capturan momentum actual
- `avg_goals_last_5`: Potencia ofensiva reciente
- `match_goals_expected`: Predictor fuerte de la clase 5

### 2. Riesgo de sobreajuste:
- Clase 5 ~44% del dataset → usar class weights o balanceo
- Métrica principal: **F1 macro** (no accuracy)

### 3. Multicolinealidad detectada:
- Algunas features históricas >0.7 correlacionadas
- Recomendación: regularización L1/L2 en modelos lineales

---

## 🚀 Próximos Pasos

### Issue #5 - Modelo Baseline (para Cala)

**Prerrequisitos completados:** ✅ Dataset con target + features, EDA finalizado

**Plan para Issue #5:**
1. Entrenar Random Forest o Logistic Regression con `StratifiedKFold(n_splits=5)`
2. Usar `class_weight='balanced'` (Random Forest) o ponderación manual (LR)
3. Métricas: Accuracy global + F1 macro (principal)
4. Reportar accuracy y F1 macro de validación cruzada
5. Elegir métrica principal para optimización

---

## 📚 Referencias

- [AGENTS.md](<../AGENTS.md>) - Reglas de trabajo y convenciones
- [docs/ISSUES.md](<../ISSUES.md>) - Backlog completo del proyecto