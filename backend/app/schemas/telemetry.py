from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TelemetryBase(BaseModel):
    temperature: float
    vibration: float
    pressure: float
    rpm: int
    voltage: float
    current: float
    load: float
    humidity: float


class TelemetryCreate(TelemetryBase):
    equipment_id: int


class TelemetryResponse(TelemetryBase):
    id: int
    equipment_id: int
    recorded_at: datetime

    model_config = ConfigDict(from_attributes=True)