# 📊 Preparación del Dataset - Issue #1
# Asignado a: Anna (Data & EDA Lead)

## Objetivo
Descargar, unificar y limpiar el dataset histórico de partidos de fútbol para Kiniela Predictor.

## Fuente de Datos
- **URL**: https://www.kaggle.com/datasets/football/datasets  
- **Alternativa**: https://www.football-data.co.uk/  
- **Columnas típicas**: `Date`, `Time`, `HomeTeam`, `AwayTeam`, `FH`, `AH`, `Result`

## Pasos a seguir

### 1️⃣ Descargar los datos
```python
import pandas as pd

# Cargar todos los años disponibles
dataframes = []
for year in range(1992, 2024):  # Ajustar según disponibilidad
    url = f"https://www.football-data.co.uk/Premier/{year}.txt"
    df = pd.read_csv(url)
    dataframes.append(df)

df_final = pd.concat(dataframes, ignore_index=True)
df_final.to_parquet("data/raw/premier_league_raw.parquet", index=False)
```

### 2️⃣ Limpieza básica
```python
# Eliminar duplicados (por fecha y equipos)
df = df.drop_duplicates(subset=['Date', 'HomeTeam', 'AwayTeam'])

# Limpiar nombres de equipos
df['HomeTeam'] = df['HomeTeam'].str.strip()
df['AwayTeam'] = df['AwayTeam'].str.strip()

# Asegurar tipos correctos
df['FH'] = pd.to_numeric(df['FH'], errors='coerce')  # Goles local
df['AH'] = pd.to_numeric(df['AH'], errors='coerce')  # Goles visitante
```

### 3️⃣ Guardar resultado limpio
```python
# Guardar en data/processed/
df_cleaned.to_parquet("data/processed/premier_league_clean.parquet", index=False)
df_cleaned.head()
print(f"Total de partidos: {len(df)}")
print(f"Fechas: {df['Date'].min()} a {df['Date'].max()}")
```

## Estructura esperada del dataset final
| Columna | Tipo | Descripción |
|---------|------|-------------|
| `Date` | object | Fecha del partido (YYYY-MM-DD) |
| `Time` | object | Hora del partido |
| `HomeTeam` | object | Equipo local |
| `AwayTeam` | object | Equipo visitante |
| `FH` | int64 | Goles locales |
| `AH` | int64 | Goles visitantes |
| `Result` | object | Resultado (H, A, D) |

## Estado
- [ ] Descargar dataset
- [ ] Limpiar y unificar datos
- [ ] Guardar en `data/raw/` y `data/processed/`
- [ ] Documentar el proceso en README

## Notas
Los datos se guardarán primero en formato parquet (mejor que CSV por compresión). Después convertiremos a CSV para los notebooks de EDA.