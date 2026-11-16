"""Tests for the match features (issues #3 and #34)."""

import numpy as np
import pandas as pd
import pytest

from kiniela.config import RANDOM_STATE
from kiniela.features import engineering
from kiniela.features.engineering import FEATURE_COLUMNS


def make_matches(rows, season="2324"):
    """Matches from (date, home, away, home_goals, away_goals) tuples, FTR derived."""
    frame = pd.DataFrame(rows, columns=["Date", "HomeTeam", "AwayTeam", "FTHG", "FTAG"])
    frame["FTR"] = np.select(
        [frame["FTHG"] > frame["FTAG"], frame["FTHG"] < frame["FTAG"]], ["H", "A"], "D"
    )
    frame["Season"] = season
    return frame


@pytest.fixture
def sample_matches():
    """Arsenal and Chelsea alternating venues, in ISO dates."""
    return make_matches(
        [
            ("2024-08-17", "Arsenal", "Chelsea", 3, 1),
            ("2024-09-23", "Chelsea", "Arsenal", 1, 2),
            ("2024-10-01", "Arsenal", "Chelsea", 2, 1),
            ("2024-10-28", "Chelsea", "Arsenal", 1, 1),
            ("2024-12-01", "Arsenal", "Chelsea", 2, 0),
        ]
    )


@pytest.fixture
def random_season():
    """A full double round-robin of 6 teams with random scores and day-first dates."""
    rng = np.random.default_rng(RANDOM_STATE)
    teams = [f"team {letter}" for letter in "abcdef"]
    fixtures = [(home, away) for home in teams for away in teams if home != away]
    rng.shuffle(fixtures)
    start = pd.Timestamp("2023-08-11")
    rows = []
    for number, (home, away) in enumerate(fixtures):
        # Two matches per day, so some matches share a date.
        date = start + pd.Timedelta(days=number // 2)
        rows.append((date.strftime("%d/%m/%Y"), home, away, *rng.integers(0, 5, size=2)))
    return make_matches(rows)


class TestBuildFeatures:
    def test_first_match_has_no_history(self, sample_matches):
        features = engineering.build_features(sample_matches.iloc[:1])

        assert features[list(FEATURE_COLUMNS)].iloc[0].isna().all()

    def test_features_with_history(self, sample_matches):
        features = engineering.build_features(sample_matches.iloc[:3])

        assert features[list(FEATURE_COLUMNS)].iloc[2].notna().all()

    def test_returns_the_documented_columns(self, sample_matches):
        features = engineering.build_features(sample_matches)

        expected = ["Date", "HomeTeam", "AwayTeam", *FEATURE_COLUMNS, "FTHG", "FTAG", "FTR"]
        assert list(features.columns) == expected
        assert len(features) == len(sample_matches)

    def test_empty_history_raises(self):
        with pytest.raises(ValueError):
            engineering.build_features(pd.DataFrame())

    def test_does_not_modify_the_input(self, sample_matches):
        original = sample_matches.copy()

        engineering.build_features(sample_matches)

        pd.testing.assert_frame_equal(sample_matches, original)


class TestNoDuplicates:
    def test_duplicated_features_are_removed(self, sample_matches):
        features = engineering.build_features(sample_matches)

        for removed in ["recent_home_form", "recent_away_form", "match_momentum"]:
            assert removed not in features.columns

    def test_feature_names_are_unique(self):
        assert len(set(FEATURE_COLUMNS)) == len(FEATURE_COLUMNS)


class TestFeatureSemantics:
    def test_form_is_the_mean_of_the_last_5_results(self):
        # Arsenal at home: W, L, L, D, W, W. For the 7th match only the last 5 count.
        scores = [(2, 0), (0, 1), (1, 3), (1, 1), (2, 1), (3, 0)]
        rows = [
            (f"2024-0{month}-01", "Arsenal", f"rival {month}", home, away)
            for month, (home, away) in enumerate(scores + [(0, 0)], start=1)
        ]
        features = engineering.build_features(make_matches(rows))
        last = features.iloc[-1]

        # Last 5 results: L, L, D, W, W -> (-1 - 1 + 0 + 1 + 1) / 5
        assert last["form_home_last_5"] == pytest.approx(0.0)
        assert last["avg_home_goals_last_5"] == pytest.approx((0 + 1 + 1 + 2 + 3) / 5)
        assert last["home_diff_last_5"] == pytest.approx((-1 - 2 + 0 + 1 + 3) / 5)

    def test_away_win_counts_as_a_win_for_the_away_team(self):
        matches = make_matches(
            [
                ("2024-08-17", "Burnley", "Man City", 0, 3),
                ("2024-09-01", "Arsenal", "Man City", 1, 1),
            ]
        )
        features = engineering.build_features(matches)

        assert features.iloc[1]["form_away_last_5"] == 1.0
        assert features.iloc[1]["avg_away_goals_last_5"] == 3.0
        assert features.iloc[1]["away_diff_last_5"] == 3.0

    def test_combined_features(self, sample_matches):
        row = engineering.build_features(sample_matches).iloc[-1]

        assert row["match_diff"] == pytest.approx(row["form_home_last_5"] - row["form_away_last_5"])
        assert row["match_goals_expected"] == pytest.approx(
            row["avg_home_goals_last_5"] + row["avg_away_goals_last_5"]
        )

    def test_day_first_dates_are_sorted_chronologically(self):
        # As text, "01/09/2023" sorts before "11/08/2023". Chronologically it is after.
        matches = make_matches(
            [
                ("01/09/2023", "Arsenal", "Chelsea", 0, 2),
                ("11/08/2023", "Arsenal", "Fulham", 4, 0),
            ]
        )
        features = engineering.build_features(matches)

        assert list(features["AwayTeam"]) == ["Fulham", "Chelsea"]
        assert pd.isna(features.iloc[0]["form_home_last_5"])
        assert features.iloc[1]["avg_home_goals_last_5"] == 4.0

    def test_history_restarts_every_season(self):
        matches = pd.concat(
            [
                make_matches([("2023-05-01", "Arsenal", "Chelsea", 2, 0)], season="2223"),
                make_matches([("2023-08-12", "Arsenal", "Chelsea", 1, 0)], season="2324"),
            ],
            ignore_index=True,
        )
        features = engineering.build_features(matches)

        assert features.iloc[1][list(FEATURE_COLUMNS)].isna().all()


class TestNoDataLeakage:
    def test_changing_a_result_does_not_change_its_own_features(self, random_season):
        target = 20  # a match in the second half of the 30-match season
        changed = random_season.copy()
        changed.loc[target, ["FTHG", "FTAG", "FTR"]] = [9, 0, "H"]

        original = engineering.build_features(random_season)
        modified = engineering.build_features(changed)

        # Same date ordering in both runs: the match keeps its position.
        position = original.index[
            (original["HomeTeam"] == random_season.loc[target, "HomeTeam"])
            & (original["AwayTeam"] == random_season.loc[target, "AwayTeam"])
        ][0]
        pd.testing.assert_frame_equal(
            original.loc[:position, list(FEATURE_COLUMNS)],
            modified.loc[:position, list(FEATURE_COLUMNS)],
        )

    def test_matches_on_the_same_day_do_not_see_each_other(self):
        matches = make_matches(
            [
                ("2024-08-17", "Arsenal", "Chelsea", 5, 0),
                ("2024-08-17", "Arsenal", "Fulham", 0, 0),
            ]
        )
        features = engineering.build_features(matches)

        assert pd.isna(features.iloc[1]["form_home_last_5"])


class TestBuildMatchFeatures:
    def test_returns_one_row_with_the_model_columns(self, sample_matches):
        features = engineering.build_match_features(sample_matches, "Arsenal", "Chelsea")

        assert isinstance(features, pd.DataFrame)
        assert list(features.columns) == list(FEATURE_COLUMNS)
        assert len(features) == 1
        assert features.iloc[0].notna().all()

    def test_uses_every_match_of_the_history(self, sample_matches):
        # Arsenal at home: 3-1, 2-1, 2-0. The latest home match must be included.
        features = engineering.build_match_features(sample_matches, "Arsenal", "Chelsea")

        assert features.iloc[0]["avg_home_goals_last_5"] == pytest.approx(7 / 3)
        assert features.iloc[0]["form_home_last_5"] == 1.0

    def test_team_without_history_gives_nan_but_keeps_the_columns(self, sample_matches):
        features = engineering.build_match_features(sample_matches, "Newcomer", "Chelsea")

        assert list(features.columns) == list(FEATURE_COLUMNS)
        assert pd.isna(features.iloc[0]["form_home_last_5"])
        assert pd.isna(features.iloc[0]["match_diff"])
        # Chelsea lost its three away matches: 3-1, 2-1 and 2-0.
        assert features.iloc[0]["form_away_last_5"] == -1.0

    def test_empty_history_gives_nan(self):
        features = engineering.build_match_features(pd.DataFrame(), "Arsenal", "Chelsea")

        assert list(features.columns) == list(FEATURE_COLUMNS)
        assert features.iloc[0].isna().all()

    def test_handles_missing_season(self, sample_matches):
        history = sample_matches.drop(columns="Season")

        features = engineering.build_match_features(history, "Arsenal", "Chelsea")

        assert features.iloc[0]["avg_home_goals_last_5"] == pytest.approx(7 / 3)

    def test_uses_only_the_latest_season(self):
        history = pd.concat(
            [
                make_matches([("2023-05-01", "Arsenal", "Chelsea", 6, 0)], season="2223"),
                make_matches([("2023-08-12", "Arsenal", "Fulham", 1, 0)], season="2324"),
            ],
            ignore_index=True,
        )
        features = engineering.build_match_features(history, "Arsenal", "Chelsea")

        assert features.iloc[0]["avg_home_goals_last_5"] == 1.0

    def test_matches_the_training_features(self, random_season):
        """The app must compute exactly what the model was trained on (issue #35)."""
        training = engineering.build_features(random_season)
        dates = pd.to_datetime(random_season["Date"], dayfirst=True)

        for position, match in training.iterrows():
            history = random_season[dates < match["Date"]]
            app = engineering.build_match_features(history, match["HomeTeam"], match["AwayTeam"])
            pd.testing.assert_series_equal(
                app.iloc[0],
                match[list(FEATURE_COLUMNS)].astype(float),
                check_names=False,
                obj=f"match {position}: {match['HomeTeam']} - {match['AwayTeam']}",
            )
