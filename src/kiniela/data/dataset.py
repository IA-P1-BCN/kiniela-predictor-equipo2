"""Lectura del histórico de partidos."""

from pathlib import Path

import pandas as pd


def download_premier_league_data(season: str = "2324") -> pd.DataFrame:
    """Descarga y limpia datos reales de Premier League desde football-data.co.uk.
    
    Args:
        season: Código de temporada (ej: '2324' para 2023-24).
        
    Returns:
        DataFrame con partidos limpios incluyendo goles, equipos y resultado.
    """
    url = f"https://www.football-data.co.uk/mmz4281/{season}/E0.csv"
    
    print(f"\n{'='*60}")
    print(f"Descargando datos de Premier League {season} desde {url}...")
    print(f"{'='*60}\n")
    
    df = pd.read_csv(url, encoding='utf-8')
    
    # Columnas principales: HomeTeam, AwayTeam, FTHG, FTAG, FTR
    main_cols = ["HomeTeam", "AwayTeam", "FTHG", "FTAG", "FTR"]
    
    # Verificar columnas disponibles
    available_cols = [col for col in main_cols if col in df.columns]
    print(f"✅ Columnas principales disponibles: {available_cols}")
    
    # Eliminar filas con datos faltantes en columnas clave
    df = df.dropna(subset=main_cols)
    print(f"✅ Filas después de eliminar NaN: {len(df)}")
    
    # Limpiar duplicados (puede haber partidos duplicados en el CSV)
    df_original = len(df)
    df = df.drop_duplicates()
    duplicates_removed = df_original - len(df)
    if duplicates_removed > 0:
        print(f"   Eliminados {duplicates_removed} filas duplicadas")
    
    # Normalizar nombres de equipos: quitar apóstrofes y normalizar mayúsculas/minúsculas
    def normalize_team(name):
        return name.lower().replace("'", "").strip() if isinstance(name, str) else name
    
    df["HomeTeam"] = df["HomeTeam"].apply(normalize_team)
    df["AwayTeam"] = df["AwayTeam"].apply(normalize_team)
    
    print(f"   Equipos normalizados")
    
    # Verificar resultados FTR
    tr_results = df["FTR"].value_counts()
    print(f"\n✅ Distribución de resultados (FTR):")
    for result, count in tr_results.items():
        print(f"   {result}: {count} ({count/len(df)*100:.1f}%)")
    
    print(f"\n{'='*60}")
    print(f"✅ Dataset limpio de Premier League {season}")
    print(f"   Partidos totales: {len(df)}")
    print(f"  {'='*60}\n")
    
    return df


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