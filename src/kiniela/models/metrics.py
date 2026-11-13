"""Fixed multiclass metrics used in tests and reports (issue #15)."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

from kiniela.config import N_CLASSES


@dataclass(frozen=True)
class ClassificationScores:
    """Accuracy plus precision, recall and F1 for every class 0-5."""

    accuracy: float
    precision: tuple[float, ...]
    recall: tuple[float, ...]
    f1: tuple[float, ...]

    @property
    def f1_macro(self) -> float:
        return float(np.mean(self.f1))


def score_multiclass(y_true, y_pred) -> ClassificationScores:
    """Metrics of a prediction against the true labels. ``zero_division=0``."""
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    if y_true.shape != y_pred.shape:
        raise ValueError("y_true and y_pred must have the same length.")
    labels = list(range(N_CLASSES))
    return ClassificationScores(
        accuracy=float(accuracy_score(y_true, y_pred)),
        precision=tuple(
            precision_score(y_true, y_pred, labels=labels, average=None, zero_division=0)
        ),
        recall=tuple(
            recall_score(y_true, y_pred, labels=labels, average=None, zero_division=0)
        ),
        f1=tuple(f1_score(y_true, y_pred, labels=labels, average=None, zero_division=0)),
    )
