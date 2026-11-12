"""Multiclass neural network compared with the ensembles (issue #13)."""

import pytest

from kiniela.config import CV_N_SPLITS, N_CLASSES, RANDOM_STATE
from kiniela.models.ensembles import (
    FOREST_NAME,
    LIGHTGBM_NAME,
    XGBOOST_NAME,
    compare_models,
)
from kiniela.models.neural import (
    HIDDEN_LAYERS,
    L2_ALPHA,
    NETWORK_NAME,
    ScaledMLP,
    build_network,
    compare_network,
    format_network_comparison,
    main,
)

from test_train import write_dataset

ENSEMBLES = (FOREST_NAME, XGBOOST_NAME, LIGHTGBM_NAME)


def test_network_uses_six_outputs_l2_and_early_stopping(tmp_path):
    import pandas as pd

    frame = pd.read_csv(write_dataset(tmp_path / "modelling.csv"))
    network = build_network()
    assert isinstance(network, ScaledMLP)
    assert network.hidden_layer_sizes == HIDDEN_LAYERS
    assert network.alpha == L2_ALPHA
    assert network.random_state == RANDOM_STATE
    features = frame[["form_home", "goals_avg", "home_advantage", "goal_diff_form"]]
    network.fit(features, frame["target"])
    assert network.network_.early_stopping is True
    assert network.predict_proba(features).shape[1] == N_CLASSES


def test_compares_the_network_on_the_same_scheme_as_the_ensembles(tmp_path):
    dataset = write_dataset(tmp_path / "modelling.csv")
    comparison = compare_network(dataset)
    ensembles = compare_models(dataset)

    assert comparison.n_splits == CV_N_SPLITS == ensembles.n_splits
    assert comparison.random_state == RANDOM_STATE == ensembles.random_state
    assert comparison.best_ensemble in ENSEMBLES
    assert comparison.network == NETWORK_NAME
    for name in ENSEMBLES:
        assert comparison.scores[name].f1_macro == ensembles.scores[name].f1_macro
        assert comparison.scores[name].accuracy == ensembles.scores[name].accuracy


def test_reports_f1_per_class_for_the_network(tmp_path):
    comparison = compare_network(write_dataset(tmp_path / "modelling.csv"))
    scores = comparison.scores[NETWORK_NAME]
    assert len(scores.f1_per_class) == CV_N_SPLITS
    for fold in scores.f1_per_class:
        assert len(fold) == N_CLASSES
        assert all(0.0 <= value <= 1.0 for value in fold)


def test_is_reproducible(tmp_path):
    first = compare_network(write_dataset(tmp_path / "modelling.csv"))
    second = compare_network(write_dataset(tmp_path / "modelling.csv"))
    assert first.scores[NETWORK_NAME].f1_macro == second.scores[NETWORK_NAME].f1_macro
    assert first.scores[NETWORK_NAME].accuracy == second.scores[NETWORK_NAME].accuracy
    assert first.best_ensemble == second.best_ensemble


def test_format_renders_the_network_and_the_best_ensemble(tmp_path, capsys):
    comparison = compare_network(write_dataset(tmp_path / "modelling.csv"))
    text = format_network_comparison(comparison, "modelling.csv")
    assert capsys.readouterr().out == ""
    assert "early stopping" in text
    assert NETWORK_NAME in text
    assert comparison.best_ensemble in text
    assert "f1 per class" in text
    assert f"best ensemble: {comparison.best_ensemble}" in text


def test_cli_runs_the_comparison(tmp_path, capsys):
    dataset = write_dataset(tmp_path / "modelling.csv")
    assert main(["--dataset", str(dataset)]) == 0
    output = capsys.readouterr().out
    assert "best ensemble:" in output
    assert NETWORK_NAME in output


def test_rejects_a_missing_dataset(tmp_path):
    with pytest.raises(FileNotFoundError):
        compare_network(tmp_path / "missing.csv")
