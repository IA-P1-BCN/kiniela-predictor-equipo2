"""Fixed expected scores for a known prediction (issue #15)."""

import pytest

from kiniela.config import N_CLASSES
from kiniela.models.metrics import score_multiclass
from kiniela.models.predict import predicted_class


# Six true labels, one per class, and a predictor that only misses class 5
# (predicts 2 instead). Accuracy 5/6; F1 of class 5 is 0; F1 of class 2 is 2/3.
Y_TRUE = [0, 1, 2, 3, 4, 5]
Y_PRED = [0, 1, 2, 3, 4, 2]


def test_known_case_accuracy_and_f1_per_class():
    scores = score_multiclass(Y_TRUE, Y_PRED)
    assert scores.accuracy == pytest.approx(5 / 6)
    assert len(scores.f1) == N_CLASSES
    assert scores.f1[0] == pytest.approx(1.0)
    assert scores.f1[2] == pytest.approx(2 / 3)
    assert scores.f1[5] == pytest.approx(0.0)
    assert scores.recall[5] == pytest.approx(0.0)
    assert scores.precision[2] == pytest.approx(0.5)


def test_prediction_shape_range_and_probabilities_sum_to_one():
    probabilities = [0.05, 0.10, 0.50, 0.15, 0.10, 0.10]
    assert len(probabilities) == N_CLASSES
    assert pytest.approx(sum(probabilities)) == 1
    assert predicted_class(probabilities) == 2
    assert 0 <= predicted_class(probabilities) < N_CLASSES


def test_rejects_probability_vectors_that_do_not_sum_to_one():
    with pytest.raises(ValueError, match="sumar"):
        predicted_class([0.5, 0.5, 0.5, 0.0, 0.0, 0.0])


def test_score_rejects_mismatched_lengths():
    with pytest.raises(ValueError, match="same length"):
        score_multiclass([0, 1], [0])
