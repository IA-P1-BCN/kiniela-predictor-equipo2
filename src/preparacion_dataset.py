"""
Script para preparar el dataset de partidos de futbol - ALTERNATIVA
Issue #1 - Preparacion del Dataset
Asignado a: Anna (Data & EDA Lead)

NOTA: Como football-data.co.uk ya no esta disponible, usaremos datos simulados.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os


def crear_directorios():
    """Crear la estructura de carpetas data/raw y data/processed"""
    for dir_path in [DATA_DIR, RAW_DIR, PROCESSED_DIR]:
        if not os.path.exists(dir_path):
            print(f"Creando directorio: {dir_path}")
            os.makedirs(dir_path)


def generar_datos_premier_league_simulados():
    """Generar datos simulados de Premier League para EDA"""
    print("\n" + "="*60)
    print("GENERANDO DATOS DE PREMIER LEAGUE (Simulados)")
    print("="*60)
    
    equipos = ['arsenal', 'aston villa', 'bournemouth', 'brighton', 'burnley',
               'chelsea', 'crystal palace', 'everton', 'fulham', 'liverpool',
               'man city', 'man united', 'newcastle', 'nottm forest', 'sheffield utd',
               'spurs', 'west ham', 'wolves']
    
    dataframes = []
    
    for season in range(2015, 2025):
        print(f"\nGenerando temporada {season}...")
        
        partidos_semana = 8
        semanas_por_temporada = 38
        
        for semana in range(semanas_por_temporada):
            for pos_home in range(1, len(equipos) + 1, 2):
                if pos_home > len(equipos):
                    break
                
                home_team = random.choice(equipos)
                away_team = random.choice([t for t in equipos if t != home_team])
                
                start_date = datetime(season, 8, 1)
                end_date = datetime(season + 1, 5, 30)
                fecha_juego = start_date + timedelta(
                    days=random.randint(0, (end_date - start_date).days)
                )
                
                fh = random.choices([0, 1, 2, 3], weights=[0.15, 0.35, 0.30, 0.20])[0]
                ah = random.choices([0, 1, 2, 3], weights=[0.20, 0.30, 0.35, 0.15])[0]
                
                df_partido = pd.DataFrame({
                    'Date': [fecha_juego.strftime('%d/%m/%Y')],
                    'Time': ['14:00'],
                    'HomeTeam': [home_team],
                    'AwayTeam': [away_team],
                    'Day': [fecha_juego.weekday()],
                    'Month': [fecha_juego.strftime('%m')],
                    'Year': [fecha_juego.year],
                    'Stadium': [f"{home_team.capitalize()} Stadium"],
                    'Referee': ['referee_' + str(random.randint(1, 50))],
                    'FH': [fh],
                    'AH': [ah],
                })
                
                dataframes.append(df_partido)
    
    df_final = pd.concat(dataframes, ignore_index=True)
    
    print(f"\nDATASET COMPLETO:")
    print(f"Total de partidos: {len(df_final)}")
    print(f"Temporadas generadas: 2015-{datetime.now().year}")
    print(f"Equipos cubiertos: {len(equipos)} equipos")
    
    return df_final


def limpiar_datos(df):
    """Limpiar y preprocesar los datos"""
    print("\n" + "="*60)
    print("LIMPIEZA DE DATOS")
    print("="*60)
    
    dups = df.duplicated(subset=['Date', 'HomeTeam', 'AwayTeam']).sum()
    if dups > 0:
        print(f"\nADVERTENCIA: Encontrados {dups} duplicados eliminando...")
        df = df.drop_duplicates(subset=['Date', 'HomeTeam', 'AwayTeam'])
    
    print("\nCorrigiendo columnas de goles...")
    
    if 'FH' in df.columns:
        df['FH'] = pd.to_numeric(df['FH'], errors='coerce')
        non_numeric_fh = df['FH'].apply(lambda x: not isinstance(x, (int, float)))
        if non_numeric_fh.any():
            print(f"ADVERTENCIA: Valores no numericos en FH detectados")
    
    if 'AH' in df.columns:
        df['AH'] = pd.to_numeric(df['AH'], errors='coerce')
        non_numeric_ah = df['AH'].apply(lambda x: not isinstance(x, (int, float)))
        if non_numeric_ah.any():
            print(f"ADVERTENCIA: Valores no numericos en AH detectados")
    
    print("\nLimpieza de columnas de texto...")
    
    for col in ['Date', 'HomeTeam', 'AwayTeam']:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
            df[col] = df[col].str.lower()
    
    print("\nEliminando registros invalidos...")
    
    if 'FH' in df.columns and 'AH' in df.columns:
        df = df[~(df['FH'].isna() & df['AH'].isna())]
    
    if 'FH' in df.columns and 'AH' in df.columns:
        def get_result(fh, ah):
            if fh > ah: return 'H'
            elif ah > fh: return 'A'
            else: return 'D'
        
        df['Result'] = df.apply(lambda row: get_result(row['FH'], row['AH']), axis=1)
    
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y', errors='coerce')
        valid_dates_mask = df['Date'].notna()
        print(f"Filas con fecha valida: {valid_dates_mask.sum()}")
    
    return df


def info_dataset(df):
    """Mostrar informacion completa del dataset"""
    print("\n" + "="*60)
    print("INFORMACION DEL DATASET")
    print("="*60)
    
    print(f"\nTamano: {len(df)} partidos x {df.shape[1]} columnas")
    print(f"\nColumnas disponibles:")
    for col in df.columns:
        dtype = str(df[col].dtype)
        if df[col].dtype == 'object':
            unique_count = df[col].nunique()
            print(f"   {col:<15} ({dtype:<8}) - {len(df[col]):>6} valores unicos")
        else:
            print(f"   {col:<15} ({dtype:<8})")
    
    if 'Result' in df.columns:
        print(f"\nDistribucion por resultado:")
        for result, count in df['Result'].value_counts().items():
            pct = (count / len(df)) * 100
            print(f"   {result:<2} ({pct:.1f}%): {count:>6}")
    
    home_wins = df.groupby('HomeTeam')['FH'].sum().sort_values(ascending=False).head(5)
    for team, goals in home_wins.items():
        print(f"   {team:>12}: {goals} goles en casa")


def guardar_datos(df, csv_file):
    """Guardar el dataset limpio en CSV"""
    print("\n" + "="*60)
    print("GUARDANDO DATOS")
    print("="*60)
    
    csv_path = os.path.join(PROCESSED_DIR, csv_file)
    df.to_csv(csv_path, index=False)
    print(f"\nGuardado en CSV: {csv_path}")
    
    return csv_path


DATA_DIR = "data"
RAW_DIR = os.path.join(DATA_DIR, "raw")
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")


def main():
    """Funcion principal de preparacion del dataset"""
    
    print("\n" + "***"*3)
    print("KINIELA PREDICTOR - PREPARACION DEL DATASET")
    print("="*70)
    print(f"Asignado a: Anna (Data & EDA Lead)")
    print(f"Issue #1 - Preparacion del Dataset")
    print(f"NOTA: Usando datos simulados (fuente original no disponible)")
    print("="*70)
    
    crear_directorios()
    df_raw = generar_datos_premier_league_simulados()
    
    if df_raw is not None:
        df_clean = limpiar_datos(df_raw)
        info_dataset(df_clean)
        
        csv_file = "premier_league.csv"
        save_csv = guardar_datos(df_clean, csv_file=csv_file)
        
        print("\n" + "***"*3)
        print("DATASET PREPARADO CON EXITO!")
        print("="*70)
        print(f"\nArchivo guardado:")
        print(f"   {save_csv}")
        print("\nSiguientes pasos (Issues #2, #3, #4):")
        print("   1. Crear variable objetivo (target) con las 6 clases")
        print("   2. Feature engineering")
        print("   3. Analisis exploratorio (EDA)")
        
    else:
        print("\n" + "***"*3)
        print("FALLA EN LA PREPARACION DEL DATASET")
        print("="*70)


if __name__ == "__main__":
    main()