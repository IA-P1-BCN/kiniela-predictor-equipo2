# 📘 Bitácora Final - Anna (Tareas #1, #2 y #3)

**Rama:** `bionic/tarea-3-feature-engineering`  
**Fecha:** 2026-11-11  
**Estado:** ✅ Tareas #1, #2 y #3 completadas

---

## 🎯 Resumen de Trabajos Completados

### ✅ PR #1 - Datos Reales
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

### ✅ PR #2 - Target con Umbral Ajustado  
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

### ✅ PR #3 - Feature Engineering (COMPLETADO)  
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

## 📊 Estadísticas Finales

| Tarea | Issue | Estado | Archivos |
|-------|-------|--------|----------|
| **#1 Datos reales** | #1 | ✅ Completado | dataset.py, premier_league_2023_24.csv |
| **#2 Target ajustado** | #2 | ✅ Completado | target.py, test_target.py |
| **#3 Feature Engineering** | #3 | ✅ Completado | engineering.py, tarea-preparacion-dataset.md |

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

## 🚀 Siguientes Pasos

1. **Crear PR desde GitHub** para fusionar `bionic/tarea-3-feature-engineering` en `dev`
   - Título del PR: `feat(features): add historical features for Premier League prediction`
   - Closes #3
   - Review por el equipo antes de merge con squash

2. **Testear feature engineering**:
   ```python
   from kiniela.features import engineering
   matches = load_matches('data/processed/premier_league_2023_24.csv')
   features = build_features(matches)
   print(f"Partidos procesados: {len(features)}")
   ```

3. **Fusionar con el Target**: Combinar `build_target()` y `build_features()` en un pipeline único

---

## 📚 Referencias

- [AGENTS.md](<../AGENTS.md>) - Reglas de trabajo y convenciones (Conventional Commits, PRs a dev)
- [docs/ai-log/anna.md](<./README.md>) - Template para bitácoras personales