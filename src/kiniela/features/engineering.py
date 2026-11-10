"""Forma reciente, goles, diferencia de rendimiento y localía.

Las variables históricas tienen que calcularse solo con partidos
anteriores, para no filtrar el resultado del partido que se predice.
"""

import pandas as pd


def build_features(matches: pd.DataFrame) -> pd.DataFrame:
    """Añade las features de modelado al histórico de partidos."""
    if matches.empty:
        raise ValueError("El histórico de partidos está vacío.")
    raise NotImplementedError("El feature engineering corresponde a la issue #3.")
