"""Tests for the issue #8 metrics report."""

from __future__ import annotations

import json
from types import SimpleNamespace

import numpy as np
import pandas as pd

from kiniela.config import CLASS_NAMES
from kiniela.models import report


def _report() -> report.MetricsReport:
    scores = SimpleNamespace(
        accuracy=0.4,
        precision=(0.1, 0.2, 0.3, 0.4, 0.5, 0.6),
        recall=(0.6, 0.5, 0.4, 0.3, 0.2, 0.1),
        f1=(0.2, 0.3, 0.4, 0.5, 0.4, 0.3),
    )
    matrix = np.zeros((6, 6), dtype=int)
    matrix[0, 1] = 7
    matrix[1, 0] = 3
    return report.MetricsReport(
        version="test-model",
        n_samples=10,
        n_history=12,
        n_dropped=2,
        card_f1_macro=0.35,
        support=(2, 2, 2, 2, 1, 1),
        scores=scores,  # type: ignore[arg-type]
        matrix=tuple(tuple(int(value) for value in row) for row in matrix),
        importance=(("match_diff", 0.5), ("form_home_last_5", 0.25)),
        confusions=(report.Confusion(0, 1, 7, 0.7),),
        examples=(
            report.Example("2023-01-01", "home", "away", 2, 2, 0, 1),
        ),
        feature_columns=("match_diff", "form_home_last_5"),
    )


def test_top_confusions_orders_by_count_and_keeps_the_share() -> None:
    matrix = np.array([[5, 4, 1], [3, 6, 0], [0, 2, 8]])
    confusions = report._top_confusions(matrix)
    assert [(item.true_class, item.predicted_class, item.count) for item in confusions[:2]] == [
        (0, 1, 4),
        (1, 0, 3),
    ]
    assert all(0.0 <= item.share_of_true_class <= 1.0 for item in confusions)


def test_format_report_has_every_required_section_and_spanish_numbers() -> None:
    text = report.format_report(_report())
    assert "**Accuracy global: 0,4000**" in text
    assert "## Accuracy y métricas por clase" in text
    assert "## Matriz de confusión" in text
    assert "## Clases más confundidas y ejemplos" in text
    assert "## Feature importance" in text
    for name in CLASS_NAMES.values():
        assert name in text
    assert "0,400" in text  # Spanish decimal separator, not 0.400
    assert "pendiente" not in text.lower()


def test_build_report_scores_every_class_on_a_synthetic_dataset(tmp_path, monkeypatch) -> None:
    rng = np.random.default_rng(42)
    dataset = pd.DataFrame(
        {
            "Date": ["2023-01-01"] * 60,
            "HomeTeam": ["home"] * 60,
            "AwayTeam": ["away"] * 60,
            "FTHG": [1] * 60,
            "FTAG": [1] * 60,
            "match_diff": rng.normal(size=60),
            "form_home_last_5": rng.normal(size=60),
            "target": [index % 6 for index in range(60)],
        }
    )
    predictor = SimpleNamespace(
        feature_columns=("match_diff", "form_home_last_5"), history=pd.DataFrame()
    )
    card_file = tmp_path / "model_card.json"
    card_file.write_text(
        json.dumps(
            {
                "version": "synthetic",
                "params": {"n_estimators": 2, "max_depth": 1},
                "metrics": {"f1_macro": 0.3},
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(report.joblib, "load", lambda path: predictor)
    monkeypatch.setattr(report, "build_modelling_dataset", lambda history: dataset)

    result = report.build_report(tmp_path / "model.joblib", card_file)

    assert result.version == "synthetic"
    assert result.n_samples == 60
    assert result.n_dropped == 0
    assert len(result.matrix) == 6
    assert sum(sum(row) for row in result.matrix) == 60
    assert len(result.scores.f1) == 6
    assert len(result.importance) == 2
    assert 0.0 <= result.scores.accuracy <= 1.0
