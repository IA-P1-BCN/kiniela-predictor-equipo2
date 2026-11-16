"""Download and cleaning of the Premier League matches (issue #1), without network."""

import pandas as pd
import pytest

from kiniela.data import dataset
from kiniela.features.engineering import FEATURE_COLUMNS, build_features


def raw_season(rows):
    """A football-data.co.uk E0.csv from (date, home, away, home_goals, away_goals, result)."""
    return pd.DataFrame(rows, columns=["Date", "HomeTeam", "AwayTeam", "FTHG", "FTAG", "FTR"])


@pytest.fixture
def fake_site(monkeypatch):
    """Serve fake season files instead of downloading them."""
    files = {
        "2324": raw_season(
            [
                ("01/09/2023", "Man City", "Nott'm Forest", 2, 0, "H"),
                ("11/08/2023", "Burnley", "Man City", 0, 3, "A"),
                ("11/08/2023", "Burnley", "Man City", 0, 3, "A"),  # duplicated row
                ("12/08/2023", "Arsenal", None, 2, 1, "H"),  # missing team
            ]
        ),
        "1617": raw_season([("13/08/16", "Burnley", "Swansea", 0, 1, "A")]),
    }

    def read_csv(url, **kwargs):
        code = url.split("/")[-2]
        return files[code].copy()

    monkeypatch.setattr(dataset.pd, "read_csv", read_csv)
    return files


class TestOneSeason:
    def test_cleans_and_sorts_by_date(self, fake_site):
        matches = dataset.download_premier_league_data("2324")

        # The duplicate and the row without a team are dropped.
        assert len(matches) == 2
        # 11/08 goes before 01/09: sorted as dates, not as text.
        assert list(matches["Date"]) == [pd.Timestamp("2023-08-11"), pd.Timestamp("2023-09-01")]

    def test_team_names_match_the_app(self, fake_site):
        matches = dataset.download_premier_league_data("2324")

        assert set(matches["HomeTeam"]) | set(matches["AwayTeam"]) == {
            "burnley",
            "man city",
            "nottm forest",
        }

    def test_has_no_season_column(self, fake_site):
        matches = dataset.download_premier_league_data("2324")

        assert "Season" not in matches.columns


class TestSeveralSeasons:
    def test_adds_the_season_code(self, fake_site):
        matches = dataset.download_premier_league_data(["1617", "2324"])

        assert list(matches["Season"]) == ["1617", "2324", "2324"]

    def test_two_digit_years_are_read_day_first(self, fake_site):
        matches = dataset.download_premier_league_data(["1617", "2324"])

        assert matches.loc[0, "Date"] == pd.Timestamp("2016-08-13")

    def test_features_restart_every_season(self, fake_site):
        matches = dataset.download_premier_league_data(["1617", "2324"])

        features = build_features(matches)

        # Burnley played at home in 2016-17, but 2023-24 starts without history.
        burnley_2324 = features[(features["HomeTeam"] == "burnley") & (features["Date"].dt.year == 2023)]
        assert burnley_2324[list(FEATURE_COLUMNS)].isna().all(axis=None)


def test_unreadable_date_raises(monkeypatch):
    broken = raw_season([("not a date", "Arsenal", "Chelsea", 1, 0, "H")])
    monkeypatch.setattr(dataset.pd, "read_csv", lambda url, **kwargs: broken.copy())

    with pytest.raises(ValueError):
        dataset.download_premier_league_data("2324")
