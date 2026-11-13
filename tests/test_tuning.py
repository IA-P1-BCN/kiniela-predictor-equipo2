"""Hyperparameter tuning with the < 5% overfitting guard (issue #7)."""

import joblib
import numpy as np
import pandas as pd
import pytest

from kiniela.config import CV_N_SPLITS, N_CLASSES
from kiniela.models.ensembles import build_xgboost
from kiniela.models.predict import DEFAULT_MODEL_PATH
from kiniela.models.train import FoldScores, feature_columns, prepare_xy
from kiniela.models.tuning import (
    AFTER_LABEL,
    BEFORE_LABEL,
    GAP_METRIC,
    GAP_THRESHOLD,
    SEARCH_SPACE,
    ComboResult,
    TunedXGBoost,
    choose_parameters,
    evaluate_space,
    format_tuning,
    issue6_parameters,
    main,
    tune_model,
)

from test_train import FEATURES, write_dataset

# Small grid for the tests: the documented 648-combination grid runs in the CLI.
# On the synthetic dataset only the heavily regularised combination keeps the gap
# below the threshold, which is the behaviour under test: the grid must reject
# the better-scoring but overfitted combination.
TINY_SPACE = {"max_depth": (1,), "n_estimators": (1,), "min_child_weight": (1, 100)}


def combo(params, train_f1, val_f1, accuracy=0.5) -> ComboResult:
    """A ComboResult with constant fold scores: selection logic in isolation."""
    scores = FoldScores(
        accuracy=(accuracy,) * CV_N_SPLITS,
        f1_macro=(val_f1,) * CV_N_SPLITS,
        f1_per_class=((val_f1,) * N_CLASSES,) * CV_N_SPLITS,
        train_f1_macro=(train_f1,) * CV_N_SPLITS,
    )
    return ComboResult(params, scores)


def prepared(tmp_path):
    """The synthetic dataset as the training code sees it: X and y."""
    dataset = pd.read_csv(write_dataset(tmp_path / "modelling.csv"))
    X, y, _ = prepare_xy(dataset, feature_columns(dataset))
    return X, y


def test_the_documented_search_space_is_a_valid_grid(tmp_path):
    # The grid in the docstring is the grid the code explores: 648 combinations.
    assert GAP_METRIC == "f1_macro"
    assert GAP_THRESHOLD == 0.05
    assert all(values for values in SEARCH_SPACE.values())
    assert np.prod([len(values) for values in SEARCH_SPACE.values()]) == 648
    X, y = prepared(tmp_path)
    first_values = {key: values[0] for key, values in SEARCH_SPACE.items()}
    # Every key must be a parameter XGBoost accepts: it fails at fit time.
    build_xgboost(**first_values).fit(X, y)


def test_gap_is_the_absolute_train_validation_f1_difference():
    assert combo({}, train_f1=0.9, val_f1=0.2).gap == pytest.approx(0.7)
    assert combo({}, train_f1=0.2, val_f1=0.9).gap == pytest.approx(0.7)
    assert combo({}, train_f1=0.5, val_f1=0.5).gap == pytest.approx(0.0)


def test_evaluate_space_scores_every_combination_of_the_grid(tmp_path):
    X, y = prepared(tmp_path)
    results = evaluate_space(X, y, TINY_SPACE)
    assert len(results) == 2
    assert [result.params["min_child_weight"] for result in results] == [1, 100]
    for result in results:
        assert set(result.params) == set(TINY_SPACE)
        assert len(result.scores.f1_macro) == CV_N_SPLITS
        assert len(result.scores.train_f1_macro) == CV_N_SPLITS
        assert all(0.0 <= value <= 1.0 for value in result.scores.train_f1_macro)


def test_evaluate_space_rejects_an_empty_grid(tmp_path):
    X, y = prepared(tmp_path)
    with pytest.raises(ValueError, match="empty"):
        evaluate_space(X, y, {})


def test_choose_parameters_keeps_only_combinations_below_the_threshold():
    overfitted = combo({"depth": 6}, train_f1=0.9, val_f1=0.4)  # gap 0.5
    borderline = combo({"depth": 5}, train_f1=GAP_THRESHOLD, val_f1=0.0)  # gap 0.05
    feasible = combo({"depth": 2}, train_f1=0.5, val_f1=0.49)  # gap 0.01
    weaker = combo({"depth": 1}, train_f1=0.4, val_f1=0.39)  # gap 0.01, lower val
    # The issue demands "menor que 0.05": a gap of exactly 0.05 is not feasible.
    assert borderline.gap == GAP_THRESHOLD
    chosen = choose_parameters([overfitted, borderline, feasible, weaker])
    assert chosen is feasible
    with pytest.raises(ValueError, match="0.05"):
        choose_parameters([overfitted, borderline])


def test_accuracy_only_breaks_ties_between_feasible_combinations():
    first = combo({"depth": 1}, train_f1=0.44, val_f1=0.4, accuracy=0.5)
    second = combo({"depth": 2}, train_f1=0.44, val_f1=0.4, accuracy=0.6)
    assert first.gap < GAP_THRESHOLD and second.gap < GAP_THRESHOLD
    assert choose_parameters([first, second]) is second


def test_choose_parameters_refuses_when_no_combination_is_feasible():
    results = [
        combo({"depth": 6}, train_f1=0.9, val_f1=0.4),
        combo({"depth": 5}, train_f1=0.8, val_f1=0.7),  # gap 0.1
    ]
    with pytest.raises(ValueError, match="0.05"):
        choose_parameters(results)
    with pytest.raises(ValueError, match="0.05"):
        choose_parameters([])


def test_tune_model_registers_the_chosen_parameters_with_the_model(tmp_path):
    path = tmp_path / "tuned_xgboost.joblib"
    report = tune_model(write_dataset(tmp_path / "modelling.csv"), path, space=TINY_SPACE)
    assert report.n_combos == 2
    assert report.n_feasible == 1  # only the regularised one: the other overfits
    assert report.after.gap < GAP_THRESHOLD
    assert set(report.after.params) == set(TINY_SPACE)
    # The rejected combination scores higher on validation but must not win.
    assert report.after.params["min_child_weight"] == 100
    artifact = joblib.load(path)
    assert isinstance(artifact, TunedXGBoost)
    assert artifact.version.startswith("tuned-xgb-")
    assert artifact.params == report.after.params
    assert artifact.gap == report.after.gap
    assert artifact.feature_columns == FEATURES
    probabilities = artifact.model.predict_proba(np.zeros((1, len(FEATURES))))
    assert probabilities.shape == (1, N_CLASSES)


def test_the_before_point_is_the_issue6_xgboost(tmp_path):
    report = tune_model(
        write_dataset(tmp_path / "modelling.csv"),
        tmp_path / "tuned_xgboost.joblib",
        space=TINY_SPACE,
    )
    assert report.before.params == issue6_parameters()
    assert report.before.params["n_estimators"] == 100
    assert report.before.params["learning_rate"] == 0.1
    assert len(report.before.scores.accuracy) == CV_N_SPLITS
    assert report.n_splits == CV_N_SPLITS
    assert report.gap_before == report.before.scores.f1_macro_gap


def test_tune_model_refuses_to_overwrite_the_app_model(tmp_path):
    with pytest.raises(ValueError, match="Predictor"):
        tune_model(write_dataset(tmp_path / "modelling.csv"), DEFAULT_MODEL_PATH)


def test_tune_model_rejects_a_missing_dataset(tmp_path):
    with pytest.raises(FileNotFoundError):
        tune_model(tmp_path / "missing.csv", tmp_path / "tuned_xgboost.joblib")


def test_format_tuning_renders_the_gap_table_before_and_after(tmp_path, capsys):
    path = tmp_path / "tuned_xgboost.joblib"
    report = tune_model(write_dataset(tmp_path / "modelling.csv"), path, space=TINY_SPACE)
    text = format_tuning(report, "modelling.csv", path)
    assert capsys.readouterr().out == ""  # formatting never prints
    assert f"|mean(train {GAP_METRIC}) - mean(validation {GAP_METRIC})| < 0.05" in text
    assert f"grid, {report.n_combos} combinations" in text
    assert "space explored:" in text and "max_depth" in text
    assert BEFORE_LABEL in text and AFTER_LABEL in text
    assert text.index(BEFORE_LABEL) < text.index(AFTER_LABEL)
    assert "chosen parameters:" in text
    assert f"saved: {path}" in text


def test_is_reproducible_with_the_same_seed(tmp_path):
    first = tune_model(
        write_dataset(tmp_path / "modelling.csv"),
        tmp_path / "first.joblib",
        space=TINY_SPACE,
    )
    second = tune_model(
        write_dataset(tmp_path / "modelling.csv"),
        tmp_path / "second.joblib",
        space=TINY_SPACE,
    )
    assert first.after.params == second.after.params
    assert first.after.scores.accuracy == second.after.scores.accuracy
    assert first.after.scores.f1_macro == second.after.scores.f1_macro
    assert first.gap_before == second.gap_before


def test_cli_tunes_from_the_command_line(tmp_path, capsys, monkeypatch):
    # The CLI has no space argument: it explores the documented grid. Patch it to
    # the tiny one here, or the test would run all 648 combinations.
    monkeypatch.setattr("kiniela.models.tuning.SEARCH_SPACE", TINY_SPACE)
    dataset = write_dataset(tmp_path / "modelling.csv")
    model = tmp_path / "tuned_xgboost.joblib"
    assert main(["--dataset", str(dataset), "--model", str(model)]) == 0
    output = capsys.readouterr().out
    assert "gap before and after:" in output
    assert BEFORE_LABEL in output and AFTER_LABEL in output
    assert model.is_file()
