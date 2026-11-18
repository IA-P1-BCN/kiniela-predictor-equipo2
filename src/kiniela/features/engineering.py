"""Forma reciente, goles, diferencia de rendimiento y localía.

Las variables históricas tienen que calcularse solo con partidos
anteriores, para no filtrar el resultado del partido que se predice.
"""

import pandas as pd
import numpy as np

# Number of earlier matches at the same venue used by every feature.
N_LAST_MATCHES = 5

# Model input columns, in the order build_match_features returns them.
FEATURE_COLUMNS = (
    "form_home_last_5",
    "form_away_last_5",
    "avg_home_goals_last_5",
    "avg_away_goals_last_5",
    "home_diff_last_5",
    "away_diff_last_5",
    "match_diff",
    "match_goals_expected",
)

# Points of a full-time result (FTR) from the point of view of each venue.
_RESULT_POINTS = {
    "home": {"H": 1, "D": 0, "A": -1},
    "away": {"H": -1, "D": 0, "A": 1},
}


def build_features(matches: pd.DataFrame) -> pd.DataFrame:
    """Compute the modelling features of every match in the history.

    Each row only uses matches of the same season played on an earlier date
    (``Date`` strictly lower), so the result of a match never leaks into its own
    features. The calculation per match is shared with :func:`build_match_features`,
    so the app gets exactly the same features the model was trained with.

    Args:
        matches: Matches with ``HomeTeam``, ``AwayTeam``, ``FTHG``, ``FTAG``, ``FTR``
            and ``Date`` (``datetime`` or day-first text such as ``"11/08/2023"``),
            and optionally ``Season``. Without ``Season`` all rows count as one season.

    Returns:
        A new DataFrame sorted by date with ``Date``, ``HomeTeam``, ``AwayTeam``, the
        columns in :data:`FEATURE_COLUMNS` and ``FTHG``, ``FTAG``, ``FTR``. Any other
        input column is not returned. Features are ``NaN`` while a team has no earlier
        match at that venue in the season.

    Features (see :data:`FEATURE_COLUMNS`), computed over the team's last 5 earlier
    matches at the same venue (home team at home, away team away):

    - ``form_home_last_5`` / ``form_away_last_5``: mean result from the team's point
      of view over the 5 matches (win = 1, draw = 0, loss = -1).
    - ``avg_home_goals_last_5`` / ``avg_away_goals_last_5``: mean goals scored.
    - ``home_diff_last_5`` / ``away_diff_last_5``: mean goal difference
      (goals scored minus goals conceded).
    - ``match_diff``: ``form_home_last_5 - form_away_last_5``.
    - ``match_goals_expected``: ``avg_home_goals_last_5 + avg_away_goals_last_5``.

    Raises:
        ValueError: If ``matches`` is empty.
    """
    if matches.empty:
        raise ValueError("El histórico de partidos está vacío.")

    matches = _sorted_by_date(matches)
    seasons = matches["Season"] if "Season" in matches.columns else pd.Series(0, index=matches.index)

    rows = []
    for position in range(len(matches)):
        match = matches.iloc[position]
        past = matches[(seasons == seasons.iloc[position]) & (matches["Date"] < match["Date"])]
        rows.append(_match_features(past, match["HomeTeam"], match["AwayTeam"]))

    features = pd.DataFrame(rows, columns=list(FEATURE_COLUMNS), index=matches.index)
    return pd.concat(
        [matches[["Date", "HomeTeam", "AwayTeam"]], features, matches[["FTHG", "FTAG", "FTR"]]],
        axis=1,
    )


def build_match_features(history: pd.DataFrame, home_team: str, away_team: str) -> pd.DataFrame:
    """Compute the features of one new match from the history of played matches.

    This is what the app needs to predict a match that has not been played yet. It
    uses every match in ``history`` from its latest season, so pass only matches
    played before the one being predicted.

    Args:
        history: Played matches, with the same columns as in :func:`build_features`.
        home_team: Home team, written exactly as in the dataset (``"arsenal"``).
        away_team: Away team, written exactly as in the dataset (``"chelsea"``).

    Returns:
        A one-row DataFrame with the columns of :data:`FEATURE_COLUMNS`, in that order,
        ready for ``predict_proba``. The values are ``NaN`` for a team with no earlier
        match at that venue in the season.

    Example:
        >>> features = build_match_features(history, "arsenal", "chelsea")
        >>> list(features.columns) == list(FEATURE_COLUMNS)
        True
    """
    if history.empty:
        values = dict.fromkeys(FEATURE_COLUMNS, np.nan)
    else:
        past = _sorted_by_date(history)
        if "Season" in past.columns:
            past = past[past["Season"] == past["Season"].iloc[-1]]
        values = _match_features(past, home_team, away_team)
    return pd.DataFrame([values], columns=list(FEATURE_COLUMNS))


def _sorted_by_date(matches: pd.DataFrame) -> pd.DataFrame:
    """Return a copy with ``Date`` parsed and the rows in chronological order.

    football-data.co.uk writes dates day first (``"11/08/2023"``): sorting that text
    would put 1 September before 11 August, so the dates are always parsed first.
    ISO dates (``"2024-09-01"``) are tried first, because ``dayfirst`` would read
    that one as 9 January. The stable sort keeps the input order of matches played
    on the same day.
    """
    try:
        dates = pd.to_datetime(matches["Date"], format="ISO8601")
    except ValueError:
        dates = pd.to_datetime(matches["Date"], dayfirst=True, format="mixed")
    return matches.assign(Date=dates).sort_values("Date", kind="mergesort").reset_index(drop=True)


def _team_venue_stats(past: pd.DataFrame, team: str, venue: str) -> tuple[float, float, float]:
    """Form, mean goals scored and mean goal difference of ``team`` at ``venue``.

    ``past`` must be sorted by date and hold only matches before the one predicted.
    """
    if venue == "home":
        team_column, scored, conceded = "HomeTeam", "FTHG", "FTAG"
    else:
        team_column, scored, conceded = "AwayTeam", "FTAG", "FTHG"

    last = past[past[team_column] == team].tail(N_LAST_MATCHES)
    if last.empty:
        return np.nan, np.nan, np.nan

    form = last["FTR"].map(_RESULT_POINTS[venue]).mean()
    goals = last[scored].mean()
    goal_difference = (last[scored] - last[conceded]).mean()
    return float(form), float(goals), float(goal_difference)


def _match_features(past: pd.DataFrame, home_team: str, away_team: str) -> dict[str, float]:
    """Features of one match from the matches played before it (see FEATURE_COLUMNS)."""
    home_form, home_goals, home_diff = _team_venue_stats(past, home_team, "home")
    away_form, away_goals, away_diff = _team_venue_stats(past, away_team, "away")
    # NaN propagates: the combined features are NaN when either team has no history.
    return {
        "form_home_last_5": home_form,
        "form_away_last_5": away_form,
        "avg_home_goals_last_5": home_goals,
        "avg_away_goals_last_5": away_goals,
        "home_diff_last_5": home_diff,
        "away_diff_last_5": away_diff,
        "match_diff": home_form - away_form,
        "match_goals_expected": home_goals + away_goals,
    }
