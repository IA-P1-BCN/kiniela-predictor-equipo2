"""Baseline training with StratifiedKFold (issue #5)."""

import joblib
import numpy as np
import pandas as pd
import pytest
from sklearn.model_selection import StratifiedKFold

from kiniela.config import CV_N_SPLITS, N_CLASSES, RANDOM_STATE
from kiniela.models.predict import DEFAULT_MODEL_PATH
from kiniela.models.train import (
    NON_FEATURE_COLUMNS,
    TrainedBaseline,
    feature_columns,
    format_report,
    main,
    stratified_cv,
    train_baseline,
)

FEATURES = ("form_home", "goals_avg", "home_advantage", "goal_diff_form")


def write_dataset(
    path,
    samples_per_class=40,
    with_target=True,
    with_leakage=False,
    missing_feature=None,
):
    """Synthetic modelling dataset: features centred on each class, optional extras."""
    rng = np.random.default_rng(RANDOM_STATE)
    counts = (
        [samples_per_class] * N_CLASSES
        if isinstance(samples_per_class, int)
        else list(samples_per_class)
    )
    parts = [
        pd.DataFrame(
            rng.normal(class_id, 1.0, size=(count, len(FEATURES))), columns=FEATURES
        )
        for class_id, count in enumerate(counts)
    ]
    dataset = pd.concat(parts, ignore_index=True)
    if with_target:
        dataset["target"] = np.repeat(range(N_CLASSES), counts)
    if with_leakage:
        # Post-match columns of the raw CSV: they must never become features.
        dataset["HomeTeam"] = "arsenal"
        dataset["Date"] = "11/08/2023"
        dataset["FTHG"] = 1
        dataset["FTAG"] = 0
        dataset["FTR"] = "H"
        dataset["HTHG"] = 1
        dataset["HTR"] = "H"
        dataset["HS"] = 10
        dataset["AS"] = 8
        dataset["HY"] = 2
    if missing_feature is not None:
        dataset.loc[0, missing_feature] = np.nan
    dataset.to_csv(path, index=False)
    return path


def test_reports_accuracy_and_f1_macro_for_both_models(tmp_path):
    report = train_baseline(
        write_dataset(tmp_path / "modelling.csv"), tmp_path / "baseline_rf.joblib"
    )
    for scores in (report.reference, report.random_forest):
        assert len(scores.accuracy) == CV_N_SPLITS
        assert len(scores.f1_macro) == CV_N_SPLITS
        assert all(0.0 <= value <= 1.0 for value in scores.accuracy + scores.f1_macro)
        assert 0.0 <= scores.accuracy_mean <= 1.0
        assert 0.0 <= scores.f1_macro_mean <= 1.0
    assert report.n_splits == CV_N_SPLITS
    assert report.random_state == RANDOM_STATE
    assert report.n_samples == N_CLASSES * 40
    assert report.feature_columns == FEATURES


def test_reference_is_the_majority_class_baseline(tmp_path):
    report = train_baseline(
        write_dataset(tmp_path / "modelling.csv"), tmp_path / "baseline_rf.joblib"
    )
    # Balanced classes: the majority-class dummy guesses one sixth of the matches.
    assert report.reference.accuracy_mean == pytest.approx(1 / N_CLASSES, abs=0.05)
    assert report.random_forest.f1_macro_mean > report.reference.f1_macro_mean


def test_is_reproducible_with_the_same_seed(tmp_path):
    first = train_baseline(
        write_dataset(tmp_path / "modelling.csv"), tmp_path / "first.joblib"
    )
    second = train_baseline(
        write_dataset(tmp_path / "modelling.csv"), tmp_path / "second.joblib"
    )
    assert first.random_forest.accuracy == second.random_forest.accuracy
    assert first.random_forest.f1_macro == second.random_forest.f1_macro


def test_stratified_cv_is_the_fixed_scheme():
    cv = stratified_cv()
    assert isinstance(cv, StratifiedKFold)
    assert cv.n_splits == CV_N_SPLITS
    assert cv.shuffle is True
    assert cv.random_state == RANDOM_STATE


def test_every_fold_keeps_all_the_classes():
    y = np.repeat(range(N_CLASSES), 40)
    X = np.zeros((len(y), 1))
    for _, test_index in stratified_cv().split(X, y):
        assert set(y[test_index]) == set(range(N_CLASSES))


def test_excludes_identifiers_and_post_match_columns(tmp_path):
    dataset = pd.read_csv(write_dataset(tmp_path / "modelling.csv", with_leakage=True))
    columns = feature_columns(dataset)
    assert columns == list(FEATURES)
    assert not set(columns) & NON_FEATURE_COLUMNS


def test_saves_a_loadable_artefact_with_the_fixed_scheme(tmp_path):
    path = tmp_path / "baseline_rf.joblib"
    train_baseline(write_dataset(tmp_path / "modelling.csv"), path)
    artifact = joblib.load(path)
    assert isinstance(artifact, TrainedBaseline)
    assert artifact.version.startswith("baseline-rf-")
    assert artifact.feature_columns == FEATURES
    assert artifact.report.n_splits == CV_N_SPLITS
    probabilities = artifact.model.predict_proba(np.zeros((1, len(FEATURES))))
    assert probabilities.shape == (1, N_CLASSES)


def test_refuses_to_overwrite_the_app_model(tmp_path):
    with pytest.raises(ValueError, match="Predictor"):
        train_baseline(write_dataset(tmp_path / "modelling.csv"), DEFAULT_MODEL_PATH)


def test_rejects_a_dataset_without_target(tmp_path):
    with pytest.raises(ValueError, match="target"):
        train_baseline(
            write_dataset(tmp_path / "modelling.csv", with_target=False),
            tmp_path / "baseline_rf.joblib",
        )


def test_rejects_a_class_with_fewer_samples_than_folds(tmp_path):
    counts = [40] * (N_CLASSES - 1) + [3]
    with pytest.raises(ValueError, match=f"fewer than {CV_N_SPLITS} samples"):
        train_baseline(
            write_dataset(tmp_path / "modelling.csv", samples_per_class=counts),
            tmp_path / "baseline_rf.joblib",
        )


def test_drops_rows_whose_features_have_no_history(tmp_path):
    # The first matchdays have no history: build_features leaves their features empty.
    report = train_baseline(
        write_dataset(tmp_path / "modelling.csv", missing_feature=FEATURES[0]),
        tmp_path / "baseline_rf.joblib",
    )
    assert report.n_dropped == 1
    assert report.n_samples == N_CLASSES * 40 - 1


def test_rejects_a_dataset_without_features(tmp_path):
    path = tmp_path / "only_target.csv"
    pd.DataFrame({"target": range(N_CLASSES)}).to_csv(path, index=False)
    with pytest.raises(ValueError, match="No numeric feature"):
        train_baseline(path, tmp_path / "baseline_rf.joblib")


def test_rejects_a_missing_dataset(tmp_path):
    with pytest.raises(FileNotFoundError):
        train_baseline(tmp_path / "missing.csv", tmp_path / "baseline_rf.joblib")


def test_cli_trains_again_from_the_command_line(tmp_path, capsys):
    dataset = write_dataset(tmp_path / "modelling.csv")
    exit_code = main(
        ["--dataset", str(dataset), "--model", str(tmp_path / "baseline_rf.joblib")]
    )
    output = capsys.readouterr().out
    assert exit_code == 0
    assert "StratifiedKFold(n_splits=5, shuffle=True, random_state=42)" in output
    assert "reference (majority)" in output
    assert "random_forest" in output
    assert (tmp_path / "baseline_rf.joblib").is_file()


def test_training_stays_silent_and_the_report_is_rendered_as_text(tmp_path, capsys):
    report = train_baseline(
        write_dataset(tmp_path / "modelling.csv"), tmp_path / "baseline_rf.joblib"
    )
    assert capsys.readouterr().out == ""  # printing is the caller's job
    text = format_report(report, "modelling.csv", "baseline_rf.joblib")
    assert capsys.readouterr().out == ""  # formatting does not print either
    assert isinstance(text, str)
    assert "StratifiedKFold(n_splits=5, shuffle=True, random_state=42)" in text
    assert "reference (majority)" in text
    assert "random_forest" in text
    assert "saved: baseline_rf.joblib" in text
