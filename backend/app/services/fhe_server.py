from pathlib import Path
from threading import Lock

from backend.app.config import FHE_DEPLOYMENT_DIR


class FHEServerService:
    """Load and run Concrete ML's server-side deployment artifact."""

    def __init__(self, deployment_dir: Path = FHE_DEPLOYMENT_DIR):
        self.deployment_dir = Path(deployment_dir)
        self._server = None
        self._lock = Lock()

    def load(self):
        with self._lock:
            if self._server is None:
                if not self.deployment_dir.exists():
                    raise FileNotFoundError(
                        f"FHE deployment directory not found: {self.deployment_dir}"
                    )

                # Import lazily so /health and monitoring endpoints can still
                # start even before Concrete ML is installed/configured.
                try:
                    from concrete.ml.deployment import FHEModelServer
                except ImportError as exc:
                    raise RuntimeError(
                        "Concrete ML is not installed. Install the exact version "
                        "used to export the deployment artifacts."
                    ) from exc

                server = FHEModelServer(path_dir=str(self.deployment_dir))
                server.load()
                self._server = server

        return self._server

    def run(self, encrypted_data: bytes, evaluation_keys: bytes) -> bytes:
        server = self.load()
        with self._lock:
            return server.run(encrypted_data, evaluation_keys)


fhe_server_service = FHEServerService()
