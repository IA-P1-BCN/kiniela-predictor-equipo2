import pytest

from kiniela.data.target import build_target


def test_rechaza_goles_negativos():
    """Los goles no pueden ser negativos."""
    with pytest.raises(ValueError):
        build_target(-1, 0)


@pytest.mark.parametrize("home,away,expected_class", [
    # Casos de victoria visitante ajustada (clase 3) - SIN 4+ goles totales
    (0, 1, 3),   # Visitante gana con diferencia 1 -> clase 3
    
    # Casos de victoria local ajustada (clase 1) - SIN 4+ goles totales
    (1, 0, 1),   # Local gana con diferencia 1 -> clase 1
    (2, 1, 1),   # Local gana con diferencia 1 -> clase 1
    
    # Casos de empate (normalmente clase 2) - SIN 4+ goles totales
    (1, 1, 2),   # Empate 1-1 -> clase 2
    
    # Casos de victoria visitante clara (clase 4) - SIN 4+ goles totales
    (0, 3, 4),   # Visitante gana con diferencia 3 -> clase 4
    
    # Casos de victoria local clara (clase 0) - SIN 4+ goles totales
    (2, 0, 0),   # Local gana con diferencia 2 -> clase 0
    
    # Casos de precedencia clase 5 (4+ goles totales) - precedencia absoluta
    (0, 4, 5),   # 0-4: visitante goleó con 4 goles -> clase 5
    (3, 1, 5),   # 3-1: local gana claro con 4 goles -> clase 5
    (1, 3, 5),   # 1-3: visitante goleó con 4 goles -> clase 5
    
    # Casos de empate con 4+ goles -> clase 5
    (2, 2, 5),   # Empate 2-2 con 4 goles -> clase 5
    (3, 3, 5),   # Empate 3-3 con 6 goles -> clase 5
    
    # Casos límite: diferencia >= 2 vs diferencia == 2 - SIN 4+ goles
    (2, 0, 0),   # Diferencia exactamente 2 y solo 2 goles -> clase 0
    (0, 2, 4),   # Diferencia exactamente -2 y solo 2 goles -> clase 4
    
    # Mas casos de clase 5 con diferentes diferencias
    (4, 1, 5),   # 4-1: local goleó con 5 goles -> clase 5
    (1, 4, 5),   # 1-4: visitante goleó con 5 goles -> clase 5
])
def test_clasificacion_6clases(home: int, away: int, expected_class: int):
    """Prueba todos los casos de clasificación de las 6 clases."""
    result = build_target(home, away)
    assert result == expected_class


def test_precedencia_clase_5_sobre_resultado():
    """La clase 5 tiene precedencia absoluta sobre el resultado."""
    assert build_target(2, 2) == 5
    assert build_target(3, 1) == 5


def test_simbolia_diferencia_2():
    """Diferencia exactamente de 2 cuenta como victoria clara."""
    assert build_target(2, 0) == 0
    assert build_target(0, 2) == 4


if __name__ == "__main__":
    print("Ejemplos:", [(h,a,built_target(h,a)) for h,a in [(1,0),(2,0),(2,2),(4,0),(0,3)]])
