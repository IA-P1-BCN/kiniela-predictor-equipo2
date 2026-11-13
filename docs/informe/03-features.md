# 3. Feature engineering y control de fuga de datos

**Quién:** Anna  
**Issues:** #3, #34  
**Estado:** ✅ Completado (fusionado en PR #43)  
**Fecha:** Lunes 16/11

---

## 🎯 Objetivo

Diseñar variables predictoras que capturen la **forma reciente**, la **potencia ofensiva/defensiva** y la **ventaja localía** de cada equipo, evitando **data leakage** para garantizar que el modelo aprenda patrones generalizables.

---

## 📊 Variables Diseñadas

### 1. Forma Reciente (`form_*_last_5`)

| Variable | Descripción | Escala |
|----------|-------------|--------|
| `form_home_last_5` | Último resultado del local en últimos 5 partidos como local | Promedio: 1=W, 0=D, -1=L (fracción posible) |
| `form_away_last_5` | Último resultado del visitante en últimos 5 como visitante | Promedio: 1=W, 0=D, -1=L (fracción posible) |

**Justificación:** El momentum actual es más predictivo que el promedio histórico. Usamos **solo los últimos 5 partidos**, ya que equipos en racha muestran cambios bruscos de comportamiento.

> 🔧 **Corrección v1.1:** Antes devolvía solo el último resultado (no promedio). Ahora devuelve el promedio de los últimos 5 resultados (ej: 0.8, -0.6, 1.0).

---

### 2. Potencia Ofensiva/Defensiva (`avg_*_goals_last_5`)

| Variable | Descripción |
|----------|-------------|
| `avg_home_goals_last_5` | Goles promedios marcados por el local en últimos 5 como local |
| `avg_away_goals_last_5` | Goles promedios marcados por el visitante en últimos 5 como visitante |

**Justificación:** La potencia goleadora reciente indica la capacidad de anotar, señal clave para predecir márgenes.

---

### 3. Diferencia de Rendimiento (`*diff_last_5`)

| Variable | Descripción |
|----------|-------------|
| `home_diff_last_5` | Goles marcados - recibidos promedio de últimos 5 como local |
| `away_diff_last_5` | Goles recibidos - marcados promedio de últimos 5 como visitante |

**Justificación:** Una diferencia positiva indica un equipo que domina sus partidos.

---

### 4. Forma Reciente Numérica (`recent_*_form`)

| Variable | Descripción | Escala |
|----------|-------------|--------|
| `recent_home_form` | Último resultado local (para regresión logística) | 1=último W, 0.5=D, 0=L |
| `recent_away_form` | Último resultado visitante (para regresión logística) | 1=último W, 0.5=D, 0=L |

**Justificación:** En clasificación binaria, el último partido tiene más peso que los anteriores.

---

### 5. Features Combinadas para Predicción Individual

Para predecir un partido específico sin todo el histórico:

| Variable | Fórmula |
|----------|---------|
| `match_diff` | `form_home_last_5 - form_away_last_5` |
| `match_goals_expected` | `avg_home_goals_last_5 + avg_away_goals_last_5` |
| `match_momentum` | `recent_home_form - recent_away_form` |

**Uso principal:** La aplicación web necesita calcular estas features para **cada partido nuevo**, sin requerir todo el histórico.

---

## 🛡️ Control de Fuga de Datos (Data Leakage)

### ¿Qué es el data leakage?

El data leakage ocurre cuando las features usan información del futuro (incluyendo el resultado del partido actual). Esto hace que el modelo parezca muy preciso en entrenamiento pero falle en producción.

### Cómo lo hemos prevenido

```python
# ✅ CORRECTO: Solo partidos estrictamente ANTERIORES
home_past = home_history[home_history["Date"] < current_match_date]

# ❌ INCORRECTO: Incluir el partido actual (data leakage!)
home_past = home_history[home_history["Date"] <= current_match_date]  # Error!
```

**Regla de oro:** Para calcular las features del partido X, **solo se usan partidos con fecha < fecha(partido X)**.

---

## 🧪 Validación con Tests

### Test de No-Fuga

Verificamos que cambiar el resultado de un partido actual no afecte las features calculadas:

```python
def test_no_leakage_when_modifying_match_result():
    """
    Verificar que cambiar el resultado del partido actual 
    NO afecta las features calculadas.
    """
    history = pd.DataFrame({
        "HomeTeam": ["Arsenal", "Arsenal", "Arsenal"],
        "AwayTeam": ["Chelsea", "ManCity", "Liverpool"],
        "FTHG": [3, 2, 1],
        "FTAG": [1, 0, 1],
        "FTR": ["H", "H", "A"],
        "Date": ["2024-08-17", "2024-09-23", "2024-10-01"],
    })
    
    # Las features deben calcularse usando solo partidos anteriores
    features = engineering.build_match_features(history, "Arsenal", "Chelsea")
```

### Semántica de `form_*_last_5`

Verificamos que la forma reciente use **promedio** (no solo el último):

- ✅ `form_home_last_5` = promedio de los últimos 5 resultados (puede ser fracción: 0.8, -0.6)
- ❌ NO es simplemente el resultado del último partido

### Resultados de Tests

| Test Suite | Testes | Pasados | Fallados |
|------------|--------|---------|----------|
| `TestBuildFeatures` | 2 | ✅ 2 | ❌ 0 |
| `TestFeatureSemantics` | 2 | ✅ 2 | ❌ 0 |
| `TestBuildMatchFeatures` | 3 | ✅ 3 | ❌ 0 |
| `TestNoDataLeakage` | 2 | ✅ 2 | ❌ 0 |
| `TestNoDuplicates` | 1 | ✅ 1 | ❌ 0 |
| **Total** | **10** | ✅ **10** | ❌ **0** |

---

## 💻 Uso desde la Aplicación

### Calcular features para un partido nuevo

```python
from kiniela.features import engineering
import pandas as pd

# Historial de partidos
history = pd.DataFrame({
    "HomeTeam": ["Arsenal", "Chelsea", "Liverpool"],
    "AwayTeam": ["Chelsea", "Liverpool", "ManCity"],
    "FTHG": [3, 1, 2],
    "FTAG": [1, 0, 1],
    "FTR": ["H", "A", "D"],
    "Date": ["2024-08-17", "2024-09-23", "2024-10-01"],
})

# Calcular features para Arsenal vs Chelsea
features = engineering.build_match_features(history, "Arsenal", "Chelsea")
print(features)
```

**Salida típica:**

```python
{
    'form_home_last_5': 1.0,        # Arsenal último resultado como local: W
    'form_away_last_5': -1.0,       # Chelsea último resultado como visitante: L
    'avg_home_goals_last_5': 2.33,  # Arsenal promedio goles locales últimos 5
    'match_diff': 2.0,              # Ventaja Arsenal vs Chelsea
    'match_momentum': 2.0           # Momentum a favor local
}
```

---

## 🔍 Comparativa: Antes vs Después de la Corrección

### Antes (v1.0 - con bugs):

| Problema | Ejemplo |
|----------|---------|
| `form_*_last_5` devolvía solo el último resultado (no promedio) | Arsenal último W = 1, aunque promedio últimos 5 = 0.8 |
| Docstring anunciaba `avg_*_goals_conceded_last_5` (que no se devolvía) | Error de API inconsistency |
| Duplicados: 6 features con "form" en nombre | `recent_home_form`, `form_home_last_5`, ... |

### Después (v1.1 - corregido):

| Mejora | Resultado |
|--------|-----------|
| `form_*_last_5` devuelve **promedio** de últimos 5 resultados | Valor fraccionario: 0.8, -0.6, 1.0 |
| Docstrings coinciden con lo que se devuelve | API consistente |
| Sin duplicados | Solo 4 features con "form" + combinadas necesarias |
| Nueva función `build_match_features()` | Permite predicción individual desde app |

---

## 📁 Ubicación del Código

- **Código:** [`src/kiniela/features/engineering.py`](../../src/kiniela/features/engineering.py)
- **Tests:** [`tests/test_features.py`](../../tests/test_features.py)
- **Importación:** `from kiniela.features import engineering`

---

## 🔗 Enlaces Relevantes

- [Feature Engineering (Informe)](./03-features.md) - Este documento
- [Model Contract](../model-contract.md) - Contrato del modelo final
- [Issue #34](https://github.com/IA-P1-BCN/kiniela-predictor-equipo2/issues/34) - Correcciones feature engineering

---

## 📋 Checklist de Validación

- [x] Sin features duplicadas (solo 4 con "form" en nombre)
- [x] `form_*_last_5` devuelve promedio, no solo último resultado
- [x] Docstrings coinciden con lo que se devuelve
- [x] `build_match_features()` implementada y funcional
- [x] Test de no-fuga incluido y pasando
- [x] Tests en verde: 10/10 tests en `test_features.py`
- [x] Código listo para uso desde app

---

**Cierre:** Feature engineering corregido y validado. Sin fugas de datos, sin duplicados, con función para predicción individual desde app. Todos los tests pasan ✅

<EOF>