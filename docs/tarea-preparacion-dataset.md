# Preparación del Dataset de Premier League

## Objetivo

Descargar, limpiar y preparar datos reales de partidos de la Premier League para entrenar el modelo de predicción multiclase.

## Fuente de Datos

Los datos provienen de [football-data.co.uk](https://www.football-data.co.uk/), que publica un CSV gratuito por temporada.

- **URL de cada temporada**: `https://www.football-data.co.uk/mmz4281/{temporada}/E0.csv`, con el código de temporada de 4 cifras (`2324` = 2023-24)
- **Temporadas usadas**: 2023-24 para el EDA; de 2015-16 a 2023-24 (9 temporadas) para el modelo final
- **Competición**: Premier League (`E0`)
- **Columnas principales**: HomeTeam, AwayTeam, FTHG (goles locales), FTAG (goles visitantes), FTR (resultado: H/A/D)

## Estructura del Código

### 1. Descarga de Datos (`src/kiniela/data/dataset.py`)

La función `download_premier_league_data()` descarga y limpia datos reales:

```python
matches = download_premier_league_data("2324")                  # una temporada
matches = download_premier_league_data(["2223", "2324"])        # varias: añade la columna Season
```

**Limpieza realizada:**
- Elimina filas con valores NaN en columnas principales
- Elimina duplicados
- Normaliza nombres de equipos (minúsculas, sin apóstrofes: `"Nott'm Forest"` → `"nottm forest"`)
- Convierte las fechas a fecha leyendo primero el día (`dd/mm/aaaa`, y `dd/mm/aa` en 2016-17); si una fecha no se puede leer, da error en lugar de dejarla como texto
- Ordena partidos por fecha
- Con varias temporadas, añade la columna `Season` con el código de cada una, para que las features reinicien el historial en cada temporada

**Salida:** devuelve un `DataFrame`; no guarda nada en disco. Para guardarlo, ver el flujo de trabajo de abajo.

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
- **Adaptable**: Funciona con una temporada o con varias, siempre que tengan la columna `Season` (la añade `download_premier_league_data` al pedir varias)
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

# 1. Descarga de datos (una sola temporada) y copia local (data/processed/ no se versiona)
download_premier_league_data("2324").to_csv("data/processed/premier_league_2023_24.csv", index=False)

# 2. Feature engineering
matches = load_matches("data/processed/premier_league_2023_24.csv")
features_df = engineering.build_features(matches)

# 3. Target labelling (por separado o fusionado en el pipeline de entrenamiento)
```

## Notas Importantes

### Datos Reales vs Simulados
- ✅ **Usar datos reales** desde football-data.co.uk
- ❌ **No usar datos simulados** (generan goles, equipos y resultados al azar)

### Varias temporadas: el modelo final

Con una sola temporada el modelo no superaba al modelo de prueba, así que el modelo final (#66) se entrena con las 9 temporadas de 2015-16 a 2023-24. Desde la raíz del repositorio, este comando las descarga, guarda una copia en `data/raw/premier_league_1516_2324.csv` y entrena y guarda el modelo:

```bash
PYTHONPATH=src python -m kiniela.models.final
```

Para trabajar con las mismas temporadas desde Python:

```python
SEASONS = ["1516", "1617", "1718", "1819", "1920", "2021", "2122", "2223", "2324"]
matches = download_premier_league_data(SEASONS)  # 3.420 partidos, con la columna Season
```

### Consideraciones de Data Leakage

- Las features históricas deben usar **solo partidos anteriores** al partido actual (lo garantiza `build_features`, ver la sección 3 del informe)
- Los modelos se validan con `StratifiedKFold` (5 folds, con mezcla y `RANDOM_STATE`), que mantiene la proporción de clases en cada fold. No hay fuga porque cada fila ya lleva solo información anterior al partido. Una validación temporal (entrenar con temporadas pasadas y validar con la siguiente) sería una mejora posible, pero no es la que usa el proyecto.

## Guardado del Dataset Final

El dataset unificado con features y target (el que usan los comandos de entrenamiento y de drift) se guarda en `data/processed/premier_league_with_features_and_target.csv`. Se genera con `build_modelling_dataset`, la misma función que usa el modelo final:

```python
from kiniela.data.dataset import download_premier_league_data
from kiniela.models.final import build_modelling_dataset

matches = download_premier_league_data("2324")
build_modelling_dataset(matches).to_csv(
    "data/processed/premier_league_with_features_and_target.csv", index=False
)
```

**Solo temporadas con los equipos actuales en `data/processed/`.** La app saca la lista de equipos del CSV más reciente de esa carpeta, y el modelo final solo acepta los 20 de la última temporada. Si se guarda ahí un dataset de varias temporadas, la app ofrecería también equipos descendidos (33 en total) y su predicción daría error. El de las 9 temporadas lo guarda `python -m kiniela.models.final` en `data/raw/`.

Ni este archivo ni ningún otro CSV de `data/` se suben a Git: se regeneran con el código.

## Referencias

- [AGENTS.md](<../AGENTS.md>) - Reglas de trabajo y convenciones
- [docs/ai-log/anna.md](<ai-log/anna.md>) - Bitácora de progreso