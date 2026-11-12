# 📘 Bitácora Final - Anna (Tareas #1, #2, #3 y #4)

**Rama:** `dev`  
**Fecha:** 2026-11-12  
**Estado:** ✅ Issues #1, #2, #3 y #4 completadas; ⚠️ Correcciones pendientes antes de fusionar

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
| **#2 Target** | 6-class target labelling | ✅ Completado | target.py, test_target.py (Tests 18/18) |
| **#3 Features** | Historical features | ✅ Completado | engineering.py, tarea-preparacion-dataset.md |
| **#4 EDA** | Exploratory data analysis | ✅ Completado | notebooks/01_eda.ipynb |

---

## ⚠️ Correcciones Pendientes antes de Fusionar PRs

### 🔧 Para Issue #3 (Feature Engineering) - **Necesita ajustes**

#### Problemas identificados por el equipo:

1. **Features duplicadas:**
   - `recent_home_form` = `form_home_last_5` ❌ (deben ser diferentes)
   - `match_momentum` = `match_diff` ❌ (deben ser diferentes)

2. **Cálculo de form_*_last_5 incorrecto:**
   - Actual: solo mira el último partido
   - Debe ser: la media de los 5 resultados anteriores al partido actual

3. **Docstring inconsistente:**
   - Anuncia `avg_*_goals_conceded_last_5` (calculadas pero no devueltas) ❌
   - Dice que la forma vale `1/0.5/0`, pero el código da `1/0/-1` ❌

4. **Tests faltantes en `tests/test_features.py`:**
   - Imprescindible test de **no-fuga**: si cambia el resultado de un partido, sus propias features no deben cambiar
   
5. **Función faltante para predicción desde app:**
   - Hace falta: `build_match_features(history, home_team, away_team)`
   - Necesaria para predecir partidos individuales desde la app

#### Plan de corrección para nuevo PR:

```python
# Ejemplo de correcciones necesarias en engineering.py:

def build_features(matches: pd.DataFrame) -> pd.DataFrame:
    # Corrección 1: form_*_last_5 como media de los últimos N resultados
    form_home_last_5 = home_past.tail(N)["FTHG"].mean() - home_past.tail(N)["FTAG"].mean()  # Media, no último
    
    # Corrección 2: recent_home_form como resultado del partido inmediatamente anterior (no duplicado)
    recent_home_form = result_to_num(last_n_home.iloc[-1]["FTR"])  # Valor actual (último partido)
    
    # Corrección 3: match_momentum diferente de match_diff
    match_momentum = recent_home_form - recent_away_form  # Momentum como diferencia de forma reciente

# Añadir nueva función para predicción individual:
def build_match_features(history: pd.DataFrame, home_team: str, away_team: str) -> dict:
    """Calcula features de un partido específico a partir del historial.
    
    Para usar en la app cuando el modelo necesita predecir antes de conocer el resultado.
    """
    # Implementación que busca los partidos anteriores y calcula features...
```

---

### 🔧 Para Issue #5 (Modelo Final) - **Requerimientos para Cala**

#### Documentación del contrato del modelo: `docs/model-contract.md`

El artefacto final debe cumplir:

- Clases en `src/kiniela/models/`
- Objeto con `version` y método `predict(home_team, away_team)`
- Devuelve 6 probabilidades
- Usa la función de features de Anna (punto 4 - build_match_features)

---

## 📋 Cómo hacer los próximos PRs

### Reglas generales (están en AGENTS.md):

✅ **Rama desde issue:**
```bash
gh issue develop 3 --base dev --name 3-match-features --checkout
# Nunca: bionic/tarea-3-... ni nombres en español
```

✅ **Título del PR en inglés con Conventional Commits:**
```
feat(features): add historical features for Premier League prediction
fix(data): correct feature calculations and tests
test(models): add no-leakage validation tests
```

✅ **Antes de abrir el PR:**
- `pytest` en verde en local
- Entrada en `docs/ai-log/<nombre>.md` (solo en vuestro archivo)
- Tests en verde en CI después de crear el PR
- Esperar aprobación antes de merge con Squash

✅ **Después de hacer pull desde origin/dev:**
```bash
git checkout dev && git pull
pip install -r requirements-dev.txt  # dependencias nuevas
pytest                              # verificar tests verdes
```

❌ **Nunca subir:**
- Datasets (`data/` está en .gitignore)
- Modelos entrenados (`models/` está en .gitignore)
- Variables de entorno (`.env`)

✅ **Código, comentarios y print en inglés**  
✅ **Docs y README en español**

---

## 📚 Referencias

- [AGENTS.md](<../AGENTS.md>) - Reglas de trabajo y convenciones  
- [docs/ISSUES.md](<../ISSUES.md>) - Backlog completo del proyecto
- [docs/model-contract.md](<../model-contract.md>) - Contrato para el modelo final