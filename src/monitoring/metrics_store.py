from __future__ import annotations

import csv
import json
import threading
from pathlib import Path


class MetricsStore:
    """Simple CSV/JSON store for local experiments and one-instance deployments."""

    def __init__(self, directory: str = "monitoring_results"):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        self.runs_csv = self.directory / "runs.csv"
        self._lock = threading.Lock()

    def save_run(self, run: dict, samples: list[dict]) -> None:
        with self._lock:
            exists = self.runs_csv.exists()
            with self.runs_csv.open("a", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=list(run.keys()))
                if not exists:
                    writer.writeheader()
                writer.writerow(run)

            (self.directory / f"{run['run_id']}.json").write_text(
                json.dumps({"run": run, "samples": samples}, indent=2),
                encoding="utf-8",
            )

    def history(self, limit: int = 100) -> list[dict]:
        if not self.runs_csv.exists():
            return []
        with self.runs_csv.open("r", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        rows.reverse()
        return rows[: max(1, min(limit, 1000))]

    def latest(self):
        rows = self.history(1)
        return rows[0] if rows else None

    def get_run(self, run_id: str):
        path = self.directory / f"{run_id}.json"
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))
