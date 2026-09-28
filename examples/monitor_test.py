"""Standalone smoke test for the monitoring subsystem."""

import math
import sys
import time
from pathlib import Path

# Allow both:
#   python examples/monitor_test.py
# and:
#   python -m examples.monitor_test
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.monitoring.metrics_store import MetricsStore
from src.monitoring.profiler import profile_callable


def dummy_fhe_workload():
    total = 0.0
    end = time.perf_counter() + 2.0
    while time.perf_counter() < end:
        for i in range(20000):
            total += math.sqrt((i % 1000) + 1)
    return total


if __name__ == "__main__":
    result, run, samples = profile_callable(
        dummy_fhe_workload,
        stage="monitor_smoke_test",
        metadata={"optimization": "none", "framework": "dummy"},
    )

    store = MetricsStore("monitoring_results")
    store.save_run(run, samples)

    print("Workload result:", result)
    print("Run summary:")
    for key, value in run.items():
        print(f"  {key}: {value}")
    print(f"Saved {len(samples)} resource samples.")
