from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


MaintenanceStatus = Literal["Scheduled", "In Progress", "Completed", "Cancelled"]


class MaintenanceBase(BaseModel):
    """Fields shared by maintenance creation and API responses."""

    maintenance_type: str = Field(min_length=1, max_length=100)
    description: str = Field(min_length=1, max_length=1000)
    technician: str = Field(min_length=1, max_length=100)
    cost: Decimal = Field(ge=0, max_digits=12, decimal_places=2)
    scheduled_date: date
    completed_date: date | None = None
    status: MaintenanceStatus = "Scheduled"

    @model_validator(mode="after")
    def validate_dates_and_status(self) -> "MaintenanceBase":
        """Ensure completion dates and status agree with the maintenance lifecycle."""
        if self.completed_date and self.completed_date < self.scheduled_date:
            raise ValueError("completed_date cannot be earlier than scheduled_date")
        if self.status == "Completed" and self.completed_date is None:
            raise ValueError("completed_date is required when status is Completed")
        return self


class MaintenanceCreate(MaintenanceBase):
    """Validated payload for creating a maintenance record."""

    equipment_id: int = Field(gt=0)


class MaintenanceUpdate(BaseModel):
    """Validated partial payload for updating a maintenance record."""

    equipment_id: int | None = Field(default=None, gt=0)
    maintenance_type: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, min_length=1, max_length=1000)
    technician: str | None = Field(default=None, min_length=1, max_length=100)
    cost: Decimal | None = Field(
        default=None,
        ge=0,
        max_digits=12,
        decimal_places=2,
    )
    scheduled_date: date | None = None
    completed_date: date | None = None
    status: MaintenanceStatus | None = None

    @model_validator(mode="after")
    def validate_provided_fields(self) -> "MaintenanceUpdate":
        """Reject null values for required fields and invalid provided date ranges."""
        required_fields = {
            "equipment_id",
            "maintenance_type",
            "description",
            "technician",
            "cost",
            "scheduled_date",
            "status",
        }
        for field_name in required_fields & self.model_fields_set:
            if getattr(self, field_name) is None:
                raise ValueError(f"{field_name} cannot be null")
        if (
            self.scheduled_date is not None
            and self.completed_date is not None
            and self.completed_date < self.scheduled_date
        ):
            raise ValueError("completed_date cannot be earlier than scheduled_date")
        if self.status == "Completed" and "completed_date" in self.model_fields_set:
            if self.completed_date is None:
                raise ValueError("completed_date is required when status is Completed")
        return self


class MaintenanceResponse(MaintenanceBase):
    """Maintenance record returned by the API."""

    id: int
    equipment_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
