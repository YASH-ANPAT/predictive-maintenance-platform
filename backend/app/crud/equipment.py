from sqlalchemy.orm import Session

from app.models.equipment import Equipment
from app.schemas.equipment import EquipmentCreate


def create_equipment(
    db: Session,
    equipment: EquipmentCreate,
) -> Equipment:
    """
    Create a new equipment record.
    """

    db_equipment = Equipment(
        equipment_code=equipment.equipment_code,
        name=equipment.name,
        category=equipment.category,
        manufacturer=equipment.manufacturer,
        model_number=equipment.model_number,
        installation_date=equipment.installation_date,
        status=equipment.status,
    )

    db.add(db_equipment)
    db.commit()
    db.refresh(db_equipment)

    return db_equipment

def get_equipment_by_id(
    db: Session,
    equipment_id: int,
) -> Equipment | None:
    """
    Retrieve a single equipment by its ID.
    """

    return (
        db.query(Equipment)
        .filter(Equipment.id == equipment_id)
        .first()
    )