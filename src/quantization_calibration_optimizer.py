"""Small practice optimizer for calibration and quantization.

The module has two purposes:
1. build a representative calibration set and quantization ranges; and
2. select the fastest measured candidate that keeps the accuracy constraint.

It does not compile or execute an FHE circuit. Replace the example profile
values with measurements from the team's Concrete ML-compatible model.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np


@dataclass(frozen=True)
class CalibrationRange:
    """Per-feature range learned from representative cleartext samples."""

    minimum: np.ndarray
    maximum: np.ndarray


def make_representative_calibration(
    X: np.ndarray,
    sample_size: int = 128,
) -> np.ndarray:
    """Select deterministic, evenly spaced samples for compilation calibration."""
    X = np.asarray(X, dtype=np.float64)
    if X.ndim != 2 or X.shape[0] == 0:
        raise ValueError("X must be a non-empty 2D array")
    sample_size = min(max(1, sample_size), X.shape[0])
    indices = np.linspace(0, X.shape[0] - 1, sample_size, dtype=int)
    return X[indices]


def learn_ranges(calibration: np.ndarray) -> CalibrationRange:
    """Learn feature ranges from the representative calibration set."""
    calibration = np.asarray(calibration, dtype=np.float64)
    if calibration.ndim != 2 or calibration.shape[0] == 0:
        raise ValueError("calibration must be a non-empty 2D array")
    minimum = calibration.min(axis=0)
    maximum = calibration.max(axis=0)
    # A constant feature still needs a non-zero range for quantization.
    maximum = np.where(maximum == minimum, minimum + 1.0, maximum)
    return CalibrationRange(minimum=minimum, maximum=maximum)


def quantize(X: np.ndarray, ranges: CalibrationRange, n_bits: int) -> np.ndarray:
    """Quantize values to unsigned integers using learned feature ranges."""
    if n_bits < 2 or n_bits > 16:
        raise ValueError("n_bits must be between 2 and 16")
    X = np.asarray(X, dtype=np.float64)
    if X.ndim != 2 or X.shape[1] != ranges.minimum.size:
        raise ValueError("X has an incompatible feature shape")
    qmax = (1 << n_bits) - 1
    scale = qmax / (ranges.maximum - ranges.minimum)
    return np.rint(np.clip((X - ranges.minimum) * scale, 0, qmax)).astype(np.int64)


def dequantize(qX: np.ndarray, ranges: CalibrationRange, n_bits: int) -> np.ndarray:
    """Reconstruct approximate cleartext values for an error check."""
    qmax = (1 << n_bits) - 1
    scale = (ranges.maximum - ranges.minimum) / qmax
    return qX * scale + ranges.minimum


def mean_absolute_quantization_error(
    X: np.ndarray,
    ranges: CalibrationRange,
    n_bits: int,
) -> float:
    """Return a simple numerical distortion measure for practice experiments."""
    qX = quantize(X, ranges, n_bits)
    reconstructed = dequantize(qX, ranges, n_bits)
    return float(np.mean(np.abs(np.asarray(X, dtype=float) - reconstructed)))


@dataclass(frozen=True)
class MeasuredCandidate:
    """One measured model configuration to compare after compilation."""

    name: str
    n_bits: int
    calibration_size: int
    latency_ms: float | None
    accuracy: float | None

    def passes_accuracy(self, baseline_accuracy: float, allowed_drop: float) -> bool:
        return self.accuracy is not None and self.accuracy >= baseline_accuracy - allowed_drop


def choose_fastest_valid(
    candidates: Iterable[MeasuredCandidate],
    baseline_accuracy: float,
    allowed_accuracy_drop: float = 0.01,
) -> MeasuredCandidate:
    """Choose the fastest measured candidate that meets the accuracy constraint."""
    valid = [
        candidate
        for candidate in candidates
        if candidate.latency_ms is not None
        and candidate.latency_ms > 0
        and candidate.passes_accuracy(baseline_accuracy, allowed_accuracy_drop)
    ]
    if not valid:
        raise ValueError("no measured candidate satisfies the accuracy constraint")
    return min(valid, key=lambda candidate: candidate.latency_ms)


def practice_run() -> None:
    """Run a tiny example; timing values are illustrative, not FHE results."""
    X = np.array(
        [
            [0.1, 10.0, 100.0],
            [0.2, 12.0, 105.0],
            [0.4, 14.0, 110.0],
            [0.5, 16.0, 120.0],
            [0.8, 18.0, 130.0],
            [1.0, 20.0, 140.0],
        ],
        dtype=float,
    )
    calibration = make_representative_calibration(X, sample_size=4)
    ranges = learn_ranges(calibration)
    error_8bit = mean_absolute_quantization_error(X, ranges, n_bits=8)
    error_6bit = mean_absolute_quantization_error(X, ranges, n_bits=6)

    # Replace these example values with real compiled-model measurements.
    candidates = [
        MeasuredCandidate("8-bit baseline + representative calibration", 8, 4, 100.0, 0.980),
        MeasuredCandidate("6-bit candidate + representative calibration", 6, 4, 82.0, 0.975),
        MeasuredCandidate("4-bit candidate + representative calibration", 4, 4, 65.0, 0.910),
    ]
    selected = choose_fastest_valid(candidates, baseline_accuracy=0.980, allowed_accuracy_drop=0.010)

    print("Calibration size:", len(calibration))
    print("8-bit quantization error:", round(error_8bit, 5))
    print("6-bit quantization error:", round(error_6bit, 5))
    print("Selected candidate:", selected.name)
    print("Illustrative latency:", selected.latency_ms, "ms")
    print("Replace illustrative values before reporting project results.")


if __name__ == "__main__":
    practice_run()
