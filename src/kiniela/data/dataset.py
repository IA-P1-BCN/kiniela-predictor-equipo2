"""Lectura del histórico de partidos."""

from pathlib import Path
import datetime as dt

import pandas as pd


def download_premier_league_data(season: str | list[str] = "2324") -> pd.DataFrame:
    """Descarga y limpia datos reales de Premier League desde football-data.co.uk.
    
    Args:
        season: Código de temporada (ej: '2324' para 2023-24).
                 También acepta una lista de temporadas para descarga múltiple,
                 ej: ['1516', '1617', ..., '2324'].
        
    Returns:
        DataFrame con partidos limpios incluyendo goles, equipos, resultado y fecha.
        Si season es una lista, el DataFrame resultante tendrá la columna 'Season'.
    
    Ejemplo de uso para todas las temporadas (2015-2025):
        SEASONS = ["1516", "1617", "1718", "1819", "1920", "2021", "2122", "2223", "2324", "2425"]
        matches = download_premier_league_data(SEASONS)
    """
    url_base = "https://www.football-data.co.uk/mmz4281/"
    
    if isinstance(season, str):
        seasons = [season]
    else:
        seasons = season if isinstance(season, list) else [season]
    
    frames = []
    
    for s in seasons:
        url = f"{url_base}{s}/E0.csv"
        print(f"\n{'='*60}")
        print(f"Descargando datos de Premier League {s} desde {url}...")
        print(f"{'='*60}\n")
        
        df = pd.read_csv(url, encoding="utf-8")
        main_cols = ["HomeTeam", "AwayTeam", "FTHG", "FTAG", "FTR"]
        date_col = "Date"
        
        available_main = [col for col in main_cols if col in df.columns]
        has_date = date_col in df.columns
        
        print(f"✅ Columnas principales disponibles: {available_main}")
        
        if not has_date:
            print(f"   ⚠️  La columna '{date_col}' no está disponible en esta temporada")
        
        df = df.dropna(subset=main_cols)
        print(f"✅ Filas después de eliminar NaN: {len(df)}")
        
        df_original = len(df)
        df = df.drop_duplicates()
        duplicates_removed = df_original - len(df)
        if duplicates_removed > 0:
            print(f"   Eliminados {duplicates_removed} filas duplicadas")
        
        def normalize_team(name):
            return name.lower().replace("'", "").strip() if isinstance(name, str) else name
        
        df["HomeTeam"] = df["HomeTeam"].apply(normalize_team)
        df["AwayTeam"] = df["AwayTeam"].apply(normalize_team)
        print(f"   Equipos normalizados")
        
        if has_date:
            try:
                df["Date"] = pd.to_datetime(df["Date"], dayfirst=True)
                print(f"✅ Fechas convertidas a datetime")
            except Exception as e:
                print(f"   ⚠️  Error al convertir fechas: {e}")
        
        frames.append(df)
    
    if len(frames) == 1:
        matches = frames[0]
    else:
        matches = pd.concat(frames, ignore_index=True)
        print(f"\n{'='*60}")
        print(f"✅ Dataset unificado de todas las temporadas")
        print(f"   Total partidos: {len(matches)}")
    
    if "Date" in matches.columns:
        matches = matches.sort_values("Date").reset_index(drop=True)
        print(f"✅ Partidos ordenados por fecha")
    
    if "FTR" in matches.columns:
        tr_results = matches["FTR"].value_counts()
        print(f"\n✅ Distribución de resultados (FTR):")
        for result, count in tr_results.items():
            print(f"   {result}: {count} ({count/len(matches)*100:.1f}%)")
    
    print(f"\n{'='*60}")
    if len(seasons) == 1:
        print(f"✅ Dataset de Premier League {seasons[0]}")
    else:
        print(f"✅ Dataset unificado de Premier League ({seasons[0]}-{seasons[-1]})")
    print(f"   Partidos totales: {len(matches)}")
    
    return matches


def load_matches(path: str | Path) -> pd.DataFrame:
    """Carga un CSV de partidos.

    El repositorio no incluye datos. El archivo lo genera la preparación
    del dataset y debe vivir en ``data/``.
    """
    source = Path(path)
    if not source.is_file():
        raise FileNotFoundError(
            f"No existe el dataset en {source}. Guárdalo en data/raw o data/processed."
        )
    return pd.read_csv(source)
