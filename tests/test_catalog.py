import pandas as pd
import pytest

from kiniela.data.catalog import (
    FALLBACK_TARGETS,
    FALLBACK_TEAMS,
    find_processed_dataset,
    list_teams,
    load_processed_matches,
    observed_targets,
)

MATCHES = pd.DataFrame(
    {
        "HomeTeam": ["arsenal", "chelsea", "everton"],
        "AwayTeam": ["chelsea", "arsenal", "arsenal"],
        "FTHG": [1, 2, 0],
        "FTAG": [0, 2, 3],
    }
)


def test_lists_every_team_once_sorted():
    assert list_teams(MATCHES) == ["arsenal", "chelsea", "everton"]


def test_falls_back_to_premier_league_teams_without_data():
    assert list_teams(None) == sorted(FALLBACK_TEAMS)
    assert len(FALLBACK_TEAMS) == 20


def test_builds_targets_from_final_scores():
    assert observed_targets(MATCHES) == [1, 5, 4]


def test_fallback_targets_cover_the_six_classes():
    assert observed_targets(None) == list(FALLBACK_TARGETS)
    assert set(FALLBACK_TARGETS) == {0, 1, 2, 3, 4, 5}


def test_reads_the_latest_processed_csv(tmp_path):
    assert find_processed_dataset(tmp_path) is None
    MATCHES.to_csv(tmp_path / "matches.csv", index=False)
    path = find_processed_dataset(tmp_path)
    assert path.name == "matches.csv"
    assert len(load_processed_matches(path)) == 3


@pytest.mark.parametrize("columns", [["HomeTeam", "AwayTeam"], ["foo"]])
def test_ignores_files_without_the_key_columns(tmp_path, columns):
    path = tmp_path / "other.csv"
    pd.DataFrame({column: [1] for column in columns}).to_csv(path, index=False)
    assert load_processed_matches(path) is None
