"""Etiquetado de las 6 clases de la kiniela.

## Regla definitiva (umbral >= 2)

1. **Clase 5** (4+ goles totales): Precedencia absoluta
2. **Clase 0**: Local gana con diferencia >= 2
3. **Clase 4**: Visitante gana con diferencia >= 2  
4. **Clase 1-3**: Resultados ajustados

## Distribucion esperada Premier League 2023-24:
Clase 5 ~44%, Clase 0 ~11%, Clase 4 ~7%
"""


def build_target(home_goals: int, away_goals: int) -> int:
    """Devuelve la clase 0-5 de un partido.
    
    Prioridad:
    1. Clase 5 si hay 4+ goles totales (precedencia absoluta)
    2. Clases 0/4 si hay diferencia >= 2
    3. Clases 1-3 para resultados ajustados
    
    Args:
        home_goals: Goles del local (FTHG)
        away_goals: Goles del visitante (FTAG)
        
    Returns:
        Clase 0-5
        
    Raises:
        ValueError: Si los goles son negativos
    """
    if home_goals < 0 or away_goals < 0:
        raise ValueError("Los goles no pueden ser negativos.")

    total_goals = home_goals + away_goals
    
    # Prioridad 1: Clase 5 tiene precedencia absoluta
    if total_goals >= 4:
        return 5
    
    # Prioridad 2: Diferencia grande
    goal_diff = home_goals - away_goals
    
    if goal_diff >= 2:
        return 0  # Victoria local clara
    elif goal_diff <= -2:
        return 4  # Victoria visitante clara
    
    # Prioridad 3: Resultados ajustados (diferencia de 1, 0 o -1)
    if home_goals > away_goals:
        return 1  # Local gana ajustado
    elif away_goals > home_goals:
        return 3  # Visitante gana ajustado
    else:
        return 2  # Empate
