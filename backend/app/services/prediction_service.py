from typing import Any

from sqlalchemy.orm import Session

from app.crud.equipment import get_equipment_by_id
from app.crud.prediction import (
    get_latest_prediction,
    get_prediction_history,
)
from app.models.prediction import Prediction
from app.services.risk_policy import get_risk_level, generate_maintenance_recommendation
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


def prepare_prediction_input(
    db: Session,
    equipment_id: int,
) -> dict[str, Any]:
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




