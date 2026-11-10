from kiniela.config import CLASS_NAMES, N_CLASSES


def test_hay_seis_clases():
    assert N_CLASSES == 6
    assert list(CLASS_NAMES) == [0, 1, 2, 3, 4, 5]


def test_cada_clase_tiene_nombre():
    assert all(isinstance(name, str) and name for name in CLASS_NAMES.values())
