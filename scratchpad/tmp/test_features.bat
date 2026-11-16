@echo off
pip install -q pandas numpy
python << 'ENDPYTHON'
import pandas as pd
from kiniela.features import engineering


# Cargar dataset (sin columna Season)
print("Cargando dataset...")
matches = pd.read_csv('data/processed/premier_league_2023_24.csv')
print(f"Dataset cargado: {len(matches)} partidos")
print(f"Columnas iniciales: {list(matches.columns)[:10]}...")


# Ejecutar feature engineering
print("\nEjecutando build_features()...")
features_df = engineering.build_features(matches)

print(f"\nFeatures completadas!")
print(f"Partidos procesados: {len(features_df)}")
print(f"Nuevas columnas de features:")


# Mostrar las nuevas columnas creadas
new_cols = [col for col in features_df.columns if col not in matches.columns]
for col in new_cols:
    print(f"  - {col}")

ENDPYTHON