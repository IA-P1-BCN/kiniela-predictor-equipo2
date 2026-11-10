import pytest
from sqlalchemy import inspect

from kiniela.config import N_CLASSES
from kiniela.storage import (
    feedback_stats,
    get_engine,
    init_db,
    list_history,
    resolve_database_url,
    save_feedback,
    save_prediction,
    session_scope,
)
from kiniela.storage.models import PROBABILITY_COLUMNS

PROBABILITIES = [0.1, 0.5, 0.1, 0.1, 0.1, 0.1]  # class 1 is the most likely


@pytest.fixture
def engine(tmp_path):
    """A fresh SQLite database per test."""
    engine = get_engine(f"sqlite:///{(tmp_path / 'test.db').as_posix()}")
    init_db(engine)
    yield engine
    engine.dispose()


def _predict(engine, model_version="v1", probabilities=PROBABILITIES):
    with session_scope(engine) as session:
        prediction = save_prediction(
            session,
            home_team="Arsenal",
            away_team="Chelsea",
            inputs={"home_form": 2.1, "away_form": 1.4},
            probabilities=probabilities,
            model_version=model_version,
        )
        return prediction.id


# --- Connection -------------------------------------------------------------


def test_defaults_to_local_sqlite(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    assert resolve_database_url().startswith("sqlite:///")
    assert resolve_database_url().endswith("data/kiniela.db")


def test_reads_database_url_from_environment(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite:///other.db")
    assert resolve_database_url() == "sqlite:///other.db"


@pytest.mark.parametrize("scheme", ["postgres://", "postgresql://"])
def test_uses_psycopg_driver_for_postgres_urls(scheme):
    url = resolve_database_url(f"{scheme}user:secret@host/db?sslmode=require")
    assert url == "postgresql+psycopg://user:secret@host/db?sslmode=require"


def test_creates_both_tables(engine):
    assert set(inspect(engine).get_table_names()) == {"predictions", "feedback"}


def test_has_one_probability_column_per_class():
    assert len(PROBABILITY_COLUMNS) == N_CLASSES


# --- Predictions ------------------------------------------------------------


def test_saves_prediction_with_inputs_class_and_probabilities(engine):
    prediction_id = _predict(engine)
    with session_scope(engine) as session:
        [saved] = list_history(session)
        assert saved.id == prediction_id
        assert saved.created_at is not None
        assert saved.inputs == {"home_form": 2.1, "away_form": 1.4}
        assert saved.predicted_class == 1
        assert saved.probabilities == PROBABILITIES
        assert saved.model_version == "v1"


@pytest.mark.parametrize(
    "probabilities",
    [
        [0.5, 0.5],  # not six classes
        [0.9, 0.9, 0.0, 0.0, 0.0, 0.0],  # does not add up to 1
        [1.2, -0.2, 0.0, 0.0, 0.0, 0.0],  # negative value
    ],
)
def test_rejects_invalid_probabilities(engine, probabilities):
    with pytest.raises(ValueError):
        _predict(engine, probabilities=probabilities)


@pytest.mark.parametrize(("home", "away"), [("", "Chelsea"), ("Arsenal", "  "), ("Arsenal", "arsenal")])
def test_rejects_invalid_teams(engine, home, away):
    with pytest.raises(ValueError), session_scope(engine) as session:
        save_prediction(session, home_team=home, away_team=away, inputs={},
                        probabilities=PROBABILITIES, model_version="v1")


def test_failed_save_leaves_nothing_behind(engine):
    with pytest.raises(ValueError):
        _predict(engine, probabilities=[0.5, 0.5])
    with session_scope(engine) as session:
        assert list_history(session) == []


def test_history_is_newest_first_and_limited(engine):
    ids = [_predict(engine) for _ in range(3)]
    with session_scope(engine) as session:
        assert [p.id for p in list_history(session)] == ids[::-1]
        assert len(list_history(session, limit=2)) == 2


# --- Feedback ---------------------------------------------------------------


def test_saves_feedback_linked_to_prediction(engine):
    prediction_id = _predict(engine)
    with session_scope(engine) as session:
        save_feedback(session, prediction_id, is_correct=False, actual_class=2, comment="  Draw  ")
    with session_scope(engine) as session:
        [saved] = list_history(session)
        assert saved.feedback.is_correct is False
        assert saved.feedback.actual_class == 2
        assert saved.feedback.comment == "Draw"


def test_rejects_feedback_for_unknown_prediction(engine):
    with pytest.raises(ValueError, match="does not exist"), session_scope(engine) as session:
        save_feedback(session, 999, is_correct=True)


def test_rejects_second_feedback_for_same_prediction(engine):
    prediction_id = _predict(engine)
    with session_scope(engine) as session:
        save_feedback(session, prediction_id, is_correct=True)
    with pytest.raises(ValueError, match="already has feedback"), session_scope(engine) as session:
        save_feedback(session, prediction_id, is_correct=True)


@pytest.mark.parametrize(
    ("is_correct", "actual_class"),
    [
        (True, 3),  # says correct, but the predicted class was 1
        (False, 1),  # says wrong, but 1 is the predicted class
        (False, 6),  # out of range
    ],
)
def test_rejects_inconsistent_feedback(engine, is_correct, actual_class):
    prediction_id = _predict(engine)
    with pytest.raises(ValueError), session_scope(engine) as session:
        save_feedback(session, prediction_id, is_correct=is_correct, actual_class=actual_class)


def test_deleting_a_prediction_deletes_its_feedback(engine):
    prediction_id = _predict(engine)
    with session_scope(engine) as session:
        save_feedback(session, prediction_id, is_correct=True)
    with session_scope(engine) as session:
        session.delete(list_history(session)[0])
    assert feedback_stats_for(engine)["with_feedback"] == 0


# --- Live metrics -----------------------------------------------------------


def feedback_stats_for(engine, model_version=None):
    with session_scope(engine) as session:
        return feedback_stats(session, model_version)


def test_stats_without_feedback_have_no_accuracy(engine):
    _predict(engine)
    assert feedback_stats_for(engine) == {
        "predictions": 1, "with_feedback": 0, "correct": 0, "accuracy": None,
    }


def test_stats_compute_accuracy_per_model_version(engine):
    for model_version, verdicts in {"v1": [True, True, False], "v2": [False]}.items():
        for is_correct in verdicts:
            prediction_id = _predict(engine, model_version=model_version)
            with session_scope(engine) as session:
                save_feedback(session, prediction_id, is_correct=is_correct)

    assert feedback_stats_for(engine)["accuracy"] == pytest.approx(2 / 4)
    v1 = feedback_stats_for(engine, "v1")
    assert (v1["predictions"], v1["correct"], v1["accuracy"]) == (3, 2, pytest.approx(2 / 3))
    assert feedback_stats_for(engine, "v2")["accuracy"] == 0.0
