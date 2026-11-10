"""Detección básica de data drift. El umbral se documenta al implementarla."""


def drift_report(reference_path: str, current_path: str) -> dict:
    """Compara features de referencia con un lote nuevo."""
    raise NotImplementedError("El monitoreo de drift corresponde a la issue #14.")
