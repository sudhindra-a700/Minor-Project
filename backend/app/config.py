from pathlib import Path
import os

REPO_ROOT = Path(__file__).resolve().parents[2]

FHE_DEPLOYMENT_DIR = Path(
    os.getenv(
        "FHE_DEPLOYMENT_DIR",
        str(REPO_ROOT / "model" / "fhe_deployment"),
    )
)

MONITORING_DIR = os.getenv(
    "MONITORING_DIR",
    str(REPO_ROOT / "monitoring_results"),
)

CORS_ORIGINS = [
    item.strip()
    for item in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000,http://localhost:5173",
    ).split(",")
    if item.strip()
]
