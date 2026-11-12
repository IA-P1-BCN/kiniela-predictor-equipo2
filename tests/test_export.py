from datetime import date, datetime, timezone

import pandas as pd
import pytest

from kiniela.storage import get_engine, init_db, save_feedback, save_prediction, session_scope
from kiniela.storage.export import (
    EXPORT_COLUMNS,
    export_labelled_feedback,
    labelled_feedback,
    main,
)
PROBABILITIES = [0.1, 0.5, 0.1, 0.1, 0.1, 0.1]  # predicted class 1


@pytest.fixture
def database_url(tmp_path):
    url = f"sqlite:///{(tmp_path / 'export.db').as_posix()}"
    init_db(get_engine(url))
    return url


def add_prediction(url, home="arsenal", away="chelsea", version="v1", feedback=None, created_at=None):
    """Save a prediction and, optionally, its feedback as (is_correct, actual_class)."""
    with session_scope(get_engine(url)) as session:
        prediction = save_prediction(session, home_team=home, away_team=away, inputs={},
                                     probabilities=PROBABILITIES, model_version=version)
        if created_at is not None:
            prediction.created_at = created_at
        prediction_id = prediction.id
    if feedback is not None:
        is_correct, actual_class = feedback
        with session_scope(get_engine(url)) as session:
            save_feedback(session, prediction_id, is_correct=is_correct, actual_class=actual_class)
    return prediction_id


def labelled(url, **filters) -> pd.DataFrame:
    with session_scope(get_engine(url)) as session:
        return labelled_feedback(session, **filters)


def test_exports_only_feedback_with_the_real_class(database_url):
    labelled_id = add_prediction(database_url, feedback=(False, 4))
    add_prediction(database_url, feedback=(False, None))  # wrong, real class unknown: no label
    add_prediction(database_url)  # no feedback at all

    rows = labelled(database_url)
    assert list(rows.columns) == EXPORT_COLUMNS
    assert rows["prediction_id"].tolist() == [labelled_id]
    row = rows.iloc[0]
    assert (row["HomeTeam"], row["AwayTeam"], row["target"]) == ("arsenal", "chelsea", 4)
    assert (row["predicted_class"], bool(row["is_correct"]), row["model_version"]) == (1, False, "v1")


def test_correct_predictions_are_labelled_with_the_predicted_class(database_url):
    add_prediction(database_url, feedback=(True, 1))
    assert labelled(database_url)["target"].tolist() == [1]


def test_filters_by_model_version_and_date(database_url):
    old = datetime(2026, 10, 1, 12, tzinfo=timezone.utc)
    add_prediction(database_url, version="v1", feedback=(True, 1), created_at=old)
    recent_v1 = add_prediction(database_url, version="v1", feedback=(True, 1))
    recent_v2 = add_prediction(database_url, version="v2", feedback=(False, 2))

    assert labelled(database_url, model_version="v2")["prediction_id"].tolist() == [recent_v2]
    since = labelled(database_url, since=date(2026, 11, 1))["prediction_id"].tolist()
    assert since == [recent_v1, recent_v2]


def test_rows_are_ordered_oldest_first(database_url):
    first = add_prediction(database_url, feedback=(True, 1), created_at=datetime(2026, 9, 1, tzinfo=timezone.utc))
    second = add_prediction(database_url, feedback=(True, 1), created_at=datetime(2026, 10, 1, tzinfo=timezone.utc))
    assert labelled(database_url)["prediction_id"].tolist() == [first, second]


def test_export_appends_without_duplicates(database_url, tmp_path):
    output = tmp_path / "out" / "labelled.csv"
    add_prediction(database_url, feedback=(True, 1))

    assert export_labelled_feedback(output, database_url=database_url) == 1
    assert export_labelled_feedback(output, database_url=database_url) == 0  # nothing new

    add_prediction(database_url, home="everton", away="fulham", feedback=(False, 5))
    assert export_labelled_feedback(output, database_url=database_url) == 1

    exported = pd.read_csv(output)
    assert exported["prediction_id"].is_unique
    assert exported["HomeTeam"].tolist() == ["arsenal", "everton"]
    assert list(exported.columns) == EXPORT_COLUMNS


def test_export_without_labelled_feedback_writes_nothing(database_url, tmp_path):
    output = tmp_path / "labelled.csv"
    add_prediction(database_url)
    assert export_labelled_feedback(output, database_url=database_url) == 0
    assert not output.exists()


def test_command_line_reads_database_url_and_reports(database_url, tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("DATABASE_URL", database_url)
    add_prediction(database_url, feedback=(True, 1))
    output = tmp_path / "labelled.csv"

    main(["--output", str(output), "--since", "2000-01-01"])

    assert "1 new labelled matches exported" in capsys.readouterr().out
    assert len(pd.read_csv(output)) == 1


def test_exported_target_uses_the_training_column_name():
    from kiniela.models.train import TARGET_COLUMN

    assert TARGET_COLUMN in EXPORT_COLUMNS
