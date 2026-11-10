import pytest

from kiniela.data.target import build_target


def test_rechaza_goles_negativos():
    with pytest.raises(ValueError):
        build_target(-1, 0)


def test_etiquetado_pendiente_de_reglas():
    with pytest.raises(NotImplementedError):
        build_target(2, 0)
