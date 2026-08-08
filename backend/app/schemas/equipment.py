from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

MachineType = Literal["L", "M", "H"]


class EquipmentBase(BaseModel):
    """Fields shared by equipment creation and API responses."""

    equipment_code: str
    name: str
    category: str
    machine_type: MachineType = Field(description="AI4I machine type: L, M, or H")
    manufacturer: str | None = None
    model_number: str | None = None
    installation_date: date | None = None
    status: str = "Active"


class EquipmentCreate(EquipmentBase):
    """Validated payload for creating equipment."""


class EquipmentResponse(EquipmentBase):
    """Equipment record returned by the API."""

    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EquipmentUpdate(BaseModel):
    """Validated partial payload for updating equipment."""

    equipment_code: str | None = None
    name: str | None = None
    category: str | None = None
    machine_type: MachineType | None = None
    manufacturer: str | None = None
    model_number: str | None = None
    installation_date: date | None = None
    status: str | None = None
