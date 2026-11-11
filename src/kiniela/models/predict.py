"""Prediction of the match class and its probabilities.

The app only talks to a *predictor*: an object with a ``version`` and a
``predict(home_team, away_team)`` method that returns one probability per class.

- If ``models/kiniela_model.joblib`` exists, it is loaded and must follow that contract
  (the modelling issues build it: it computes the match features and runs the model).
- Otherwise the app uses ``ReferencePredictor``: the class frequencies observed in the
  dataset. It gives the same answer for every match and is shown as a test model.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, runtime_checkable

import joblib

from kiniela.config import N_CLASSES

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_MODEL_PATH = PROJECT_ROOT / "models" / "kiniela_model.joblib"
REFERENCE_VERSION = "reference-class-frequencies"


@runtime_checkable
class Predictor(Protocol):
    """What the app needs from any model."""

    version: str

    def predict(self, home_team: str, away_team: str) -> list[float]:
        """Return the probability of each class, in class order (0-5)."""
        ...


def validate_teams(home_team: str, away_team: str) -> tuple[str, str]:
    """Return both team names stripped, or raise ``ValueError`` with a readable message."""
    home, away = (home_team or "").strip(), (away_team or "").strip()
    if not home or not away:
        raise ValueError("Both teams are required.")
    if home.casefold() == away.casefold():
        raise ValueError("A team cannot play against itself.")
    return home, away


def class_frequencies(targets: Iterable[int]) -> list[float]:
    """Share of each class (0-5) in a sequence of targets."""
    counts = Counter(int(target) for target in targets)
    total = sum(counts.values())
    if total == 0:
        raise ValueError("At least one labelled match is needed.")
    if any(not 0 <= target < N_CLASSES for target in counts):
        raise ValueError(f"Targets must be between 0 and {N_CLASSES - 1}.")
    return [counts[class_id] / total for class_id in range(N_CLASSES)]


@dataclass(frozen=True)
class ReferencePredictor:
    """Test model: always predicts the class frequencies of the training data."""

    probabilities: tuple[float, ...]
    version: str = REFERENCE_VERSION
    # Lets the app warn that these are not real predictions
    is_reference: bool = True

    def __post_init__(self) -> None:
        predicted_class(list(self.probabilities))  # validates the distribution

    def predict(self, home_team: str, away_team: str) -> list[float]:
        validate_teams(home_team, away_team)
        return list(self.probabilities)


def load_predictor(
    model_path: str | Path = DEFAULT_MODEL_PATH,
    reference_targets: Sequence[int] | None = None,
) -> Predictor:
    """Load the promoted model, or build the reference predictor when there is none.

    ``reference_targets`` are the dataset's target values used for the class
    frequencies. Raises ``FileNotFoundError`` if there is neither a model nor targets,
    and ``TypeError`` if the saved model does not follow the ``Predictor`` contract.
    """
    path = Path(model_path)
    if path.is_file():
        model = joblib.load(path)
        if not isinstance(model, Predictor):
            raise TypeError(
                f"{path.name} must have a 'version' and a 'predict(home_team, away_team)' method."
            )
        return model
    if not reference_targets:
        raise FileNotFoundError(f"No model in {path} and no data to build the reference model.")
    return ReferencePredictor(tuple(class_frequencies(reference_targets)))


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
