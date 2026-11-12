"""XGBoost and LightGBM compared against the baseline with the same validation scheme.

Issue #6: both ensembles train with the baseline's splitter and seed
(:func:`kiniela.models.train.stratified_cv`) on the same prepared data, so the numbers
are directly comparable. The comparison reports, for the reference, the baseline
Random Forest, XGBoost and LightGBM, their accuracy, F1 macro and **F1 per class**.

Class imbalance is handled the same way in every model and only with the training
fold's labels: the Random Forest and LightGBM through ``class_weight="balanced"``,
XGBoost through sample weights computed per fold (it has no ``class_weight``).

The candidate is the model with the highest mean F1 macro. Accuracy rewards predicting
the majority class (about 46% of the matches), while F1 macro weights the six classes
equally, which is what the kiniela needs; accuracy only breaks ties.

Run it again with::

    PYTHONPATH=src python -m kiniela.models.ensembles \\
        --dataset data/processed/premier_league_with_features_and_target.csv
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
from lightgbm import LGBMClassifier
from xgboost import XGBClassifier

from kiniela.config import CV_N_SPLITS, RANDOM_STATE
from kiniela.models.train import (
    FoldScores,
    build_forest,
    build_reference,
    cross_validate_model,
    feature_columns,
    prepare_xy,
    stratified_cv,
)

REFERENCE_NAME = "reference (majority)"
FOREST_NAME = "random_forest"
XGBOOST_NAME = "xgboost"
LIGHTGBM_NAME = "lightgbm"

CANDIDATE_CRITERION = "highest mean F1 macro across the folds"


@dataclass(frozen=True)
class ModelComparison:
    """The metrics of every model on the fixed scheme, and the chosen candidate."""

    n_splits: int
    random_state: int
    n_samples: int
    n_dropped: int
    feature_columns: tuple[str, ...]
    scores: dict[str, FoldScores]
    candidate: str
    criterion: str = CANDIDATE_CRITERION


def build_ensembles() -> dict[str, object]:
    """The two ensembles of issue #6, with their library defaults plus a fixed seed.

    Hyperparameter search is issue #7: here the comparison has to be reproducible
    and fair, not optimised.
    """
    return {
        FOREST_NAME: build_forest(),
        XGBOOST_NAME: XGBClassifier(
            n_estimators=100,
            learning_rate=0.1,
            objective="multi:softprob",
            eval_metric="mlogloss",
            tree_method="hist",
            random_state=RANDOM_STATE,
            n_jobs=-1,
        ),
        LIGHTGBM_NAME: LGBMClassifier(
            n_estimators=100,
            learning_rate=0.1,
            class_weight="balanced",
            random_state=RANDOM_STATE,
            n_jobs=1,  # fixed thread count: keeps LightGBM reproducible
            deterministic=True,
            force_row_wise=True,
            verbosity=-1,
        ),
    }


def choose_candidate(scores: dict[str, FoldScores]) -> str:
    """Highest mean F1 macro among the trained models; accuracy only breaks ties.

    The reference is not eligible: it is the trivial bar, not a candidate.
    """
    trained = {name: value for name, value in scores.items() if name != REFERENCE_NAME}
    return max(
        trained,
        key=lambda name: (trained[name].f1_macro_mean, trained[name].accuracy_mean),
    )


def compare_models(dataset_path: str | Path) -> ModelComparison:
    """Train the reference, the baseline and the two ensembles on the fixed scheme.

    Args:
        dataset_path: Modelling CSV with numeric features and a ``target`` column.

    Returns:
        The metrics of every model and the chosen candidate.

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
    X, y, n_dropped = prepare_xy(dataset, columns)

    models = {REFERENCE_NAME: build_reference(), **build_ensembles()}
    scores = {
        name: cross_validate_model(X, y, model, balanced=name == XGBOOST_NAME)
        for name, model in models.items()
    }

    return ModelComparison(
        n_splits=CV_N_SPLITS,
        random_state=RANDOM_STATE,
        n_samples=len(X),
        n_dropped=n_dropped,
        feature_columns=tuple(columns),
        scores=scores,
        candidate=choose_candidate(scores),
    )


def format_comparison(comparison: ModelComparison, dataset_path: str | Path) -> str:
    """Render the comparison as text. Pure function: it never prints."""
    lines = [
        "Model comparison (Random Forest vs XGBoost vs LightGBM)",
        f"  validation: StratifiedKFold(n_splits={comparison.n_splits}, shuffle=True, "
        f"random_state={comparison.random_state})",
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
    lines.extend(
        [
            "",
            f"  candidate: {comparison.candidate}",
            f"  reason: {comparison.criterion} — accuracy favours the majority class, "
            "F1 macro weights the six classes equally.",
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point: ``python -m kiniela.models.ensembles --dataset ...``."""
    parser = argparse.ArgumentParser(
        description="Compare XGBoost and LightGBM against the baseline (issue #6)."
    )
    parser.add_argument(
        "--dataset",
        required=True,
        help="Modelling CSV with numeric features and a 'target' column.",
    )
    args = parser.parse_args(argv)
    comparison = compare_models(args.dataset)
    print(format_comparison(comparison, args.dataset))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
