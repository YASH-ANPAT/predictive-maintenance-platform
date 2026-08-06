from datetime import date

from sqlalchemy.orm import Session

from app.models.maintenance import Maintenance
from app.schemas.maintenance import MaintenanceCreate, MaintenanceUpdate


def create_maintenance(db: Session, maintenance: MaintenanceCreate) -> Maintenance:
    """Create and return a maintenance record."""
    db_maintenance = Maintenance(**maintenance.model_dump())
    db.add(db_maintenance)
    db.commit()
    db.refresh(db_maintenance)
    return db_maintenance


def get_maintenance_by_id(db: Session, maintenance_id: int) -> Maintenance | None:
    """Return one maintenance record by its primary key."""
    return db.query(Maintenance).filter(Maintenance.id == maintenance_id).first()


def get_all_maintenance(db: Session) -> list[Maintenance]:
    """Return all maintenance records, newest scheduled records first."""
    return db.query(Maintenance).order_by(Maintenance.scheduled_date.desc()).all()


def get_equipment_maintenance(db: Session, equipment_id: int) -> list[Maintenance]:
    """Return all maintenance records belonging to one equipment item."""
    return (
        db.query(Maintenance)
        .filter(Maintenance.equipment_id == equipment_id)
        .order_by(Maintenance.scheduled_date.desc())
        .all()
    )


def update_maintenance(
    db: Session,
    maintenance: Maintenance,
    updated_data: MaintenanceUpdate,
) -> Maintenance:
    """Apply a validated partial update and return the refreshed record."""
    update_data = updated_data.model_dump(exclude_unset=True)
    proposed_scheduled_date = update_data.get("scheduled_date", maintenance.scheduled_date)
    proposed_completed_date: date | None = update_data.get(
        "completed_date", maintenance.completed_date
    )
    proposed_status = update_data.get("status", maintenance.status)

    if proposed_completed_date and proposed_completed_date < proposed_scheduled_date:
        raise ValueError("completed_date cannot be earlier than scheduled_date")
    if proposed_status == "Completed" and proposed_completed_date is None:
        raise ValueError("completed_date is required when status is Completed")

    for field, value in update_data.items():
        setattr(maintenance, field, value)

    db.commit()
    db.refresh(maintenance)
    return maintenance


def delete_maintenance(db: Session, maintenance: Maintenance) -> None:
    """Delete a maintenance record."""
    db.delete(maintenance)
    db.commit()
