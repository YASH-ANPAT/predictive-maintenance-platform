from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, computed_field

from app.services.risk_policy import get_risk_level


class PredictionCreate(BaseModel):
    """Validated payload for recording a failure prediction."""

    equipment_id: int = Field(gt=0)
    telemetry_id: int | None = Field(default=None, gt=0)
    failure_probability: float = Field(ge=0, le=1)
    predicted_failure: bool
    prediction_time: datetime | None = None
    model_version: str = Field(min_length=1, max_length=100)
    recommendation: str = Field(min_length=1, max_length=1000)


class PredictionResponse(BaseModel):
    """Prediction record returned by the API."""

    id: int
    equipment_id: int
    telemetry_id: int | None
    failure_probability: float
    predicted_failure: bool
    prediction_time: datetime
    model_version: str
    recommendation: str

    @computed_field
    @property
    def risk_level(self) -> str:
        """Return the five-level risk classification for this prediction."""
        return get_risk_level(self.failure_probability)

    model_config = ConfigDict(from_attributes=True)


