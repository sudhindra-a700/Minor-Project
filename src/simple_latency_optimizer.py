"""Simple reusable practice code for FHE latency optimization.

This is a planning and profiling prototype. It does not implement encryption,
bootstrapping, or a Concrete ML compiler pass. Replace the example timing values
with measurements from the real FHE model when the team has that environment.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Iterable


@dataclass(frozen=True)
class CandidateMethod:
    """One possible way to reduce inference latency."""

    name: str
    baseline_ms: float
    candidate_ms: float
    accuracy: float
    accuracy_floor: float = 0.95
    supported: bool = True
    effort: int = 1  # 1 = easy, 5 = difficult
    notes: str = ""

    @property
    def speedup(self) -> float:
        if self.candidate_ms <= 0:
            raise ValueError("candidate_ms must be positive")
        return self.baseline_ms / self.candidate_ms

    @property
    def latency_reduction_percent(self) -> float:
        return (1.0 - self.candidate_ms / self.baseline_ms) * 100.0

    @property
    def feasible(self) -> bool:
        return (
            self.supported
            and self.candidate_ms > 0
            and self.accuracy >= self.accuracy_floor
        )

    def score(self) -> float:
        """Prefer fast, accurate, supported, and low-effort candidates."""
        if not self.feasible:
            return float("-inf")
        accuracy_margin = self.accuracy - self.accuracy_floor
        return self.speedup + accuracy_margin - (0.05 * self.effort)

    def to_dict(self) -> dict[str, object]:
        return {
            **asdict(self),
            "speedup": round(self.speedup, 3),
            "latency_reduction_percent": round(self.latency_reduction_percent, 2),
            "feasible": self.feasible,
            "score": round(self.score(), 3) if self.feasible else None,
        }


def rank_methods(methods: Iterable[CandidateMethod]) -> list[CandidateMethod]:
    """Return feasible methods first, ordered by the transparent score."""
    return sorted(
        methods,
        key=lambda method: (method.feasible, method.score()),
        reverse=True,
    )


def choose_method(methods: Iterable[CandidateMethod]) -> CandidateMethod:
    ranked = rank_methods(methods)
    if not ranked or not ranked[0].feasible:
        raise ValueError("no supported candidate satisfies the accuracy constraint")
    return ranked[0]


def print_report(methods: Iterable[CandidateMethod]) -> None:
    ranked = rank_methods(methods)
    print("FHE latency-optimization practice report")
    print("-" * 42)
    for position, method in enumerate(ranked, start=1):
        status = "FEASIBLE" if method.feasible else "REJECTED"
        print(f"{position}. {method.name}: {status}")
        print(f"   baseline: {method.baseline_ms:.2f} ms")
        print(f"   candidate: {method.candidate_ms:.2f} ms")
        print(f"   accuracy: {method.accuracy:.3f}")
        print(f"   speedup: {method.speedup:.2f}x")
        print(f"   reason: {method.notes}")

    selected = choose_method(ranked)
    print("\nSelected practice candidate:")
    print(f"{selected.name} ({selected.speedup:.2f}x estimated speedup)")
    print("Replace the example timings with real FHE measurements before reporting results.")


def example_methods() -> tuple[CandidateMethod, ...]:
    """Example values only; they demonstrate the selection logic."""
    return (
        CandidateMethod(
            name="baseline Concrete ML configuration",
            baseline_ms=100.0,
            candidate_ms=100.0,
            accuracy=0.98,
            effort=1,
            notes="Reference configuration for comparison.",
        ),
        CandidateMethod(
            name="representative calibration",
            baseline_ms=100.0,
            candidate_ms=92.0,
            accuracy=0.98,
            effort=2,
            notes="Candidate to test by compiling with a representative calibration set.",
        ),
        CandidateMethod(
            name="supported lower-bit quantization",
            baseline_ms=100.0,
            candidate_ms=78.0,
            accuracy=0.97,
            effort=3,
            notes="Candidate to test only if the selected Concrete ML release supports it.",
        ),
        CandidateMethod(
            name="native bootstrapping modification",
            baseline_ms=100.0,
            candidate_ms=55.0,
            accuracy=0.96,
            supported=False,
            effort=5,
            notes="Rejected for this practice prototype because it requires backend changes.",
        ),
        CandidateMethod(
            name="unsafe low-bit candidate",
            baseline_ms=100.0,
            candidate_ms=60.0,
            accuracy=0.88,
            effort=2,
            notes="Rejected because it fails the accuracy floor.",
        ),
    )


if __name__ == "__main__":
    print_report(example_methods())
