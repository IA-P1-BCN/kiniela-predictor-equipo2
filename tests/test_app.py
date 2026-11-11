"""End-to-end tests of the Streamlit app with Streamlit's AppTest (no browser)."""

from pathlib import Path

import pytest
import streamlit as st
from streamlit.testing.v1 import AppTest

from kiniela.storage import get_engine, init_db, list_history, session_scope

APP = str(Path(__file__).resolve().parents[1] / "app" / "streamlit_app.py")


@pytest.fixture
def database_url(tmp_path, monkeypatch):
    """Each test gets its own SQLite database and fresh Streamlit caches."""
    url = f"sqlite:///{(tmp_path / 'app.db').as_posix()}"
    monkeypatch.setenv("DATABASE_URL", url)
    st.cache_resource.clear()
    st.cache_data.clear()
    yield url
    st.cache_resource.clear()


def start_app() -> AppTest:
    app = AppTest.from_file(APP, default_timeout=30)
    app.run()
    assert not app.exception
    return app


def predict(app: AppTest, home: str | None, away: str | None) -> None:
    app.selectbox(key="home_team").set_value(home)
    app.selectbox(key="away_team").set_value(away)
    app.button[1].click()  # the form's "Predecir" button (0 is the example button)
    app.run()
    assert not app.exception


def saved_predictions(url: str) -> list:
    engine = get_engine(url)
    init_db(engine)  # the app only creates the tables once it touches the database
    with session_scope(engine) as session:
        return list_history(session)


def test_app_starts_and_warns_about_the_test_model(database_url):
    app = start_app()
    assert app.title[0].value == "Kiniela Predictor"
    assert "Modelo de prueba" in app.warning[0].value


@pytest.mark.parametrize(
    ("home", "away", "message"),
    [
        (None, None, "Elige el equipo local y el visitante."),
        ("arsenal", None, "Elige el equipo local y el visitante."),
        ("arsenal", "arsenal", "no pueden ser el mismo"),
    ],
)
def test_invalid_input_shows_a_message_and_saves_nothing(database_url, home, away, message):
    app = start_app()
    predict(app, home, away)
    assert message in app.error[0].value
    assert saved_predictions(database_url) == []


def test_example_match_predicts_shows_six_probabilities_and_saves(database_url):
    app = start_app()
    app.button[0].click().run()  # "Usar un partido de ejemplo"
    assert app.selectbox(key="home_team").value == "arsenal"
    predict(app, "arsenal", "chelsea")

    assert app.metric[0].value.startswith("5 ·")  # class 5 is the most frequent one
    assert len(app.dataframe[0].value) == 6
    [saved] = saved_predictions(database_url)
    assert (saved.home_team, saved.away_team, saved.predicted_class) == ("arsenal", "chelsea", 5)


def test_feedback_is_saved_for_the_prediction(database_url):
    app = start_app()
    predict(app, "arsenal", "chelsea")
    prediction_id = saved_predictions(database_url)[0].id

    app.radio(key=f"verdict_{prediction_id}").set_value("No, falló").run()
    app.selectbox(key=f"actual_{prediction_id}").set_value(2).run()
    app.button(key=f"send_{prediction_id}").click().run()

    assert not app.exception
    assert "Gracias" in app.success[0].value
    feedback = saved_predictions(database_url)[0].feedback
    assert (feedback.is_correct, feedback.actual_class) == (False, 2)


def test_feedback_requires_a_verdict(database_url):
    app = start_app()
    predict(app, "arsenal", "chelsea")
    prediction_id = saved_predictions(database_url)[0].id
    app.button(key=f"send_{prediction_id}").click().run()
    assert "Indica si la predicción" in app.error[0].value
    assert saved_predictions(database_url)[0].feedback is None


def test_history_page_shows_predictions_and_live_accuracy(database_url):
    app = start_app()
    predict(app, "arsenal", "chelsea")
    app.switch_page("views/history.py").run()

    assert not app.exception
    assert app.title[0].value == "Historial"
    assert app.metric[0].value == "1"  # predictions of the current model
    assert app.metric[2].value == "—"  # no feedback yet
    assert len(app.dataframe[0].value) == 1


def test_history_page_without_predictions_explains_what_to_do(database_url):
    app = start_app()
    app.switch_page("views/history.py").run()
    assert "Todavía no hay predicciones" in app.info[0].value
