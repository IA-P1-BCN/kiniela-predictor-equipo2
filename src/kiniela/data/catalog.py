"""What the app needs from the dataset: the list of teams and the observed classes.

The app must also work without data (for example inside the Docker image, which does not
include ``data/``), so every function here has a fallback.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from kiniela.data.target import build_target

PROJECT_ROOT = Path(__file__).resolve().parents[3]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

# Premier League 2023-24, written as in the processed dataset (lowercase, normalised)
FALLBACK_TEAMS = (
    "arsenal", "aston villa", "bournemouth", "brentford", "brighton", "burnley", "chelsea",
    "crystal palace", "everton", "fulham", "liverpool", "luton", "man city", "man united",
    "newcastle", "nottm forest", "sheffield united", "tottenham", "west ham", "wolves",
)

# Class counts of the Premier League 2023-24 (380 matches, 6-class target): used for the
# reference model when the dataset is not available
FALLBACK_TARGETS = (0,) * 42 + (1,) * 53 + (2,) * 49 + (3,) * 44 + (4,) * 26 + (5,) * 166

REQUIRED_COLUMNS = ("HomeTeam", "AwayTeam", "FTHG", "FTAG")


def find_processed_dataset(directory: Path = PROCESSED_DIR) -> Path | None:
    """The most recently modified CSV in ``data/processed``, or ``None`` if there is none."""
    csv_files = sorted(directory.glob("*.csv"), key=lambda path: path.stat().st_mtime)
    return csv_files[-1] if csv_files else None


def load_processed_matches(path: Path | None = None) -> pd.DataFrame | None:
    """Read the processed matches, or ``None`` if the file is missing or lacks key columns."""
    path = path or find_processed_dataset()
    if path is None or not path.is_file():
        return None
    matches = pd.read_csv(path)
    if not set(REQUIRED_COLUMNS).issubset(matches.columns):
        return None
    return matches.dropna(subset=list(REQUIRED_COLUMNS))


def list_teams(matches: pd.DataFrame | None) -> list[str]:
    """Sorted list of every team that played at home or away."""
    if matches is None or matches.empty:
        return sorted(FALLBACK_TEAMS)
    return sorted(set(matches["HomeTeam"]) | set(matches["AwayTeam"]))


def observed_targets(matches: pd.DataFrame | None) -> list[int]:
    """The 6-class target of every match, built from the final score."""
    if matches is None or matches.empty:
        return list(FALLBACK_TARGETS)
    return [build_target(int(home), int(away)) for home, away in zip(matches["FTHG"], matches["FTAG"])]
