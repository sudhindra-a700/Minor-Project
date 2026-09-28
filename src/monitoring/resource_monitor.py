from __future__ import annotations

import os
import threading
import time
from dataclasses import dataclass, asdict
import psutil


@dataclass
class ResourceSample:
    elapsed_s: float
    system_cpu_percent: float
    process_cpu_percent: float
    process_rss_mb: float
    system_ram_percent: float
    process_threads: int


class ResourceMonitor:
    """Continuously sample CPU/RAM for the process running FHE inference."""

    def __init__(self, interval: float = 0.10):
        self.interval = max(0.05, float(interval))
        self.process = psutil.Process(os.getpid())
        self.samples: list[ResourceSample] = []
        self._start = 0.0
        self._thread: threading.Thread | None = None
        self._stop = threading.Event()

    def _loop(self) -> None:
        psutil.cpu_percent(interval=None)
        self.process.cpu_percent(interval=None)

        while not self._stop.is_set():
            try:
                vm = psutil.virtual_memory()
                self.samples.append(
                    ResourceSample(
                        elapsed_s=time.perf_counter() - self._start,
                        system_cpu_percent=psutil.cpu_percent(interval=None),
                        process_cpu_percent=self.process.cpu_percent(interval=None),
                        process_rss_mb=self.process.memory_info().rss / (1024 ** 2),
                        system_ram_percent=vm.percent,
                        process_threads=self.process.num_threads(),
                    )
                )
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

            self._stop.wait(self.interval)

    def start(self) -> None:
        self.samples = []
        self._stop.clear()
        self._start = time.perf_counter()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=2)
        self._thread = None

    def summary(self) -> dict:
        if not self.samples:
            return {}

        def values(name: str) -> list[float]:
            return [getattr(x, name) for x in self.samples]

        def avg(items: list[float]) -> float:
            return sum(items) / len(items)

        system_cpu = values("system_cpu_percent")
        process_cpu = values("process_cpu_percent")
        rss = values("process_rss_mb")
        ram = values("system_ram_percent")

        return {
            "sample_count": len(self.samples),
            "avg_system_cpu_percent": round(avg(system_cpu), 3),
            "peak_system_cpu_percent": round(max(system_cpu), 3),
            "avg_process_cpu_percent": round(avg(process_cpu), 3),
            "peak_process_cpu_percent": round(max(process_cpu), 3),
            "avg_process_rss_mb": round(avg(rss), 3),
            "peak_process_rss_mb": round(max(rss), 3),
            "avg_system_ram_percent": round(avg(ram), 3),
            "peak_system_ram_percent": round(max(ram), 3),
            "peak_threads": max(x.process_threads for x in self.samples),
        }

    def as_dicts(self) -> list[dict]:
        return [asdict(x) for x in self.samples]
