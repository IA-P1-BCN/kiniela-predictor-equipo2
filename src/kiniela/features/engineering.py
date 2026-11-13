"""Forma reciente, goles, diferencia de rendimiento y localía.

Las variables históricas tienen que calcularse solo con partidos
anteriores, para no filtrar el resultado del partido que se predice.
"""

import pandas as pd
import numpy as np


def build_features(matches: pd.DataFrame) -> pd.DataFrame:
    """Añade las features de modelado al histórico de partidos.
    
    Args:
        matches: DataFrame con columnas: HomeTeam, AwayTeam, FTHG, FTAG, FTR, Date (y opcionalmente Season)
        
    Returns:
        DataFrame con features añadidas y ordenadas por fecha.
    
    Features creadas:
    - **form_home_last_5**: Promedio de resultados del local en últimos 5 partidos como local (1=W, 0=D, -1=L)
    - **form_away_last_5**: Promedio de resultados del visitante en últimos 5 partidos como visitante (1=W, 0=D, -1=L)  
    - **avg_home_goals_last_5**: Promedio goles marcados por local en últimos 5 partidos como local
    - **avg_away_goals_last_5**: Promedio goles marcados por visitante en últimos 5 partidos como visitante
    - **home_diff_last_5**: Diferencia goles (local-visitante) promedio de últimos 5 partidos del local
    - **away_diff_last_5**: Diferencia goles (visitante-local) promedio de últimos 5 partidos del visitante
    - **recent_home_form**: Forma reciente local (1=último partido W, 0.5=D, 0=último L) en últimos 5 como local
    - **recent_away_form**: Forma reciente visitante (1=último partido W, 0.5=D, 0=último L) en últimos 5 como visitante
    - **match_diff**: Diferencia entre form_home_last_5 y form_away_last_5
    - **match_goals_expected**: Suma de avg_home_goals_last_5 y avg_away_goals_last_5
    - **match_momentum**: Diferencia entre recent_home_form y recent_away_form
    
    Justificación:
    - La forma reciente (promedio) captura el momentum actual del equipo
    - Los promedios de goles indican la potencia ofensiva reciente
    - Las diferencias de rendimiento muestran la fortaleza defensiva/ofensiva neta
    - La localía reciente refleja si el equipo está rindiendo bien en su estadio
    
    Cada feature solo usa información de PARTIDOS ANTERIORES para evitar data leakage.
    
    Notes:
    - `form_*_last_5` devuelve el PROMEDIO de los últimos 5 resultados (no solo el último)
    - `recent_*_form` devuelve el resultado del último partido en escala ponderada (1/0.5/0)
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
    
    N = 5  # Últimos 5 partidos para forma reciente
    
    print(f"Calculando historial por equipo ({N} partidos recientes)...")
    
    features_list = []
    
    for idx, row in matches.iterrows():
        home_team = str(row["HomeTeam"])
        away_team = str(row["AwayTeam"])
        
        # Detectar si el dataset tiene columna Season o no
        if "Season" not in matches.columns:
            season_matches = matches.copy()
        else:
            season_matches = matches[matches["Season"] == row["Season"]]
        
        # Encontrar todos los partidos del local y visitante hasta ahora (ordenados por fecha)
        home_history = season_matches[season_matches["HomeTeam"] == home_team].sort_values("Date")
        away_history = season_matches[season_matches["AwayTeam"] == away_team].sort_values("Date")
        
        # Calcular estadísticas del local usando solo partidos anteriores (evitando data leakage)
        if len(home_history) > 0:
            current_date = row["Date"]
            home_past = home_history[home_history["Date"] < current_date]
            
            if len(home_past) > 0:
                # Últimos N partidos como local
                last_n_home = home_past.tail(N).copy()
                
                form_home_last_5 = last_n_home["ResultHome"].mean()
                avg_home_goals_last_5 = last_n_home["FTHG"].tail(N).mean()
                away_goals_conceded_last_5 = last_n_home["FTAG"].tail(N).mean()
                home_diff_last_5 = (last_n_home["FTHG"] - last_n_home["FTAG"]).tail(N).mean()
                
                # Forma reciente: resultado del último partido en escala ponderada
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
                # Últimos N partidos como visitante
                last_n_away = away_past.tail(N).copy()
                
                form_away_last_5 = last_n_away["ResultAway"].mean()
                avg_away_goals_last_5 = last_n_away["FTAG"].tail(N).mean()
                home_goals_conceded_last_5 = last_n_away["FTHG"].tail(N).mean()
                away_diff_last_5 = (last_n_away["FTAG"] - last_n_away["FTHG"]).tail(N).mean()
                
                # Forma reciente: resultado del último partido en escala ponderada
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
        if pd.notna(form_home_last_5) and pd.notna(form_away_last_5):
            match_diff = form_home_last_5 - form_away_last_5
        else:
            match_diff = np.nan
        
        if pd.notna(avg_home_goals_last_5) and pd.notna(avg_away_goals_last_5):
            match_goals_expected = avg_home_goals_last_5 + avg_away_goals_last_5
        else:
            match_goals_expected = np.nan
        
        if pd.notna(recent_home_form) and pd.notna(recent_away_form):
            match_momentum = recent_home_form - recent_away_form
        else:
            match_momentum = np.nan
        
        features_list.append({
            "HomeTeam": home_team,
            "AwayTeam": away_team,
            # Formas recientes (promedio y último)
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
            # Features combinadas
            "match_diff": match_diff,
            "match_goals_expected": match_goals_expected,
            "match_momentum": match_momentum,
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
    """Calcula las features para un partido específico a partir del historial.
    
    Esta función es necesaria para predecir partidos individuales desde la app,
    donde no tenemos todo el histórico de partidos disponible. Calcula las 
    features del local y visitante basándose solo en sus partidos anteriores 
    (evitando data leakage).
    
    Args:
        history: DataFrame con historial de partidos (columnas: HomeTeam, AwayTeam, 
                 FTHG, FTAG, FTR, Date, Season)
        home_team: Nombre del equipo que juega local
        away_team: Nombre del equipo que juega visitante
        
    Returns:
        dict con las siguientes features:
        - form_home_last_5: Promedio de últimos 5 resultados como local (1=W, 0=D, -1=L)
        - form_away_last_5: Promedio de últimos 5 resultados como visitante (1=W, 0=D, -1=L)
        - avg_home_goals_last_5: Promedio goles marcados por local en últimos 5 como local
        - avg_away_goals_last_5: Promedio goles marcados por visitante en últimos 5 como visitante
        - home_diff_last_5: Diferencia goles promedio de últimos 5 del local (FTHG-FTAG)
        - away_diff_last_5: Diferencia goles promedio de últimos 5 del visitante (FTAG-FTHG)
        - recent_home_form: Último resultado local en escala ponderada (1=W, 0.5=D, 0=L)
        - recent_away_form: Último resultado visitante en escala ponderada (1=W, 0.5=D, 0=L)
        - match_diff: Diferencia de forma entre equipos (form_home_last_5 - form_away_last_5)
        - match_goals_expected: Goles esperados en el partido (avg_home + avg_away)
        - match_momentum: Momentum reciente (recent_home_form - recent_away_form)
        
    Notes:
    - Usa solo partidos ANTERIORES al momento de predicción (evita data leakage)
    - Si no hay historial suficiente, devuelve NaN para las features
    - Los nombres de equipo deben coincidir exactamente (case-sensitive)
    
    Example:
        >>> history = pd.DataFrame({...})
        >>> features = build_match_features(history, "Arsenal", "Chelsea")
        >>> print(features['form_home_last_5'])  # Verificar feature local
    """
    
    if history.empty:
        return {k: np.nan for k in ["form_home_last_5", "form_away_last_5", 
                                      "avg_home_goals_last_5", "avg_away_goals_last_5",
                                      "home_diff_last_5", "away_diff_last_5",
                                      "recent_home_form", "recent_away_form",
                                      "match_diff", "match_goals_expected", "match_momentum"]}
    
    # Ordenar historial por fecha
    history = history.sort_values("Date")
    
    N = 5  # Últimos 5 partidos para forma reciente
    
    # Detectar si el historial tiene columna Season
    if "Season" not in history.columns:
        matches_to_use = history.copy()
    else:
        # Para predicción, necesitamos la temporada actual. 
        # Si no se especifica, usamos la última temporada disponible.
        if "Date" in history.columns:
            last_season = str(history["Season"].iloc[-1])
            matches_to_use = history[history["Season"] == last_season]
        else:
            matches_to_use = history
    
    # Filtrar historial del local y visitante hasta ahora (ordenados por fecha)
    home_history = matches_to_use[matches_to_use["HomeTeam"] == home_team].sort_values("Date")
    away_history = matches_to_use[matches_to_use["AwayTeam"] == away_team].sort_values("Date")
    
    # Función para convertir resultado a número (W=1, D=0, L=-1)
    def result_to_num(result):
        if result == "H": return 1
        elif result == "A": return -1
        else: return 0
    
    features = {}
    
    # Calcular features del local
    if len(home_history) > 0:
        current_date_matches = matches_to_use[matches_to_use["Date"] < home_history["Date"].max()]
        
        if len(current_date_matches) > 0:
            last_n_home = current_date_matches[current_date_matches["HomeTeam"] == home_team].tail(N)
            
            features["form_home_last_5"] = last_n_home["ResultHome"].mean() if "ResultHome" in last_n_home.columns else np.nan
            features["avg_home_goals_last_5"] = last_n_home["FTHG"].mean() if not last_n_home.empty else np.nan
            features["home_diff_last_5"] = (last_n_home["FTHG"] - last_n_home["FTAG"]).mean() if not last_n_home.empty else np.nan
            features["recent_home_form"] = result_to_num(last_n_home.iloc[-1]["FTR"]) if not last_n_home.empty else np.nan
    
    # Calcular features del visitante
    if len(away_history) > 0:
        current_date_matches = matches_to_use[matches_to_use["Date"] < away_history["Date"].max()]
        
        if len(current_date_matches) > 0:
            last_n_away = current_date_matches[current_date_matches["AwayTeam"] == away_team].tail(N)
            
            features["form_away_last_5"] = last_n_away["ResultAway"].mean() if "ResultAway" in last_n_away.columns else np.nan
            features["avg_away_goals_last_5"] = last_n_away["FTAG"].mean() if not last_n_away.empty else np.nan
            features["away_diff_last_5"] = (last_n_away["FTAG"] - last_n_away["FTHG"]).mean() if not last_n_away.empty else np.nan
            features["recent_away_form"] = result_to_num(last_n_away.iloc[-1]["FTR"]) if not last_n_away.empty else np.nan
    
    # Features combinadas (siempre calcularlas, pueden ser NaN para predicción temprana)
    if pd.notna(features.get("form_home_last_5")) and pd.notna(features.get("form_away_last_5")):
        features["match_diff"] = features["form_home_last_5"] - features["form_away_last_5"]
    else:
        # Solo hay datos de un equipo - usar NaN para match_diff
        features["match_diff"] = np.nan
    
    if pd.notna(features.get("avg_home_goals_last_5")) and pd.notna(features.get("avg_away_goals_last_5")):
        features["match_goals_expected"] = features["avg_home_goals_last_5"] + features["avg_away_goals_last_5"]
    else:
        # Solo hay datos de un equipo - usar NaN para match_goals_expected
        features["match_goals_expected"] = np.nan
    
    if pd.notna(features.get("recent_home_form")) and pd.notna(features.get("recent_away_form")):
        features["match_momentum"] = features["recent_home_form"] - features["recent_away_form"]
    else:
        # Solo hay datos de un equipo - usar NaN para match_momentum
        features["match_momentum"] = np.nan
    
    return {k: v for k, v in features.items() if k not in ["away_goals_conceded_last_5", "home_goals_conceded_last_5"]}
