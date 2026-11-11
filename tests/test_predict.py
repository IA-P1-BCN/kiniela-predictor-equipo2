import joblib
import pytest

from kiniela.models.predict import (
    REFERENCE_VERSION,
    Predictor,
    ReferencePredictor,
    class_frequencies,
    load_predictor,
    predicted_class,
    validate_teams,
)


def test_elige_la_clase_mas_probable():
    assert predicted_class([0.1, 0.2, 0.05, 0.15, 0.1, 0.4]) == 5


def test_rechaza_un_vector_incompleto():
    with pytest.raises(ValueError):
        predicted_class([0.5, 0.5])


# --- Predictor contract and reference model (issue #9) ----------------------


def test_class_frequencies_follow_class_order():
    assert class_frequencies([5, 5, 0, 2]) == [0.25, 0.0, 0.25, 0.0, 0.0, 0.5]


@pytest.mark.parametrize("targets", [[], [6], [-1, 0]])
def test_class_frequencies_reject_empty_or_out_of_range(targets):
    with pytest.raises(ValueError):
        class_frequencies(targets)


@pytest.mark.parametrize(("home", "away"), [("", "chelsea"), ("arsenal", " "), ("Arsenal", "arsenal")])
def test_validate_teams_rejects_missing_or_equal_teams(home, away):
    with pytest.raises(ValueError):
        validate_teams(home, away)


def test_validate_teams_strips_names():
    assert validate_teams(" arsenal ", "chelsea") == ("arsenal", "chelsea")


def test_reference_predictor_returns_six_probabilities_that_add_up_to_one():
    predictor = ReferencePredictor(tuple(class_frequencies([0, 1, 2, 3, 4, 5, 5])))
    probabilities = predictor.predict("arsenal", "chelsea")
    assert len(probabilities) == 6
    assert sum(probabilities) == pytest.approx(1)
    assert predicted_class(probabilities) == 5
    assert isinstance(predictor, Predictor)


def test_reference_predictor_validates_teams():
    predictor = ReferencePredictor(tuple(class_frequencies([1])))
    with pytest.raises(ValueError):
        predictor.predict("arsenal", "arsenal")


def test_load_predictor_falls_back_to_reference_model(tmp_path):
    predictor = load_predictor(tmp_path / "missing.joblib", reference_targets=[2, 2, 5])
    assert predictor.version == REFERENCE_VERSION
    assert predictor.predict("a", "b") == pytest.approx([0, 0, 2 / 3, 0, 0, 1 / 3])


def test_load_predictor_without_model_or_data_fails(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_predictor(tmp_path / "missing.joblib", reference_targets=[])


def test_load_predictor_loads_a_saved_model(tmp_path):
    path = tmp_path / "kiniela_model.joblib"
    joblib.dump(ReferencePredictor(tuple(class_frequencies([3])), version="v-test"), path)
    assert load_predictor(path).version == "v-test"


def test_load_predictor_rejects_objects_without_the_contract(tmp_path):
    path = tmp_path / "kiniela_model.joblib"
    joblib.dump({"not": "a predictor"}, path)
    with pytest.raises(TypeError):
        load_predictor(path)
