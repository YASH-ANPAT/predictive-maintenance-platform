from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.crud.equipment import create_equipment
from app.database.database import get_db
from app.schemas.equipment import EquipmentCreate, EquipmentResponse

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