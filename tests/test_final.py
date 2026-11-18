"""Tests of the final model of the app (issue #35)."""

import json
from datetime import date, timedelta
from itertools import permutations

import numpy as np
import pandas as pd
import pytest

from kiniela.config import N_CLASSES, RANDOM_STATE
from kiniela.data.catalog import FALLBACK_TEAMS
from kiniela.features.engineering import FEATURE_COLUMNS, build_match_features
from kiniela.models.ab_testing import load_model_card
from kiniela.models.final import (
    MatchPredictor,
    build_modelling_dataset,
    main,
    save_final_model,
    train_final_model,
)
from kiniela.models.predict import DEFAULT_MODEL_PATH, Predictor, load_predictor, predicted_class
from kiniela.models.tuning import GAP_THRESHOLD

# One strongly regularised combination: fast, and its gap stays below the threshold
SMALL_SPACE = {
    "max_depth": (1,),
    "n_estimators": (5,),
    "learning_rate": (0.1,),
    "min_child_weight": (100,),
    "reg_lambda": (500,),
    "subsample": (1.0,),
    "colsample_bytree": (1.0,),
}


def synthetic_season(n_teams: int = 20) -> pd.DataFrame:
    """A double round robin with random scores, dates written day first as in the CSV."""
    rng = np.random.default_rng(RANDOM_STATE)
    teams = [f"team {i:02d}" for i in range(n_teams)]
    rows = []
    for number, (home, away) in enumerate(permutations(teams, 2)):
        home_goals, away_goals = rng.poisson(1.5), rng.poisson(1.2)
        played = date(2023, 8, 11) + timedelta(days=number // 10)
        result = "H" if home_goals > away_goals else "A" if away_goals > home_goals else "D"
        rows.append({"Date": played.strftime("%d/%m/%Y"), "HomeTeam": home, "AwayTeam": away,
                     "FTHG": home_goals, "FTAG": away_goals, "FTR": result})
    return pd.DataFrame(rows)


@pytest.fixture(scope="module")
def trained():
    return train_final_model(synthetic_season(), source="synthetic.csv", space=SMALL_SPACE)


class StubModel:
    """A model that only knows some classes, to check the class order of the output."""

    classes_ = np.array([0, 2, 5])

    def predict_proba(self, features):
        return np.array([[0.2, 0.3, 0.5]])


# --- The predictor --------------------------------------------------------------------

def test_final_model_follows_the_app_contract(trained):
    predictor, _ = trained
    assert isinstance(predictor, Predictor)
    probabilities = predictor.predict("team 00", "team 01")
    assert len(probabilities) == N_CLASSES
    assert sum(probabilities) == pytest.approx(1)
    assert 0 <= predicted_class(probabilities) < N_CLASSES


def test_predictor_uses_the_training_features(trained):
    predictor, _ = trained
    assert predictor.feature_columns == FEATURE_COLUMNS
    features = build_match_features(predictor.history, "team 03", "team 07")
    expected = predictor.model.predict_proba(features)[0]
    assert predictor.predict("team 03", "team 07") == pytest.approx(expected.tolist())


def test_probabilities_are_placed_at_their_class():
    history = synthetic_season(4)
    predictor = MatchPredictor(StubModel(), history, FEATURE_COLUMNS, "stub")
    assert predictor.predict("team 00", "team 01") == [0.2, 0.0, 0.3, 0.0, 0.0, 0.5]


@pytest.mark.parametrize(("home", "away"), [("team 00", "team 00"), ("", "team 01"),
                                            ("team 00", "unknown fc")])
def test_predictor_rejects_invalid_teams(trained, home, away):
    predictor, _ = trained
    with pytest.raises(ValueError):
        predictor.predict(home, away)


def test_history_keeps_only_the_played_matches_with_parsed_dates(trained):
    predictor, _ = trained
    assert len(predictor.history) == 380
    assert pd.api.types.is_datetime64_any_dtype(predictor.history["Date"])
    assert predictor.history["Date"].is_monotonic_increasing


def test_modelling_dataset_has_features_and_target():
    dataset = build_modelling_dataset(synthetic_season())
    assert set(FEATURE_COLUMNS) <= set(dataset.columns)
    assert dataset["target"].between(0, N_CLASSES - 1).all()


# --- Model card and saving ------------------------------------------------------------

def test_card_has_what_the_ab_rule_and_the_contract_need(trained):
    predictor, card = trained
    assert card["version"] == predictor.version
    assert card["metrics"]["overfitting_gap"] < GAP_THRESHOLD
    assert 0 <= card["metrics"]["f1_macro"] <= 1
    assert card["features"] == list(FEATURE_COLUMNS)
    assert card["random_state"] == RANDOM_STATE
    assert card["training_data"]["source"] == "synthetic.csv"


def test_saved_model_is_loaded_by_the_app(trained, tmp_path):
    predictor, card = trained
    model_path, card_path = save_final_model(predictor, card, tmp_path)
    loaded = load_predictor(model_path)
    assert loaded.version == predictor.version
    assert loaded.predict("team 00", "team 01") == pytest.approx(predictor.predict("team 00", "team 01"))
    assert load_model_card(card_path)["version"] == predictor.version


def test_command_line_writes_model_and_card(tmp_path, monkeypatch, capsys):
    import kiniela.models.final as final

    matches = tmp_path / "matches.csv"
    synthetic_season().to_csv(matches, index=False)
    original = final.train_final_model
    monkeypatch.setattr(final, "train_final_model",
                        lambda data, source: original(data, source=source, space=SMALL_SPACE))

    main(["--matches", str(matches), "--models-dir", str(tmp_path / "models")])

    assert "Validation F1 macro" in capsys.readouterr().out
    card = json.loads((tmp_path / "models" / "model_card.json").read_text(encoding="utf-8"))
    assert card["training_data"]["source"] == "matches.csv"


# --- The artefact committed in models/ ------------------------------------------------

def test_committed_model_follows_the_contract():
    predictor = load_predictor(DEFAULT_MODEL_PATH)
    card = load_model_card(DEFAULT_MODEL_PATH.parent / "model_card.json")

    assert not getattr(predictor, "is_reference", False)
    assert predictor.version == card["version"]
    assert card["metrics"]["overfitting_gap"] < GAP_THRESHOLD
    probabilities = predictor.predict("arsenal", "chelsea")
    assert len(probabilities) == N_CLASSES
    assert sum(probabilities) == pytest.approx(1)


def test_committed_model_knows_every_team_of_the_app():
    # Inside Docker there is no dataset: the app offers FALLBACK_TEAMS, so the model must know them
    predictor = load_predictor(DEFAULT_MODEL_PATH)
    assert set(FALLBACK_TEAMS) <= set(predictor.teams)


@pytest.mark.filterwarnings("ignore:.*found in sys.modules:RuntimeWarning")  # expected with runpy
def test_model_saved_by_the_command_line_loads_in_another_process(tmp_path, monkeypatch):
    """``python -m`` must not save the class as ``__main__.MatchPredictor`` (the app could not load it)."""
    import runpy
    import subprocess
    import sys

    import kiniela.models.final as final

    matches = tmp_path / "matches.csv"
    synthetic_season().to_csv(matches, index=False)
    original = final.train_final_model
    monkeypatch.setattr(final, "train_final_model",
                        lambda data, source: original(data, source=source, space=SMALL_SPACE))
    monkeypatch.setattr(sys, "argv", ["final", "--matches", str(matches), "--models-dir", str(tmp_path)])

    with pytest.raises(SystemExit):
        runpy.run_module("kiniela.models.final", run_name="__main__")

    check = "import joblib, sys; print(type(joblib.load(sys.argv[1])).__module__)"
    result = subprocess.run([sys.executable, "-c", check, str(tmp_path / "kiniela_model.joblib")],
                            capture_output=True, text=True, env={**__import__("os").environ, "PYTHONPATH": "src"},
                            check=True)
    assert result.stdout.strip() == "kiniela.models.final"


# --- Several seasons ------------------------------------------------------------------

def two_seasons() -> pd.DataFrame:
    """Season 1 with teams 00-05, season 2 with teams 00-04 and a promoted team 99."""
    first = synthetic_season(6).assign(Season="2223")
    second = synthetic_season(6).replace("team 05", "team 99").assign(Season="2324")
    second["Date"] = (pd.to_datetime(second["Date"], dayfirst=True) + pd.DateOffset(years=1)).dt.strftime("%d/%m/%Y")
    return pd.concat([first, second], ignore_index=True)


def test_predictor_only_accepts_teams_of_the_latest_season():
    predictor = MatchPredictor(StubModel(), two_seasons(), FEATURE_COLUMNS, "stub")
    assert "team 99" in predictor.teams
    assert "team 05" not in predictor.teams  # relegated: no history in the latest season
    with pytest.raises(ValueError, match="Unknown team"):
        predictor.predict("team 05", "team 00")


def test_download_seasons_tags_each_season(monkeypatch):
    import kiniela.models.final as final

    def fake_download(season):
        print("progress output that must not reach the console")
        return synthetic_season(4)

    monkeypatch.setattr(final, "download_premier_league_data", fake_download)
    matches = final.download_seasons(["2223", "2324"])
    assert matches.groupby("Season").size().to_dict() == {"2223": 12, "2324": 12}
