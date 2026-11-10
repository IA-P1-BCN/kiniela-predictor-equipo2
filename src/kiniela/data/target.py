"""Etiquetado de las 6 clases de la kiniela.

La regla todavía no está cerrada. Antes de implementar hay que dejar
por escrito el umbral entre victoria clara y ajustada, y si la clase 5
(4+ goles) sustituye al resultado local/visitante/empate.
"""


def build_target(home_goals: int, away_goals: int) -> int:
    """Devuelve la clase 0-5 de un partido a partir de los goles."""
    if home_goals < 0 or away_goals < 0:
        raise ValueError("Los goles no pueden ser negativos.")
    raise NotImplementedError(
        "Falta acordar el umbral clara/ajustada y la precedencia de la clase 5."
    )
