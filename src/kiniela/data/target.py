"""Etiquetado de las 6 clases de la kiniela.

## Regla definitiva (umbral >= 2)

La clasificación se determina por orden de prioridad:

1. **Clase 5** (4+ goles totales): Precedencia absoluta, anula resultado local/visitante
2. **Clase 0**: Local gana con diferencia ≥ 2 (FTHG - FTAG >= 2)
3. **Clase 4**: Visitante gana con diferencia ≥ 2 (FTAG - FTHG >= 2)  
4. **Clase 1-3**: Resultados ajustados:
   - Home > Away sin diferencia clara: Clase 1, 2 o 3
   - Away > Home sin diferencia clara: Clase 3 o 4

## Distribución esperada con datos reales Premier League 2023-24

| Clase | Condición | Frecuencia estimada |
|-------|-----------|---------------------|
| 5 | ≥4 goles totales | ~44% |
| 0 | Local gana, diff≥2 | ~11% |
| 4 | Visitante gana, diff≥2 | ~7% |
| 1-3 | Resto resultados ajustados | ~38% |

Con este umbral >= 2, las clases raras son más frecuentes que con >= 3,
facilitando el aprendizaje del modelo.
"""


def build_target(home_goals: int, away_goals: int) -> int:
    """Devuelve la clase 0-5 de un partido a partir de los goles.

    La precedencia es:
    1. Clase 5 si hay 4+ goles totales (precedencia absoluta)
    2. Clases 0/4 si hay diferencia >= 2
    3. Clases 1-3 para resultados ajustados

    Args:
        home_goals: Goles del local (FTHG)
        away_goals: Goles del visitante (FTAG)

    Returns:
        Clase 0-5 según la regla definida

    Raises:
        ValueError: Si los goles son negativos
    """
    if home_goals < 0 or away_goals < 0:
        raise ValueError("Los goles no pueden ser negativos.")

    total_goals = home_goals + away_goals

    # Prioridad 1: Clase 5 tiene precedencia absoluta (4+ goles totales)
    if total_goals >= 4:
        return 5

    # Prioridad 2: Diferencia grande
    goal_diff = home_goals - away_goals

    if goal_diff >= 2:
        return 0  # Victoria local clara
    elif goal_diff <= -2:
        return 4  # Victoria visitante clara

    # Prioridad 3: Resultados ajustados (diferencia de 1, 0 o -1)
    # En estos casos, clasificamos dentro del rango 1-3
    if home_goals > away_goals:
        # Local gana con diferencia 1
        return 1
    elif away_goals > home_goals:
        # Visitante gana con diferencia 1
        return 3
    else:
        # Empate
        return 2