"""Schema, nulls, ranges and target checks for a labelled match table (issue #15)."""

from __future__ import annotations

import pandas as pd

from kiniela.config import N_CLASSES

REQUIRED_COLUMNS = ("HomeTeam", "AwayTeam", "FTHG", "FTAG")
OPTIONAL_TARGET = "target"


def validate_matches(matches: pd.DataFrame, *, require_target: bool = False) -> None:
    """Raise ``ValueError`` if the table cannot be used for labelling or training.

    Checks, in order: required columns, empty table, nulls in critical columns,
    non-negative integer goals, distinct teams, and ``target`` in ``0 .. N_CLASSES-1``
    when the column is present or required.
    """
    missing = [column for column in REQUIRED_COLUMNS if column not in matches.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}.")
    if matches.empty:
        raise ValueError("The match table is empty.")

    critical = list(REQUIRED_COLUMNS)
    if require_target or OPTIONAL_TARGET in matches.columns:
        if OPTIONAL_TARGET not in matches.columns:
            raise ValueError(f"Missing required column: '{OPTIONAL_TARGET}'.")
        critical.append(OPTIONAL_TARGET)

    nulls = {column: int(matches[column].isna().sum()) for column in critical}
    dirty = {column: count for column, count in nulls.items() if count}
    if dirty:
        raise ValueError(f"Nulls in critical columns: {dirty}.")

    for column in ("FTHG", "FTAG"):
        goals = pd.to_numeric(matches[column], errors="coerce")
        if goals.isna().any():
            raise ValueError(f"Column '{column}' must be numeric.")
        if (goals < 0).any():
            raise ValueError(f"Column '{column}' cannot be negative.")
        if not goals.eq(goals.astype(int)).all():
            raise ValueError(f"Column '{column}' must be whole goals.")

    same_team = matches["HomeTeam"].astype(str).str.casefold() == matches["AwayTeam"].astype(
        str
    ).str.casefold()
    if same_team.any():
        raise ValueError("A team cannot play against itself.")

    if OPTIONAL_TARGET in matches.columns:
        target = pd.to_numeric(matches[OPTIONAL_TARGET], errors="coerce")
        if target.isna().any():
            raise ValueError(f"Column '{OPTIONAL_TARGET}' must be numeric.")
        if not target.isin(range(N_CLASSES)).all():
            raise ValueError(
                f"Column '{OPTIONAL_TARGET}' values must be between 0 and {N_CLASSES - 1}."
            )
