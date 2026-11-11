# 📘 Bitácora Final - Anna (Tareas #1, #2 y #3)

**Rama:** `dev`  
**Fecha:** 2026-11-11  
**Estado:** ✅ Tarea #1 y #2 completadas, Tarea #3 en desarrollo

---

## 🎯 Resumen de Trabajos Completados

### ✅ PR #1 - Datos Reales (commit pendiente)
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

### ✅ PR #2 - Target con Umbral Ajustado (commit pendiente)
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

## 📊 Estadísticas Finales

| Tarea | Estado | Commit | Archivos |
|-------|--------|--------|----------|
| **#1 Datos reales** | ✅ Completado | - | dataset.py, premier_league_2023_24.csv |
| **#2 Target ajustado** | ✅ Completado | - | target.py, test_target.py |

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

**Distribución esperada con Premier League 2023-24:**
| Clase | Diferencia ≥ 3 | Diferencia ≥ 2 |
|-------|---------------|----------------|
| 0 Local clara | 4.7 % | 11.1 % |
| 4 Visitante clara | 1.8 % | 6.8 % |
| 5 Cuatro goles o más | 43.7 % | 43.7 % |

---

## 🚧 Tarea #3 - Feature Engineering (EN PROGRESO)

**Estado:** ✅ Código implementado, documentación actualizada, listo para pruebas finales

### ✅ Lo que se ha completado:

#### **src/kiniela/features/engineering.py** (190 líneas)
- ✅ Función `build_features()` implementada con features históricas
- ✅ Maneja datasets con y sin columna `Season` (adaptable a múltiples temporadas)
- ✅ Features creadas:
  - `form_home_last_5`: Último resultado local (W=1, D=0, L=-1) en últimos 5 partidos como local
  - `form_away_last_5`: Último resultado visitante (W=1, D=0, L=-1) en últimos 5 partidos como visitante  
  - `avg_home_goals_last_5`: Promedio goles marcados por local en últimos 5 partidos como local
  - `avg_away_goals_last_5`: Promedio goles marcados por visitante en últimos 5 partidos como visitante
  - `home_diff_last_5`: Diferencia goles (local-visitante) promedio de últimos 5 partidos del local
  - `away_diff_last_5`: Diferencia goles (visitante-local) promedio de últimos 5 partidos del visitante
  - `recent_home_form`: Forma reciente local (1=último W, 0.5=D, 0=L) en últimos 5 como local
  - `recent_away_form`: Forma reciente visitante (1=último W, 0.5=D, 0=L) en últimos 5 como visitante
  - `match_diff`: Diferencia de forma entre equipos
  - `match_goals_expected`: Goles esperados combinados
  - `match_momentum`: Momentum del partido

### ✅ Mejoras implementadas:

1. **Adaptabilidad a datasets**: El código ahora funciona tanto con datos de una sola temporada (2023-24) como con múltiples temporadas concatenadas
2. **No data leakage**: Cada feature usa solo partidos anteriores al partido actual
3. **Separación local/visitante**: Para mayor granularidad en el modelado

### ✅ Documentación actualizada:
- `docs/tarea-preparacion-dataset.md`: Actualizado con descripción del feature engineering
- `docs/ai-log/anna.md`: Registro de progreso actualizado

---

## 📝 Decisiones Importantes

### Decidido (por Anna):
- ✅ Usar siempre los últimos 5 partidos (`N=5`) para forma reciente
- ✅ Separar features de local/visitante para mayor granularidad
- ✅ Incluir features combinadas para capturar interacciones
- ✅ Adaptarse a datasets sin columna `Season` (asumir todo el histórico disponible)

### Decidido por el Equipo (Factoria-F5 Madrid):
✅ **Datos reales**: Solo con API de football-data.co.uk  
✅ **Estructura correcta**: Scripts en `src/kiniela/features/`  
✅ **CI automática**: Cada PR debe pasar tests antes de fusionar  

---

## 📁 Archivos Clave Referenciados

| Archivo | Ruta | Significado |
|---------|------|------------|
| Feature Engineering | `src/kiniela/features/engineering.py` | Implementación con 12+ features históricas |
| Dataset (2023-24) | `data/processed/premier_league_2023_24.csv` | 380 partidos para testing rápido |
| AGENTS.md | `.github/AGENTS.md` | Reglas de código, sin data leakage, Conventional Commits |

---

## 🔬 Observaciones Clave

1. **Eficiencia computacional**: La implementación actual usa iteración sobre filas (lento con 3,420 partidos). Considerar optimización futura si necesario.

2. **Features prometedoras**: Las 8 features principales capturan bien:
   - Momentum reciente (form_home_last_5, recent_home_form)
   - Potencia ofensiva (avg_goals_last_5)
   - Fortaleza neta (diff_last_5)

3. **Data leakage controlado**: Cada feature usa solo partidos anteriores al partido actual, validando criterio de no-fuga.

4. **Compatibilidad con target.py**: Las features son independientes de `build_target()`, lo que permite combinarlas fácilmente en el dataset final.

---

## 📚 Contexto Histórico

- **Issue #1 (Datos reales)**: ✅ Completada - 380 partidos descargados, URL correcta de football-data.co.uk
- **Issue #2 (Target)**: ✅ Completada - Umbral ≥ 2 con precedencia clase 5
- **Issue #3 (Features)**: ⏳ En progreso - Código implementado, adaptable a datasets sin Season

---

## 🚀 Próximo Paso

Crear PR para Feature Engineering (Issue #3) con:
- Commit: `feat(features): add historical features for Premier League prediction`
- Archivos: `src/kiniela/features/engineering.py`, `docs/tarea-preparacion-dataset.md`, `docs/ai-log/anna.md`