"""Read and write predictions and feedback.

Functions receive an open session and never commit: the caller decides the transaction,
normally with ``session_scope``.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from kiniela.config import N_CLASSES
from kiniela.models.predict import predicted_class
from kiniela.storage.models import PROBABILITY_COLUMNS, Feedback, Prediction

MAX_COMMENT_LENGTH = 1000


def save_prediction(
    session: Session,
    *,
    home_team: str,
    away_team: str,
    inputs: Mapping[str, Any],
    probabilities: Sequence[float],
    model_version: str,
) -> Prediction:
    """Store a prediction. The predicted class is derived from the probabilities.

    Raises ``ValueError`` if the teams are empty or equal, or if the probabilities are
    not a valid distribution over the six classes.
    """
    home, away = home_team.strip(), away_team.strip()
    if not home or not away:
        raise ValueError("Both teams are required.")
    if home.casefold() == away.casefold():
        raise ValueError("A team cannot play against itself.")
    # Same validation as the app: six non-negative values that add up to ~1
    class_id = predicted_class(list(probabilities))

    prediction = Prediction(
        home_team=home,
        away_team=away,
        inputs=dict(inputs),
        model_version=model_version,
        predicted_class=class_id,
        **{column: float(p) for column, p in zip(PROBABILITY_COLUMNS, probabilities, strict=True)},
    )
    session.add(prediction)
    session.flush()  # assigns the id, so the app can attach feedback to it
    return prediction


def save_feedback(
    session: Session,
    prediction_id: int,
    *,
    is_correct: bool,
    actual_class: int | None = None,
    comment: str | None = None,
) -> Feedback:
    """Store the user's verdict on a prediction.

    Raises ``ValueError`` if the prediction does not exist, already has feedback, the
    actual class is out of range, or it contradicts ``is_correct``.
    """
    prediction = session.get(Prediction, prediction_id)
    if prediction is None:
        raise ValueError(f"Prediction {prediction_id} does not exist.")
    if prediction.feedback is not None:
        raise ValueError(f"Prediction {prediction_id} already has feedback.")
    if actual_class is not None:
        if not 0 <= actual_class < N_CLASSES:
            raise ValueError(f"The actual class must be between 0 and {N_CLASSES - 1}.")
        if (actual_class == prediction.predicted_class) != is_correct:
            raise ValueError("The actual class contradicts whether the prediction was correct.")

    feedback = Feedback(
        prediction=prediction,
        is_correct=is_correct,
        actual_class=actual_class,
        comment=(comment or "").strip()[:MAX_COMMENT_LENGTH] or None,
    )
    session.add(feedback)
    session.flush()
    return feedback


def list_history(session: Session, limit: int = 50) -> list[Prediction]:
    """The most recent predictions first, with their feedback already loaded."""
    query = (
        select(Prediction)
        .options(selectinload(Prediction.feedback))
        .order_by(Prediction.created_at.desc(), Prediction.id.desc())
        .limit(limit)
    )
    return list(session.scalars(query))


def feedback_stats(session: Session, model_version: str | None = None) -> dict[str, Any]:
    """Live metrics from user feedback, optionally for a single model version.

    ``accuracy`` is the share of correct predictions among those with feedback, or
    ``None`` while there is no feedback yet.
    """
    predictions = select(func.count(Prediction.id))
    reviewed = select(func.count(Feedback.id)).join(Feedback.prediction)
    correct = reviewed.where(Feedback.is_correct.is_(True))
    if model_version is not None:
        predictions = predictions.where(Prediction.model_version == model_version)
        reviewed = reviewed.where(Prediction.model_version == model_version)
        correct = correct.where(Prediction.model_version == model_version)

    total_reviewed = session.scalar(reviewed) or 0
    total_correct = session.scalar(correct) or 0
    return {
        "predictions": session.scalar(predictions) or 0,
        "with_feedback": total_reviewed,
        "correct": total_correct,
        "accuracy": total_correct / total_reviewed if total_reviewed else None,
    }
