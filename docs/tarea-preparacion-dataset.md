# Preparación del Dataset de Premier League

## Objetivo

Descargar, limpiar y preparar datos reales de partidos de la Premier League para entrenar el modelo de predicción multiclase.

## Fuente de Datos

Los datos provienen de [football-data.co.uk](https://www.football-data.co.uk/) (API gratuita).

- **URL base**: `https://www.football-data.co.uk/mmz4281/`
- **Temporadas disponibles**: 2015-16 hasta la más reciente
- **Competición**: Premier League (`E0`)
- **Columnas principales**: HomeTeam, AwayTeam, FTHG (goles locales), FTAG (goles visitantes), FTR (resultado: H/A/D)

## Estructura del Código

### 1. Descarga de Datos (`src/kiniela/data/dataset.py`)

La función `download_premier_league_data()` descarga y limpia datos reales:

```python
matches = download_premier_league_data(season="2324")  # Temporada 2023-24
```

**Limpieza realizada:**
- Elimina filas con valores NaN en columnas principales
- Elimina duplicados
- Normaliza nombres de equipos (lowercase, sin apóstrofes)
- Convierte fechas al formato datetime (`dayfirst=True` por convención británica)
- Ordena partidos por fecha

**Salida:** Dataset limpio en `data/processed/premier_league_XX.csv`

### 2. Feature Engineering (`src/kiniela/features/engineering.py`)

La función `build_features()` calcula las features de cada partido del histórico y `build_match_features(history, home_team, away_team)` las de un partido nuevo para la app. Las dos usan el mismo cálculo, así que la app recibe exactamente las features con las que se entrena el modelo. La lista y su orden están en `FEATURE_COLUMNS`.

**Features creadas** (últimos 5 partidos anteriores de la temporada en la misma condición: el local en casa, el visitante fuera):
- `form_home_last_5` / `form_away_last_5`: media de los 5 resultados desde el punto de vista del equipo (victoria = 1, empate = 0, derrota = -1)
- `avg_home_goals_last_5` / `avg_away_goals_last_5`: media de goles marcados
- `home_diff_last_5` / `away_diff_last_5`: media de la diferencia de goles (marcados - encajados)
- `match_diff`: `form_home_last_5 - form_away_last_5`
- `match_goals_expected`: `avg_home_goals_last_5 + avg_away_goals_last_5`

Se eliminaron `recent_home_form`, `recent_away_form` y `match_momentum` porque duplicaban la información de las anteriores (issue #34). Si un equipo aún no tiene partidos previos en esa condición, sus features quedan vacías (`NaN`).

**Principios clave:**
- **No data leakage**: Solo se usan partidos de fechas anteriores al partido actual (los del mismo día tampoco cuentan)
- **Fechas**: Las fechas `dd/mm/aaaa` del CSV se convierten a fecha antes de ordenar; ordenadas como texto, el 1 de septiembre quedaría antes que el 11 de agosto
- **Adaptable**: Funciona con datasets de una sola temporada o múltiples temporadas concatenadas
- **Granularidad**: Features separadas por localía para capturar el contexto específico

### 3. Target Labelling (`src/kiniela/data/target.py`)

La función `build_target()` etiqueta la clase del resultado según la regla establecida:

**Regla de clasificación (6 clases):**
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

**Distribución real (Premier League 2023-24, 380 partidos):**
| Clase | Descripción | Porcentaje |
|-------|-------------|-----------|
| 0 | Victoria local clara (diff ≥ 2) | 11,1 % |
| 1 | Local gana ajustado (diff = 1) | 13,9 % |
| 2 | Empate (diff = 0) | 12,9 % |
| 3 | Visitante gana ajustado (diff = -1) | 11,6 % |
| 4 | Victoria visitante clara (diff ≤ -2) | 6,8 % |
| 5 | Partido alto con 4+ goles totales | 43,7 % |

Todo partido con 4 o más goles es clase 5, aunque sea un empate o una victoria (por ejemplo 2-2 o 3-1). Por eso las clases 0-4 quedan por debajo de los porcentajes habituales de victoria local, empate y victoria visitante.

## Flujo de Trabajo Completo

Desde la raíz del repositorio, con `PYTHONPATH=src`:

```python
from kiniela.data.dataset import download_premier_league_data, load_matches
from kiniela.features import engineering

# 1. Descarga de datos (una sola temporada)
download_premier_league_data("2324")

# 2. Feature engineering
matches = load_matches("data/processed/premier_league_2023_24.csv")
features_df = engineering.build_features(matches)

# 3. Target labelling (por separado o fusionado en el pipeline de entrenamiento)
```

## Notas Importantes

### Datos Reales vs Simulados
- ✅ **Usar datos reales** desde football-data.co.uk
- ❌ **No usar datos simulados** (generan goles, equipos y resultados al azar)
- La API `football-data.co.uk` funciona correctamente con la URL: `/Premier/{year}.txt`

### Temporadas Disponibles
El modelo necesita múltiples temporadas para evitar sobreajuste. Se recomienda descargar al menos 2015-16 hasta la temporada más reciente disponible.

**Ejemplo con múltiples temporadas:**
```python
SEASONS = ["1516", "1617", "1718", "1819", "1920", "2021", "2122", "2223", "2324"]
matches = download_premier_league_data(SEASONS)
```

### Consideraciones de Data Leakage
- Las features históricas deben usar **solo partidos anteriores** al partido actual
- El dataset final debe estar ordenado por fecha antes del train/test split
- Validación cruzada temporal (time-based CV) es preferible a k-fold aleatorio

## Guardado del Dataset Final

El dataset unificado con features y target debe guardarse en:

```
data/processed/premier_league_with_features_and_target.csv
```

Este archivo **NO** debe ser versionado en Git, ya que contiene datos dinámicos.

## Referencias

- [AGENTS.md](<../AGENTS.md>) - Reglas de trabajo y convenciones
- [docs/ai-log/anna.md](<ai-log/anna.md>) - Bitácora de progreso