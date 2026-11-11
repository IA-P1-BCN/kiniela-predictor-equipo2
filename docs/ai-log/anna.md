# 📘 Bitácora Final - Anna (Tarea #1 y #2)

**Rama:** `bionic/tarea-1-y-2-datos-reales-y-target`  
**Fecha:** 2026-11-11  
**Estado:** ✅ Ambas tareas completadas

---

## 🎯 Resumen de Trabajos Completados

### ✅ PR #1 - Datos Reales (commit `f705f45`)
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

### ✅ PR #2 - Target con Umbral Ajustado (commit `f99d733`)
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

- **`docs/ai-log/anna.md`** (bitácora de progreso)

#### Tests Pasan: 18/18 ✅

---

## 📊 Estadísticas Finales

| Tarea | Estado | Commit | Archivos |
|-------|--------|--------|----------|
| **#1 Datos reales** | ✅ Completado | f705f45 | dataset.py, premier_league_2023_24.csv |
| **#2 Target ajustado** | ✅ Completado | f99d733 | target.py, test_target.py |

---

## 📈 Regla Final de Clasificación 6 Clases

```python
build_target(home_goals, away_goals) -> int:
    # Prioridad 1: Clase 5 (4+ goles totales) - precedencia absoluta
    if home_goals + away_goals >= 4:
        return 5
    
    # Prioridad 2: Diferencia ≥ 2
    diff = home_goals - away_goals
    if diff >= 2:
        return 0  # Victoria local clara
    elif diff <= -2:
        return 4  # Victoria visitante clara
    
    # Prioridad 3: Resultados ajustados (diferencia < 2)
    if home_goals > away_goals:
        return 1  # Local gana ajustado
    elif away_goals > home_goals:
        return 3  # Visitante gana ajustado
    else:
        return 2  # Empate
```

---

## 🎯 Observaciones Clave

✅ **Datos reales:** Los datos de Premier League muestran ventaja local real (46.1% vs 32.4%).  
✅ **Umbral optimizado:** Con umbral >= 2, las clases raras son más frecuentes que con >= 3.  
✅ **Tests robustos:** 18 tests cubren todos los casos incluyendo límites críticos.  
✅ **Precedencia clara:** Clase 5 (4+ goles) anula siempre el resultado local/visitante/empate.

---

## 🚀 Próximos Pasos Sugeridos

### Opción A: Crear dos PRs separados a `dev`
1. Crear PR #1 desde `bionic/tarea-1-y-2-datos-reales-y-target` → `dev`
   - Archivos: dataset.py, premier_league_2023_24.csv
2. Crear PR #2 desde `bionic/tarea-1-y-2-datos-reales-y-target` → `dev`  
   - Archivos: target.py, test_target.py

### Opción B: Unificar en un solo commit
- Mantener ambos cambios en la rama actual hasta que sea necesario separarlos.

---

**Hecho por:** Anna  
**Fecha:** 2026-11-11  
**Rama actual:** `bionic/tarea-1-y-2-datos-reales-y-target`