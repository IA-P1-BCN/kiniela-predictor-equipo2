# Bitácora Final - Anna (Tarea #1 y #2)

**Rama:** bionic/tarea-1-y-2-datos-reales-y-target-resueltos  
**Fecha:** 2026-11-11  
**Estado:** ✅ Ambas tareas completadas

---

## Resumen de Cambios

### PR #1 - Datos Reales
- Funcion: download_premier_league_data() con API real de football-data.co.uk
- Temporada: 2324 (2023-24), 380 partidos reales
- Guardar en: data/processed/premier_league_2023_24.csv
- Distribucion: H=175 (46.1%), A=123 (32.4%), D=82 (21.6%)

### PR #2 - Target con Umbral Ajustado  
- Umbral: diferencia >= 2 para victoria clara/ajustada
- Precedencia absoluta: Clase 5 (4+ goles totales)
- Tests: 14/14 pasando
- Distribucion esperada: Clase 5 ~44%, Clase 0 ~11%, Clase 4 ~7%

---

## Archivos Modificados

| Archivo | Cambios | Tarea |
|---------|---------|-------|
| src/kiniela/data/dataset.py | +37 lineas netas | #1 y #2 |
| data/processed/premier_league_2023_24.csv | 380 partidos reales | #1 |
| src/kiniela/data/target.py | +41 lineas netas | #2 |
| tests/test_target.py | +42 lineas netas | #2 |

---

## Regla Final de Clasificacion (6 clases)

```python
build_target(home, away):
    if home + away >= 4: return 5  # Clase 5: precedencia absoluta
    diff = home - away
    if diff >= 2: return 0        # Victoria local clara
    elif diff <= -2: return 4     # Victoria visitante clara
    elif home > away: return 1    # Local gana ajustado
    elif away > home: return 3    # Visitante gana ajustado
    else: return 2                # Empate
```

---

## Pruebas Exitosas

- tests/test_target.py: 14/14 PASADOS
- Dataset real: 380 partidos descargados y guardados
- Todos los casos limite cubiertos (1-0, 2-0, 2-2, 4-0)
- Precedencia clase 5 verificada

---

## Siguientes Pasos

1. Commit de PR #1 (datos reales) con dataset.py y CSV
2. Commit de PR #2 (target) con target.py y tests
3. Crear dos PRs separados a dev
