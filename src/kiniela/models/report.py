"""Full metrics report of the serving model (issue #8).

The numbers come from **out-of-fold predictions** on the project's fixed scheme
(:func:`kiniela.models.train.stratified_cv`), not from scoring the training set
with the final model: that would inflate every metric. The same tuned
hyperparameters of ``models/model_card.json`` are fitted in every fold, with
class-balanced sample weights computed on the training fold only.

Run it from the repo root::

    PYTHONPATH=src python -m kiniela.models.report

It writes ``docs/metrics-report.md``. The pure functions build the report and
render it as Markdown; only :func:`main` writes files or prints.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

import joblib
import numpy as np
from sklearn.base import clone
from sklearn.metrics import confusion_matrix
from sklearn.utils.class_weight import compute_sample_weight

from kiniela.config import CLASS_NAMES, N_CLASSES, RANDOM_STATE
from kiniela.models.ab_testing import CURRENT_CARD_NAME
from kiniela.models.ensembles import build_xgboost
from kiniela.models.final import build_modelling_dataset
from kiniela.models.metrics import ClassificationScores, score_multiclass
from kiniela.models.predict import DEFAULT_MODEL_PATH
from kiniela.models.train import CV_N_SPLITS, TARGET_COLUMN, prepare_xy, stratified_cv

REPORT_PATH = Path("docs") / "metrics-report.md"
EXAMPLES_PER_CONFUSION = 2


@dataclass(frozen=True)
class Confusion:
    """An off-diagonal pair of the confusion matrix, ordered by frequency."""

    true_class: int
    predicted_class: int
    count: int
    share_of_true_class: float


@dataclass(frozen=True)
class Example:
    """A real match behind a confusion, with its score and both class labels."""

    date: str
    home_team: str
    away_team: str
    home_goals: int
    away_goals: int
    true_class: int
    predicted_class: int


@dataclass(frozen=True)
class MetricsReport:
    """Everything the issue #8 asks to document, with its fixed scheme."""

    version: str
    n_samples: int
    n_history: int
    n_dropped: int
    card_f1_macro: float
    support: tuple[int, ...]
    scores: ClassificationScores
    matrix: tuple[tuple[int, ...], ...]
    importance: tuple[tuple[str, float], ...]
    confusions: tuple[Confusion, ...]
    examples: tuple[Example, ...]
    feature_columns: tuple[str, ...]

    @property
    def pooled_f1_macro(self) -> float:
        """Macro F1 of all out-of-fold predictions together (not the mean of folds)."""
        return float(np.mean(self.scores.f1))


def _out_of_fold_predictions(X: np.ndarray, y: np.ndarray, params: Any) -> np.ndarray:
    """Predict every row with a model that never saw that row during training."""
    estimator = build_xgboost(**params)
    predictions = np.empty(len(y), dtype=int)
    for train_index, test_index in stratified_cv().split(X, y):
        fold_model = clone(estimator)
        fold_model.fit(
            X[train_index],
            y[train_index],
            sample_weight=compute_sample_weight("balanced", y[train_index]),
        )
        predictions[test_index] = fold_model.predict(X[test_index])
    return predictions


def _top_confusions(matrix: np.ndarray, limit: int = 5) -> tuple[Confusion, ...]:
    """Off-diagonal pairs with the most mistakes, with their share of the true class."""
    pairs = [
        Confusion(
            true_class=true,
            predicted_class=predicted,
            count=int(matrix[true, predicted]),
            share_of_true_class=(
                float(matrix[true, predicted] / matrix[true].sum())
                if matrix[true].sum()
                else 0.0
            ),
        )
        for true in range(matrix.shape[0])
        for predicted in range(matrix.shape[1])
        if true != predicted and matrix[true, predicted] > 0
    ]
    pairs.sort(key=lambda item: (-item.count, item.true_class, item.predicted_class))
    return tuple(pairs[:limit])


def _examples(matches: Any, y: np.ndarray, predictions: np.ndarray,
              confusions: Sequence[Confusion], per_confusion: int) -> tuple[Example, ...]:
    """Pick real matches for the most frequent confusions, in dataset order."""
    examples: list[Example] = []
    for confusion in confusions:
        indexes = np.flatnonzero(
            (y == confusion.true_class) & (predictions == confusion.predicted_class)
        )[:per_confusion]
        for index in indexes:
            match = matches.iloc[index]
            examples.append(
                Example(
                    date=str(match["Date"])[:10],
                    home_team=str(match["HomeTeam"]),
                    away_team=str(match["AwayTeam"]),
                    home_goals=int(match["FTHG"]),
                    away_goals=int(match["FTAG"]),
                    true_class=confusion.true_class,
                    predicted_class=confusion.predicted_class,
                )
            )
    return tuple(examples)


def build_report(
    model_path: str | Path = DEFAULT_MODEL_PATH,
    card_path: str | Path | None = None,
    *,
    examples_per_confusion: int = EXAMPLES_PER_CONFUSION,
) -> MetricsReport:
    """Rebuild the dataset from the saved predictor and measure the serving model.

    Args:
        model_path: The app's ``MatchPredictor`` artefact, with the match history.
        card_path: Its metadata, with the tuned hyperparameters. Defaults to
            ``model_card.json`` next to the model.
        examples_per_confusion: Real matches to show for each frequent confusion.

    Returns:
        Accuracy, precision/recall/F1 per class, confusion matrix, most confused
        pairs with examples, and feature importance of the selected model.
    """
    path = Path(model_path)
    predictor = joblib.load(path)
    card_file = Path(card_path) if card_path is not None else path.parent / CURRENT_CARD_NAME
    card = json.loads(card_file.read_text(encoding="utf-8"))

    dataset = build_modelling_dataset(predictor.history)
    columns = list(predictor.feature_columns)
    X, y, n_dropped = prepare_xy(dataset, columns)

    predictions = _out_of_fold_predictions(X, y, card["params"])
    scores = score_multiclass(y, predictions)
    matrix = confusion_matrix(y, predictions, labels=list(range(N_CLASSES)))

    # Importance of the model trained on all usable rows, the one the app serves.
    final_model = build_xgboost(**card["params"], importance_type="gain")
    final_model.fit(X, y, sample_weight=compute_sample_weight("balanced", y))
    importance = tuple(
        sorted(zip(columns, final_model.feature_importances_), key=lambda item: -item[1])
    )

    # prepare_xy drops the first matchdays; keep the same rows for the examples.
    usable = dataset[columns + [TARGET_COLUMN]].dropna()
    matches = dataset.loc[usable.index].reset_index(drop=True)
    confusions = _top_confusions(matrix)
    examples = _examples(matches, y, predictions, confusions, examples_per_confusion)

    return MetricsReport(
        version=str(card["version"]),
        n_samples=len(y),
        n_history=len(dataset),
        n_dropped=n_dropped,
        card_f1_macro=float(card["metrics"]["f1_macro"]),
        support=tuple(int(count) for count in np.bincount(y, minlength=N_CLASSES)),
        scores=scores,
        matrix=tuple(tuple(int(value) for value in row) for row in matrix),
        importance=importance,
        confusions=confusions,
        examples=examples,
        feature_columns=tuple(columns),
    )


def _class_name(index: int) -> str:
    return f"{index} · {CLASS_NAMES[index]}"


def _num(value: float, digits: int = 3) -> str:
    """Spanish decimal separator, as in the rest of the report."""
    return f"{value:.{digits}f}".replace(".", ",")


def _pct(value: float, digits: int = 1) -> str:
    return _num(value * 100, digits) + " %"


def format_report(report: MetricsReport) -> str:
    """Render the metrics as Markdown. Pure function: it never prints or writes."""
    lines = [
        "# Informe de métricas del modelo seleccionado",
        "",
        f"**Modelo:** `{report.version}` · **Issue:** #8 · **Generado con** "
        "`python -m kiniela.models.report`",
        "",
        "Las métricas usan **predicciones fuera de fold** con "
        f"`StratifiedKFold(n_splits={CV_N_SPLITS}, shuffle=True, "
        f"random_state={RANDOM_STATE})`: cada partido se puntúa con un modelo que no lo "
        "vio al entrenar. Se usa la misma rejilla de hiperparámetros y los mismos pesos "
        "por clase que en la ficha del modelo. Las métricas de entrenamiento se excluyen "
        "a propósito.",
        "",
        f"Datos: {report.n_samples} partidos con historial de {report.n_history}; "
        f"{report.n_dropped} primeras jornadas descartadas por no tener features. "
        f"Features: {len(report.feature_columns)}.",
        "",
        "## Accuracy y métricas por clase",
        "",
        f"**Accuracy global: {_num(report.scores.accuracy, 4)}** "
        f"({_pct(report.scores.accuracy)} de los partidos bien clasificados).",
        "",
        "| Clase | Support | Precision | Recall | F1 |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for index in range(N_CLASSES):
        lines.append(
            f"| {_class_name(index)} | {report.support[index]} | "
            f"{_num(report.scores.precision[index])} | "
            f"{_num(report.scores.recall[index])} | "
            f"{_num(report.scores.f1[index])} |"
        )
    lines.extend(
        [
            f"| **Macro** | {sum(report.support)} | "
            f"{_num(float(np.mean(report.scores.precision)))} | "
            f"{_num(float(np.mean(report.scores.recall)))} | "
            f"**{_num(report.pooled_f1_macro)}** |",
            "",
            "El F1 macro de esta tabla se calcula sobre todas las predicciones fuera de "
            "fold a la vez. La ficha del modelo da la media de los F1 de los 5 folds "
            f"({_num(report.card_f1_macro, 4)}); son dos agregaciones distintas del mismo "
            "esquema, no dos modelos.",
            "",
            "## Matriz de confusión",
            "",
            "Filas = clase real, columnas = clase predicha.",
            "",
            "| Real \\ Predicha | " + " | ".join(str(index) for index in range(N_CLASSES)) + " |",
            "| --- | " + " | ".join("---:" for _ in range(N_CLASSES)) + " |",
        ]
    )
    for true in range(N_CLASSES):
        lines.append(
            f"| {_class_name(true)} | " + " | ".join(str(value) for value in report.matrix[true]) + " |"
        )
    lines.extend(
        [
            "",
            "## Clases más confundidas y ejemplos",
            "",
            "| Confusión | Partidos | % de la clase real |",
            "| --- | ---: | ---: |",
        ]
    )
    for confusion in report.confusions:
        lines.append(
            f"| {_class_name(confusion.true_class)} → "
            f"{_class_name(confusion.predicted_class)} | {confusion.count} | "
            f"{_pct(confusion.share_of_true_class)} |"
        )
    lines.extend(
        [
            "",
            "Ejemplos reales de las confusiones más frecuentes:",
            "",
            "| Fecha | Partido | Resultado | Clase real | Predicha |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for example in report.examples:
        lines.append(
            f"| {example.date} | {example.home_team} – {example.away_team} | "
            f"{example.home_goals}-{example.away_goals} | "
            f"{_class_name(example.true_class)} | {_class_name(example.predicted_class)} |"
        )
    most_missed = min(range(N_CLASSES), key=lambda index: report.scores.recall[index])
    least_precise = min(range(N_CLASSES), key=lambda index: report.scores.precision[index])
    lines.extend(
        [
            "",
            "### Lectura de errores",
            "",
            f"La clase {most_missed} ({CLASS_NAMES[most_missed]}) es la que más se pierde: "
            f"solo se recupera {_pct(report.scores.recall[most_missed])} de sus partidos. "
            f"La clase {least_precise} ({CLASS_NAMES[least_precise]}) es la menos fiable "
            f"cuando se predice: solo {_pct(report.scores.precision[least_precise])} de "
            "esos pronósticos aciertan. El modelo cae con frecuencia en las victorias "
            "claras cuando no distingue entre el resto de clases.",
            "",
            "## Feature importance",
            "",
            "Importancia `gain` del modelo entrenado con todas las filas útiles "
            "(el que se sirve en la app):",
            "",
            "| Feature | Gain |",
            "| --- | ---: |",
        ]
    )
    for feature, value in report.importance:
        lines.append(f"| `{feature}` | {_num(value, 4)} |")
    lines.extend(
        [
            "",
            "## Límites",
            "",
            "- La matriz y las métricas por clase son de validación fuera de fold, no de "
            "partidos futuros: retratan el rendimiento esperado sobre datos de la misma "
            "distribución (Premier League 2015-16 a 2023-24).",
            "- Los ejemplos son partidos reales del histórico; no permiten explicar por "
            "qué el modelo se equivocó en cada uno, solo dónde se concentra el error.",
            "- Solo hay 8 features de forma y goles, sin tiros, lesiones ni alineaciones.",
            "",
        ]
    )
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entry point: ``python -m kiniela.models.report``."""
    parser = argparse.ArgumentParser(description="Generate the issue #8 metrics report.")
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL_PATH,
                        help="MatchPredictor artefact of the serving model.")
    parser.add_argument("--card", type=Path, default=None,
                        help="Model card with the tuned params (next to the model by default).")
    parser.add_argument("--output", type=Path, default=REPORT_PATH,
                        help="Markdown file to write.")
    args = parser.parse_args(argv)
    report = build_report(args.model, args.card)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(format_report(report), encoding="utf-8")
    print(f"Wrote {args.output} (accuracy {report.scores.accuracy:.4f}, "
          f"{report.n_samples} matches).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
