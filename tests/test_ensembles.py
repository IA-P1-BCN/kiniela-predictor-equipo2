"""Ensemble comparison: XGBoost and LightGBM against the baseline (issue #6)."""

import pytest

from kiniela.config import CV_N_SPLITS, N_CLASSES, RANDOM_STATE
from kiniela.models.ensembles import (
    FOREST_NAME,
    LIGHTGBM_NAME,
    REFERENCE_NAME,
    XGBOOST_NAME,
    choose_candidate,
    compare_models,
    format_comparison,
    main,
)
from kiniela.models.train import FoldScores, train_baseline

from test_train import write_dataset


def uniform_scores(value: float) -> FoldScores:
    """FoldScores with the same value everywhere, to test the choice in isolation."""
    fold = (value,) * N_CLASSES
    return FoldScores(
        (value,) * CV_N_SPLITS, (value,) * CV_N_SPLITS, (fold,) * CV_N_SPLITS
    )


def test_compares_every_model_with_the_baseline_scheme(tmp_path):
    comparison = compare_models(write_dataset(tmp_path / "modelling.csv"))
    assert set(comparison.scores) == {
        REFERENCE_NAME,
        FOREST_NAME,
        XGBOOST_NAME,
        LIGHTGBM_NAME,
    }
    assert comparison.n_splits == CV_N_SPLITS
    assert comparison.random_state == RANDOM_STATE


def test_the_baseline_forest_scores_the_same_as_in_the_baseline(tmp_path):
    # Same model, same data, same splitter: the comparison must reproduce #5.
    dataset = write_dataset(tmp_path / "modelling.csv")
    comparison = compare_models(dataset)
    baseline = train_baseline(dataset, tmp_path / "baseline_rf.joblib")
    assert comparison.n_splits == baseline.n_splits
    assert comparison.random_state == baseline.random_state
    assert comparison.scores[FOREST_NAME].accuracy == baseline.random_forest.accuracy
    assert comparison.scores[FOREST_NAME].f1_macro == baseline.random_forest.f1_macro


def test_reports_f1_per_class_for_the_six_classes(tmp_path):
    comparison = compare_models(write_dataset(tmp_path / "modelling.csv"))
    for scores in comparison.scores.values():
        assert len(scores.f1_per_class) == CV_N_SPLITS
        for fold in scores.f1_per_class:
            assert len(fold) == N_CLASSES
            assert all(0.0 <= value <= 1.0 for value in fold)
        assert len(scores.f1_per_class_mean) == N_CLASSES


def test_candidate_is_the_best_f1_macro_and_never_the_reference(tmp_path):
    comparison = compare_models(write_dataset(tmp_path / "modelling.csv"))
    trained = {
        name: scores
        for name, scores in comparison.scores.items()
        if name != REFERENCE_NAME
    }
    best_f1 = max(trained, key=lambda name: trained[name].f1_macro_mean)
    assert comparison.candidate == best_f1
    assert comparison.candidate != REFERENCE_NAME
    assert comparison.criterion


def test_candidate_ignores_the_reference_even_with_the_best_score():
    scores = {
        REFERENCE_NAME: uniform_scores(0.9),
        FOREST_NAME: uniform_scores(0.5),
    }
    assert choose_candidate(scores) == FOREST_NAME


def test_is_reproducible_for_every_model(tmp_path):
    first = compare_models(write_dataset(tmp_path / "modelling.csv"))
    second = compare_models(write_dataset(tmp_path / "modelling.csv"))
    for name, scores in first.scores.items():
        assert scores.accuracy == second.scores[name].accuracy
        assert scores.f1_macro == second.scores[name].f1_macro
        assert scores.f1_per_class == second.scores[name].f1_per_class


def test_format_comparison_renders_the_table_and_the_candidate(tmp_path, capsys):
    comparison = compare_models(write_dataset(tmp_path / "modelling.csv"))
    text = format_comparison(comparison, "modelling.csv")
    assert capsys.readouterr().out == ""  # formatting never prints
    assert "StratifiedKFold(n_splits=5, shuffle=True, random_state=42)" in text
    assert "f1 per class" in text
    for name in (REFERENCE_NAME, FOREST_NAME, XGBOOST_NAME, LIGHTGBM_NAME):
        assert name in text
    assert f"candidate: {comparison.candidate}" in text


def test_cli_runs_the_comparison(tmp_path, capsys):
    dataset = write_dataset(tmp_path / "modelling.csv")
    assert main(["--dataset", str(dataset)]) == 0
    output = capsys.readouterr().out
    assert "candidate:" in output
    assert XGBOOST_NAME in output
    assert LIGHTGBM_NAME in output


def test_rejects_a_missing_dataset(tmp_path):
    with pytest.raises(FileNotFoundError):
        compare_models(tmp_path / "missing.csv")
