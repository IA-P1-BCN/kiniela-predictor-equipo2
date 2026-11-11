import pytest

from kiniela.data.target import build_target


def test_rechaza_goles_negativos():
    """Los goles no pueden ser negativos."""
    with pytest.raises(ValueError):
        build_target(-1, 0)


@pytest.mark.parametrize("home,away,expected_class", [
    # Casos de victoria visitante ajustada (clase 3)
    (0, 1, 3),   # Visitante gana con diferencia 1
    
    # Casos de victoria local ajustada (clase 1)
    (1, 0, 1),   # Local gana con diferencia 1
    (2, 1, 1),   # Local gana con diferencia 1
    
    # Empate (normalmente clase 2)
    (1, 1, 2),   # Empate 1-1
    
    # Casos de victoria visitante clara (clase 4) - SIN 4+ goles
    (0, 3, 4),   # Visitante gana con diferencia 3 (solo 3 goles)
    
    # Casos de victoria local clara (clase 0) - SIN 4+ goles
    (2, 0, 0),   # Local gana con diferencia 2 (solo 2 goles)
    
    # Precedencia clase 5 (4+ goles totales)
    (0, 4, 5),   # 0-4: visitante goleó -> clase 5
    (3, 1, 5),   # 3-1: local gana claro con 4 goles -> clase 5
    
    # Empate con 4+ goles -> clase 5
    (2, 2, 5),   # Empate 2-2 con 4 goles -> clase 5
    
    # Diferencia exacta de 2
    (0, 2, 4),   # Visitante gana con diferencia exacta -2 -> clase 4
    
    # Mas casos de clase 5
    (4, 1, 5),   # 4-1: local goleó con 5 goles -> clase 5
])
def test_clasificacion_6clases(home: int, away: int, expected_class: int):
    """Prueba todos los casos de clasificación."""
    result = build_target(home, away)
    assert result == expected_class


def test_precedencia_clase_5_sobre_resultado():
    """La clase 5 tiene precedencia absoluta sobre el resultado."""
    assert build_target(2, 2) == 5  # Empate con 4 goles -> clase 5
    assert build_target(3, 1) == 5  # Victoria clara con 4 goles -> clase 5


def test_simbolia_diferencia_2():
    """Diferencia exactamente de 2 cuenta como victoria clara (si no hay 4+ goles)."""
    assert build_target(2, 0) == 0  # Diferencia exacta 2 y solo 2 goles -> clase 0
    assert build_target(0, 2) == 4  # Diferencia exacta -2 y solo 2 goles -> clase 4


if __name__ == "__main__":
    print("Ejemplos:", [(h,a,built_target(h,a)) for h,a in [(1,0),(2,0),(2,2),(4,0),(0,3)]])
