from kiniela.config import CLASS_NAMES, MAX_PREDICTIONS_PER_SESSION, N_CLASSES


def test_hay_seis_clases():
    assert N_CLASSES == 6
    assert list(CLASS_NAMES) == [0, 1, 2, 3, 4, 5]


def test_cada_clase_tiene_nombre():
    assert all(isinstance(name, str) and name for name in CLASS_NAMES.values())


def test_session_prediction_limit_is_a_small_positive_cap():
    assert 1 <= MAX_PREDICTIONS_PER_SESSION <= 50
