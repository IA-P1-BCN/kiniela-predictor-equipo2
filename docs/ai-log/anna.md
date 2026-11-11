# 📘 Bitácora de IA - Anna

**Rama:** `bionic/tarea-1-y-2-datos-reales-y-target`  
**Fecha:** 2026-11-11

---

## ✅ Tarea #1 Completada: Datos Reales

### Cambios Implementados:

#### 📊 Dataset Real de Premier League
- **Fuente:** `https://www.football-data.co.uk/mmz4281/2324/E0.csv`
- **Temporada:** 2324 (2023-24)
- **Partidos descargados:** 380 partidos reales
- **Guardado en:** `data/processed/premier_league_2023_24.csv`

#### 🔄 Archivo Actualizado:
- **`src/kiniela/data/dataset.py`** (+58 líneas)
  - ✅ Nueva función `download_premier_league_data()` que descarga desde API real
  - ✅ Limpieza de datos: elimina NaN, duplicados
  - ✅ Normalización de nombres de equipos (minúsculas, sin apóstrofes)
  - ✅ Mantiene función `load_matches()` para compatibilidad

---

## 🎯 Tarea #2 Completada: Target con Umbral Ajustado

### Cambios Implementados:

#### 🎯 Lógica de Clasificación 6 Clases
- **Umbral:** Diferencia ≥ 2 para victoria clara (ajustado según feedback del equipo)
- **Precedencia absoluta:** Clase 5 (4+ goles totales) anula resultado local/visitante
- **Clases:**
  - 0: Local gana con diferencia ≥ 2
  - 1: Local gana con diferencia = 1
  - 2: Empate
  - 3: Visitante gana con diferencia = 1
  - 4: Visitante gana con diferencia ≥ 2
  - 5: 4+ goles totales (precedencia absoluta)

#### 🔄 Archivos Actualizados:
1. **`src/kiniela/data/target.py`** (+74 líneas)
   - ✅ Implementación completa de `build_target()` con umbral >= 2
   - ✅ Documentación detallada de la regla y distribución esperada
   
2. **`tests/test_target.py`** (+86 líneas, sin duplicados)
   - ✅ 19 tests que cubren todos los casos (sin duplicados)
   - ✅ Casos límite: 1-0, 2-0, 2-2, 4-0
   - ✅ Validación de precedencia clase 5

#### ✅ Tests Pasan: 19/19

---

## 📝 Próximos Pasos

### Crear dos PRs separados a `dev`:

#### PR #1 - Datos Reales ✅ COMPLETADO
- **Rama actual:** `bionic/tarea-1-y-2-datos-reales-y-target`  
- **Cambios:** dataset.py, premier_league_2023_24.csv
- **Título:** `feat(data): download and clean real Premier League matches`
- **Closes:** #1

#### PR #2 - Target con Umbral >= 2 ⏳ PENDIENTE
- **Cambios:** target.py, test_target.py  
- **Título:** `feat(data): add 6-class target labelling with difference threshold >= 2`
- **Closes:** #2

---

## 📊 Estadísticas del Dataset Real

| Métrica | Valor |
|---------|-------|
| Partidos totales | 380 |
| Ventanas locales (H) | 175 (46.1%) |
| Visitante gana (A) | 123 (32.4%) |
| Empate (D) | 82 (21.6%) |

**Columnas disponibles:** HomeTeam, AwayTeam, FTHG, FTAG, FTR  
*(y muchas columnas adicionales para features futuras)*

---

## 🔬 Observaciones Clave

✅ **Datos reales vs simulados:** Los datos muestran ventaja local real y distribución natural de goles.  
✅ **Tamaño suficiente:** 380 partidos es un buen conjunto inicial para entrenar el modelo.  
✅ **Columnas extra:** Dispondremos de tiros, córners y cuotas para features adicionales.  
✅ **Umbral optimizado:** Con umbral >= 2, las clases raras son más frecuentes que con >= 3, facilitando el aprendizaje del modelo.
