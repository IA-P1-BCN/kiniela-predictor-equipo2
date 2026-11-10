"""Storage of predictions and user feedback (issue #11).

Typical use from the app::

    from kiniela.storage import get_engine, init_db, session_scope, save_prediction

    engine = get_engine()
    init_db(engine)
    with session_scope(engine) as session:
        prediction = save_prediction(session, home_team="Arsenal", away_team="Chelsea",
                                     inputs={...}, probabilities=[...], model_version="v1")
"""

from kiniela.storage.database import get_engine, init_db, resolve_database_url, session_scope
from kiniela.storage.models import Feedback, Prediction
from kiniela.storage.repository import (
    feedback_stats,
    list_history,
    save_feedback,
    save_prediction,
)

__all__ = [
    "Feedback",
    "Prediction",
    "feedback_stats",
    "get_engine",
    "init_db",
    "list_history",
    "resolve_database_url",
    "save_feedback",
    "save_prediction",
    "session_scope",
]
