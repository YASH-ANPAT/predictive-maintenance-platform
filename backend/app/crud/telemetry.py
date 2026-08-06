from sqlalchemy.orm import Session

from app.models.telemetry import Telemetry
from app.schemas.telemetry import TelemetryCreate


def create_telemetry(
    db: Session,
    telemetry: TelemetryCreate,
) -> Telemetry:
    """
    Create a new telemetry record.
    """

    db_telemetry = Telemetry(**telemetry.model_dump())

    db.add(db_telemetry)
    db.commit()
    db.refresh(db_telemetry)

    return db_telemetry


def get_telemetry_by_id(
    db: Session,
    telemetry_id: int,
) -> Telemetry | None:
    """
    Retrieve a telemetry record by ID.
    """

    return (
        db.query(Telemetry)
        .filter(Telemetry.id == telemetry_id)
        .first()
    )


def get_all_telemetry(
    db: Session,
) -> list[Telemetry]:
    """
    Retrieve all telemetry records.
    """

    return (
        db.query(Telemetry)
        .order_by(Telemetry.recorded_at.desc())
        .all()
    )


def get_equipment_telemetry(
    db: Session,
    equipment_id: int,
) -> list[Telemetry]:
    """
    Retrieve telemetry for a specific equipment.
    """

    return (
        db.query(Telemetry)
        .filter(Telemetry.equipment_id == equipment_id)
        .order_by(Telemetry.recorded_at.desc())
        .all()
    )
    
def get_latest_telemetry(
    db: Session,
    equipment_id: int,
) -> Telemetry | None:
    """
    Retrieve the latest telemetry record for a specific equipment.
    """

    return (
        db.query(Telemetry)
        .filter(Telemetry.equipment_id == equipment_id)
        .order_by(Telemetry.recorded_at.desc())
        .first()
    )    