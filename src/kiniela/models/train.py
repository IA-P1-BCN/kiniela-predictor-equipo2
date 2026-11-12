"""Baseline training with a fixed stratified cross-validation scheme.

Validation scheme, documented once here so every model of the project compares
against the same numbers (issues #5 to #8 use it):

- Splitter: ``StratifiedKFold(n_splits=CV_N_SPLITS, shuffle=True, random_state=RANDOM_STATE)``.
- Seed: ``RANDOM_STATE`` from :mod:`kiniela.config`, used by the splitter and by the model.
- Metrics per fold: ``accuracy`` and ``f1_macro``; the report shows their mean and
  standard deviation across folds.
- Reference: a majority-class ``DummyClassifier`` evaluated on the same folds, so the
  Random Forest is always compared against the trivial baseline.

The dataset must be the modelling CSV of issue #3: numeric features plus a ``target``
column with the 6 classes of issue #2. Features are the numeric columns minus
:data:`NON_FEATURE_COLUMNS`, which removes identifiers and post-match statistics that
would leak the result (shots, half-time score, cards...). Rows whose features are
missing are dropped and counted in the report: the first matchdays have no history
behind them, so ``build_features`` leaves them empty.

Run it again with::

    PYTHONPATH=src python -m kiniela.models.train \\
        --dataset data/processed/modelling.csv --model models/baseline_rf.joblib

The artefact is **not** the model the app loads: the app only accepts a ``Predictor``
(see ``docs/model-contract.md``), which wraps the features of issue #3. Save the
baseline outside ``models/kiniela_model.joblib``.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import StratifiedKFold

from kiniela.config import CV_N_SPLITS, N_CLASSES, RANDOM_STATE
from kiniela.models.predict import DEFAULT_MODEL_PATH

TARGET_COLUMN = "target"

# Identifiers and post-match columns: they must never be features (data leakage).
NON_FEATURE_COLUMNS = frozenset(
    {
        "Div", "Date", "Time", "Referee", "HomeTeam", "AwayTeam",
        "FTHG", "FTAG", "FTR",  # full-time score and outcome: they define the target
        "HTHG", "HTAG", "HTR",  # half-time score and outcome
        "HS", "AS", "HST", "AST",  # shots and shots on target
        "HF", "AF",  # fouls
        "HC", "AC",  # corners
        "HY", "AY", "HR", "AR",  # cards
    }
)

VERSION_PREFIX = "baseline-rf"


@dataclass(frozen=True)
class FoldScores:
    """Accuracy and F1 macro of each fold of the cross-validation."""

    accuracy: tuple[float, ...]
    f1_macro: tuple[float, ...]

    @property
    def accuracy_mean(self) -> float:
        return float(np.mean(self.accuracy))

    @property
    def accuracy_std(self) -> float:
        return float(np.std(self.accuracy))

    @property
    def f1_macro_mean(self) -> float:
        return float(np.mean(self.f1_macro))

    @property
    def f1_macro_std(self) -> float:
        return float(np.std(self.f1_macro))


@dataclass(frozen=True)
class BaselineReport:
    """Everything fixed and measured by the baseline run (issues #5 and #6)."""

    n_splits: int
    random_state: int
    n_samples: int
    n_dropped: int  # rows without history, dropped before training
    feature_columns: tuple[str, ...]
    reference: FoldScores  # majority-class dummy
    random_forest: FoldScores


@dataclass(frozen=True)
class TrainedBaseline:
    """Saved artefact: the fitted forest plus what is needed to reproduce it."""

    model: RandomForestClassifier
    feature_columns: tuple[str, ...]
    version: str
    report: BaselineReport


def feature_columns(dataset: pd.DataFrame) -> list[str]:
    """Numeric columns usable as features: identifiers and post-match data excluded."""
    candidates = dataset.select_dtypes(include="number").columns
    columns = [
        column
        for column in candidates
        if column != TARGET_COLUMN and column not in NON_FEATURE_COLUMNS
    ]
    if not columns:
        raise ValueError(
            "No numeric feature columns found. Expected the modelling dataset of issue #3: "
            "numeric features plus a 'target' column."
        )
    return columns


def stratified_cv() -> StratifiedKFold:
    """The project's fixed validation scheme: same splitter and seed for every model."""
    return StratifiedKFold(
        n_splits=CV_N_SPLITS, shuffle=True, random_state=RANDOM_STATE
    )


def _cross_validate(X: np.ndarray, y: np.ndarray, estimator) -> FoldScores:
    """Fit ``estimator`` on each fold and score it on the held-out fold."""
    accuracy: list[float] = []
    f1_macro: list[float] = []
    for train_index, test_index in stratified_cv().split(X, y):
        fold_model = clone(estimator)
        fold_model.fit(X[train_index], y[train_index])
        predictions = fold_model.predict(X[test_index])
        accuracy.append(accuracy_score(y[test_index], predictions))
        f1_macro.append(
            f1_score(y[test_index], predictions, average="macro", zero_division=0)
        )
    return FoldScores(tuple(accuracy), tuple(f1_macro))


def _prepare(dataset: pd.DataFrame, columns: list[str]) -> tuple[np.ndarray, np.ndarray, int]:
    """Validate the target, drop the rows without features and return ``X``, ``y``, dropped.

    The first matchdays have no history behind them, so ``build_features`` leaves their
    features empty: those rows cannot train a model and are counted, not hidden.
    """
    if TARGET_COLUMN not in dataset.columns:
        raise ValueError(
            f"The dataset has no '{TARGET_COLUMN}' column (issues #2 and #3)."
        )
    usable = dataset[columns + [TARGET_COLUMN]].dropna()
    n_dropped = len(dataset) - len(usable)
    y = usable[TARGET_COLUMN].to_numpy()
    if not np.isin(y, range(N_CLASSES)).all():
        raise ValueError(f"'{TARGET_COLUMN}' values must be between 0 and {N_CLASSES - 1}.")
    counts = pd.Series(y).value_counts()
    too_small = counts[counts < CV_N_SPLITS]
    if not too_small.empty:
        raise ValueError(
            f"Classes {sorted(too_small.index)} have fewer than {CV_N_SPLITS} samples: "
            f"StratifiedKFold with {CV_N_SPLITS} splits needs at least that many."
        )
    return usable[columns].to_numpy(), y, n_dropped


def _print_report(report: BaselineReport, dataset_path: Path, model_path: Path) -> None:
    """Human-readable summary of what was fixed and what was measured."""
    print("Baseline training (Random Forest)")
    print(
        f"  validation: StratifiedKFold(n_splits={report.n_splits}, shuffle=True, "
        f"random_state={report.random_state})"
    )
    print(
        f"  dataset: {dataset_path} ({report.n_samples} rows"
        + (f", {report.n_dropped} dropped without history" if report.n_dropped else "")
        + f", {len(report.feature_columns)} features)"
    )
    print()
    print(f"  {'model':<22}{'accuracy':<22}{'f1_macro'}")
    for name, scores in (
        ("reference (majority)", report.reference),
        ("random_forest", report.random_forest),
    ):
        print(
            f"  {name:<22}{scores.accuracy_mean:.3f} +/- {scores.accuracy_std:.3f}"
            f"{'':<8}{scores.f1_macro_mean:.3f} +/- {scores.f1_macro_std:.3f}"
        )
    print()
    print(f"  saved: {model_path}")


def train_baseline(dataset_path: str | Path, model_path: str | Path) -> BaselineReport:
    """Train the baseline with the project's stratified scheme and save the artefact.

    Trains a majority-class reference and a ``RandomForestClassifier`` with
    ``StratifiedKFold`` (seed and splits in :mod:`kiniela.config`), reports accuracy
    and F1 macro per model, fits the forest on the whole dataset and saves it with
    joblib.

    Args:
        dataset_path: Modelling CSV with numeric features and a ``target`` column.
        model_path: Where to save the trained artefact. Not ``kiniela_model.joblib``:
            the app only loads objects that follow the ``Predictor`` contract.

    Returns:
        The cross-validation report: fixed scheme, features and metrics.

    Raises:
        FileNotFoundError: If the dataset does not exist.
        ValueError: If the dataset has no usable features, no valid ``target``,
            or too few samples per class after dropping the rows without features.
    """
    path = Path(dataset_path)
    if not path.is_file():
        raise FileNotFoundError(f"No dataset at {path}.")
    dataset = pd.read_csv(path)

    columns = feature_columns(dataset)
    X, y, n_dropped = _prepare(dataset, columns)

    reference = _cross_validate(
        X, y, DummyClassifier(strategy="most_frequent", random_state=RANDOM_STATE)
    )
    forest = RandomForestClassifier(
        n_estimators=100,
        class_weight="balanced",
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )
    scores = _cross_validate(X, y, forest)

    report = BaselineReport(
        n_splits=CV_N_SPLITS,
        random_state=RANDOM_STATE,
        n_samples=len(X),
        n_dropped=n_dropped,
        feature_columns=tuple(columns),
        reference=reference,
        random_forest=scores,
    )

    destination = Path(model_path)
    if destination.resolve() == DEFAULT_MODEL_PATH.resolve():
        raise ValueError(
            "The app loads models/kiniela_model.joblib and requires a 'Predictor' "
            "(docs/model-contract.md). Save the baseline to another path, for example "
            "models/baseline_rf.joblib."
        )
    forest.fit(X, y)
    artifact = TrainedBaseline(
        model=forest,
        feature_columns=tuple(columns),
        version=f"{VERSION_PREFIX}-{date.today().isoformat()}",
        report=report,
    )
    destination.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(artifact, destination)

    _print_report(report, path, destination)
    return report


def main(argv: list[str] | None = None) -> int:
    """CLI entry point: ``python -m kiniela.models.train --dataset ... --model ...``."""
    parser = argparse.ArgumentParser(
        description="Train the Random Forest baseline with StratifiedKFold (issue #5)."
    )
    parser.add_argument(
        "--dataset",
        required=True,
        help="Modelling CSV with numeric features and a 'target' column.",
    )
    parser.add_argument(
        "--model",
        required=True,
        help="Output path of the artefact, for example models/baseline_rf.joblib.",
    )
    args = parser.parse_args(argv)
    train_baseline(args.dataset, args.model)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
