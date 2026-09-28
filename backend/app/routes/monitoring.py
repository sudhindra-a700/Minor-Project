from fastapi import APIRouter, HTTPException, Query

from backend.app.services.monitoring_service import store

router = APIRouter(prefix="/api/monitor", tags=["Monitoring"])


@router.get("/latest")
def latest():
    value = store.latest()
    if value is None:
        raise HTTPException(404, "No monitoring runs have been recorded yet")
    return value


@router.get("/history")
def history(limit: int = Query(50, ge=1, le=1000)):
    return store.history(limit)


@router.get("/run/{run_id}")
def run_details(run_id: str):
    value = store.get_run(run_id)
    if value is None:
        raise HTTPException(404, "Run not found")
    return value
