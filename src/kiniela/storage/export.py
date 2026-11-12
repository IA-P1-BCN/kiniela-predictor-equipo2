"""Export labelled feedback for future retraining (issue #36).

Every prediction whose feedback includes the real class becomes a labelled match: the
teams, the date, the real class (``target``) and where it came from (prediction id,
model version, predicted class). The columns follow the historical dataset
(``HomeTeam``, ``AwayTeam``, ``Date``) so the rows can be appended to it and go through
the same feature engineering before training.

The export is incremental: rows whose ``prediction_id`` is already in the output file
are skipped, so running it every day never duplicates a match.

Usage (reads ``DATABASE_URL``; without it, the local SQLite database)::

    python -m kiniela.storage.export
    python -m kiniela.storage.export --since 2026-11-01 --model-version v1
"""

from __future__ import annotations

import argparse
from datetime import UTC, date, datetime, time
from pathlib import Path

import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import Session

from kiniela.models.train import TARGET_COLUMN
from kiniela.storage.database import PROJECT_ROOT, get_engine, init_db, session_scope
from kiniela.storage.models import Feedback, Prediction

# data/raw is not versioned: exported feedback never ends up in git
DEFAULT_OUTPUT = PROJECT_ROOT / "data" / "raw" / "feedback" / "labelled_matches.csv"

EXPORT_COLUMNS = [
    "prediction_id",
    "Date",
    "HomeTeam",
    "AwayTeam",
    TARGET_COLUMN,
    "predicted_class",
    "is_correct",
    "model_version",
    "feedback_at",
]


def labelled_feedback(
    session: Session,
    since: date | None = None,
    model_version: str | None = None,
) -> pd.DataFrame:
    """Predictions whose feedback has the real class, oldest first.

    Feedback without ``actual_class`` is left out: without the real class there is no
    label to learn from.
    """
    query = (
        select(Prediction, Feedback)
        .join(Feedback, Feedback.prediction_id == Prediction.id)
        .where(Feedback.actual_class.is_not(None))
        .order_by(Prediction.created_at, Prediction.id)
    )
    if since is not None:
        # Predictions are stored in UTC, so the day starts at 00:00 UTC
        query = query.where(Prediction.created_at >= datetime.combine(since, time.min, tzinfo=UTC))
    if model_version is not None:
        query = query.where(Prediction.model_version == model_version)

    rows = [
        {
            "prediction_id": prediction.id,
            "Date": prediction.created_at.date().isoformat(),
            "HomeTeam": prediction.home_team,
            "AwayTeam": prediction.away_team,
            TARGET_COLUMN: feedback.actual_class,
            "predicted_class": prediction.predicted_class,
            "is_correct": feedback.is_correct,
            "model_version": prediction.model_version,
            "feedback_at": feedback.created_at.isoformat(),
        }
        for prediction, feedback in session.execute(query)
    ]
    return pd.DataFrame(rows, columns=EXPORT_COLUMNS)


def append_new_rows(new_rows: pd.DataFrame, output: Path) -> int:
    """Append the rows not yet in ``output`` (matched by ``prediction_id``). Returns how many."""
    if output.is_file():
        already_exported = set(pd.read_csv(output, usecols=["prediction_id"])["prediction_id"])
        new_rows = new_rows[~new_rows["prediction_id"].isin(already_exported)]
    if new_rows.empty:
        return 0
    output.parent.mkdir(parents=True, exist_ok=True)
    new_rows.to_csv(output, mode="a", header=not output.is_file(), index=False)
    return len(new_rows)


def export_labelled_feedback(
    output: Path = DEFAULT_OUTPUT,
    since: date | None = None,
    model_version: str | None = None,
    database_url: str | None = None,
) -> int:
    """Export the new labelled matches from the database to ``output``. Returns how many."""
    engine = get_engine(database_url)
    init_db(engine)
    with session_scope(engine) as session:
        rows = labelled_feedback(session, since=since, model_version=model_version)
    return append_new_rows(rows, output)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT,
                        help=f"CSV file to append to (default: {DEFAULT_OUTPUT.relative_to(PROJECT_ROOT)})")
    parser.add_argument("--since", type=date.fromisoformat,
                        help="only predictions made on or after this date (YYYY-MM-DD)")
    parser.add_argument("--model-version", help="only predictions made by this model version")
    args = parser.parse_args(argv)

    added = export_labelled_feedback(args.output, since=args.since, model_version=args.model_version)
    print(f"{added} new labelled matches exported to {args.output}")


if __name__ == "__main__":
    main()
