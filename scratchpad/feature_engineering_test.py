#!/usr/bin/env python3
"""Feature Engineering Test Script."""
# -*- coding: utf-8 -*-

import sys
sys.path.insert(0, '.')

# Importar módulos directamente desde el repositorio local
import pandas as pd
import numpy as np

# Cargar dataset.py directamente
dataset_path = 'D:/-GEEK-/FACTORIA F5/IA/PROYECTOS/M2/ai_predictor/kiniela-predictor-equipo2/src/kiniela/data/dataset.py'
with open(dataset_path, 'r', encoding='utf-8') as f:
    dataset_code = f.read()

# Ejecutar el código para definir las funciones
namespace = {}
exec(compile(dataset_code, dataset_path, 'exec'), namespace)
download_premier_league_data = namespace['download_premier_league_data']

print("="*60)
print("TEST FEATURE ENGINEERING")
print("="*60)

# Descargar datos de prueba
matches = download_premier_league_data('2324')
print(f'\nPartidos cargados (2023-24): {len(matches)}')
