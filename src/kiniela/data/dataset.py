"""Lectura del histórico de partidos."""

from pathlib import Path

import pandas as pd


def load_matches(path: str | Path) -> pd.DataFrame:
    """Carga un CSV de partidos.

    El repositorio no incluye datos. El archivo lo genera la preparación
    del dataset y debe vivir en ``data/``.
    """
    source = Path(path)
    if not source.is_file():
        raise FileNotFoundError(
            f"No existe el dataset en {source}. Guárdalo en data/raw o data/processed."
        )
    return pd.read_csv(source)
