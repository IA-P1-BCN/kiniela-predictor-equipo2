"""Match-table validation: schema, nulls, ranges and target (issue #15)."""

import pandas as pd
import pytest

from kiniela.data.validate import validate_matches


def labelled_row(**overrides):
    row = {
        "HomeTeam": "arsenal",
        "AwayTeam": "chelsea",
        "FTHG": 1,
        "FTAG": 0,
        "target": 1,
    }
    row.update(overrides)
    return row


def test_accepts_a_clean_labelled_table():
    validate_matches(pd.DataFrame([labelled_row()]), require_target=True)


def test_rejects_missing_required_columns():
    with pytest.raises(ValueError, match="Missing required columns"):
        validate_matches(pd.DataFrame([{"HomeTeam": "arsenal"}]))


def test_rejects_an_empty_table():
    with pytest.raises(ValueError, match="empty"):
        validate_matches(
            pd.DataFrame(columns=["HomeTeam", "AwayTeam", "FTHG", "FTAG"])
        )


def test_rejects_nulls_in_critical_columns():
    frame = pd.DataFrame([labelled_row(FTHG=None)])
    with pytest.raises(ValueError, match="Nulls"):
        validate_matches(frame)


def test_rejects_negative_or_fractional_goals():
    with pytest.raises(ValueError, match="negative"):
        validate_matches(pd.DataFrame([labelled_row(FTAG=-1)]))
    with pytest.raises(ValueError, match="whole goals"):
        validate_matches(pd.DataFrame([labelled_row(FTHG=1.5)]))


def test_rejects_a_team_playing_itself():
    with pytest.raises(ValueError, match="against itself"):
        validate_matches(pd.DataFrame([labelled_row(AwayTeam="Arsenal")]))


def test_rejects_a_target_outside_0_5():
    with pytest.raises(ValueError, match="between 0 and 5"):
        validate_matches(pd.DataFrame([labelled_row(target=6)]))
    with pytest.raises(ValueError, match="between 0 and 5"):
        validate_matches(pd.DataFrame([labelled_row(target=-1)]))


def test_require_target_fails_when_the_column_is_missing():
    frame = pd.DataFrame([labelled_row()])
    del frame["target"]
    with pytest.raises(ValueError, match="target"):
        validate_matches(frame, require_target=True)
