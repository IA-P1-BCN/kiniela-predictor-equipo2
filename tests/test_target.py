"""
Tests de la variable objetivo (target) - Issue #2
Criterios: Umbral victoria clara/ajustada, precedencia clase 5 (4+ goles)

Clases Kiniela:
- 0: Victoria local clara (ej: 3-0, 4-0+)
- 1: Victoria local ajustada (ej: 2-0, 2-1)
- 2: Empate (ej: 0-0, 1-1, 2-2)
- 3: Victoria visitante ajustada (ej: 0-2, 1-2)
- 4: Victoria visitante clara (ej: 0-3, 1-3+)
- 5: Partido con 4+ goles total (precedencia sobre todo!)

Reglas:
1. Primero verificar clase 5 (FH + AH >= 4) → precedencia absoluta
2. Luego umbral victoria:
   - Victoria local clara: diferencia de goles >= 3 → clase 0
   - Victoria local ajustada: diferencia de goles 1-2 → clase 1
   - Empate: FH == AH → clase 2 (si no hay precedencia clase 5)
   - Victoria visitante ajustada: diferencia visitante 1-2 → clase 3
   - Victoria visitante clara: diferencia visitante >= 3 → clase 4

Nota: Umbral entre victoria clara/ajustada:
- Clara: diferencia de goles >= 3 (ej: 3-0, 4-0)
- Ajustada: diferencia de goles = 1 o 2 (ej: 2-0, 2-1, 1-0)

Principio de máxima verosimilitud:
- Victoria local con margen pequeño → clase 1 (ajustada)
- Victoria visitante con margen pequeño → clase 3 (ajustada)
"""

import pytest
from kiniela.data.target import build_target


class TestBuildTarget:
    """Tests parametrizados para build_target"""
    
    @pytest.mark.parametrize("home_goals, away_goals, expected_class", [
        # --- CLASE 5: 4+ GOLES (precedencia absoluta) ---
        (2, 2, 5),      # Empate 2-2 con 4 goles totales → clase 5
        (3, 1, 5),      # Victoria local 3-1 con 4 goles totales → clase 5
        (1, 3, 5),      # Victoria visitante 1-3 con 4 goles totales → clase 5
        (4, 0, 5),      # Victoria local clara 4-0 con 4 goles totales → clase 5
        (0, 4, 5),      # Victoria visitante clara 0-4 con 4 goles totales → clase 5
        
        # --- CLASE 0: VICTORIA LOCAL CLARA (sin precedencia clase 5) ---
        (3, 0, 0),      # 3-0: diferencia=3, local gana → victoria local clara
        
        # --- CLASE 1: VICTORIA LOCAL AJUSTADA (sin precedencia clase 5) ---
        (2, 0, 1),      # 2-0: diferencia=2, local gana → victoria local ajustada
        (2, 1, 1),      # 2-1: diferencia=1, local gana → victoria local ajustada
        (1, 0, 1),      # 1-0: diferencia=1, local gana → victoria local ajustada
        
        # --- CLASE 2: EMPATE (sin precedencia clase 5) ---
        (0, 0, 2),      # 0-0: empate → clase 2
        (1, 1, 2),      # 1-1: empate → clase 2
        
        # --- CLASE 3: VICTORIA VISITANTE AJUSTADA (sin precedencia clase 5) ---
        (0, 2, 3),      # 0-2: diferencia visitante=2, visitante gana → clase 3
        (1, 2, 3),      # 1-2: diferencia visitante=1, visitante gana → clase 3
        
        # NOTA: 2-3 tiene 5 goles totales (≥ 4) → clase 5 por precedencia
        (2, 3, 5),      # 2-3 con 5 goles → clase 5
        
        # --- CLASE 4: VICTORIA VISITANTE CLARA (sin precedencia clase 5) ---
        (0, 3, 4),      # 0-3: diferencia visitante=3, visitante gana → clase 4
        
        # --- CASOS DE BORDE IMPORTANTES ---
        (1, 3, 5),      # 1-3 con 4 goles totales → clase 5 por precedencia
        (2, 0, 1),      # Umbral: diferencia=2 → victoria local ajustada
        
        # --- CASOS ADICIONALES PARA COBERTURA ---
        (0, 1, 3),      # Mínima victoria visitante ajustada
        (0, 2, 3),      # Otra victoria visitante ajustada
        (0, 0, 2),      # Empate más bajo
        (0, 3, 4),      # Mínima victoria visitante clara
        (1, 0, 1),      # Victoria local mínima ajustada
        
        # --- VICTORIA VISITANTE CLARA EXTRA ---
        (0, 3, 4),      # Repetido para cobertura
        
    ])
    def test_etiquetado_por_goles(self, home_goals, away_goals, expected_class):
        """Test parametrizado de etiquetado según goles"""
        target = build_target(home_goals, away_goals)
        assert target == expected_class, f"Expected class {expected_class} for {home_goals}-{away_goals}, got {target}"
    
    @pytest.mark.parametrize("home_goals, away_goals", [
        # Casos negativos que deben ser rechazados
        (-1, 0),
        (0, -1),
        (-5, 2),
        (2, -3),
    ])
    def test_rechaza_goles_negativos(self, home_goals, away_goals):
        """Test de que se rechazan goles negativos"""
        with pytest.raises(ValueError, match="goles no pueden ser negativos"):
            build_target(home_goals, away_goals)
    
    def test_precedencia_clase_5_sobre_victoria_local_clara(self):
        """
        Test crítico: 3-1 con 4 goles debería ser clase 5 (no clase 0)
        Esto verifica que la precedencia de clase 5 está correctamente implementada.
        """
        target = build_target(3, 1)
        assert target == 5, "Precedencia de clase 5 no está funcionando correctamente"
    
    def test_umbral_victoria_local_clara_vs_ajustada(self):
        """
        Test del umbral: 
        - 2-0 = victoria local ajustada (clase 1) ✓ diferencia=2 pero <3
        - 3-0 = victoria local clara (clase 0) ✓ diferencia=3, total=3 (<4, sin precedencia)
        """
        target_2_minus_0 = build_target(2, 0)
        assert target_2_minus_0 == 1, "2-0 debería ser clase 1 (victoria local ajustada)"
        
        target_3_minus_0 = build_target(3, 0)
        # Nota: 3-0 es solo 3 goles totales (< 4), así que no hay precedencia clase 5
        assert target_3_minus_0 == 0, "3-0 debería ser clase 0 (victoria local clara)"
    
    def test_umbral_victoria_visitante_clara_vs_ajustada(self):
        """
        Test del umbral visitante:
        - 0-2 = victoria visitante ajustada (clase 3) ✓ diferencia=2 pero <3
        - 0-3 = victoria visitante clara (clase 4) ✓ diferencia=3, total=3 (<4, sin precedencia)
        """
        target_0_minus_2 = build_target(0, 2)
        assert target_0_minus_2 == 3, "0-2 debería ser clase 3 (victoria visitante ajustada)"
        
        target_0_minus_3 = build_target(0, 3)
        # Nota: 0-3 es solo 3 goles totales (< 4), así que no hay precedencia clase 5
        assert target_0_minus_3 == 4, "0-3 debería ser clase 4 (victoria visitante clara)"
    
    def test_empate_puro_vs_clase_5(self):
        """
        Test crítico: empate con muchos goles es clase 5
        - 2-2 = empatado PERO con 4 goles → clase 5 (precedencia)
        - No debería ser clase 2 aunque esté empatado
        """
        target = build_target(2, 2)
        assert target == 5, "2-2 con 4 goles debería ser clase 5 por precedencia, no clase 2"
        
    def test_casos_borde_clase_1_vs_3(self):
        """
        Test de casos donde local y visitante tienen diferencia similar.
        Verifica que la clasificación es correcta según quién ganó.
        """
        # Local gana con diferencia ajustada (no clara porque diferencia < 3)
        target_local_win = build_target(2, 1)  # Local gana por 1 gol
        assert target_local_win == 1, "Local ganando por 1 gol debe ser clase 1 (ajustada)"
        
        # Visitante gana con diferencia ajustada  
        target_away_win = build_target(1, 2)  # Visitante gana por 1 gol
        assert target_away_win == 3, "Visitante ganando por 1 gol debe ser clase 3 (ajustada)"