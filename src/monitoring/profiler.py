from __future__ import annotations

import time
import uuid
from datetime import datetime, timezone
from typing import Any, Callable

from .resource_monitor import ResourceMonitor


def profile_callable(
    fn: Callable,
    *args,
    stage: str,
    sample_interval: float = 0.10,
    metadata: dict[str, Any] | None = None,
    **kwargs,
):
    """Run one callable while measuring wall time, CPU and RAM."""

    monitor = ResourceMonitor(interval=sample_interval)
    monitor.start()
    start = time.perf_counter()

    try:
        result = fn(*args, **kwargs)
    finally:
        elapsed = time.perf_counter() - start
        monitor.stop()

    run = {
        "run_id": uuid.uuid4().hex,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "stage": stage,
        "latency_s": round(elapsed, 6),
        **monitor.summary(),
        **(metadata or {}),
    }

    return result, run, monitor.as_dicts()
