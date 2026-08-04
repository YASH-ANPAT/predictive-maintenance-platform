from fastapi import FastAPI
from sqlalchemy import text
from app.database.database import engine

from app.database.base import Base
from app.models import Equipment

app = FastAPI(
    title="Predictive Equipment Maintenance Platform API",
    description=(
        "REST API for equipment management, telemetry ingestion, "
        "maintenance records, and predictive maintenance."
    ),
    version="1.0.0",
)

Base.metadata.create_all(bind=engine)


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