"""Population Stability Index (PSI) drift between training data and a new batch.

Issue #14: compare the numeric modelling features of a **reference** CSV
(the training set) with a **current** CSV (new matches). The method is PSI
with ten quantile bins taken from the reference; a feature has drifted when
its PSI is at least :data:`PSI_DRIFT_THRESHOLD` (0.20). The batch has drifted
when **any** feature crosses that threshold.

How to read PSI (the same cut-offs used in credit-risk monitoring):

- below 0.10: no material shift
- 0.10 to 0.20: slight shift, watch it
- 0.20 or more: drift

The mean and standard deviation of each feature are reported as extra
evidence; they do not decide the flag.

Run it again with::

    PYTHONPATH=src python -m kiniela.monitoring.drift \\
        --reference data/processed/modelling.csv \\
        --current data/processed/new_batch.csv
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from kiniela.models.train import TARGET_COLUMN, feature_columns

PSI_DRIFT_THRESHOLD = 0.20
PSI_SLIGHT_THRESHOLD = 0.10
N_BINS = 10
# Floor every bin share so ``log`` never sees zero when a bin is empty.
_PSI_FLOOR = 1e-4


@dataclass(frozen=True)
class FeatureDrift:
    """PSI and summary stats of one numeric feature."""

    name: str
    psi: float
    drifted: bool
    reference_mean: float
    current_mean: float
    reference_std: float
    current_std: float


@dataclass(frozen=True)
class DriftReport:
    """Per-feature PSI plus the global yes/no flag."""

    n_reference: int
    n_current: int
    features: tuple[FeatureDrift, ...]
    threshold: float = PSI_DRIFT_THRESHOLD

    @property
    def drifted(self) -> bool:
        """True when at least one feature has PSI at or above the threshold."""
        return any(feature.drifted for feature in self.features)

    def to_dict(self) -> dict:
        """JSON-friendly copy of the report."""
        return {
            "drifted": self.drifted,
            "threshold": self.threshold,
            "n_reference": self.n_reference,
            "n_current": self.n_current,
            "features": [
                {
                    "name": feature.name,
                    "psi": feature.psi,
                    "drifted": feature.drifted,
                    "reference_mean": feature.reference_mean,
                    "current_mean": feature.current_mean,
                    "reference_std": feature.reference_std,
                    "current_std": feature.current_std,
                }
                for feature in self.features
            ],
        }


def _load_numeric(path: Path) -> pd.DataFrame:
    if not path.is_file():
        raise FileNotFoundError(f"No dataset at {path}.")
    return pd.read_csv(path)


def _shared_columns(reference: pd.DataFrame, current: pd.DataFrame) -> list[str]:
    """Numeric modelling features present in both frames, same order as training."""
    reference_columns = feature_columns(
        reference if TARGET_COLUMN in reference.columns else reference.assign(**{TARGET_COLUMN: 0})
    )
    current_names = set(current.columns)
    columns = [column for column in reference_columns if column in current_names]
    if not columns:
        raise ValueError(
            "No shared numeric modelling features. Both CSVs need the same "
            "feature columns as the modelling dataset."
        )
    return columns


def _bin_edges(reference: np.ndarray) -> np.ndarray:
    """Ten quantile edges from the reference, open at both ends."""
    finite = reference[np.isfinite(reference)]
    if finite.size == 0:
        return np.array([-np.inf, np.inf])
    unique = np.unique(finite)
    if unique.size == 1:
        value = float(unique[0])
        return np.array([-np.inf, value, np.inf])
    quantiles = np.linspace(0.0, 1.0, N_BINS + 1)
    edges = np.quantile(finite, quantiles)
    edges = np.unique(edges)
    edges[0] = -np.inf
    edges[-1] = np.inf
    if edges.size < 2:
        return np.array([-np.inf, np.inf])
    return edges


def _shares(values: np.ndarray, edges: np.ndarray) -> np.ndarray:
    finite = values[np.isfinite(values)]
    if finite.size == 0:
        counts = np.zeros(len(edges) - 1, dtype=float)
    else:
        counts = np.histogram(finite, bins=edges)[0].astype(float)
    total = counts.sum()
    if total == 0:
        shares = np.full(len(counts), 1.0 / len(counts))
    else:
        shares = counts / total
    return np.clip(shares, _PSI_FLOOR, None)


def population_stability_index(reference: np.ndarray, current: np.ndarray) -> float:
    """PSI of ``current`` against ``reference`` using quantile bins of the latter."""
    edges = _bin_edges(reference)
    expected = _shares(reference, edges)
    actual = _shares(current, edges)
    return float(np.sum((actual - expected) * np.log(actual / expected)))


def compare_features(
    reference: pd.DataFrame, current: pd.DataFrame, columns: list[str]
) -> tuple[FeatureDrift, ...]:
    """PSI and moments of every shared feature, dropping rows with missing values."""
    results: list[FeatureDrift] = []
    for column in columns:
        ref_values = pd.to_numeric(reference[column], errors="coerce").to_numpy()
        cur_values = pd.to_numeric(current[column], errors="coerce").to_numpy()
        ref_finite = ref_values[np.isfinite(ref_values)]
        cur_finite = cur_values[np.isfinite(cur_values)]
        psi = population_stability_index(ref_finite, cur_finite)
        results.append(
            FeatureDrift(
                name=column,
                psi=psi,
                drifted=psi >= PSI_DRIFT_THRESHOLD,
                reference_mean=float(np.mean(ref_finite)) if ref_finite.size else float("nan"),
                current_mean=float(np.mean(cur_finite)) if cur_finite.size else float("nan"),
                reference_std=float(np.std(ref_finite)) if ref_finite.size else float("nan"),
                current_std=float(np.std(cur_finite)) if cur_finite.size else float("nan"),
            )
        )
    return tuple(results)


def compute_drift(reference_path: str | Path, current_path: str | Path) -> DriftReport:
    """Compare the modelling features of two CSVs and return the drift report."""
    reference = _load_numeric(Path(reference_path))
    current = _load_numeric(Path(current_path))
    columns = _shared_columns(reference, current)
    return DriftReport(
        n_reference=len(reference),
        n_current=len(current),
        features=compare_features(reference, current, columns),
    )


def drift_report(reference_path: str, current_path: str) -> dict:
    """Compare features of the reference set with a new batch. Returns a dict."""
    return compute_drift(reference_path, current_path).to_dict()


def format_drift_report(
    report: DriftReport, reference_path: str | Path, current_path: str | Path
) -> str:
    """Readable PSI table. Pure function: it never prints."""
    flag = "YES" if report.drifted else "NO"
    lines = [
        "Data drift report (Population Stability Index)",
        f"  method: PSI with {N_BINS} quantile bins from the reference",
        f"  threshold: a feature has drifted when PSI >= {report.threshold:.2f}; "
        "the batch has drifted when any feature has",
        f"  reference: {reference_path} ({report.n_reference} rows)",
        f"  current:   {current_path} ({report.n_current} rows)",
        f"  global drift: {flag}",
        "",
        f"  {'feature':<32}{'PSI':<12}{'drift':<8}{'ref mean':<12}{'cur mean'}",
    ]
    for feature in report.features:
        lines.append(
            f"  {feature.name:<32}{feature.psi:<12.4f}"
            f"{('YES' if feature.drifted else 'no'):<8}"
            f"{feature.reference_mean:<12.3f}{feature.current_mean:.3f}"
        )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point: ``python -m kiniela.monitoring.drift --reference ... --current ...``."""
    parser = argparse.ArgumentParser(
        description="Detect data drift with PSI between a reference CSV and a new batch (issue #14)."
    )
    parser.add_argument(
        "--reference",
        required=True,
        help="Training CSV (modelling features of issue #3).",
    )
    parser.add_argument(
        "--current",
        required=True,
        help="New batch CSV with the same feature columns.",
    )
    args = parser.parse_args(argv)
    report = compute_drift(args.reference, args.current)
    print(format_drift_report(report, args.reference, args.current))
    return 1 if report.drifted else 0


if __name__ == "__main__":
    raise SystemExit(main())
