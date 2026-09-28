from backend.app.config import MONITORING_DIR
from src.monitoring.metrics_store import MetricsStore

store = MetricsStore(MONITORING_DIR)
