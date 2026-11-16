"""Lectura del histórico de partidos."""

from collections.abc import Sequence
from pathlib import Path

import pandas as pd

BASE_URL = "https://www.football-data.co.uk/mmz4281/"
MATCH_COLUMNS = ["HomeTeam", "AwayTeam", "FTHG", "FTAG", "FTR"]


def download_premier_league_data(season: str | Sequence[str] = "2324") -> pd.DataFrame:
    """Download and clean real Premier League matches from football-data.co.uk.

    Args:
        season: football-data.co.uk season code, e.g. ``"2324"`` for 2023-24, or a
            list of codes, e.g. ``["1516", "1617", ..., "2324"]``.

    Returns:
        One row per match, sorted by date: teams in lowercase without apostrophes,
        goals, result and ``Date`` as a datetime. With a list of seasons it also has a
        ``Season`` column with each code, so the features restart every season (see
        :func:`kiniela.features.engineering.build_features`).

    Nothing is saved to disk: write the result with ``DataFrame.to_csv``
    (see ``docs/tarea-preparacion-dataset.md``).
    """
    several = not isinstance(season, str)
    seasons = list(season) if several else [season]

    frames = []
    for code in seasons:
        url = f"{BASE_URL}{code}/E0.csv"
        print(f"Downloading Premier League {code} from {url}")
        frame = pd.read_csv(url, encoding="utf-8")

        frame = frame.dropna(subset=MATCH_COLUMNS).drop_duplicates()
        for column in ("HomeTeam", "AwayTeam"):
            frame[column] = frame[column].map(_normalize_team)
        if "Date" in frame.columns:
            # Most seasons use dd/mm/yyyy and 2016-17 uses dd/mm/yy: parse each value
            # day first. A date that cannot be parsed raises instead of staying as text,
            # because text dates sort in the wrong order.
            frame["Date"] = pd.to_datetime(frame["Date"], dayfirst=True, format="mixed")
        else:
            print(f"Warning: season {code} has no Date column")
        if several:
            frame["Season"] = str(code)
        frames.append(frame)

    matches = pd.concat(frames, ignore_index=True)
    if "Date" in matches.columns:
        # Stable sort: matches on the same day keep the order of the file.
        matches = matches.sort_values("Date", kind="mergesort").reset_index(drop=True)

    label = seasons[0] if len(seasons) == 1 else f"{seasons[0]} to {seasons[-1]}"
    print(f"Premier League {label}: {len(matches)} matches")
    return matches


def _normalize_team(name):
    """Team name as the app writes it: lowercase, no apostrophes ("Nott'm Forest" -> "nottm forest")."""
    return name.lower().replace("'", "").strip() if isinstance(name, str) else name


def load_matches(path: str | Path) -> pd.DataFrame:
    """Carga un CSV de partidos.

    El repositorio no incluye datos. El archivo lo genera la preparación
    del dataset y debe vivir en ``data/``.
    """
    source = Path(path)
    if not source.is_file():
        raise FileNotFoundError(
            f"No existe el dataset en {source}. Guárdalo en data/raw o data/processed."
        )
    return pd.read_csv(source)
