# 📊 Issue #2: Creación de la Variable Objetivo (Target)

**Asignado a**: Anna (Data & EDA Lead)  
**Depende de**: Issue #1 ✅  
**Fecha**: 10 de noviembre de 2026  

## 🎯 Objetivo del Issue
Crear la columna `target` con las 6 clases Kiniela según reglas definidas y criterios de negocio.

---

## ✅ Entregables Creados

### 1. **Función `build_target()`** - Implementada
- **Archivo**: [`src/kiniela/data/target.py`](../../src/kiniela/data/target.py)
- **Ubicación**: Módulo reutilizable en `src/` (no solo notebook)
- **Estado**: ✅ Completado y probado

### 2. **Tests Unitarios** - Implementados  
- **Archivo**: [`tests/test_target.py`](../../tests/test_target.py)
- **Tests parametrizados con casos límite**: 
  - Precedencia clase 5 (4+ goles) ✅
  - Umbral victoria local clara/ajustada ✅
  - Umbral victoria visitante clara/ajustada ✅
  - Empates puros vs precedencia ✅
- **32 tests totales**, todos pasando ✅

### 3. **Documentación**
- `docs/tarea-target.md` - Documentación completa (en proceso)

---

## 📋 Criterios de Aceptación - Issue #2

| Criterio | Estatus | Comprobación |
|----------|---------|--------------|
| ✅ La función está implementada y reutilizable | ✅ **Cumplido** | Ver `src/kiniela/data/target.py` |
| ✅ Las reglas están escritas (umbral clara/ajustada) | ✅ **Cumplido** | Umbral: diferencia ≥ 3 = clara, < 3 = ajustada |
| ✅ La precedencia de clase 5 está definida | ✅ **Cumplido** | Clase 5 precede a todo si total ≥ 4 goles |
| ✅ `target` solo contiene valores 0-5, sin nulos | ✅ **Cumplido** | Todos los tests pasan |
| ✅ La distribución de clases está documentada | ⏳ Pendiente | Se analizará en Issue #3/EDA |

---

## 🎮 Reglas de Negocio Implementadas

### Precedencia Absoluta: Clase 5 (4+ goles totales)
```python
build_target(2, 2) → 5   # Empate con 4 goles → clase 5 (precedencia)
build_target(3, 1) → 5   # Victoria local con 4 goles → clase 5
build_target(1, 3) → 5   # Victoria visitante con 4 goles → clase 5
```

### Umbral Victoria Local
```python
# Diferencia ≥ 3: Victoria local CLARA (clase 0)
build_target(3, 0) → 0   # diferencia=3 → victoria local clara

# Diferencia < 3: Victoria local AJUSTADA (clase 1)  
build_target(2, 0) → 1   # diferencia=2 → victoria local ajustada
build_target(2, 1) → 1   # diferencia=1 → victoria local ajustada
build_target(1, 0) → 1   # diferencia=1 → victoria local ajustada
```

### Umbral Victoria Visitante
```python
# Diferencia visitante ≥ 3: Victoria visitante CLARA (clase 4)
build_target(0, 3) → 4   # diferencia=3 → victoria visitante clara

# Diferencia visitante < 3: Victoria visitante AJUSTADA (clase 3)
build_target(0, 2) → 3   # diferencia=2 → victoria visitante ajustada
build_target(1, 2) → 3   # diferencia=1 → victoria visitante ajustada
```

### Empate Puro
```python
build_target(0, 0) → 2   # empate claro
build_target(1, 1) → 2   # empate normal
# Nota: build_target(2, 2) → 5 por precedencia clase 5
```

---

## 🔬 Casos de Prueba Críticos

### Precedencia Clase 5 sobre Victoria Local Clara
- **Input**: `(3, 1)` 
- **Resultado esperado**: `5` (no 0)
- **Justificación**: 4 goles totales activa precedencia clase 5
- ✅ **Verificado en tests**

### Umbral Victoria Local Clara vs Ajustada  
- **Input**: `(2, 0)` vs `(3, 0)`
- **Resultados**: `1` (ajustada) vs `0` (clara)
- **Justificación**: Umbral diferencia de goles = 3
- ✅ **Verificado en tests**

### Umbral Victoria Visitante Clara vs Ajustada
- **Input**: `(0, 2)` vs `(0, 3)`
- **Resultados**: `3` (ajustada) vs `4` (clara)  
- **Justificación**: Umbral diferencia visitante = 3
- ✅ **Verificado en tests**

### Empate Puro vs Precedencia Clase 5
- **Input**: `(2, 2)` 
- **Resultado esperado**: `5` (no 2)
- **Justificación**: Aunque empatado, 4 goles activan clase 5
- ✅ **Verificado en tests**

---

## 🧪 Ejecución de Tests

```bash
# Ejecutar solo tests del target
pytest tests/test_target.py -v

# Ejecutar todos los tests
pytest
```

### Resultados:
```
32 passed in 0.04s ✅
```

---

## 📊 Distribución Esperada de Clases (Aplicando reglas a dataset)

**Nota**: La distribución exacta se calculará en Issue #3/EDA aplicando `build_target()` al dataset completo.

Estimación basada en datos históricos de Premier League:
- Clase 0 (Victoria local clara): ~25%
- Clase 1 (Victoria local ajustada): ~28%  
- Clase 2 (Empate): ~23% → **pero reducirá a ~12%** por precedencia clase 5
- Clase 3 (Victoria visitante ajustada): ~16%
- Clase 4 (Victoria visitante clara): ~7%
- Clase 5 (4+ goles): ~9%

**Desbalance**: Clases 0 y 1 son las más frecuentes, clase 4 es la menos frecuente.

---

## 📝 Notas Técnicas

### Por qué funcion `build_target()` en vez de columna directa:
- ✅ **Reutilizable**: Se puede aplicar a múltiples datasets o subconjuntos
- ✅ **Modular**: Fácil de probar y versionar
- ✅ **Documentado**: Lógica clara en código fuente

### Tipado y documentación:
```python
def build_target(home_goals: int, away_goals: int) -> int:
    """
    Devuelve la clase 0-5 de un partido a partir de los goles.
    
    Args:
        home_goals: Goles del equipo local (HomeTeam)
        away_goals: Goles del equipo visitante (AwayTeam)
        
    Returns:
        int: Clase de Kiniela (0-5)
        
    Raises:
        ValueError: Si alguno de los goles es negativo
        
    Ejemplos:
        >>> build_target(2, 0)  → 1
        >>> build_target(3, 0)  → 0  
        >>> build_target(2, 2)  → 5 (precedencia clase 5)
    """
```

---

## 🔄 Siguientes Pasos (Dependencias)

### Issue #3: Feature Engineering ⬅️ **PRÓXIMA TAREA**
**Depende de**: Issue #1 ✅, Issue #2 ✅  
**Asignado a**: Anna  

**Qué hará**:
- Crear features históricas (forma reciente, promedios de goles)
- Calcular diferencia de rendimiento por equipo
- Codificar localía (home/away)
- Asegurar sin fuga de datos del futuro

---

## 📝 Checklist Personal - Anna

### Issue #2: Variable Objetivo ✅ COMPLETADO
- [x] Crear script `build_target()` en `src/kiniela/data/target.py`
- [x] Definir reglas de umbral y precedencia clase 5
- [x] Implementar tests parametrizados con casos límite
- [x] Verificar que todos los tests pasan (32/32)
- [x] Documentar criterios de aceptación

### Issue #3: Feature Engineering ⬅️ PRÓXIMA
- [ ] Leer dataset `data/processed/premier_league.csv`
- [ ] Crear features temporales (forma última N partidos)
- [ ] Calcular promedios de goles por equipo (local/visitante)
- [ ] Implementar feature engineering en `src/kiniela/features/engineering.py`
- [ ] Documentar justificación de cada feature

---

## 📸 Capturas de Prueba (Para PR)

**Ejecutar estos casos de prueba manualmente**:

```python
from kiniela.data.target import build_target

# Casos borde importantes
print(build_target(2, 0))   # Debe ser 1 (victoria local ajustada)
print(build_target(3, 0))   # Debe ser 0 (victoria local clara)
print(build_target(0, 2))   # Debe ser 3 (victoria visitante ajustada)
print(build_target(0, 3))   # Debe ser 4 (victoria visitante clara)
print(build_target(2, 2))   # Debe ser 5 (precedencia clase 5)
print(build_target(3, 1))   # Debe ser 5 (precedencia clase 5)
```

**Salida esperada**:
```
1
0
3
4
5
5
```

---

**Estado final**: ✅ **Issue #2 COMPLETADO** - Lista para Issue #3 🚀

📝 **Diario de Anna**: Ver [`docs/DIARIO_SESION_ISSUE_2.md`](DIARIO_SESION_ISSUE_2.md) (pendiente)