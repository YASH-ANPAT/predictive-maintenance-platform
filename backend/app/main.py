from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from app.database.database import engine

from app.database.base import Base
from app.models import Equipment

from app.api.equipment import router as equipment_router
from app.api.maintenance import router as maintenance_router
from app.api.prediction import router as prediction_router
from app.api.telemetry import router as telemetry_router
from app.ml.model_loader import load_model

app = FastAPI(
    title="Predictive Equipment Maintenance Platform API",
    description=(
        "REST API for equipment management, telemetry ingestion, "
        "maintenance records, and predictive maintenance."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(equipment_router)
app.include_router(maintenance_router)
app.include_router(prediction_router)
app.include_router(telemetry_router)


@app.on_event("startup")
def load_ml_model_on_startup() -> None:
    """Load the trained ML model once when the API process starts."""
    load_model()


@app.get("/", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "message": "Predictive Equipment Maintenance Platform API is running",
        "version": "1.0.0",
    }


@app.get("/db-test", tags=["Health"])
def database_connection_test():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))

        return {
            "database": "connected",
            "result": result.scalar(),
        }