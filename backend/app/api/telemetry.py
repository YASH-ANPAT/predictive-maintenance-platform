from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.crud.telemetry import (
    create_telemetry,
    get_all_telemetry,
    get_equipment_telemetry,
    get_telemetry_by_id,
)
from app.database.database import get_db
from app.schemas.telemetry import (
    TelemetryCreate,
    TelemetryResponse,
)
from app.services.telemetry_service import validate_equipment_exists

router = APIRouter(
    prefix="/telemetry",
    tags=["Telemetry"],
)


@router.post(
    "/",
    response_model=TelemetryResponse,
    status_code=201,
)
def create_new_telemetry(
    telemetry: TelemetryCreate,
    db: Session = Depends(get_db),
)-> TelemetryResponse:
    try:
        validate_equipment_exists(db, telemetry.equipment_id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error

    return create_telemetry(
        db=db,
        telemetry=telemetry,
    )

@router.get(
    "/",
    response_model=list[TelemetryResponse],
)
def get_all_telemetry_endpoint(
    db: Session = Depends(get_db),
) -> list[TelemetryResponse]:
    return get_all_telemetry(db=db)


@router.get(
    "/{telemetry_id}",
    response_model=TelemetryResponse,
)
def get_telemetry(
    telemetry_id: int,
    db: Session = Depends(get_db),
) -> TelemetryResponse:
    telemetry = get_telemetry_by_id(
        db=db,
        telemetry_id=telemetry_id,
    )

    if telemetry is None:
        raise HTTPException(
            status_code=404,
            detail="Telemetry record not found",
        )

    return telemetry


@router.get(
    "/equipment/{equipment_id}",
    response_model=list[TelemetryResponse],
)
def get_equipment_telemetry_endpoint(
    equipment_id: int,
    db: Session = Depends(get_db),
) -> list[TelemetryResponse]:
    try:
        validate_equipment_exists(db, equipment_id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error

    return get_equipment_telemetry(
        db=db,
        equipment_id=equipment_id,
    )
