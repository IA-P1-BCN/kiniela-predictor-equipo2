"""Multiclass neural network compared with the ensembles (issue #13).

The network trains on the same prepared matrix and the same
``StratifiedKFold`` as the baseline and the ensembles
(:func:`kiniela.models.train.cross_validate_model`), with ``RANDOM_STATE``.
The report compares it with the best ensemble: the one with the highest mean
F1 macro among Random Forest, XGBoost and LightGBM.

Regularization, both of them on every run:

- L2 penalty ``alpha`` on the network weights.
- Early stopping: a fraction of each training fold is held out and training
  stops when validation loss does not improve for ``N_ITER_NO_CHANGE`` passes.

Features are standardized inside each fold, after the split, so the scaler
never sees the held-out fold. Class imbalance uses the same per-fold sample
weights as XGBoost.

Run it again with::

    PYTHONPATH=src python -m kiniela.models.neural \\
        --dataset data/processed/premier_league_with_features_and_target.csv
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler

from kiniela.config import CV_N_SPLITS, RANDOM_STATE
from kiniela.models.ensembles import (
    CANDIDATE_CRITERION,
    FOREST_NAME,
    LIGHTGBM_NAME,
    REFERENCE_NAME,
    XGBOOST_NAME,
    choose_candidate,
)
from kiniela.models.train import (
    FoldScores,
    build_reference,
    cross_validate_model,
    feature_columns,
    prepare_xy,
)
from kiniela.models.ensembles import build_ensembles

NETWORK_NAME = "neural_network"

# Fixed architecture. Early stopping and L2 are part of the comparison, not a
# search: issue #7 owns hyperparameter search for the ensembles.
HIDDEN_LAYERS = (32, 16)
L2_ALPHA = 1e-4
VALIDATION_FRACTION = 0.15
N_ITER_NO_CHANGE = 10
MAX_ITER = 300


class ScaledMLP(BaseEstimator, ClassifierMixin):
    """MLP with a scaler fitted only on the rows passed to ``fit``.

    ``clone`` and the project's cross-validation call ``fit`` with optional
    ``sample_weight``. The scaler is not a separate pipeline step so that
    weight reaches the network directly.
    """

    def __init__(
        self,
        hidden_layer_sizes: tuple[int, ...] = HIDDEN_LAYERS,
        alpha: float = L2_ALPHA,
        validation_fraction: float = VALIDATION_FRACTION,
        n_iter_no_change: int = N_ITER_NO_CHANGE,
        max_iter: int = MAX_ITER,
        random_state: int = RANDOM_STATE,
    ) -> None:
        self.hidden_layer_sizes = hidden_layer_sizes
        self.alpha = alpha
        self.validation_fraction = validation_fraction
        self.n_iter_no_change = n_iter_no_change
        self.max_iter = max_iter
        self.random_state = random_state

    def fit(self, X, y, sample_weight=None):
        self.scaler_ = StandardScaler()
        scaled = self.scaler_.fit_transform(X)
        self.network_ = MLPClassifier(
            hidden_layer_sizes=self.hidden_layer_sizes,
            activation="relu",
            solver="adam",
            alpha=self.alpha,
            batch_size="auto",
            learning_rate_init=0.001,
            max_iter=self.max_iter,
            shuffle=True,
            random_state=self.random_state,
            early_stopping=True,
            validation_fraction=self.validation_fraction,
            n_iter_no_change=self.n_iter_no_change,
        )
        self.network_.fit(scaled, y, sample_weight=sample_weight)
        self.classes_ = self.network_.classes_
        return self

    def predict(self, X):
        return self.network_.predict(self.scaler_.transform(X))

    def predict_proba(self, X) -> np.ndarray:
        return self.network_.predict_proba(self.scaler_.transform(X))


def build_network() -> ScaledMLP:
    """The issue #13 network: 6-class MLP, L2 and early stopping, fixed seed."""
    return ScaledMLP()


@dataclass(frozen=True)
class NetworkComparison:
    """Network metrics next to the ensembles, on the shared validation scheme."""

    n_splits: int
    random_state: int
    n_samples: int
    n_dropped: int
    feature_columns: tuple[str, ...]
    scores: dict[str, FoldScores]
    best_ensemble: str
    network: str = NETWORK_NAME
    criterion: str = CANDIDATE_CRITERION


def compare_network(dataset_path: str | Path) -> NetworkComparison:
    """Cross-validate the network and the ensembles on the same folds.

    Args:
        dataset_path: Modelling CSV with numeric features and a ``target`` column.

    Returns:
        Metrics for the reference, the three ensembles and the network, plus
        which ensemble is the best by mean F1 macro.

    Raises:
        FileNotFoundError: If the dataset does not exist.
        ValueError: If the dataset has no usable features, no valid ``target``,
            or too few samples per class after dropping rows without features.
    """
    path = Path(dataset_path)
    if not path.is_file():
        raise FileNotFoundError(f"No dataset at {path}.")
    dataset = pd.read_csv(path)

    columns = feature_columns(dataset)
    X, y, n_dropped = prepare_xy(dataset, columns)

    models = {
        REFERENCE_NAME: build_reference(),
        **build_ensembles(),
        NETWORK_NAME: build_network(),
    }
    scores = {
        name: cross_validate_model(
            X, y, model, balanced=name in {XGBOOST_NAME, NETWORK_NAME}
        )
        for name, model in models.items()
    }
    ensembles_only = {
        name: value
        for name, value in scores.items()
        if name in {FOREST_NAME, XGBOOST_NAME, LIGHTGBM_NAME}
    }
    return NetworkComparison(
        n_splits=CV_N_SPLITS,
        random_state=RANDOM_STATE,
        n_samples=len(X),
        n_dropped=n_dropped,
        feature_columns=tuple(columns),
        scores=scores,
        best_ensemble=choose_candidate(ensembles_only),
    )


def format_network_comparison(comparison: NetworkComparison, dataset_path: str | Path) -> str:
    """Render the network-versus-ensemble table. Pure function: it never prints."""
    lines = [
        "Neural network compared with the ensembles",
        f"  validation: StratifiedKFold(n_splits={comparison.n_splits}, shuffle=True, "
        f"random_state={comparison.random_state})",
        "  regularization: L2 "
        f"(alpha={L2_ALPHA}) and early stopping "
        f"(validation_fraction={VALIDATION_FRACTION}, n_iter_no_change={N_ITER_NO_CHANGE})",
        f"  dataset: {dataset_path} ({comparison.n_samples} rows"
        + (
            f", {comparison.n_dropped} dropped without history"
            if comparison.n_dropped
            else ""
        )
        + f", {len(comparison.feature_columns)} features)",
        "",
        f"  {'model':<22}{'accuracy':<22}{'f1_macro':<22}f1 per class (0-5)",
    ]
    for name, scores in comparison.scores.items():
        per_class = " ".join(f"{value:.2f}" for value in scores.f1_per_class_mean)
        lines.append(
            f"  {name:<22}{scores.accuracy_mean:.3f} +/- {scores.accuracy_std:.3f}"
            f"{'':<8}{scores.f1_macro_mean:.3f} +/- {scores.f1_macro_std:.3f}"
            f"{'':<8}{per_class}"
        )
    network = comparison.scores[comparison.network]
    ensemble = comparison.scores[comparison.best_ensemble]
    lines.extend(
        [
            "",
            f"  best ensemble: {comparison.best_ensemble} "
            f"(F1 macro {ensemble.f1_macro_mean:.3f})",
            f"  neural network: F1 macro {network.f1_macro_mean:.3f}, "
            f"accuracy {network.accuracy_mean:.3f}",
            f"  reason: {comparison.criterion}.",
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point: ``python -m kiniela.models.neural --dataset ...``."""
    parser = argparse.ArgumentParser(
        description="Compare the multiclass neural network with the ensembles (issue #13)."
    )
    parser.add_argument(
        "--dataset",
        required=True,
        help="Modelling CSV with numeric features and a 'target' column.",
    )
    args = parser.parse_args(argv)
    comparison = compare_network(args.dataset)
    print(format_network_comparison(comparison, args.dataset))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
