from statistics import mean
from typing import Any

from sqlalchemy.orm import Session

from app.crud.equipment import get_equipment_by_id
from app.crud.telemetry import get_equipment_telemetry
from app.models.telemetry import Telemetry

TELEMETRY_NUMERIC_FIELDS = (
    "temperature",
    "vibration",
    "pressure",
    "rpm",
    "voltage",
    "current",
    "load",
    "humidity",
)


def validate_equipment_exists(db: Session, equipment_id: int) -> None:
    """Validate that an equipment record exists before service processing."""
    if get_equipment_by_id(db, equipment_id) is None:
        raise ValueError("Equipment not found")


def get_latest_telemetry(db: Session, equipment_id: int) -> Telemetry | None:
    """Return the latest telemetry record for an existing equipment item."""
    validate_equipment_exists(db, equipment_id)
    telemetry_records = get_equipment_telemetry(db, equipment_id)
    return telemetry_records[0] if telemetry_records else None


def get_telemetry_history(db: Session, equipment_id: int) -> list[Telemetry]:
    """Return telemetry history for an existing equipment item."""
    validate_equipment_exists(db, equipment_id)
    return get_equipment_telemetry(db, equipment_id)


def get_telemetry_statistics(db: Session, equipment_id: int) -> dict[str, Any]:
    """Calculate min, max, and average values for equipment telemetry history."""
    telemetry_records = get_telemetry_history(db, equipment_id)

    if not telemetry_records:
        return {
            "equipment_id": equipment_id,
            "record_count": 0,
            "statistics": {},
        }

    statistics: dict[str, dict[str, float]] = {}
    for field in TELEMETRY_NUMERIC_FIELDS:
        values = [float(getattr(record, field)) for record in telemetry_records]
        statistics[field] = {
            "min": min(values),
            "max": max(values),
            "average": mean(values),
        }

    return {
        "equipment_id": equipment_id,
        "record_count": len(telemetry_records),
        "statistics": statistics,
    }
