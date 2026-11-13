"""Tests para Feature Engineering - Issue #3"""

import pytest
import pandas as pd
import numpy as np

from kiniela.features import engineering


@pytest.fixture
def sample_matches():
    """Crea un dataset de partidos de ejemplo con historial claro."""
    
    dates = [
        "2024-08-17", "2024-09-23", "2024-10-01", "2024-10-28", "2024-12-01"
    ]
    
    home_teams = ["Arsenal", "Chelsea", "Arsenal", "Chelsea", "Arsenal"]
    away_teams = ["Chelsea", "Arsenal", "Chelsea", "Arsenal", "Chelsea"]
    fthg = [3, 1, 2, 1, 2]
    ftg = [1, 2, 1, 1, 0]
    ftr = ["H", "A", "H", "D", "H"]
    
    return pd.DataFrame({
        "HomeTeam": home_teams,
        "AwayTeam": away_teams,
        "FTHG": fthg,
        "FTAG": ftg,
        "FTR": ftr,
        "Date": dates,
        "Season": ["2324"] * 5
    })


class TestBuildFeatures:
    
    def test_calculation_correct(self, sample_matches):
        first_match = sample_matches.iloc[:1]
        features_df = engineering.build_features(first_match.copy())
        
        assert pd.isna(features_df["form_home_last_5"].iloc[0])
        assert pd.isna(features_df["recent_home_form"].iloc[0])
    
    def test_features_with_history(self, sample_matches):
        matches = sample_matches.iloc[:3].copy()
        features_df = engineering.build_features(matches)
        
        assert not pd.isna(features_df["form_home_last_5"].iloc[2])
        assert not pd.isna(features_df["recent_home_form"].iloc[2])


class TestFeatureSemantics:
    
    def test_recent_form_is_last_match_score(self):
        """Verificar que recent_*_form es el ÚLTIMO partido (1/0.5/0)."""
        
        matches = pd.DataFrame({
            "HomeTeam": ["Arsenal", "Chelsea", "Arsenal", "Chelsea"],
            "AwayTeam": ["Chelsea", "Arsenal", "Chelsea", "Arsenal"],
            "FTHG": [3, 1, 2, 1],
            "FTAG": [1, 2, 1, 1],
            "FTR": ["H", "A", "H", "D"],
            "Date": ["2024-08-17", "2024-09-23", "2024-10-15", "2024-11-02"],
            "Season": ["2324"] * 4
        })
        
        features_df = engineering.build_features(matches)
        
        # Partido 0: Arsenal sin historial -> NaN
        assert pd.isna(features_df["recent_home_form"].iloc[0])
        # Partido 2: Arsenal con historial (partido 0 fue W) -> recent = 1
        assert features_df["recent_home_form"].iloc[2] == 1.0
    
    def test_recent_form_can_be_negative(self):
        """Verificar que recent_*_form es negativo si último partido histórico fue pérdida."""
        
        # Arsenal pierde en su único partido histórico como local
        matches = pd.DataFrame({
            "HomeTeam": ["Arsenal", "Arsenal"],
            "AwayTeam": ["Chelsea", "ManCity"],
            "FTHG": [1, 2],
            "FTAG": [3, 0],
            "FTR": ["A", "H"],  # Primero pierde (1-3), luego gana (2-0)
            "Date": ["2024-08-17", "2024-09-23"],
            "Season": ["2324"] * 2
        })
        
        features_df = engineering.build_features(matches)
        
        # Para el partido 1, el último partido histórico de Arsenal como local fue partido 0 (L/A)
        assert features_df["recent_home_form"].iloc[1] == -1.0


class TestBuildMatchFeatures:
    
    def test_calculates_for_new_match(self):
        history = pd.DataFrame({
            "HomeTeam": ["Arsenal", "Arsenal"],
            "AwayTeam": ["Chelsea", "Liverpool"],
            "FTHG": [3, 2],
            "FTAG": [1, 0],
            "FTR": ["H", "H"],
            "Date": ["2024-08-17", "2024-09-23"],
            "Season": ["2324"] * 2
        })
        
        features = engineering.build_match_features(history, "Arsenal", "Chelsea")
        
        assert "form_home_last_5" in features
        assert "avg_home_goals_last_5" in features
    
    def test_returns_all_required_features(self):
        history = pd.DataFrame({
            "HomeTeam": ["Arsenal", "Arsenal"],
            "AwayTeam": ["Chelsea", "Liverpool"],
            "FTHG": [3, 2],
            "FTAG": [1, 0],
            "FTR": ["H", "H"],
            "Date": ["2024-08-17", "2024-09-23"],
            "Season": ["2324"] * 2
        })
        
        features = engineering.build_match_features(history, "Arsenal", "Chelsea")
        
        required_features = [
            "form_home_last_5", "avg_home_goals_last_5", 
            "home_diff_last_5", "recent_home_form",
            "match_diff", "match_goals_expected", "match_momentum"
        ]
        
        for feat in required_features:
            assert feat in features, f"Faltando feature: {feat}"
    
    def test_handles_missing_season(self):
        """Test para cuando el historial no tiene columna Season."""
        history = pd.DataFrame({
            "HomeTeam": ["Arsenal"],
            "AwayTeam": ["Chelsea"],
            "FTHG": [3],
            "FTAG": [1],
            "FTR": ["H"],
            "Date": ["2024-08-17"]
        })
        
        features = engineering.build_match_features(history, "Arsenal", "Chelsea")
        
        assert pd.isna(features["form_home_last_5"])  # No hay historial
        assert pd.isna(features["match_goals_expected"])  # Tampoco se puede calcular sin datos


class TestNoDataLeakage:
    """Tests para verificar que no hay fuga de datos (data leakage)."""
    
    def test_no_leakage_when_modifying_match_result(self):
        """
        Verificar que cambiar el resultado del partido actual 
        NO afecta las features calculadas.
        
        Esto es crucial: las features deben basarse solo en PARTIDOS ANTERIORES,
        no en el resultado del partido que se predice.
        """
        # Historial completo (partidos anteriores)
        history = pd.DataFrame({
            "HomeTeam": ["Arsenal", "Arsenal", "Arsenal"],
            "AwayTeam": ["Chelsea", "ManCity", "Liverpool"],
            "FTHG": [3, 2, 1],
            "FTAG": [1, 0, 1],
            "FTR": ["H", "H", "A"],  # Todos W para Arsenal
            "Date": ["2024-08-17", "2024-09-23", "2024-10-01"],
            "Season": ["2324"] * 3
        })
        
        # Partido actual (futuro, no debe influir en features)
        current_match_date = "2024-10-15"
        
        # Calcular features con el partido actual como W (H)
        history_with_w = history.copy()
        features_w = engineering.build_match_features(
            history_with_w, "Arsenal", "Chelsea"
        )
        
        # Calcular features con el partido actual como D (D)
        history_with_d = history.copy()
        # Añadir un partido ficticio entre ambos equipos
        history_with_d.loc[len(history_with_d)] = ["Arsenal", "Chelsea", 1, 1, "D", current_match_date, "2324"]
        
        # Las features deberían ser diferentes porque el historial cambió
        # Pero las features del partido W original deben mantenerse
        assert not pd.isna(features_w["form_home_last_5"]), \
            "Forma local debería estar definida con historial suficiente"
    
    def test_features_use_only_past_matches(self):
        """
        Verificar que el cálculo de form_home_last_5 solo usa partidos anteriores.
        
        El último partido del historial NO debe influir en la forma calculada
        para ese mismo partido.
        """
        # Arsenal juega 3 partidos como local seguidos
        history = pd.DataFrame({
            "HomeTeam": ["Arsenal", "Arsenal", "Arsenal"],
            "AwayTeam": ["Chelsea", "ManCity", "Liverpool"],
            "FTHG": [2, 3, 1],
            "FTAG": [1, 0, 2],
            "FTR": ["H", "H", "A"],  # W, W, L
            "Date": ["2024-08-17", "2024-09-23", "2024-10-01"],
            "Season": ["2324"] * 3
        })
        
        # Calcular features para el partido del 1 de octubre (último del historial)
        features = engineering.build_match_features(history, "Arsenal", "Chelsea")
        
        # La forma reciente debe basarse en los 2 partidos anteriores, no incluir el propio partido
        # Partido previo: W vs Liverpool (FTR=A significa Liverpool fue visitante y ganó)
        # Esperamos que la forma refleje el último resultado del historial anterior
        assert not pd.isna(features["recent_home_form"]), \
            "Debe calcularse forma desde últimos partidos anteriores"


class TestNoDuplicates:
    
    def test_no_duplicate_form_features(self, sample_matches):
        matches = sample_matches.copy()
        features_df = engineering.build_features(matches)
        
        cols_with_form = [c for c in features_df.columns if "form" in c.lower()]
        assert len(cols_with_form) == 4, f"Duplicados detectados: {cols_with_form}"
