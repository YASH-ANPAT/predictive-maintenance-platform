from typing import Any

from sqlalchemy.orm import Session

from app.crud.equipment import get_equipment_by_id
from app.crud.prediction import (
    get_latest_prediction,
    get_prediction_history,
)
from app.models.prediction import Prediction
from app.services.telemetry_service import get_latest_telemetry

PREDICTION_INPUT_FIELDS = (
    "air_temperature",
    "process_temperature",
    "rotational_speed",
    "torque",
    "tool_wear",
)


def _validate_equipment_exists(db: Session, equipment_id: int) -> None:
    """Validate that an equipment record exists before service processing."""
    if get_equipment_by_id(db, equipment_id) is None:
        raise ValueError("Equipment not found")


def prepare_prediction_input(db: Session, equipment_id: int) -> dict[str, Any]:
    """Build a model input payload from the latest equipment telemetry."""
    latest_telemetry = get_latest_telemetry(db, equipment_id)
    if latest_telemetry is None:
        raise ValueError("No telemetry found for equipment")

    return {
        "equipment_id": equipment_id,
        "telemetry_id": latest_telemetry.id,
        "recorded_at": latest_telemetry.recorded_at,
        "machine_type": latest_telemetry.equipment.machine_type,
        "features": {
            field: getattr(latest_telemetry, field)
            for field in PREDICTION_INPUT_FIELDS
        },
    }


def generate_maintenance_recommendation(
    failure_probability: float,
    predicted_failure: bool,
) -> str:
    """Generate a maintenance recommendation from prediction results."""
    if not 0 <= failure_probability <= 1:
        raise ValueError("failure_probability must be between 0 and 1")

    if predicted_failure or failure_probability >= 0.8:
        return "Immediate maintenance inspection recommended."
    if failure_probability >= 0.5:
        return "Schedule preventive maintenance soon."
    if failure_probability >= 0.25:
        return "Monitor equipment closely and review upcoming maintenance."
    return "No immediate maintenance action required."


def get_latest_equipment_prediction(
    db: Session,
    equipment_id: int,
) -> Prediction | None:
    """Return the latest prediction for an existing equipment item."""
    _validate_equipment_exists(db, equipment_id)
    return get_latest_prediction(db, equipment_id)


def get_equipment_prediction_history(
    db: Session,
    equipment_id: int,
) -> list[Prediction]:
    """Return prediction history for an existing equipment item."""
    _validate_equipment_exists(db, equipment_id)
    return get_prediction_history(db, equipment_id)
