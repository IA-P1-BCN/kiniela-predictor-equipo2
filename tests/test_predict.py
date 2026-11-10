import pytest

from kiniela.models.predict import predicted_class


def test_elige_la_clase_mas_probable():
    assert predicted_class([0.1, 0.2, 0.05, 0.15, 0.1, 0.4]) == 5


def test_rechaza_un_vector_incompleto():
    with pytest.raises(ValueError):
        predicted_class([0.5, 0.5])
