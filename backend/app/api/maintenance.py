from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud.equipment import get_equipment_by_id
from app.crud.maintenance import (
    create_maintenance,
    delete_maintenance,
    get_all_maintenance,
    get_equipment_maintenance,
    get_maintenance_by_id,
    update_maintenance,
)
from app.database.database import get_db
from app.schemas.maintenance import (
    MaintenanceCreate,
    MaintenanceResponse,
    MaintenanceUpdate,
)

router = APIRouter(prefix="/maintenance", tags=["Maintenance"])


def _get_existing_equipment(db: Session, equipment_id: int) -> None:
    """Raise a 404 error when the referenced equipment does not exist."""
    if get_equipment_by_id(db, equipment_id) is None:
        raise HTTPException(status_code=404, detail="Equipment not found")


@router.post("/", response_model=MaintenanceResponse, status_code=status.HTTP_201_CREATED)
def create_new_maintenance(
    maintenance: MaintenanceCreate,
    db: Session = Depends(get_db),
) -> MaintenanceResponse:
    """Create a maintenance record for an existing equipment item."""
    _get_existing_equipment(db, maintenance.equipment_id)
    return create_maintenance(db, maintenance)


@router.get("/", response_model=list[MaintenanceResponse])
def get_all_maintenance_endpoint(db: Session = Depends(get_db)) -> list[MaintenanceResponse]:
    """List all maintenance records."""
    return get_all_maintenance(db)


@router.get("/{maintenance_id}", response_model=MaintenanceResponse)
def get_maintenance(
    maintenance_id: int,
    db: Session = Depends(get_db),
) -> MaintenanceResponse:
    """Retrieve one maintenance record."""
    maintenance = get_maintenance_by_id(db, maintenance_id)
    if maintenance is None:
        raise HTTPException(status_code=404, detail="Maintenance record not found")
    return maintenance


@router.put("/{maintenance_id}", response_model=MaintenanceResponse)
def update_existing_maintenance(
    maintenance_id: int,
    updated_data: MaintenanceUpdate,
    db: Session = Depends(get_db),
) -> MaintenanceResponse:
    """Partially update a maintenance record."""
    maintenance = get_maintenance_by_id(db, maintenance_id)
    if maintenance is None:
        raise HTTPException(status_code=404, detail="Maintenance record not found")
    if "equipment_id" in updated_data.model_fields_set:
        _get_existing_equipment(db, updated_data.equipment_id)
    try:
        return update_maintenance(db, maintenance, updated_data)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error


@router.delete("/{maintenance_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_maintenance(
    maintenance_id: int,
    db: Session = Depends(get_db),
) -> None:
    """Delete a maintenance record."""
    maintenance = get_maintenance_by_id(db, maintenance_id)
    if maintenance is None:
        raise HTTPException(status_code=404, detail="Maintenance record not found")
    delete_maintenance(db, maintenance)


@router.get("/equipment/{equipment_id}", response_model=list[MaintenanceResponse])
def get_equipment_maintenance_endpoint(
    equipment_id: int,
    db: Session = Depends(get_db),
) -> list[MaintenanceResponse]:
    """List maintenance records for an existing equipment item."""
    _get_existing_equipment(db, equipment_id)
    return get_equipment_maintenance(db, equipment_id)
