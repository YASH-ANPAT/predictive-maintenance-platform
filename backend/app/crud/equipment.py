from sqlalchemy.orm import Session

from app.models.equipment import Equipment
from app.schemas.equipment import (
    EquipmentCreate,
    EquipmentUpdate,
)


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
    
    
def get_all_equipment(
    db: Session,
) -> list[Equipment]:
    """
    Retrieve all equipment records.
    """

    return (
        db.query(Equipment)
        .order_by(Equipment.id)
        .all()
    )    
        
    
def update_equipment(
    db: Session,
    equipment: Equipment,
    updated_data: EquipmentUpdate,
) -> Equipment:
    """
    Update an existing equipment record.
    """

    update_data = updated_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(equipment, field, value)

    db.commit()
    db.refresh(equipment)

    return equipment    


def delete_equipment(
    db: Session,
    equipment: Equipment,
) -> None:
    """
    Delete an equipment record.
    """

    db.delete(equipment)
    db.commit()