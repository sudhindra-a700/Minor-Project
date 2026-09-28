from __future__ import annotations

import csv
import json
import threading
from pathlib import Path


class MetricsStore:
    """File-backed metrics store for local experiments and one-instance deployments."""

    def __init__(self, directory: str = "monitoring_results"):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        self.runs_csv = self.directory / "runs.csv"
        self._lock = threading.Lock()

    def _read_csv_rows(self) -> tuple[list[str], list[dict]]:
        if not self.runs_csv.exists():
            return [], []

        with self.runs_csv.open("r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return list(reader.fieldnames or []), list(reader)

    def _write_csv_rows(self, fieldnames: list[str], rows: list[dict]) -> None:
        with self.runs_csv.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(rows)

    def save_run(self, run: dict, samples: list[dict]) -> None:
        with self._lock:
            # JSON is the canonical typed record for the run.
            (self.directory / f"{run['run_id']}.json").write_text(
                json.dumps({"run": run, "samples": samples}, indent=2),
                encoding="utf-8",
            )

            # Keep CSV convenient for analysis while safely handling runs whose
            # metadata fields differ (for example dummy test vs SAC inference).
            existing_fields, existing_rows = self._read_csv_rows()

            if not existing_fields:
                fieldnames = list(run.keys())
                self._write_csv_rows(fieldnames, [run])
                return

            fieldnames = list(existing_fields)
            for key in run.keys():
                if key not in fieldnames:
                    fieldnames.append(key)

            if fieldnames != existing_fields:
                self._write_csv_rows(fieldnames, [*existing_rows, run])
            else:
                with self.runs_csv.open("a", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(
                        f,
                        fieldnames=fieldnames,
                        extrasaction="ignore",
                    )
                    writer.writerow(run)

    def history(self, limit: int = 100) -> list[dict]:
        if not self.runs_csv.exists():
            return []

        _, rows = self._read_csv_rows()
        rows.reverse()
        selected = rows[: max(1, min(limit, 1000))]

        # Return the typed JSON summary whenever available, rather than CSV
        # strings. This is friendlier for frontend charting.
        result = []
        for row in selected:
            run_id = row.get("run_id")
            path = self.directory / f"{run_id}.json" if run_id else None
            if path is not None and path.exists():
                try:
                    result.append(
                        json.loads(path.read_text(encoding="utf-8"))["run"]
                    )
                    continue
                except (json.JSONDecodeError, KeyError):
                    pass
            result.append(row)

        return result

    def latest(self):
        rows = self.history(1)
        return rows[0] if rows else None

    def get_run(self, run_id: str):
        path = self.directory / f"{run_id}.json"
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))
