from fastapi import APIRouter, Depends, HTTPException
from app.crud.equipment import (
    create_equipment,
    get_equipment_by_id,
)
from app.database.database import get_db
from app.schemas.equipment import EquipmentCreate, EquipmentResponse

from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/equipment",
    tags=["Equipment"],
)


@router.post(
    "/",
    response_model=EquipmentResponse,
    status_code=201,
)
def create_new_equipment(
    equipment: EquipmentCreate,
    db: Session = Depends(get_db),
):
    return create_equipment(
        db=db,
        equipment=equipment,
    )
    
@router.get(
    "/{equipment_id}",
    response_model=EquipmentResponse,
)
def get_equipment(
    equipment_id: int,
    db: Session = Depends(get_db),
):
    equipment = get_equipment_by_id(
        db=db,
        equipment_id=equipment_id,
    )

    if equipment is None:
        raise HTTPException(
            status_code=404,
            detail="Equipment not found",
        )

    return equipment    