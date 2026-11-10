"""Entrenamiento reproducible. Todavía no hay modelo ni datos."""

from pathlib import Path


def train_baseline(dataset_path: str | Path, model_path: str | Path) -> None:
    """Entrena el baseline con validación estratificada y guarda el artefacto."""
    raise NotImplementedError(
        "El entrenamiento empieza cuando existan datos y target en data/processed."
    )
