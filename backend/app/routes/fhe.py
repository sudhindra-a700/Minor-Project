from fastapi import APIRouter, File, HTTPException, Response, UploadFile

from backend.app.services.fhe_server import fhe_server_service
from backend.app.services.monitoring_service import store
from src.monitoring.profiler import profile_callable

router = APIRouter(prefix="/api/fhe", tags=["FHE"])


@router.get("/status")
def status():
    try:
        fhe_server_service.load()
        return {
            "status": "ready",
            "framework": "Concrete ML",
            "execution": "server-side FHE",
        }
    except Exception as exc:
        return {"status": "not_ready", "detail": str(exc)}


@router.post("/predict")
async def predict(
    encrypted_data: UploadFile = File(...),
    evaluation_keys: UploadFile = File(...),
):
    encrypted_bytes = await encrypted_data.read()
    evaluation_key_bytes = await evaluation_keys.read()

    if not encrypted_bytes or not evaluation_key_bytes:
        raise HTTPException(
            400,
            "encrypted_data and evaluation_keys are required",
        )

    try:
        encrypted_result, run, samples = profile_callable(
            fhe_server_service.run,
            encrypted_bytes,
            evaluation_key_bytes,
            stage="fhe_server_inference",
            metadata={
                "framework": "Concrete ML",
                "optimization": "SAC",
            },
        )
        store.save_run(run, samples)

        return Response(
            content=encrypted_result,
            media_type="application/octet-stream",
            headers={
                "X-FHE-Run-Id": run["run_id"],
                "X-FHE-Latency-Seconds": str(run["latency_s"]),
                "X-Peak-CPU-Percent": str(
                    run.get("peak_system_cpu_percent", 0)
                ),
                "X-Peak-RAM-MB": str(
                    run.get("peak_process_rss_mb", 0)
                ),
            },
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"FHE inference failed: {exc}",
        )
