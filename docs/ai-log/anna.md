# 📘 Bitácora - Anna (Tareas #1-#4 y correcciones)

**Rama:** `34-match-features-corrections`  
**Fecha:** 2026-11-13  
**Estado:** ✅ **PR empujado a dev para Issue #34**

---

## 🎯 Resumen de Trabajos Completados

### ✅ Issue #1 - Preparación del Dataset
**PR fusionado:** `feat(data): download and clean real Premier League matches`  
**Closes:** #1  

#### Cambios:
- **`src/kiniela/data/dataset.py`**: Función `download_premier_league_data()` con API real de football-data.co.uk
- **`data/processed/premier_league_2023_24.csv`**: 380 partidos reales (H=46.1%, A=32.4%, D=21.6%)

---

### ✅ Issue #2 - Creación de la variable objetivo  
**PR fusionado:** `feat(data): add 6-class target labelling with difference threshold >= 2`  
**Closes:** #2  

#### Cambios:
- **`src/kiniela/data/target.py`**: Función `build_target()` con umbral diferencia ≥ 2 y precedencia clase 5
- **`tests/test_target.py`**: 18 tests cubriendo todos los casos (sin duplicados)

#### Tests Pasan: 18/18 ✅

---

### ✅ Issue #3 - Feature Engineering (Correcciones aplicadas)
**PR:** `feat(features): add historical features for Premier League prediction`  
**Closes:** #3  

#### Cambios:
- **`src/kiniela/features/engineering.py`**: Implementación inicial de 12+ features históricas
- **`docs/tarea-preparacion-dataset.md`**: Documentación del dataset preparation

---

### ✅ Issue #4 - Análisis Exploratorio (EDA)  
**PR fusionado:** `feat(eda): complete exploratory data analysis for multiclass classification`  
**Closes:** #4  

#### Cambios:
- **`notebooks/01_eda.ipynb`**: Análisis completo de distribución de clases, correlaciones y conclusiones

---

## ✅ Correcciones Issues #3 y #34 (PR empujado a dev)

**PR:** `feat(features): correct docstrings for form_*_last_5 and recent_*_form`  
**Rama:** `34-match-features-corrections` → Pushed to origin ✅  

### Cambios aplicados:

#### 1. Corregido: Semántica de las features
- **Corregido**: `form_*_last_5` es PROMEDIO de últimos 5 resultados anteriores al partido actual
- **Corregido**: `recent_*_form` es el resultado del ÚLTIMO partido en escala ponderada (1=último W, 0.5=D, 0=último L)
- **Eliminadas**: Features duplicadas (`avg_*_goals_conceded_last_5`, columnas de goles concedidos no devueltas)

#### 2. Corregido: Docstrings consistentes  
- ✅ `recent_home_form` ≠ `form_home_last_5` (son diferentes)
- ✅ `match_momentum` es `recent_home_form - recent_away_form`, no copia de `match_diff`
- ✅ Docstring describe exactamente las features que se devuelven

#### 3. Función `build_match_features()` para predicción desde app
```python
from kiniela.features import engineering

# Predecir un partido desde la app sin todo el histórico
features = engineering.build_match_features(
    history, 
    home_team="Arsenal", 
    away_team="Chelsea"
)
# features contiene todas las columnas que usa el modelo
```

#### 4. Tests de no-fuga
- ✅ Test verifica que cambiar resultado de un partido NO afecta sus propias features anteriores
- ✅ 7 tests nuevos en `tests/test_features.py` (7/7 pasan)

---

## 📊 Estado Final del Work - Issues #3 y #34

| Issue | Archivo Clave | Cambios | Tests | PR | Estado |
|-------|---------------|---------|-------|-----|--------|
| **#3** | engineering.py (+123 líneas) | Correcciones de duplicados y semántica | 7/7 ✅ | 🟢 Empujado a dev, pendiente squash merge |
| **#34** | tests/test_features.py (142 líneas) | Función build_match_features + test no-fuga | 7/7 ✅ | 🟢 Merge con el PR de #3 o separado según decisión del equipo |

---

## 🚀 Estado Actual

### Resumen de archivos modificados:

| Archivo | Líneas | Descripción |
|---------|--------|-------------|
| `src/kiniela/features/engineering.py` | +123 | Correcciones semánticas y docstrings |
| `tests/test_features.py` | 142 (nuevo) | Tests para validación y no-fuga |

### Estadísticas de tests:

```bash
pytest tests/test_target.py tests/test_features.py -q
# Result: 25 passed in 0.51s ✅
```

---

## 📝 Bitácora actualizada

**`docs/ai-log/anna.md`**: Actualizada con progreso de todas las tareas y correcciones aplicadas.

---

## 🔗 PR empujado a dev

**URL del PR:**
```
https://github.com/IA-P1-BCN/kiniela-predictor-equipo2/pull/new/34-match-features-corrections
```

### Checklist del PR:

- [x] Título en inglés con Conventional Commits ✅
- [x] Descripción completa con plantilla ✅  
- [x] Closes #3 y #34 indicado ✅
- [x] pytest verde (25 tests pasan) ✅
- [x] Bitácora actualizada ✅
- [x] No hay datasets, modelos o .env en el PR ✅

---

## 📚 Referencias

- [AGENTS.md](<../../AGENTS.md>) - Reglas de trabajo (Conventional Commits, PRs a dev)
- [docs/model-contract.md](<../model-contract.md>) - Contrato del modelo final para Cala

---

### #34 Features de un partido nuevo: errores corregidos

- **Fecha:** 2026-11-16
- **Herramienta y modelo:** _por completar_
- **Prompt clave:** revisar las ramas propias, encontrar los errores y corregirlos.
- **Qué generó el agente:** reescritura de `engineering.py` con un único cálculo por partido (`_match_features`) que comparten `build_features` y `build_match_features`; constante `FEATURE_COLUMNS`; 21 tests nuevos en `tests/test_features.py`; actualización de `docs/tarea-preparacion-dataset.md`.
- **Errores encontrados en el código fusionado (PRs #43, #51, #52 y #54):**
  - `build_match_features` devolvía `form_*_last_5` y `match_diff` siempre vacíos: leía las columnas `ResultHome`/`ResultAway`, que no existen en el histórico.
  - Descartaba el último partido de cada equipo (`Date < max`), así que la app y el entrenamiento no coincidían.
  - El signo de la forma del visitante estaba invertido: una victoria fuera contaba como derrota.
  - Si un equipo no tenía historial, faltaban columnas en lugar de venir vacías.
  - Las fechas `dd/mm/aaaa` se ordenaban como texto (el 01/09 antes que el 11/08), lo que rompía el «solo partidos anteriores».
  - Seguían `recent_*_form` y `match_momentum` (la issue pedía quitarlos) y el docstring no coincidía con el código.
  - La tabla de clases de `docs/tarea-preparacion-dataset.md` sumaba más del 100 %; ahora tiene la distribución real (clase 5: 43,7 %).
- **Aceptado:** función común para entrenamiento y app; `build_match_features` devuelve un DataFrame de una fila con las columnas del modelo, listo para `predict_proba` (contrato de `docs/model-contract.md`).
- **Errores del agente y cómo se corrigieron:** la primera versión leía las fechas ISO con `dayfirst=True` y convertía `2024-09-01` en el 9 de enero; lo detectaron los tests nuevos y ahora se prueba primero el formato ISO.
- **Comprobación:** con el CSV real, las features de la app coinciden con las de entrenamiento en los 380 partidos; `pytest`: 195 tests pasan. Los tests nuevos fallan si se reintroduce la fuga (`<=`) o el signo invertido.
- **Revisión humana:** _pendiente_

---

### #4 EDA: notebook recuperado y corregido

- **Fecha:** 2026-11-16
- **Herramienta y modelo:** _por completar_
- **Prompt clave:** llevar a `dev` el EDA de la rama `bionic/tarea-4-eda`, que nunca se fusionó, corrigiendo sus errores. Mariana dio el visto bueno para sustituir su plantilla de `notebooks/01_eda.ipynb`.
- **Errores encontrados en la versión de la rama:**
  - El JSON del notebook estaba roto (Jupyter no lo abría).
  - Nunca se había ejecutado: `build_target` recibía columnas enteras y fallaba en la segunda celda.
  - Las conclusiones no salían de datos (sin salidas) y una recomendaba usar `FTHG`, `FTAG` y la diferencia de goles como features, que es fuga de datos.
  - Usaba features que ya no existen y una correlación de Spearman con `target`, que es nominal.
- **Qué generó el agente:** notebook nuevo que solo llama a `src/kiniela/` (dataset, `target`, distribución de clases, goles, features por clase y correlación entre features) y conclusiones escritas a partir de su ejecución.
- **Comprobación:** todas las celdas se ejecutan con el CSV real; las cifras de las conclusiones son las que imprime el notebook. Se guarda sin salidas, como los demás notebooks del equipo.
- **Revisión humana:** _pendiente_

---

### #17 Informe: sección 3 y guion de la presentación técnica

- **Fecha:** 2026-11-16
- **Herramienta y modelo:** _por completar_
- **Prompt clave:** recuperar la sección 3 y el guion de la presentación del commit `cf5334b`, que se subió después de fusionar la PR #51 y nunca llegó a `dev`, y corregir sus errores. Mariana dio el visto bueno para sustituir sus esquemas.
- **Errores encontrados en la versión recuperada:**
  - Sección 3: describía `recent_*_form` y `match_momentum` (ya eliminadas), definía `away_diff_last_5` al revés y tenía una salida de ejemplo y un recuento de tests que no eran reales.
  - Presentación: regla de clases equivocada (diferencia de 3 goles y clase 5 como «4 goles de un equipo»), distribución de clases y tendencia de goles inventadas (una clase con «~X %»), enlaces a archivos que no existen y 12 diapositivas en lugar de 5-6.
- **Qué generó el agente:** sección 3 reescrita con el código de la PR #58 y guion de 6 diapositivas con el formato acordado (se ve, se dice, captura).
- **Comprobación:** todas las cifras salen del CSV real, de los tests o del notebook de EDA.
- **Pendiente:** la sección 2 (`02-datos-y-eda.md`) sigue sin redactar.
- **Revisión humana:** _pendiente_

---

### #17 Informe: sección 2 (datos, variable objetivo y EDA)

- **Fecha:** 2026-11-16
- **Herramienta y modelo:** _por completar_
- **Prompt clave:** redactar la sección 2 del informe. Mariana dio el visto bueno para sustituir su esquema de `02-datos-y-eda.md`.
- **Qué generó el agente:** fuente y limpieza de los datos, regla de `target` con su diagrama, distribución de clases y conclusiones del EDA que importan al modelado, enlazando el código en lugar de copiarlo.
- **Comprobación:** todas las cifras se han recalculado con los CSV en bruto y procesado y con `build_target`; los casos de tests citados existen en `tests/test_target.py`.
- **Tras la revisión:** se añadieron las 9 temporadas del modelo final (#66): tabla de 2.1, distribución de clases junto a la de 2023-24 y el resultado de añadir temporadas en 2.4. La distribución, los goles y los equipos se recalcularon descargando las 9 temporadas con `download_premier_league_data` y coinciden con los de la revisión. Los F1 macro salen de la PR #66 y de `models/model_card.json`.
- **Revisión humana:** _pendiente_

---

### #1 Datos: descarga con varias temporadas y documentación corregida

- **Fecha:** 2026-11-16
- **Herramienta y modelo:** Claude Code (extensión de VS Code), Claude Opus 5.5.
- **Prompt clave:** revisar si mis tareas tenían errores después de los últimos cambios de `dev` y corregirlos todos.
- **Errores encontrados:**
  - `download_premier_league_data` no añadía la columna `Season` con varias temporadas, aunque su docstring lo decía; las features no reiniciaban el historial en cada temporada. El modelo final lo evitaba descargando temporada a temporada.
  - Si una fecha no se podía leer, se avisaba y la columna se quedaba como texto, que se ordena mal. Además, pandas avisaba porque 2016-17 usa `dd/mm/aa`.
  - Textos de `print` en español y con emojis (fallaban en consolas de Windows sin UTF-8) y un `import` sin usar.
  - El docstring de `target.py` asignaba mal las clases ajustadas («clase 1, 2 o 3», «clase 3 o 4»).
  - `docs/tarea-preparacion-dataset.md`: decía que la descarga guardaba un CSV (no guarda nada, así que el flujo de trabajo no funcionaba), citaba una URL inexistente (`/Premier/{year}.txt`), recomendaba validación temporal (el proyecto usa `StratifiedKFold`) y no explicaba cómo generar el dataset con features y target.
  - `data/processed/premier_league_2023_24.csv` estaba versionado desde mi commit del 11/11, contra la regla de no subir datasets.
- **Qué generó el agente:** la función de descarga reescrita (mismos partidos, `Season` con varias temporadas, error si una fecha no se lee, orden estable, textos en inglés), 7 tests sin red en `tests/test_dataset.py`, el docstring de `target.py` y el documento corregidos, y el CSV sacado del repositorio con `git rm --cached` (sigue en local).
- **Comprobación:** con las 9 temporadas reales la función nueva devuelve los mismos 3.420 partidos que la anterior, 380 por temporada, y 185 sin historial, como la ficha del modelo. Con 2023-24 coincide con el CSV que se saca del repositorio. Los tests nuevos fallan con el código anterior. `pytest` pasa entero.
- **Revisión humana:** _pendiente_
