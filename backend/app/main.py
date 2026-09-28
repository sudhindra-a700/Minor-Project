from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.config import CORS_ORIGINS
from backend.app.routes import fhe, monitoring

app = FastAPI(
    title="Minor Project FHE API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(fhe.router)
app.include_router(monitoring.router)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "model_task": "credit-risk classification",
        "privacy": "FHE",
        "optimizer": "SAC",
    }
