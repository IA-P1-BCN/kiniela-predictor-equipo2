"""Constantes compartidas del proyecto."""

CLASS_NAMES: dict[int, str] = {
    0: "Victoria local clara",
    1: "Victoria local ajustada",
    2: "Empate",
    3: "Victoria visitante ajustada",
    4: "Victoria visitante clara",
    5: "Partido de muchos goles (4+ goles)",
}

N_CLASSES = len(CLASS_NAMES)
RANDOM_STATE = 42
