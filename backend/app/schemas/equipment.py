from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class EquipmentCreate(BaseModel):
    equipment_code: str
    name: str
    category: str
    manufacturer: str | None = None
    model_number: str | None = None
    installation_date: date | None = None
    status: str = "Active"


class EquipmentResponse(BaseModel):
    id: int
    equipment_code: str
    name: str
    category: str
    manufacturer: str | None
    model_number: str | None
    installation_date: date | None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EquipmentUpdate(BaseModel):
    equipment_code: str | None = None
    name: str | None = None
    category: str | None = None
    manufacturer: str | None = None
    model_number: str | None = None
    installation_date: date | None = None
    status: str | None = None