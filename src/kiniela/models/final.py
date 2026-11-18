"""Final model of the app (issue #35): the tuned XGBoost behind the ``Predictor`` contract.

The app only knows two team names. :class:`MatchPredictor` turns them into the model
inputs with :func:`kiniela.features.engineering.build_match_features` (the same
calculation used for training, issue #34) and returns the six class probabilities.

Build and save it, from the repo root::

    PYTHONPATH=src python -m kiniela.models.final            # the 9 default seasons
    PYTHONPATH=src python -m kiniela.models.final --matches data/raw/<file>.csv

By default it downloads :data:`DEFAULT_SEASONS` from football-data.co.uk (one season
is too little data: no combination beats the reference model), keeps a copy in
``data/raw/`` (not versioned) and writes ``models/kiniela_model.joblib`` and
``models/model_card.json``. The
hyperparameters are chosen again by the search of issue #7 (:func:`tune_model`, same
``StratifiedKFold``, ``RANDOM_STATE`` and gap < 0.05), so they always match the
current features. See ``docs/model-contract.md``.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import tempfile
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from xgboost import XGBClassifier

from kiniela.config import CV_N_SPLITS, N_CLASSES, RANDOM_STATE
from kiniela.data.dataset import download_premier_league_data
from kiniela.data.target import build_target
from kiniela.features.engineering import (  # same date parsing as the features
    _sorted_by_date,
    build_features,
    build_match_features,
)
from kiniela.models.ab_testing import CURRENT_CARD_NAME
from kiniela.models.predict import DEFAULT_MODEL_PATH, validate_teams
from kiniela.models.train import TARGET_COLUMN
from kiniela.models.tuning import GAP_METRIC, GAP_THRESHOLD, TuningReport, tune_model

# Columns of the played matches kept inside the model to compute new features
HISTORY_COLUMNS = ["Date", "HomeTeam", "AwayTeam", "FTHG", "FTAG", "FTR"]

# Premier League seasons used for training, as football-data.co.uk codes (2015-16 to 2023-24)
DEFAULT_SEASONS = ("1516", "1617", "1718", "1819", "1920", "2021", "2122", "2223", "2324")
RAW_DIR = DEFAULT_MODEL_PATH.parents[1] / "data" / "raw"


@dataclass(frozen=True)
class MatchPredictor:
    """The trained model plus the match history it needs to build features."""

    model: XGBClassifier
    history: pd.DataFrame  # played matches (HISTORY_COLUMNS), the base of every prediction
    feature_columns: tuple[str, ...]
    version: str

    @property
    def teams(self) -> list[str]:
        """Teams of the latest season, written as in the dataset.

        New features use the latest season only, so a team relegated before it would
        have no history and its prediction would be meaningless.
        """
        latest = self.history
        if "Season" in latest.columns:
            latest = latest[latest["Season"] == latest["Season"].iloc[-1]]
        return sorted(set(latest["HomeTeam"]) | set(latest["AwayTeam"]))

    def predict(self, home_team: str, away_team: str) -> list[float]:
        """Probability of each class (0-5) for a match that has not been played yet.

        Raises ``ValueError`` if a team is missing, repeated or unknown to the model.
        """
        home, away = validate_teams(home_team, away_team)
        unknown = [team for team in (home, away) if team not in self.teams]
        if unknown:
            raise ValueError(f"Unknown team: {', '.join(unknown)}.")

        features = build_match_features(self.history, home, away)[list(self.feature_columns)]
        probabilities = self.model.predict_proba(features)[0]
        # predict_proba follows model.classes_; place each value at its class (0-5)
        by_class = np.zeros(N_CLASSES)
        by_class[self.model.classes_.astype(int)] = probabilities
        return by_class.tolist()


def download_seasons(seasons: Sequence[str] = DEFAULT_SEASONS) -> pd.DataFrame:
    """Download several seasons with the data pipeline of issue #1, tagged with ``Season``.

    ``Season`` keeps the features of each season apart: a team's form starts again
    every season, as :func:`build_features` expects.
    """
    frames = []
    with contextlib.redirect_stdout(io.StringIO()):  # the download prints its progress
        for season in seasons:
            frames.append(download_premier_league_data(season).assign(Season=str(season)))
    return pd.concat(frames, ignore_index=True)


def build_modelling_dataset(matches: pd.DataFrame) -> pd.DataFrame:
    """Features of every match (issue #3) plus its 6-class ``target`` (issue #2)."""
    dataset = build_features(matches)
    dataset[TARGET_COLUMN] = [
        build_target(int(home), int(away)) for home, away in zip(dataset["FTHG"], dataset["FTAG"])
    ]
    return dataset


def model_card(predictor: MatchPredictor, report: TuningReport, params: Mapping[str, Any],
               source: str) -> dict[str, Any]:
    """Metadata saved next to the model. ``metrics`` is what the A/B rule reads (#37)."""
    after, before = report.after.scores, report.before.scores
    return {
        "version": predictor.version,
        "created_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "model": "XGBClassifier (issue #6), hyperparameters from the grid search of issue #7",
        "params": dict(params),
        "metrics": {
            "f1_macro": after.f1_macro_mean,
            "f1_macro_std": after.f1_macro_std,
            "accuracy": after.accuracy_mean,
            "train_f1_macro": after.train_f1_macro_mean,
            "overfitting_gap": report.after.gap,
        },
        "before_tuning": {
            "f1_macro": before.f1_macro_mean,
            "train_f1_macro": before.train_f1_macro_mean,
            "overfitting_gap": report.before.gap,
        },
        "validation": (
            f"StratifiedKFold(n_splits={CV_N_SPLITS}, shuffle=True, random_state={RANDOM_STATE}); "
            f"gap = |train {GAP_METRIC} - validation {GAP_METRIC}| < {GAP_THRESHOLD}"
        ),
        "features": list(predictor.feature_columns),
        "random_state": RANDOM_STATE,
        "training_data": {
            "source": source,
            "matches": len(predictor.history),
            "rows_used": report.n_samples,
            "rows_without_history": report.n_dropped,
        },
    }


def train_final_model(
    matches: pd.DataFrame,
    *,
    source: str = "matches",
    space: Mapping[str, Sequence[int | float]] | None = None,
) -> tuple[MatchPredictor, dict[str, Any]]:
    """Tune and fit the final model on ``matches``. Returns the predictor and its card.

    Raises ``ValueError`` (from :func:`tune_model`) if no combination keeps the gap
    below the threshold: the project never ships an overfitted model.
    """
    with tempfile.TemporaryDirectory() as folder:
        dataset_path = Path(folder) / "modelling.csv"
        tuned_path = Path(folder) / "tuned.joblib"
        build_modelling_dataset(matches).to_csv(dataset_path, index=False)
        report = tune_model(dataset_path, tuned_path, space=space)
        tuned = joblib.load(tuned_path)

    # Played matches with parsed dates; Season is kept so new features use the latest one
    columns = HISTORY_COLUMNS + (["Season"] if "Season" in matches.columns else [])
    history = _sorted_by_date(matches)[columns]
    predictor = MatchPredictor(
        model=tuned.model,
        history=history,
        feature_columns=tuple(tuned.feature_columns),
        version=tuned.version,
    )
    return predictor, model_card(predictor, report, tuned.params, source)


def save_final_model(predictor: MatchPredictor, card: Mapping[str, Any],
                     models_dir: Path = DEFAULT_MODEL_PATH.parent) -> tuple[Path, Path]:
    """Write ``kiniela_model.joblib`` and ``model_card.json`` in ``models_dir``."""
    models_dir.mkdir(parents=True, exist_ok=True)
    model_path = models_dir / DEFAULT_MODEL_PATH.name
    card_path = models_dir / CURRENT_CARD_NAME
    joblib.dump(predictor, model_path)
    card_path.write_text(json.dumps(card, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return model_path, card_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Train and save the final model of the app (issue #35).")
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--seasons", nargs="+", default=list(DEFAULT_SEASONS),
                        help="football-data.co.uk season codes to download (default: 2015-16 to 2023-24).")
    source.add_argument("--matches", type=Path,
                        help="Use a matches CSV instead of downloading (HomeTeam, AwayTeam, FTHG, FTAG, "
                             "FTR, Date and optionally Season).")
    parser.add_argument("--models-dir", type=Path, default=DEFAULT_MODEL_PATH.parent,
                        help="Where to write kiniela_model.joblib and model_card.json.")
    args = parser.parse_args(argv)

    if args.matches is not None:
        matches = pd.read_csv(args.matches, dtype={"Season": str})
        source_name = args.matches.name
    else:
        matches = download_seasons(args.seasons)
        source_name = f"football-data.co.uk Premier League, seasons {', '.join(args.seasons)}"
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        raw_copy = RAW_DIR / f"premier_league_{args.seasons[0]}_{args.seasons[-1]}.csv"
        matches.to_csv(raw_copy, index=False)
        print(f"Downloaded {len(matches)} matches; copy in {raw_copy}.")

    predictor, card = train_final_model(matches, source=source_name)
    model_path, card_path = save_final_model(predictor, card, args.models_dir)
    metrics = card["metrics"]
    print(f"Saved {model_path} and {card_path} ({predictor.version}).")
    print(f"Validation F1 macro {metrics['f1_macro']:.3f}, accuracy {metrics['accuracy']:.3f}, "
          f"gap {metrics['overfitting_gap']:.4f} (< {GAP_THRESHOLD}).")
    return 0


if __name__ == "__main__":
    # With ``python -m`` this file runs as ``__main__``, and joblib would save the class
    # as ``__main__.MatchPredictor``, which the app cannot import. Running the package
    # module saves it as ``kiniela.models.final.MatchPredictor``.
    from kiniela.models.final import main as package_main

    raise SystemExit(package_main())
