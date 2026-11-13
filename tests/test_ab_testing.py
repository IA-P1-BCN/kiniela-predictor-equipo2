"""Tests of the A/B router, the promotion rule and the promotion script (issue #37)."""

import json
import random

import joblib
import pytest

from kiniela.config import RANDOM_STATE
from kiniela.models.ab_testing import (
    CANDIDATE_CARD_NAME,
    CANDIDATE_MODEL_NAME,
    CURRENT_CARD_NAME,
    MAX_OVERFITTING_GAP,
    MIN_FEEDBACK,
    MIN_F1_IMPROVEMENT,
    ABRouter,
    VersionEvidence,
    candidate_share,
    load_candidate,
    load_model_card,
    should_promote,
)
from kiniela.models.predict import REFERENCE_VERSION, ReferencePredictor, class_frequencies
from kiniela.models.promote import evaluate, main, promote_candidate
from kiniela.storage import get_engine, init_db, save_feedback, save_prediction, session_scope

PROBABILITIES = tuple(class_frequencies([0, 1, 2, 3, 4, 5]))


def model(version: str) -> ReferencePredictor:
    """Any object with the Predictor contract works as a fake model."""
    return ReferencePredictor(PROBABILITIES, version=version)


def evidence(version="v", f1=0.40, gap=0.02, with_feedback=MIN_FEEDBACK, accuracy=0.30):
    return VersionEvidence(version, f1, gap, predictions=with_feedback, with_feedback=with_feedback,
                           accuracy=accuracy)


# --- AB_CANDIDATE_SHARE ---------------------------------------------------------------

@pytest.mark.parametrize(("raw", "share"), [("", 0.0), ("  ", 0.0), ("0", 0.0), ("0.3", 0.3), ("1", 1.0)])
def test_candidate_share_reads_values_between_0_and_1(raw, share):
    assert candidate_share(raw) == share


@pytest.mark.parametrize("raw", ["half", "-0.1", "1.5"])
def test_candidate_share_rejects_invalid_values(raw):
    with pytest.raises(ValueError):
        candidate_share(raw)


def test_candidate_share_defaults_to_the_environment(monkeypatch):
    monkeypatch.setenv("AB_CANDIDATE_SHARE", "0.25")
    assert candidate_share() == 0.25
    monkeypatch.delenv("AB_CANDIDATE_SHARE")
    assert candidate_share() == 0.0


# --- Loading the candidate and the cards ----------------------------------------------

def test_load_candidate_returns_none_without_file(tmp_path):
    assert load_candidate(tmp_path / CANDIDATE_MODEL_NAME) is None


def test_load_candidate_loads_and_checks_the_contract(tmp_path):
    path = tmp_path / CANDIDATE_MODEL_NAME
    joblib.dump(model("v2"), path)
    assert load_candidate(path).version == "v2"
    joblib.dump({"not": "a predictor"}, path)
    with pytest.raises(TypeError):
        load_candidate(path)


def test_load_model_card(tmp_path):
    path = tmp_path / CURRENT_CARD_NAME
    assert load_model_card(path) is None
    path.write_text(json.dumps({"version": "v1"}), encoding="utf-8")
    assert load_model_card(path) == {"version": "v1"}


# --- Router ---------------------------------------------------------------------------

def test_router_without_candidate_always_uses_the_current_model():
    router = ABRouter(model("v1"), share=0.5)
    assert not router.is_active
    assert {router.choose().version for _ in range(50)} == {"v1"}


def test_router_with_share_zero_never_uses_the_candidate():
    router = ABRouter(model("v1"), model("v2"), share=0.0)
    assert not router.is_active
    assert {router.choose().version for _ in range(50)} == {"v1"}


def test_router_splits_predictions_by_the_share():
    router = ABRouter(model("v1"), model("v2"), share=0.3, rng=random.Random(RANDOM_STATE))
    chosen = [router.choose().version for _ in range(2000)]
    assert router.is_active
    assert chosen.count("v2") / len(chosen) == pytest.approx(0.3, abs=0.03)


def test_router_with_share_one_always_uses_the_candidate():
    router = ABRouter(model("v1"), model("v2"), share=1.0)
    assert {router.choose().version for _ in range(50)} == {"v2"}


@pytest.mark.parametrize(("candidate", "share"), [("v2", 1.5), ("v1", 0.5)])
def test_router_rejects_invalid_setups(candidate, share):
    with pytest.raises(ValueError):
        ABRouter(model("v1"), model(candidate), share=share)


# --- Promotion rule (fixed cases) -----------------------------------------------------

def test_promotes_a_candidate_that_meets_every_condition():
    current = evidence("v1", f1=0.40, accuracy=0.30)
    candidate = evidence("v2", f1=0.40 + MIN_F1_IMPROVEMENT, accuracy=0.30)
    assert should_promote(current, candidate).promote


def test_does_not_promote_a_tie_in_f1():
    decision = should_promote(evidence("v1", f1=0.40), evidence("v2", f1=0.405))
    assert not decision.promote
    assert any("F1 macro" in reason for reason in decision.reasons)


def test_does_not_promote_with_overfitting():
    decision = should_promote(evidence("v1"), evidence("v2", f1=0.50, gap=MAX_OVERFITTING_GAP))
    assert not decision.promote
    assert any("gap" in reason for reason in decision.reasons)


def test_does_not_promote_without_enough_feedback():
    decision = should_promote(evidence("v1"), evidence("v2", f1=0.50, with_feedback=MIN_FEEDBACK - 1))
    assert not decision.promote
    assert any("feedback" in reason for reason in decision.reasons)


def test_does_not_promote_with_lower_feedback_accuracy():
    decision = should_promote(evidence("v1", accuracy=0.35), evidence("v2", f1=0.50, accuracy=0.34))
    assert not decision.promote
    assert any("accuracy" in reason for reason in decision.reasons)


def test_does_not_promote_a_candidate_without_card_metrics():
    decision = should_promote(evidence("v1"), evidence("v2", f1=None, gap=None))
    assert not decision.promote


def test_reference_model_without_card_is_compared_only_with_feedback():
    current = evidence(REFERENCE_VERSION, f1=None, gap=None, accuracy=0.25)
    decision = should_promote(current, evidence("v2", f1=0.30, accuracy=0.31))
    assert decision.promote
    assert any("only feedback" in reason for reason in decision.reasons)


def test_lists_every_failed_condition():
    decision = should_promote(
        evidence("v1", f1=0.40, with_feedback=0, accuracy=None),
        evidence("v2", f1=0.39, gap=0.08, with_feedback=0, accuracy=None),
    )
    assert not decision.promote
    assert len(decision.reasons) == 4  # gap, F1 and feedback for both versions


# --- Promotion script -----------------------------------------------------------------

@pytest.fixture
def database_url(tmp_path):
    url = f"sqlite:///{(tmp_path / 'ab.db').as_posix()}"
    init_db(get_engine(url))
    return url


def add_feedback(url: str, version: str, correct: int, wrong: int) -> None:
    """Store predictions of ``version`` (class 0) with their feedback."""
    probabilities = [0.5, 0.1, 0.1, 0.1, 0.1, 0.1]
    with session_scope(get_engine(url)) as session:
        for is_correct in [True] * correct + [False] * wrong:
            prediction = save_prediction(session, home_team="arsenal", away_team="chelsea", inputs={},
                                         probabilities=probabilities, model_version=version)
            save_feedback(session, prediction.id, is_correct=is_correct)


def write_model(models_dir, name, card_name, version, f1=None, gap=None):
    joblib.dump(model(version), models_dir / name)
    metrics = {} if f1 is None else {"f1_macro": f1, "overfitting_gap": gap}
    (models_dir / card_name).write_text(json.dumps({"version": version, "metrics": metrics}),
                                        encoding="utf-8")


@pytest.fixture
def models_dir(tmp_path):
    folder = tmp_path / "models"
    folder.mkdir()
    write_model(folder, "kiniela_model.joblib", CURRENT_CARD_NAME, "v1", f1=0.40, gap=0.02)
    write_model(folder, CANDIDATE_MODEL_NAME, CANDIDATE_CARD_NAME, "v2", f1=0.45, gap=0.03)
    return folder


def test_evaluate_uses_cards_and_feedback(models_dir, database_url):
    add_feedback(database_url, "v1", correct=10, wrong=20)
    add_feedback(database_url, "v2", correct=12, wrong=18)
    current, candidate, decision = evaluate(models_dir, database_url)
    assert (current, candidate, decision.promote) == ("v1", "v2", True)


def test_evaluate_needs_a_candidate(tmp_path, database_url):
    with pytest.raises(FileNotFoundError):
        evaluate(tmp_path, database_url)


def test_evaluate_rejects_a_card_of_another_version(models_dir, database_url):
    card = models_dir / CANDIDATE_CARD_NAME
    card.write_text(json.dumps({"version": "other", "metrics": {}}), encoding="utf-8")
    with pytest.raises(ValueError):
        evaluate(models_dir, database_url)


def test_promote_archives_the_current_model(models_dir):
    archive = promote_candidate(models_dir, "v1")
    assert archive == models_dir / "archive" / "v1"
    assert joblib.load(archive / "kiniela_model.joblib").version == "v1"
    assert joblib.load(models_dir / "kiniela_model.joblib").version == "v2"
    assert load_model_card(models_dir / CURRENT_CARD_NAME)["version"] == "v2"
    assert not (models_dir / CANDIDATE_MODEL_NAME).exists()


def test_command_line_dry_run_moves_nothing(models_dir, database_url, monkeypatch, capsys):
    monkeypatch.setenv("DATABASE_URL", database_url)
    add_feedback(database_url, "v1", correct=10, wrong=20)
    add_feedback(database_url, "v2", correct=12, wrong=18)

    main(["--models-dir", str(models_dir), "--dry-run"])

    assert "Would promote" in capsys.readouterr().out
    assert (models_dir / CANDIDATE_MODEL_NAME).exists()


def test_command_line_promotes_when_the_rule_says_so(models_dir, database_url, monkeypatch, capsys):
    monkeypatch.setenv("DATABASE_URL", database_url)
    add_feedback(database_url, "v1", correct=10, wrong=20)
    add_feedback(database_url, "v2", correct=12, wrong=18)

    main(["--models-dir", str(models_dir)])

    assert "Promoted 'v2'" in capsys.readouterr().out
    assert joblib.load(models_dir / "kiniela_model.joblib").version == "v2"


def test_command_line_keeps_the_model_when_the_rule_says_no(models_dir, database_url, monkeypatch, capsys):
    monkeypatch.setenv("DATABASE_URL", database_url)
    add_feedback(database_url, "v1", correct=3, wrong=2)  # not enough feedback

    main(["--models-dir", str(models_dir)])

    assert "Not promoted." in capsys.readouterr().out
    assert joblib.load(models_dir / "kiniela_model.joblib").version == "v1"


def test_command_line_without_candidate_explains_and_fails(tmp_path, database_url, monkeypatch, capsys):
    monkeypatch.setenv("DATABASE_URL", database_url)
    with pytest.raises(SystemExit) as exit_info:
        main(["--models-dir", str(tmp_path)])
    assert exit_info.value.code == 1
    assert "candidate_model.joblib" in capsys.readouterr().err
