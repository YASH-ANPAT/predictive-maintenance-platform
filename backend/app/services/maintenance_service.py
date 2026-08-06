from datetime import date

from sqlalchemy.orm import Session

from app.crud.equipment import get_equipment_by_id
from app.crud.maintenance import get_equipment_maintenance
from app.models.maintenance import Maintenance

INACTIVE_MAINTENANCE_STATUSES = {"Completed", "Cancelled"}


def _validate_equipment_exists(db: Session, equipment_id: int) -> None:
    """Validate that an equipment record exists before service processing."""
    if get_equipment_by_id(db, equipment_id) is None:
        raise ValueError("Equipment not found")


def get_maintenance_history(db: Session, equipment_id: int) -> list[Maintenance]:
    """Return all maintenance records for an existing equipment item."""
    _validate_equipment_exists(db, equipment_id)
    return get_equipment_maintenance(db, equipment_id)


def get_upcoming_maintenance(
    db: Session,
    equipment_id: int,
    as_of: date | None = None,
) -> list[Maintenance]:
    """Return scheduled maintenance that is due today or later."""
    reference_date = as_of or date.today()
    maintenance_records = get_maintenance_history(db, equipment_id)

    return [
        record
        for record in maintenance_records
        if record.scheduled_date >= reference_date
        and record.status not in INACTIVE_MAINTENANCE_STATUSES
    ]


def get_overdue_maintenance(
    db: Session,
    equipment_id: int,
    as_of: date | None = None,
) -> list[Maintenance]:
    """Return unfinished maintenance records whose scheduled date has passed."""
    reference_date = as_of or date.today()
    maintenance_records = get_maintenance_history(db, equipment_id)

    return [
        record
        for record in maintenance_records
        if record.scheduled_date < reference_date
        and record.status not in INACTIVE_MAINTENANCE_STATUSES
    ]
