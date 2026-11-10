"""Tables for predictions and feedback. The schema is documented in docs/database.md."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import JSON, CheckConstraint, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from kiniela.config import N_CLASSES

# One column per class: probabilities can be filtered and aggregated directly in SQL
PROBABILITY_COLUMNS = tuple(f"prob_{class_id}" for class_id in range(N_CLASSES))


def utc_now() -> datetime:
    return datetime.now(UTC)


class Base(DeclarativeBase):
    pass


class Prediction(Base):
    """One prediction made by the app."""

    __tablename__ = "predictions"
    __table_args__ = (
        CheckConstraint(f"predicted_class BETWEEN 0 AND {N_CLASSES - 1}", name="ck_predicted_class"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, index=True)
    # Links each prediction to the model that made it (A/B testing, monitoring)
    model_version: Mapped[str] = mapped_column(String(64), index=True)
    home_team: Mapped[str] = mapped_column(String(100))
    away_team: Mapped[str] = mapped_column(String(100))
    # Model inputs as JSON: the feature set (issue #3) can evolve without schema changes
    inputs: Mapped[dict[str, Any]] = mapped_column(JSON)
    predicted_class: Mapped[int]
    prob_0: Mapped[float]
    prob_1: Mapped[float]
    prob_2: Mapped[float]
    prob_3: Mapped[float]
    prob_4: Mapped[float]
    prob_5: Mapped[float]

    feedback: Mapped[Feedback | None] = relationship(
        back_populates="prediction", cascade="all, delete-orphan", uselist=False
    )

    @property
    def probabilities(self) -> list[float]:
        """The six probabilities in class order."""
        return [getattr(self, column) for column in PROBABILITY_COLUMNS]


class Feedback(Base):
    """The user's verdict on a prediction. At most one per prediction."""

    __tablename__ = "feedback"
    __table_args__ = (
        CheckConstraint(
            f"actual_class IS NULL OR actual_class BETWEEN 0 AND {N_CLASSES - 1}",
            name="ck_actual_class",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    prediction_id: Mapped[int] = mapped_column(
        ForeignKey("predictions.id", ondelete="CASCADE"), unique=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    is_correct: Mapped[bool]
    # The real class, when the user knows the final result
    actual_class: Mapped[int | None]
    comment: Mapped[str | None] = mapped_column(Text)

    prediction: Mapped[Prediction] = relationship(back_populates="feedback")
