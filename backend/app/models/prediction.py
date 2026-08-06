from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from app.database.base import Base


class Prediction(Base):
    """Database record of a machine-learning failure prediction."""

    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True)
    equipment_id = Column(
        Integer,
        ForeignKey("equipment.id"),
        nullable=False,
        index=True,
    )
    failure_probability = Column(Float, nullable=False)
    predicted_failure = Column(Boolean, nullable=False)
    prediction_time = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    model_version = Column(String(100), nullable=False)
    recommendation = Column(String(1000), nullable=False)

    equipment = relationship("Equipment")
