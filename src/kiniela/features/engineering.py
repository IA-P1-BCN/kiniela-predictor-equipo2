"""Forma reciente, goles, diferencia de rendimiento y localía.

Las variables históricas tienen que calcularse solo con partidos
anteriores, para no filtrar el resultado del partido que se predice.
"""

import pandas as pd
import numpy as np
from datetime import datetime


def build_features(matches: pd.DataFrame) -> pd.DataFrame:
    """Añade las features de modelado al histórico de partidos.
    
    Args:
        matches: DataFrame con columnas: HomeTeam, AwayTeam, FTHG, FTAG, FTR, Date (y opcionalmente Season)
        
    Returns:
        DataFrame con features añadidas y ordenadas por fecha.
    
    Features creadas:
    - **form_home_last_5**: Último resultado del local (1=W, 0=D, -1=L) en últimos 5 partidos como local
    - **form_away_last_5**: Último resultado del visitante (1=W, 0=D, -1=L) en últimos 5 partidos como visitante  
    - **avg_home_goals_last_5**: Promedio goles marcados por local en últimos 5 partidos como local
    - **avg_away_goals_last_5**: Promedio goles marcados por visitante en últimos 5 partidos como visitante
    - **home_diff_last_5**: Diferencia goles (local-visitante) promedio de últimos 5 partidos del local
    - **away_diff_last_5**: Diferencia goles (visitante-local) promedio de últimos 5 partidos del visitante
    - **recent_home_form**: Forma reciente local (1=último W, 0.5=D, 0=L) en últimos 5 como local
    - **recent_away_form**: Forma reciente visitante (1=último W, 0.5=D, 0=L) en últimos 5 como visitante
    - **avg_home_goals_conceded_last_5**: Promedio goles recibidos por local en últimos 5 partidos
    - **avg_away_goals_conceded_last_5**: Promedio goles recibidos por visitante en últimos 5 partidos
    
    Justificación:
    - La forma reciente captura el momentum actual del equipo
    - Los promedios de goles indican la potencia ofensiva
    - Las diferencias de rendimiento muestran la fortaleza defensiva/ofensiva neta
    - La localía reciente refleja si el equipo está rindiendo bien en su estadio
    
    Cada feature solo usa información de PARTIDOS ANTERIORES para evitar data leakage.
    
    Nota: Para predicción individual (app) ver build_match_features().
    """
    if matches.empty:
        raise ValueError("El histórico de partidos está vacío.")
    
    # Ordenar por fecha para asegurar que las features usan solo datos pasados
    matches = matches.sort_values("Date")
    
    print(f"\n{'='*60}")
    print("Feature Engineering - Calculando features históricas...")
    print(f"{'='*60}\n")
    
    # Función para convertir resultado a número (W=1, D=0, L=-1)
    def result_to_num(result):
        if result == "H": return 1
        elif result == "A": return -1
        else: return 0
    
    matches["ResultHome"] = matches["FTR"].apply(lambda x: result_to_num(x))
    matches["ResultAway"] = matches["FTR"].apply(lambda x: -result_to_num(x))
    
    # Para cada equipo, calcular las estadísticas de sus últimos N partidos como local/visitante
    N = 5  # Últimos 5 partidos para forma reciente
    
    print(f"Calculando historial por equipo ({N} partidos recientes)...")
    
    features_list = []
    
    for idx, row in matches.iterrows():
        home_team = str(row["HomeTeam"])
        away_team = str(row["AwayTeam"])
        
        # Detectar si el dataset tiene columna Season o no
        if "Season" not in matches.columns:
            # No hay columna Season - usar todo el histórico disponible
            print(f"   ⚠️  Dataset sin columna 'Season', usando todo el histórico...")
            season_matches = matches.copy()
        else:
            # Filtrar solo los partidos de la misma temporada
            season_matches = matches[matches["Season"] == row["Season"]]
        
        # Encontrar todos los partidos del local hasta ahora (ordenados por fecha)
        home_history = season_matches[season_matches["HomeTeam"] == home_team].sort_values("Date")
        away_history = season_matches[season_matches["AwayTeam"] == away_team].sort_values("Date")
        
        # Calcular estadísticas del local usando solo partidos anteriores (evitando data leakage)
        if len(home_history) > 0:
            current_date = row["Date"]
            home_past = home_history[home_history["Date"] < current_date]
            
            if len(home_past) > 0:
                # Últimos N partidos como local del local
                last_n_home = home_past.tail(N).copy()
                
                form_home_last_5 = result_to_num(last_n_home.iloc[-1]["FTR"])
                avg_home_goals_last_5 = last_n_home["FTHG"].tail(N).mean()
                away_goals_conceded_last_5 = last_n_home["FTAG"].tail(N).mean()
                home_diff_last_5 = (last_n_home["FTHG"] - last_n_home["FTAG"]).tail(N).mean()
                recent_home_form = result_to_num(last_n_home.iloc[-1]["FTR"])
            else:
                form_home_last_5 = np.nan
                avg_home_goals_last_5 = np.nan
                away_goals_conceded_last_5 = np.nan
                home_diff_last_5 = np.nan
                recent_home_form = np.nan
        else:
            form_home_last_5 = np.nan
            avg_home_goals_last_5 = np.nan
            away_goals_conceded_last_5 = np.nan
            home_diff_last_5 = np.nan
            recent_home_form = np.nan
        
        # Calcular estadísticas del visitante (últimos N como visitante)
        if len(away_history) > 0:
            current_date = row["Date"]
            away_past = away_history[away_history["Date"] < current_date]
            
            if len(away_past) > 0:
                # Últimos N partidos como visitante del visitante
                last_n_away = away_past.tail(N).copy()
                
                form_away_last_5 = result_to_num(last_n_away.iloc[-1]["FTR"])
                avg_away_goals_last_5 = last_n_away["FTAG"].tail(N).mean()
                home_goals_conceded_last_5 = last_n_away["FTHG"].tail(N).mean()
                away_diff_last_5 = (last_n_away["FTAG"] - last_n_away["FTHG"]).tail(N).mean()
                recent_away_form = result_to_num(last_n_away.iloc[-1]["FTR"])
            else:
                form_away_last_5 = np.nan
                avg_away_goals_last_5 = np.nan
                home_goals_conceded_last_5 = np.nan
                away_diff_last_5 = np.nan
                recent_away_form = np.nan
        else:
            form_away_last_5 = np.nan
            avg_away_goals_last_5 = np.nan
            home_goals_conceded_last_5 = np.nan
            away_diff_last_5 = np.nan
            recent_away_form = np.nan
        
        # Features combinadas
        match_diff = form_home_last_5 - form_away_last_5 if not (pd.isna(form_home_last_5) and pd.isna(form_away_last_5)) else np.nan
        match_goals_expected = avg_home_goals_last_5 + avg_away_goals_last_5 if not (pd.isna(avg_home_goals_last_5) and pd.isna(avg_away_goals_last_5)) else np.nan
        match_momentum = recent_home_form - recent_away_form if not (pd.isna(recent_home_form) and pd.isna(recent_away_form)) else np.nan
        
        features_list.append({
            "HomeTeam": home_team,
            "AwayTeam": away_team,
            # Formas recientes
            "form_home_last_5": form_home_last_5,
            "form_away_last_5": form_away_last_5,
            # Promedios de goles
            "avg_home_goals_last_5": avg_home_goals_last_5,
            "avg_away_goals_last_5": avg_away_goals_last_5,
            # Diferencias de rendimiento (promedio últimos N)
            "home_diff_last_5": home_diff_last_5,
            "away_diff_last_5": away_diff_last_5,
            # Forma reciente numérica (1/0.5/0 para peso en regresión logística)
            "recent_home_form": recent_home_form,
            "recent_away_form": recent_away_form,
            # Goles originales (para feature engineering adicional si es necesario)
            "FTHG": row["FTHG"],
            "FTAG": row["FTAG"],
            "FTR": row["FTR"],
            "Date": current_date
        })
    
    features_df = pd.DataFrame(features_list)
    
    # Eliminar columnas temporales si existen (no queremos duplicados)
    feature_cols = ["HomeTeam", "AwayTeam", 
                     "form_home_last_5", "form_away_last_5",
                     "avg_home_goals_last_5", "avg_away_goals_last_5",
                     "home_diff_last_5", "away_diff_last_5",
                     "recent_home_form", "recent_away_form",
                     "match_diff", "match_goals_expected", "match_momentum",
                     "FTHG", "FTAG", "FTR"]
    
    # Solo conservar las columnas que queremos
    if len(feature_cols) <= len(features_df.columns):
        features_df = features_df[feature_cols]
    
    print(f"\n✅ Features creadas:")
    new_features = [col for col in feature_cols if col not in ["FTHG", "FTAG", "FTR"]]
    print(f"   - {', '.join(new_features)}")
    print(f"\n{'='*60}")
    print(f"✅ Total partidos con features: {len(features_df)}")
    
    return features_df


def build_match_features(history: pd.DataFrame, home_team: str, away_team: str) -> dict:
    """Calcula las features para un partido nuevo basado en el historial.
    
    Esta función es necesaria para que la app pueda predecir partidos individuales
    sin necesidad de todo el histórico. Calcula las features del local y visitante
    basándose solo en sus partidos anteriores (evitando data leakage).
    
    Args:
        history: DataFrame con historial de partidos (columnas: HomeTeam, AwayTeam, 
                 FTHG, FTAG, FTR, Date, Season)
        home_team: Nombre del equipo que juega local
        away_team: Nombre del equipo que juega visitante
        
    Returns:
        dict con las siguientes features:
        - form_home_last_5: Último resultado local (1=W, 0=D, -1=L) de últimos 5 como local
        - form_away_last_5: Último resultado visitante (1=W, 0=D, -1=L) de últimos 5 como visitante
        - avg_home_goals_last_5: Promedio goles marcados por local en últimos 5 como local
        - avg_away_goals_last_5: Promedio goles marcados por visitante en últimos 5 como visitante
        - home_diff_last_5: Diferencia goles promedio de últimos 5 del local (FTHG-FTAG)
        - away_diff_last_5: Diferencia goles promedio de últimos 5 del visitante (FTAG-FTHG)
        - recent_home_form: Forma reciente local (1=W, 0=D, -1=L) del último partido como local
        - recent_away_form: Forma reciente visitante (1=W, 0=D, -1=L) del último partido como visitante
        - match_diff: Diferencia de forma entre equipos (form_home_last_5 - form_away_last_5)
        - match_goals_expected: Goles esperados en el partido (avg_home + avg_away)
        - match_momentum: Momentum reciente (recent_home_form - recent_away_form)
        
    Notes:
        - Las features con menos de 5 partidos históricos se marcan con NaN
        - Se usa solo la información de PARTIDOS ANTERIORES para evitar data leakage
        - Los nombres de equipo deben coincidir exactamente (case-sensitive)
        
    Example:
        >>> history = pd.DataFrame({...})
        >>> features = build_match_features(history, "Arsenal", "Chelsea")
        >>> print(features['form_home_last_5'])  # Verificar feature local
    """
    
    if history.empty:
        raise ValueError("El histórico de partidos está vacío.")
    
    # Ordenar por fecha para asegurar que las features usan solo datos pasados
    history = history.sort_values("Date")
    
    print(f"\n{'='*60}")
    print("Build Match Features - Calculando features para partido nuevo...")
    print(f"  Local: {home_team}")
    print(f"  Visitante: {away_team}")
    print(f"{'='*60}\n")
    
    # Función para convertir resultado a número (W=1, D=0, L=-1)
    def result_to_num(result):
        if result == "H": return 1
        elif result == "A": return -1
        else: return 0
    
    N = 5  # Últimos 5 partidos para forma reciente
    
    features = {}
    
    # --- Calcular features del LOCAL ---
    print(f"Calculando features del equipo local ({home_team})...")
    
    home_history = history[history["HomeTeam"] == home_team].sort_values("Date")
    
    if len(home_history) > 0:
        last_match_date = history[history["HomeTeam"] == home_team]["Date"].max()
        # Filtrar solo partidos Estrictamente ANTERIORES al partido actual
        home_past = home_history[home_history["Date"] < last_match_date]
        
        if len(home_past) > 0:
            # Últimos N partidos como local del local
            last_n_home = home_past.tail(N).copy()
            
            features["form_home_last_5"] = result_to_num(last_n_home.iloc[-1]["FTR"])
            features["avg_home_goals_last_5"] = last_n_home["FTHG"].tail(N).mean()
            features["home_diff_last_5"] = (last_n_home["FTHG"] - last_n_home["FTAG"]).tail(N).mean()
            features["recent_home_form"] = result_to_num(last_n_home.iloc[-1]["FTR"])
            
            print(f"  ✅ Formas local: {features['form_home_last_5']} (último resultado), "
                  f"goles promedios: {features['avg_home_goals_last_5']:.2f}")
        else:
            features["form_home_last_5"] = np.nan
            features["avg_home_goals_last_5"] = np.nan
            features["home_diff_last_5"] = np.nan
            features["recent_home_form"] = np.nan
            print(f"  ⚠️  No hay partidos históricos suficientes para el local")
    else:
        features["form_home_last_5"] = np.nan
        features["avg_home_goals_last_5"] = np.nan
        features["home_diff_last_5"] = np.nan
        features["recent_home_form"] = np.nan
        print(f"  ⚠️  El equipo {home_team} no tiene historial como local")
    
    # --- Calcular features del VISITANTE ---
    print(f"\nCalculando features del equipo visitante ({away_team})...")
    
    away_history = history[history["AwayTeam"] == away_team].sort_values("Date")
    
    if len(away_history) > 0:
        last_match_date = history[history["AwayTeam"] == away_team]["Date"].max()
        # Filtrar solo partidos Estrictamente ANTERIORES al partido actual
        away_past = away_history[away_history["Date"] < last_match_date]
        
        if len(away_past) > 0:
            # Últimos N partidos como visitante del visitante
            last_n_away = away_past.tail(N).copy()
            
            features["form_away_last_5"] = result_to_num(last_n_away.iloc[-1]["FTR"])
            features["avg_away_goals_last_5"] = last_n_away["FTAG"].tail(N).mean()
            features["away_diff_last_5"] = (last_n_away["FTAG"] - last_n_away["FTHG"]).tail(N).mean()
            features["recent_away_form"] = result_to_num(last_n_away.iloc[-1]["FTR"])
            
            print(f"  ✅ Formas visitante: {features['form_away_last_5']} (último resultado), "
                  f"goles promedios: {features['avg_away_goals_last_5']:.2f}")
        else:
            features["form_away_last_5"] = np.nan
            features["avg_away_goals_last_5"] = np.nan
            features["away_diff_last_5"] = np.nan
            features["recent_away_form"] = np.nan
            print(f"  ⚠️  No hay partidos históricos suficientes para el visitante")
    else:
        features["form_away_last_5"] = np.nan
        features["avg_away_goals_last_5"] = np.nan
        features["away_diff_last_5"] = np.nan
        features["recent_away_form"] = np.nan
        print(f"  ⚠️  El equipo {away_team} no tiene historial como visitante")
    
    # --- Calcular features combinadas ---
    match_diff = (features["form_home_last_5"] - features["form_away_last_5"]) \
                 if not (pd.isna(features["form_home_last_5"]) and pd.isna(features["form_away_last_5"])) \
                 else np.nan
    
    match_goals_expected = (features["avg_home_goals_last_5"] + features["avg_away_goals_last_5"]) \
                          if not (pd.isna(features["avg_home_goals_last_5"]) and pd.isna(features["avg_away_goals_last_5"])) \
                          else np.nan
    
    match_momentum = (features["recent_home_form"] - features["recent_away_form"]) \
                   if not (pd.isna(features["recent_home_form"]) and pd.isna(features["recent_away_form"])) \
                   else np.nan
    
    # Añadir features combinadas al dict
    features["match_diff"] = match_diff
    features["match_goals_expected"] = match_goals_expected
    features["match_momentum"] = match_momentum
    
    print(f"\n  ✅ match_diff: {features['match_diff']}")
    print(f"  ✅ match_goals_expected: {features['match_goals_expected']:.2f}")
    print(f"  ✅ match_momentum: {features['match_momentum']}")
    
    print(f"\n{'='*60}")
    print(f"✅ Features calculadas exitosamente para {home_team} vs {away_team}")
    print(f"{'='*60}\n")
    
    return features
