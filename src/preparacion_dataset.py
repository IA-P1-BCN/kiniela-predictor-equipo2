"""
📦 Script para preparar el dataset de partidos de fútbol
Issue #1 - Preparación del Dataset
Asignado a: Anna (Data & EDA Lead)
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os

# Configuración de directorios
DATA_DIR = "data"
RAW_DIR = os.path.join(DATA_DIR, "raw")
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")


def crear_directorios():
    """Crear la estructura de carpetas data/raw y data/processed"""
    for dir_path in [DATA_DIR, RAW_DIR, PROCESSED_DIR]:
        if not os.path.exists(dir_path):
            print(f"✅ Creando directorio: {dir_path}")
            os.makedirs(dir_path)


def descargar_datos_premier_league():
    """
    Descargar datos históricos de Premier League desde 2015 hasta actualidad
    
    Fuente: https://www.football-data.co.uk/Premier/
    
    Returns:
        DataFrame con todos los partidos descargados
    """
    print("\n" + "="*60)
    print("📥 DESCARGANDO DATOS DE PREMIER LEAGUE")
    print("="*60)
    
    dataframes = []
    years_range = list(range(2015, 2024))  # Años disponibles en la fuente
    
    for year in years_range:
        url = f"https://www.football-data.co.uk/Premier/{year}.txt"
        
        try:
            print(f"\n📥 Descargando Premier League {year}...")
            print(f"   URL: {url}")
            
            df = pd.read_csv(url)
            
            # Guardar temporalmente para verificar
            temp_file = f"data/raw/temp_premier_{year}.txt"
            df.to_csv(temp_file, index=False)
            
            dataframes.append(df)
            print(f"   ✅ {len(df)} partidos cargados correctamente")
            
        except Exception as e:
            print(f"   ❌ Error descargando año {year}: {str(e)[:100]}")
    
    # Eliminar archivos temporales
    for year in years_range:
        try:
            temp_file = f"data/raw/temp_premier_{year}.txt"
            if os.path.exists(temp_file):
                os.remove(temp_file)
                print(f"   🗑️  Eliminando archivo temporal: {temp_file}")
        except:
            pass
    
    # Concatenar todos los DataFrames
    if dataframes:
        df_final = pd.concat(dataframes, ignore_index=True)
        print(f"\n📊 DATASET COMPLETO:")
        print(f"   Total de partidos: {len(df_final)}")
        print(f"   Años cubiertos: {years_range[0]}-{years_range[-1]}")
        
        return df_final
    else:
        print("\n❌ No se pudieron descargar datos.")
        return None


def limpiar_datos(df):
    """
    Limpiar y preprocesar los datos
    
    Args:
        df: DataFrame crudo con partidos
        
    Returns:
        DataFrame limpio y listo para análisis
    """
    print("\n" + "="*60)
    print("🧹 LIMPIEZA DE DATOS")
    print("="*60)
    
    # 1. Verificar duplicados
    dups = df.duplicated(subset=['Date', 'HomeTeam', 'AwayTeam']).sum()
    if dups > 0:
        print(f"\n⚠️  Encontrados {dups} duplicados eliminando...")
        df = df.drop_duplicates(subset=['Date', 'HomeTeam', 'AwayTeam'])
    
    # 2. Verificar y corregir valores numéricos (goles)
    print("\n🔢 Corrigiendo columnas de goles...")
    
    # Columna FH (Full Time Home - Goles del local)
    if 'FH' in df.columns:
        df['FH'] = pd.to_numeric(df['FH'], errors='coerce')
        
        # Reemplazar valores no numéricos por 0 o NaN según corresponda
        non_numeric_fh = df['FH'].apply(lambda x: not isinstance(x, (int, float)))
        if non_numeric_fh.any():
            print(f"   ⚠️  Valores no numéricos en FH detectados")
            # Opción: convertir a string y luego intentar parsear
            df['FH'] = df['FH'].astype(str).replace('D', '-1').replace('A', '-2')
    
    # Columna AH (Full Time Away - Goles del visitante)
    if 'AH' in df.columns:
        df['AH'] = pd.to_numeric(df['AH'], errors='coerce')
        
        non_numeric_ah = df['AH'].apply(lambda x: not isinstance(x, (int, float)))
        if non_numeric_ah.any():
            print(f"   ⚠️  Valores no numéricos en AH detectados")
            df['AH'] = df['AH'].astype(str).replace('D', '-1').replace('A', '-2')
    
    # 3. Limpiar columnas de texto
    print("\n📝 Limpieza de columnas de texto...")
    
    for col in ['Date', 'HomeTeam', 'AwayTeam', 'Hteam', 'ATEam']:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
            # Normalizar mayúsculas/minúsculas para consistencia
            df[col] = df[col].str.lower()
    
    # 4. Eliminar filas con datos inválidos (goles negativos o NaN en ambas columnas)
    print("\n❌ Eliminando registros inválidos...")
    
    if 'FH' in df.columns and 'AH' in df.columns:
        df = df[~(df['FH'].isna() & df['AH'].isna())]  # Eliminar si ambos goles faltan
    
    # 5. Crear columna de resultado (para referencia)
    if 'FH' in df.columns and 'AH' in df.columns:
        def get_result(fh, ah):
            if fh > ah: return 'H'  # Home win
            elif ah > fh: return 'A'  # Away win
            else: return 'D'  # Draw
        
        df['Result'] = df.apply(lambda row: get_result(row['FH'], row['AH']), axis=1)
    
    # 6. Convertir Date a datetime para análisis temporal
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y', errors='coerce')
        
        # Eliminar filas con fecha inválida
        valid_dates_mask = df['Date'].notna()
        print(f"   Filas con fecha válida: {valid_dates_mask.sum()}")
    
    return df


def guardar_datos(df, parquet_file, csv_file):
    """
    Guardar el dataset limpio en formatos diferentes
    
    Args:
        df: DataFrame limpio
        parquet_file: nombre del archivo parquet
        csv_file: nombre del archivo CSV
    """
    print("\n" + "="*60)
    print("💾 GUARDANDO DATOS")
    print("="*60)
    
    # Guardar en Parquet (formato binario compacto)
    parquet_path = os.path.join(PROCESSED_DIR, parquet_file)
    df.to_parquet(parquet_path, index=False)
    print(f"\n✅ Guardado en Parquet: {parquet_path}")
    
    # Guardar en CSV (para notebooks y análisis más fácil)
    csv_path = os.path.join(PROCESSED_DIR, csv_file)
    df.to_csv(csv_path, index=False)
    print(f"✅ Guardado en CSV: {csv_path}")
    
    return parquet_path, csv_path


def info_dataset(df):
    """Mostrar información completa del dataset"""
    print("\n" + "="*60)
    print("📊 INFORMACIÓN DEL DATASET")
    print("="*60)
    
    print(f"\n📦 Tamaño: {len(df)} partidos × {df.shape[1]} columnas")
    print(f"\n📅 Fecha de los datos:")
    if 'Date' in df.columns:
        print(f"   Inicio: {df['Date'].min()}")
        print(f"   Fin: {df['Date'].max()}")
    
    print(f"\n🏆 Temporada cubierta: Premier League {list(range(2015, 2024))}")
    
    print(f"\n📈 Columnas:")
    for col in df.columns:
        dtype = str(df[col].dtype)
        if df[col].dtype == 'object':
            unique_count = df[col].nunique()
            print(f"   • {col:<15} ({dtype:<8}) - {len(df[col]):>6} valores únicos")
    
    # Estadísticas por tipo de resultado
    if 'Result' in df.columns:
        print(f"\n📊 Distribución por resultado:")
        for result, count in df['Result'].value_counts().items():
            pct = (count / len(df)) * 100
            print(f"   • {result:<2} ({pct:.1f}%): {count:>6}")


def main():
    """Función principal de preparación del dataset"""
    
    print("\n" + "🏆"*3)
    print("KINIELA PREDICTOR - PREPARACIÓN DEL DATASET")
    print("="*70)
    print(f"👤 Asignado a: Anna (Data & EDA Lead)")
    print(f"🎯 Issue #1 - Preparación del Dataset")
    print("="*70)
    
    # 1. Crear estructura de directorios
    crear_directorios()
    
    # 2. Descargar datos
    df_raw = descargar_datos_premier_league()
    
    if df_raw is not None:
        # 3. Limpiar datos
        df_clean = limpiar_datos(df_raw)
        
        # 4. Mostrar información
        info_dataset(df_clean)
        
        # 5. Guardar dataset procesado
        parquet_file = "premier_league.parquet"
        csv_file = "premier_league.csv"
        
        save_parquet, save_csv = guardar_datos(
            df_clean, 
            parquet_file=parquet_file, 
            csv_file=csv_file
        )
        
        print("\n" + "✅"*3)
        print("¡DATASET PREPARADO CON ÉXITO!")
        print("="*70)
        print(f"\n📂 Archivos guardados:")
        print(f"   • {save_parquet}")
        print(f"   • {save_csv}")
        print("\n📝 Siguientes pasos (Issues #2, #3, #4):")
        print("   1. Crear variable objetivo (target) con las 6 clases")
        print("   2. Feature engineering")
        print("   3. Análisis exploratorio (EDA)")
        
    else:
        print("\n" + "❌"*3)
        print("FALLA EN LA PREPARACIÓN DEL DATASET")
        print("="*70)


if __name__ == "__main__":
    main()