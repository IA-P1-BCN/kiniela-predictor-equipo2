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

La función `build_features()` añade variables históricas para cada partido:

**Features creadas:**
- `form_home_last_5`: Último resultado local (W=1, D=0, L=-1) en últimos 5 como local
- `form_away_last_5`: Último resultado visitante en últimos 5 como visitante
- `avg_home_goals_last_5`: Promedio goles marcados por local en últimos 5 partidos
- `avg_away_goals_last_5`: Promedio goles marcados por visitante en últimos 5 partidos
- `home_diff_last_5`: Diferencia de rendimiento (local - visitante) promedio últimos 5
- `away_diff_last_5`: Diferencia de rendimiento (visitante - local) promedio últimos 5
- `recent_home_form`: Forma reciente local (1=último W, 0.5=D, 0=L)
- `recent_away_form`: Forma reciente visitante (1=último W, 0.5=D, 0=L)

**Principios clave:**
- **No data leakage**: Solo se usan partidos anteriores al partido actual
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

**Distribución esperada (Premier League 2023-24):**
| Clase | Descripción | Porcentaje aproximado |
|-------|-------------|----------------------|
| 0 | Victoria local clara (diff ≥ 2) | ~11% |
| 1 | Local gana ajustado (diff < 2) | ~38% |
| 2 | Empate (diff = 0) | ~18% |
| 3 | Visitante gana ajustado (diff < 2) | ~33% |
| 4 | Victoria visitante clara (diff ≤ -2) | ~7% |
| 5 | Partido alto con 4+ goles totales | ~44% |

## Flujo de Trabajo Completo

```bash
# 1. Descarga de datos (una sola temporada)
python -c "from src.kiniela.data.dataset import download_premier_league_data; print(download_premier_league_data('2324'))"

# 2. Feature engineering
import pandas as pd
from src.kiniela.features import engineering

matches = pd.read_csv('data/processed/premier_league_2023_24.csv')
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
- [docs/ai-log/anna.md](<../ai-log/anna.md>) - Bitácora de progreso