"""Predicción de la clase y de sus probabilidades."""

from pathlib import Path

from kiniela.config import N_CLASSES


def load_model(model_path: str | Path):
    """Carga el modelo versionado desde ``models/``."""
    path = Path(model_path)
    if not path.is_file():
        raise FileNotFoundError(f"No hay modelo en {path}.")
    raise NotImplementedError("La carga del modelo se conecta al entrenar el baseline.")


def predict_proba(model, features: list[float]) -> list[float]:
    """Devuelve una probabilidad por clase. Deben sumar 1."""
    if model is None:
        raise ValueError("No hay modelo cargado.")
    if len(features) == 0:
        raise ValueError("Hacen falta features para predecir.")
    raise NotImplementedError("La predicción se conecta cuando exista un modelo entrenado.")


def predicted_class(probabilities: list[float]) -> int:
    """Índice de la clase con mayor probabilidad."""
    if len(probabilities) != N_CLASSES:
        raise ValueError(f"Se esperaban {N_CLASSES} probabilidades.")
    if any(probability < 0 for probability in probabilities):
        raise ValueError("Una probabilidad no puede ser negativa.")
    total = sum(probabilities)
    if abs(total - 1) > 0.01:
        raise ValueError("Las probabilidades deben sumar aproximadamente 1.")
    return max(range(N_CLASSES), key=probabilities.__getitem__)
