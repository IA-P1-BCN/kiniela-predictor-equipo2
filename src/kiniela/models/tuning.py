"""Hyperparameter search with an overfitting guard (issue #7).

The candidate of issue #6 is XGBoost, so the search tunes that model only, on the
same fixed scheme as every other model of the project
(``StratifiedKFold(n_splits=CV_N_SPLITS, shuffle=True, random_state=RANDOM_STATE)``,
built by :func:`kiniela.models.train.stratified_cv`) and with the same per-fold
balanced sample weights. Nothing else changes between the "before" and the
"after": only the hyperparameters.

**Method.** Exhaustive grid search (:func:`evaluate_space`), no new dependencies:
Optuna was rejected because a grid over a documented, small space is reproducible
and reviewable in a diff. The grid is the cartesian product of:

- ``max_depth``: 1, 2 -- shallow trees; the default depth of 6 overfits 359 rows.
- ``n_estimators``: 25, 100, 300 -- boosting rounds.
- ``learning_rate``: 0.01, 0.03, 0.1 -- shrinkage per round (pairs with the rounds).
- ``min_child_weight``: 1, 5, 20 -- minimum leaf weight: bigger values split less.
- ``reg_lambda``: 10, 100, 500 -- L2 regularisation on the weights.
- ``subsample``: 0.7, 1.0 -- row fraction sampled per tree.
- ``colsample_bytree``: 0.7, 1.0 -- feature fraction sampled per tree.

648 combinations in total. ``objective``, ``eval_metric``, ``tree_method``,
``random_state`` and ``n_jobs`` are fixed by
:func:`kiniela.models.ensembles.build_xgboost` and are not searched.

**Declared gap metric (AC of the issue).** ``f1_macro`` -- the same metric that
chose the candidate in #6. The gap of a combination is
``|mean(train f1_macro) - mean(validation f1_macro)|`` across the fixed folds
(:attr:`kiniela.models.train.FoldScores.f1_macro_gap`), and a combination is
feasible only while that gap is **strictly below** :data:`GAP_THRESHOLD` (0.05,
the 5% of the issue).

**Selection rule.** Among the feasible combinations, the highest mean validation
F1 macro wins; accuracy only breaks ties (the rule of issue #6, unchanged). If no
combination keeps the gap below the threshold the search raises instead of
silently returning an overfitted model.

**Before and after.** The report renders the gap of the issue #6 defaults
(``build_xgboost()``) next to the gap of the chosen combination, so the
improvement is one table away. The chosen hyperparameters are registered with
the model inside the saved artefact (``params`` in :class:`TunedXGBoost`), which
is never ``kiniela_model.joblib``: the app only loads ``Predictor`` objects
(see ``docs/model-contract.md``).

Run it again with::

    PYTHONPATH=src python -m kiniela.models.tuning \\
        --dataset data/processed/premier_league_with_features_and_target.csv \\
        --model models/tuned_xgboost.joblib
"""

from __future__ import annotations

import argparse
import itertools
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.utils.class_weight import compute_sample_weight
from xgboost import XGBClassifier

from kiniela.config import CV_N_SPLITS, RANDOM_STATE
from kiniela.models.ensembles import build_xgboost
from kiniela.models.predict import DEFAULT_MODEL_PATH
from kiniela.models.train import (
    FoldScores,
    cross_validate_model,
    feature_columns,
    prepare_xy,
)

# The metric that measures the gap, declared once: the issue requires it explicit.
GAP_METRIC = "f1_macro"
# Absolute train-vs-validation difference allowed by the issue: strictly < 5%.
GAP_THRESHOLD = 0.05

VERSION_PREFIX = "tuned-xgb"

BEFORE_LABEL = "before (#6 defaults)"
AFTER_LABEL = "after (grid best)"

# The grid documented in the module docstring: the space actually explored.
SEARCH_SPACE: dict[str, tuple[int | float, ...]] = {
    "max_depth": (1, 2),
    "n_estimators": (25, 100, 300),
    "learning_rate": (0.01, 0.03, 0.1),
    "min_child_weight": (1, 5, 20),
    "reg_lambda": (10, 100, 500),
    "subsample": (0.7, 1.0),
    "colsample_bytree": (0.7, 1.0),
}


@dataclass(frozen=True)
class ComboResult:
    """One hyperparameter combination and how it scored on the fixed scheme."""

    params: dict[str, object]
    scores: FoldScores

    @property
    def gap(self) -> float:
        """The declared gap metric for this combination (train vs validation)."""
        return self.scores.f1_macro_gap


@dataclass(frozen=True)
class TuningReport:
    """The whole search: space explored, feasibility and the before/after gap."""

    n_splits: int
    random_state: int
    n_samples: int
    n_dropped: int
    feature_columns: tuple[str, ...]
    space: dict[str, tuple[int | float, ...]]
    n_combos: int
    n_feasible: int
    before: ComboResult  # issue #6 defaults: the gap before the optimisation
    after: ComboResult  # chosen combination: the gap after the optimisation
    gap_metric: str = GAP_METRIC
    gap_threshold: float = GAP_THRESHOLD

    @property
    def gap_before(self) -> float:
        return self.before.gap

    @property
    def gap_after(self) -> float:
        return self.after.gap


@dataclass(frozen=True)
class TunedXGBoost:
    """Saved artefact: the tuned model with the hyperparameters that produced it."""

    model: XGBClassifier
    feature_columns: tuple[str, ...]
    params: dict[str, object]  # the chosen hyperparameters, registered with the model
    gap: float  # value of the declared gap metric for those hyperparameters
    version: str


def issue6_parameters() -> dict[str, object]:
    """The issue #6 XGBoost settings among the searched keys: the "before" point.

    ``build_xgboost()`` leaves the rest of the parameters at the XGBoost library
    defaults; ``get_params()`` reports those as ``None``, so only the explicitly
    set keys are shown.
    """
    params = build_xgboost().get_params()
    return {
        key: value
        for key, value in params.items()
        if key in SEARCH_SPACE and value is not None
    }


def evaluate_space(
    X: np.ndarray,
    y: np.ndarray,
    space: Mapping[str, Sequence[int | float]] | None = None,
) -> list[ComboResult]:
    """Run the grid: fit and score every combination of ``space`` on the fixed folds.

    Args:
        X: Feature matrix, one row per match and one column per numeric feature.
        y: Target labels, one per match, values between 0 and ``N_CLASSES - 1``.
        space: Parameter values to combine. Defaults to :data:`SEARCH_SPACE`.

    Returns:
        One :class:`ComboResult` per combination, in the deterministic order of
        ``itertools.product`` over ``space``.

    Raises:
        ValueError: If the space or any of its value lists is empty.
    """
    grid = SEARCH_SPACE if space is None else space
    if not grid or any(not values for values in grid.values()):
        raise ValueError("The search space is empty: nothing to optimise.")
    keys = tuple(grid)
    results: list[ComboResult] = []
    for values in itertools.product(*(grid[key] for key in keys)):
        params = dict(zip(keys, values))
        scores = cross_validate_model(X, y, build_xgboost(**params), balanced=True)
        results.append(ComboResult(params, scores))
    return results


def choose_parameters(results: Sequence[ComboResult]) -> ComboResult:
    """The feasible combination with the highest validation F1 macro.

    Feasible means the declared gap metric stays strictly below
    :data:`GAP_THRESHOLD`; accuracy only breaks ties, exactly as in issue #6.

    Args:
        results: Every combination evaluated by :func:`evaluate_space`.

    Returns:
        The chosen combination, ready to be registered with the model.

    Raises:
        ValueError: If no combination keeps the gap below the threshold (or if
            ``results`` is empty). The search never returns an overfitted model
            silently.
    """
    feasible = [result for result in results if result.gap < GAP_THRESHOLD]
    if not feasible:
        raise ValueError(
            f"No combination keeps the {GAP_METRIC} gap below {GAP_THRESHOLD}: "
            "widen the search space or relax the threshold before training."
        )
    return max(
        feasible,
        key=lambda result: (
            result.scores.f1_macro_mean,
            result.scores.accuracy_mean,
        ),
    )


def tune_model(
    dataset_path: str | Path,
    model_path: str | Path,
    *,
    space: Mapping[str, Sequence[int | float]] | None = None,
) -> TuningReport:
    """Search the grid, keep the feasible best and save the tuned artefact.

    The "before" is the issue #6 XGBoost evaluated on the same folds, so the gap
    improvement compares two models that differ only in their hyperparameters.
    The chosen model is finally refitted on **all** the rows with the same
    balanced sample weights used inside the folds, and saved with its
    hyperparameters and gap inside the artefact.

    Args:
        dataset_path: Modelling CSV with numeric features and a ``target`` column.
        model_path: Where to save the tuned artefact. Not ``kiniela_model.joblib``:
            the app only loads objects that follow the ``Predictor`` contract.
        space: Parameter values to combine. Defaults to :data:`SEARCH_SPACE`.

    Returns:
        The search: space explored, feasible count, before/after gap and choice.

    Raises:
        FileNotFoundError: If the dataset does not exist.
        ValueError: If ``model_path`` is the app's model, if the dataset is not
            usable, if the space is empty, or if no combination keeps the gap
            below :data:`GAP_THRESHOLD`.
    """
    path = Path(dataset_path)
    if not path.is_file():
        raise FileNotFoundError(f"No dataset at {path}.")
    destination = Path(model_path)
    if destination.resolve() == DEFAULT_MODEL_PATH.resolve():
        raise ValueError(
            "The app loads models/kiniela_model.joblib and requires a 'Predictor' "
            "(docs/model-contract.md). Save the tuned model to another path, for "
            "example models/tuned_xgboost.joblib."
        )
    dataset = pd.read_csv(path)

    columns = feature_columns(dataset)
    X, y, n_dropped = prepare_xy(dataset, columns)

    before = ComboResult(
        issue6_parameters(), cross_validate_model(X, y, build_xgboost(), balanced=True)
    )
    results = evaluate_space(X, y, space)
    after = choose_parameters(results)

    model = build_xgboost(**after.params)
    model.fit(X, y, sample_weight=compute_sample_weight("balanced", y))
    artifact = TunedXGBoost(
        model=model,
        feature_columns=tuple(columns),
        params=dict(after.params),
        gap=after.gap,
        version=f"{VERSION_PREFIX}-{date.today().isoformat()}",
    )
    destination.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(artifact, destination)

    return TuningReport(
        n_splits=CV_N_SPLITS,
        random_state=RANDOM_STATE,
        n_samples=len(X),
        n_dropped=n_dropped,
        feature_columns=tuple(columns),
        space=dict(SEARCH_SPACE if space is None else space),
        n_combos=len(results),
        n_feasible=sum(1 for result in results if result.gap < GAP_THRESHOLD),
        before=before,
        after=after,
    )


def format_tuning(
    report: TuningReport, dataset_path: str | Path, model_path: str | Path
) -> str:
    """Render the search and the before/after gap table as text. Never prints."""
    lines = [
        "Hyperparameter tuning (issue #7)",
        f"  validation: StratifiedKFold(n_splits={report.n_splits}, shuffle=True, "
        f"random_state={report.random_state})",
        f"  dataset: {dataset_path} ({report.n_samples} rows"
        + (
            f", {report.n_dropped} dropped without history"
            if report.n_dropped
            else ""
        )
        + f", {len(report.feature_columns)} features)",
        f"  gap metric: |mean(train {report.gap_metric}) - "
        f"mean(validation {report.gap_metric})| < {report.gap_threshold}",
        f"  search: grid, {report.n_combos} combinations "
        f"({report.n_feasible} feasible)",
        "  space explored:",
    ]
    for key, values in report.space.items():
        lines.append(f"    {key}: {', '.join(str(value) for value in values)}")
    lines.extend(
        [
            "",
            "  gap before and after:",
            f"    {'stage':<24}{'train f1_macro':<18}{'val f1_macro':<18}"
            f"{'gap':<10}val accuracy",
        ]
    )
    for label, combo in ((BEFORE_LABEL, report.before), (AFTER_LABEL, report.after)):
        scores = combo.scores
        lines.append(
            f"    {label:<24}{scores.train_f1_macro_mean:<18.3f}"
            f"{scores.f1_macro_mean:<18.3f}{combo.gap:<10.3f}"
            f"{scores.accuracy_mean:.3f}"
        )
    before_params = ", ".join(
        f"{key}={value}" for key, value in sorted(report.before.params.items())
    )
    lines.extend(
        [
            f"  before parameters: {before_params} (the rest at XGBoost library "
            "defaults)",
            "  chosen parameters: "
            + ", ".join(
                f"{key}={value}" for key, value in sorted(report.after.params.items())
            ),
            f"  rule: highest validation {report.gap_metric} among the combinations "
            f"with gap < {report.gap_threshold}; accuracy breaks ties.",
            f"  saved: {model_path}",
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point: ``python -m kiniela.models.tuning --dataset ... --model ...``."""
    parser = argparse.ArgumentParser(
        description=(
            "Tune XGBoost with a grid search and a < 5% overfitting gap (issue #7)."
        )
    )
    parser.add_argument(
        "--dataset",
        required=True,
        help="Modelling CSV with numeric features and a 'target' column.",
    )
    parser.add_argument(
        "--model",
        required=True,
        help="Output path of the artefact, for example models/tuned_xgboost.joblib.",
    )
    args = parser.parse_args(argv)
    report = tune_model(args.dataset, args.model)
    print(format_tuning(report, args.dataset, args.model))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
