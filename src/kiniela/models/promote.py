"""Promote the candidate model when it beats the current one (issue #37).

Run from the repo root, with ``DATABASE_URL`` pointing to the database that holds the
feedback (Neon in production)::

    python -m kiniela.models.promote --dry-run   # only show the decision
    python -m kiniela.models.promote             # promote if the rule says so

Promoting means: the current model and its card are archived in
``models/archive/<version>/`` and the candidate files take their names. The deployed app
only changes after those files are committed and Render is redeployed (docs/ab-testing.md).
"""

from __future__ import annotations

import argparse
from pathlib import Path

import joblib

from kiniela.models.ab_testing import (
    CANDIDATE_CARD_NAME,
    CANDIDATE_MODEL_NAME,
    CURRENT_CARD_NAME,
    MODELS_DIR,
    Decision,
    load_candidate,
    load_model_card,
    should_promote,
    version_evidence,
)
from kiniela.models.predict import DEFAULT_MODEL_PATH, REFERENCE_VERSION
from kiniela.storage import get_engine, init_db, session_scope

CURRENT_MODEL_NAME = DEFAULT_MODEL_PATH.name


def current_version(models_dir: Path) -> str:
    """Version of the current model, or the reference model's when there is none."""
    path = models_dir / CURRENT_MODEL_NAME
    return joblib.load(path).version if path.is_file() else REFERENCE_VERSION


def evaluate(models_dir: Path = MODELS_DIR, database_url: str | None = None) -> tuple[str, str, Decision]:
    """Compare the current model with the candidate. Returns both versions and the decision.

    Raises ``FileNotFoundError`` when there is no candidate or no candidate card, and
    ``ValueError`` when the candidate card describes another version.
    """
    candidate = load_candidate(models_dir / CANDIDATE_MODEL_NAME)
    candidate_card = load_model_card(models_dir / CANDIDATE_CARD_NAME)
    if candidate is None or candidate_card is None:
        raise FileNotFoundError(
            f"Promotion needs {CANDIDATE_MODEL_NAME} and {CANDIDATE_CARD_NAME} in {models_dir}."
        )
    if candidate_card.get("version") != candidate.version:
        raise ValueError(
            f"{CANDIDATE_CARD_NAME} is for '{candidate_card.get('version')}', "
            f"but the candidate model is '{candidate.version}'."
        )

    current = current_version(models_dir)
    engine = get_engine(database_url)
    init_db(engine)
    with session_scope(engine) as session:
        current_evidence = version_evidence(
            session, current, load_model_card(models_dir / CURRENT_CARD_NAME)
        )
        candidate_evidence = version_evidence(session, candidate.version, candidate_card)
    return current, candidate.version, should_promote(current_evidence, candidate_evidence)


def promote_candidate(models_dir: Path, current: str) -> Path | None:
    """Archive the current model files and give the candidate files their names.

    Returns the archive folder, or ``None`` when there was no current model (reference).
    """
    archive = None
    current_files = [models_dir / CURRENT_MODEL_NAME, models_dir / CURRENT_CARD_NAME]
    if current_files[0].is_file():
        archive = models_dir / "archive" / current
        archive.mkdir(parents=True, exist_ok=True)
        for path in current_files:
            if path.is_file():
                path.replace(archive / path.name)
    (models_dir / CANDIDATE_MODEL_NAME).replace(models_dir / CURRENT_MODEL_NAME)
    (models_dir / CANDIDATE_CARD_NAME).replace(models_dir / CURRENT_CARD_NAME)
    return archive


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Promote the candidate model if it beats the current one.")
    parser.add_argument("--models-dir", type=Path, default=MODELS_DIR, help="Folder with the model files.")
    parser.add_argument("--dry-run", action="store_true", help="Show the decision without moving files.")
    args = parser.parse_args(argv)

    try:
        current, candidate, decision = evaluate(args.models_dir)
    except (FileNotFoundError, ValueError) as error:
        parser.exit(1, f"{error}\n")

    print(f"Current: {current} | Candidate: {candidate}")
    for reason in decision.reasons:
        print(f"- {reason}")

    if not decision.promote:
        print("Not promoted.")
    elif args.dry_run:
        print("Would promote the candidate (dry run, no files moved).")
    else:
        archive = promote_candidate(args.models_dir, current)
        if archive is not None:
            print(f"Previous model archived in {archive}.")
        print(f"Promoted '{candidate}'. Commit the model files and redeploy the app.")


if __name__ == "__main__":
    main()
