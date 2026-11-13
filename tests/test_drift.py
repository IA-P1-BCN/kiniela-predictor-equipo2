"""Data-drift detection with PSI (issue #14)."""

import numpy as np
import pandas as pd
import pytest

from kiniela.monitoring.drift import (
    PSI_DRIFT_THRESHOLD,
    compute_drift,
    drift_report,
    format_drift_report,
    main,
    population_stability_index,
)

from test_train import FEATURES, write_dataset


def test_identical_batches_have_no_drift(tmp_path):
    path = write_dataset(tmp_path / "modelling.csv")
    report = compute_drift(path, path)
    assert report.drifted is False
    assert report.threshold == PSI_DRIFT_THRESHOLD
    assert {feature.name for feature in report.features} == set(FEATURES)
    assert all(feature.drifted is False for feature in report.features)
    assert all(feature.psi < PSI_DRIFT_THRESHOLD for feature in report.features)


def test_a_shifted_feature_flags_global_drift(tmp_path):
    reference = write_dataset(tmp_path / "reference.csv")
    frame = pd.read_csv(reference)
    frame["form_home"] = frame["form_home"] + 8.0
    current = tmp_path / "current.csv"
    frame.to_csv(current, index=False)

    report = compute_drift(reference, current)
    by_name = {feature.name: feature for feature in report.features}
    assert by_name["form_home"].drifted is True
    assert by_name["form_home"].psi >= PSI_DRIFT_THRESHOLD
    assert report.drifted is True


def test_psi_is_zero_for_the_same_sample():
    values = np.linspace(0.0, 1.0, 200)
    assert population_stability_index(values, values) == pytest.approx(0.0, abs=1e-12)


def test_drift_report_dict_matches_the_dataclass(tmp_path):
    path = write_dataset(tmp_path / "modelling.csv")
    as_dict = drift_report(str(path), str(path))
    report = compute_drift(path, path)
    assert as_dict["drifted"] is False
    assert as_dict["threshold"] == PSI_DRIFT_THRESHOLD
    assert len(as_dict["features"]) == len(report.features)
    assert {item["name"] for item in as_dict["features"]} == set(FEATURES)


def test_format_mentions_the_threshold_and_the_flag(tmp_path, capsys):
    path = write_dataset(tmp_path / "modelling.csv")
    report = compute_drift(path, path)
    text = format_drift_report(report, "reference.csv", "current.csv")
    assert capsys.readouterr().out == ""
    assert "PSI" in text
    assert f"{PSI_DRIFT_THRESHOLD:.2f}" in text
    assert "global drift: NO" in text
    assert "form_home" in text


def test_cli_returns_zero_when_there_is_no_drift(tmp_path, capsys):
    path = write_dataset(tmp_path / "modelling.csv")
    assert main(["--reference", str(path), "--current", str(path)]) == 0
    output = capsys.readouterr().out
    assert "global drift: NO" in output


def test_cli_returns_one_when_there_is_drift(tmp_path, capsys):
    reference = write_dataset(tmp_path / "reference.csv")
    frame = pd.read_csv(reference)
    frame["goals_avg"] = frame["goals_avg"] + 10.0
    current = tmp_path / "current.csv"
    frame.to_csv(current, index=False)
    assert main(["--reference", str(reference), "--current", str(current)]) == 1
    assert "global drift: YES" in capsys.readouterr().out


def test_rejects_a_missing_file(tmp_path):
    path = write_dataset(tmp_path / "modelling.csv")
    with pytest.raises(FileNotFoundError):
        compute_drift(path, tmp_path / "missing.csv")
