from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TelemetryBase(BaseModel):
    """Telemetry fields matching the final XGBoost model input contract."""

    air_temperature: float = Field(gt=0)
    process_temperature: float = Field(gt=0)
    rotational_speed: int = Field(gt=0)
    torque: float = Field(ge=0)
    tool_wear: int = Field(ge=0)


class TelemetryCreate(TelemetryBase):
    """Validated payload for creating telemetry."""

    equipment_id: int = Field(gt=0)


class TelemetryResponse(TelemetryBase):
    """Telemetry record returned by the API."""

    id: int
    equipment_id: int
    recorded_at: datetime

    model_config = ConfigDict(from_attributes=True)
