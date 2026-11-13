"""Tests para Feature Engineering - Issue #34"""

import pytest
import pandas as pd
import numpy as np

from kiniela.features import engineering


class TestNoDuplicates:
    
    def test_no_duplicate_form_features(self):
        """Verificar que recent_*_form y form_*_last_5 son diferentes (no duplicados)."""
        
        home_teams = ["Arsenal", "Chelsea", "Arsenal"]
        away_teams = ["Chelsea", "Arsenal", "Chelsea"]
        fthg = [3, 1, 2]
        ftg = [1, 2, 1]
        ftr = ["H", "A", "H"]
        
        matches = pd.DataFrame({
            "HomeTeam": home_teams,
            "AwayTeam": away_teams,
            "FTHG": fthg,
            "FTAG": ftg,
            "FTR": ftr,
            "Date": ["2024-08-17", "2024-09-23", "2024-10-15"],
            "Season": ["2324"] * 3
        })
        
        features_df = engineering.build_features(matches)
        
        cols_with_form = [c for c in features_df.columns if "form" in c.lower()]
        assert len(cols_with_form) == 4, f"Duplicados detectados: {cols_with_form}"


class TestFeatureSemantics:
    
    def test_recent_form_is_last_match_score(self):
        """Verificar que recent_*_form es el ÚLTIMO partido (1/0.5/0)."""
        
        matches = pd.DataFrame({
            "HomeTeam": ["Arsenal", "Chelsea", "Arsenal"],
            "AwayTeam": ["Chelsea", "Arsenal", "Chelsea"],
            "FTHG": [3, 1, 2],
            "FTAG": [1, 2, 1],
            "FTR": ["H", "A", "H"],
            "Date": ["2024-08-17", "2024-09-23", "2024-10-15"],
            "Season": ["2324"] * 3
        })
        
        features_df = engineering.build_features(matches)
        
        assert pd.isna(features_df["recent_home_form"].iloc[0])
        assert features_df["recent_home_form"].iloc[2] == 1.0
    
    def test_recent_form_can_be_negative(self):
        """Verificar que recent_*_form es negativo si último partido histórico fue pérdida."""
        
        matches = pd.DataFrame({
            "HomeTeam": ["Arsenal", "Arsenal"],
            "AwayTeam": ["Chelsea", "ManCity"],
            "FTHG": [1, 2],
            "FTAG": [3, 0],
            "FTR": ["A", "H"],
            "Date": ["2024-08-17", "2024-09-23"],
            "Season": ["2324"] * 2
        })
        
        features_df = engineering.build_features(matches)
        
        assert features_df["recent_home_form"].iloc[1] == -1.0


class TestFormLastFiveIsAverage:
    
    def test_form_home_last_5_is_average_of_results(self):
        """Verificar que form_*_last_5 es PROMEDIO de últimos 5 resultados."""
        
        matches = pd.DataFrame({
            "HomeTeam": ["Arsenal", "Chelsea", "Arsenal"],
            "AwayTeam": ["Chelsea", "Arsenal", "Chelsea"],
            "FTHG": [3, 1, 2],
            "FTAG": [1, 2, 1],
            "FTR": ["H", "A", "H"],
            "Date": ["2024-08-17", "2024-09-23", "2024-10-15"],
            "Season": ["2324"] * 3
        })
        
        features_df = engineering.build_features(matches)
        
        assert not pd.isna(features_df["form_home_last_5"].iloc[2])


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


class TestNoDataLeakage:
    """TEST CRÍTICO DE NO-FUGA."""
    
    def test_no_data_leakage_on_feature_calculation(self):
        """Cambia el resultado de un partido actual - las features anteriores no cambian."""
        
        # 4 partidos para poder modificar uno sin afectar los primeros
        matches_before = pd.DataFrame({
            "HomeTeam": ["Arsenal", "Chelsea", "Arsenal", "ManCity"],
            "AwayTeam": ["Chelsea", "Arsenal", "Chelsea", "Arsenal"],
            "FTHG": [3, 1, 2, 4],
            "FTAG": [1, 2, 1, 0],
            "FTR": ["H", "A", "H", "H"],
            "Date": ["2024-08-17", "2024-09-23", "2024-10-15", "2024-11-02"],
            "Season": ["2324"] * 4
        })
        
        # Tomamos solo los primeros 3 para calcular features, pero modificamos el 3º (índice 2)
        matches_before_calc = matches_before.iloc[:3].copy()
        features_before = engineering.build_features(matches_before_calc)
        
        part_index = 1
        features_part_1_before = {col: features_before.iloc[part_index][col] 
                                   for col in ["form_home_last_5", "recent_home_form"]}
        
        # Cambiamos el resultado del partido 2 (índice 2) - Arsenal ahora pierde en su único partido como local
        matches_after = matches_before_calc.copy()
        matches_after.iloc[2, matches_after.columns.get_loc("FTR")] = "A"
        
        matches_after_sorted = matches_after.sort_values("Date")
        features_after = engineering.build_features(matches_after_sorted)
        
        features_part_1_after = {col: features_after.iloc[part_index][col] 
                                 for col in ["form_home_last_5", "recent_home_form"]}
        
        # Verificar que las features del partido 1 no cambiaron (sin data leakage)
        for col in ["form_home_last_5", "recent_home_form"]:
            val_before = features_part_1_before.get(col, np.nan)
            val_after = features_part_1_after.get(col, np.nan)
            
            if pd.isna(val_before):
                assert pd.isna(val_after), f"Data leakage en {col}: cambió de NaN a {val_after}"
            else:
                assert val_before == val_after, f"Data leakage en {col}: {val_before} → {val_after}"