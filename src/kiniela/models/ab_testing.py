"""A/B testing of two model versions and the rule that decides a promotion (issue #37).

- The **current** model is ``models/kiniela_model.joblib`` (or the reference model).
- An optional **candidate** is ``models/candidate_model.joblib``. When it exists and
  ``AB_CANDIDATE_SHARE`` is above 0, that share of the predictions goes to it.
- Each prediction stores its ``model_version``, so the user feedback measures each
  version separately. ``should_promote`` compares both versions with that feedback and
  with the validation metrics of their ``model_card.json``.

The thresholds of the rule are below, in one place. See ``docs/ab-testing.md``.
"""

from __future__ import annotations

import json
import os
import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import joblib
from sqlalchemy.orm import Session

from kiniela.models.predict import DEFAULT_MODEL_PATH, Predictor
from kiniela.storage.repository import feedback_stats

MODELS_DIR = DEFAULT_MODEL_PATH.parent
CURRENT_CARD_NAME = "model_card.json"
CANDIDATE_MODEL_NAME = "candidate_model.joblib"
CANDIDATE_CARD_NAME = "candidate_model_card.json"
CANDIDATE_SHARE_ENV = "AB_CANDIDATE_SHARE"

# Promotion rule (agreed metric: F1 macro, the one declared for the project)
MIN_F1_IMPROVEMENT = 0.01  # the candidate must beat the current F1 macro by this much
MAX_OVERFITTING_GAP = 0.05  # project rule: train/validation gap below 0.05
MIN_FEEDBACK = 30  # predictions with feedback needed per version before deciding


def candidate_share(value: str | None = None) -> float:
    """Share of predictions for the candidate, read from ``AB_CANDIDATE_SHARE`` (0 to 1).

    Empty or missing means 0 (no A/B test). Raises ``ValueError`` for anything else.
    """
    raw = os.environ.get(CANDIDATE_SHARE_ENV, "") if value is None else value
    if not raw.strip():
        return 0.0
    try:
        share = float(raw)
    except ValueError:
        raise ValueError(f"{CANDIDATE_SHARE_ENV} must be a number between 0 and 1.") from None
    if not 0 <= share <= 1:
        raise ValueError(f"{CANDIDATE_SHARE_ENV} must be a number between 0 and 1.")
    return share


def load_candidate(path: str | Path = MODELS_DIR / CANDIDATE_MODEL_NAME) -> Predictor | None:
    """The candidate model, or ``None`` when there is none.

    Raises ``TypeError`` if the file exists but does not follow the ``Predictor`` contract.
    """
    path = Path(path)
    if not path.is_file():
        return None
    model = joblib.load(path)
    if not isinstance(model, Predictor):
        raise TypeError(
            f"{path.name} must have a 'version' and a 'predict(home_team, away_team)' method."
        )
    return model


def load_model_card(path: str | Path) -> dict[str, Any] | None:
    """The model card as a dict, or ``None`` when the file does not exist."""
    path = Path(path)
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


@dataclass
class ABRouter:
    """Chooses which model answers each prediction.

    Each prediction goes to the candidate with probability ``share``; the rest go to the
    current model. Without a candidate, or with ``share`` 0, it is always the current one.
    """

    current: Predictor
    candidate: Predictor | None = None
    share: float = 0.0
    rng: random.Random = field(default_factory=random.Random)

    def __post_init__(self) -> None:
        if not 0 <= self.share <= 1:
            raise ValueError("The candidate share must be between 0 and 1.")
        if self.candidate is not None and self.candidate.version == self.current.version:
            raise ValueError("The candidate needs a version different from the current model.")

    @property
    def is_active(self) -> bool:
        """True when some predictions go to the candidate."""
        return self.candidate is not None and self.share > 0

    def choose(self) -> Predictor:
        if self.is_active and self.rng.random() < self.share:
            return self.candidate
        return self.current


@dataclass(frozen=True)
class VersionEvidence:
    """What is known about one model version: validation metrics and live feedback."""

    version: str
    f1_macro: float | None  # validation F1 macro from the model card
    overfitting_gap: float | None  # train minus validation, from the model card
    predictions: int
    with_feedback: int
    accuracy: float | None  # share of correct predictions according to the feedback


def version_evidence(session: Session, version: str, card: dict[str, Any] | None) -> VersionEvidence:
    """Join the model card metrics with the feedback stored for ``version``."""
    metrics = (card or {}).get("metrics", {})
    stats = feedback_stats(session, model_version=version)
    return VersionEvidence(
        version=version,
        f1_macro=metrics.get("f1_macro"),
        overfitting_gap=metrics.get("overfitting_gap"),
        predictions=stats["predictions"],
        with_feedback=stats["with_feedback"],
        accuracy=stats["accuracy"],
    )


@dataclass(frozen=True)
class Decision:
    promote: bool
    reasons: tuple[str, ...]


def should_promote(current: VersionEvidence, candidate: VersionEvidence) -> Decision:
    """Apply the promotion rule. Every failed condition is listed in ``reasons``.

    The candidate is promoted only if all of these hold:

    1. Its model card has F1 macro and an overfitting gap below ``MAX_OVERFITTING_GAP``.
    2. Its F1 macro beats the current one by at least ``MIN_F1_IMPROVEMENT``. When the
       current model has no card (the reference model), this check is skipped.
    3. Both versions have at least ``MIN_FEEDBACK`` predictions with feedback.
    4. Its accuracy according to the feedback is not lower than the current one.
    """
    failures: list[str] = []
    notes: list[str] = []

    if candidate.f1_macro is None or candidate.overfitting_gap is None:
        failures.append("The candidate model card needs 'f1_macro' and 'overfitting_gap'.")
    else:
        if candidate.overfitting_gap >= MAX_OVERFITTING_GAP:
            failures.append(
                f"Candidate overfitting gap {candidate.overfitting_gap:.3f} is not below "
                f"{MAX_OVERFITTING_GAP}."
            )
        if current.f1_macro is None:
            notes.append("The current model has no validation F1 macro: only feedback is compared.")
        elif candidate.f1_macro < current.f1_macro + MIN_F1_IMPROVEMENT:
            failures.append(
                f"Candidate F1 macro {candidate.f1_macro:.3f} does not beat the current "
                f"{current.f1_macro:.3f} by {MIN_F1_IMPROVEMENT}."
            )

    for evidence in (current, candidate):
        if evidence.with_feedback < MIN_FEEDBACK:
            failures.append(
                f"'{evidence.version}' has {evidence.with_feedback} predictions with feedback; "
                f"{MIN_FEEDBACK} are needed."
            )
    accuracies_known = candidate.accuracy is not None and current.accuracy is not None
    if accuracies_known and candidate.accuracy < current.accuracy:
        failures.append(
            f"Candidate feedback accuracy {candidate.accuracy:.0%} is below the current "
            f"{current.accuracy:.0%}."
        )

    if failures:
        return Decision(promote=False, reasons=tuple(failures + notes))
    return Decision(promote=True, reasons=("The candidate meets every condition.", *notes))
