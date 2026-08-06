from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    func,
)
from sqlalchemy.orm import relationship

from app.database.base import Base


class Telemetry(Base):
    __tablename__ = "telemetry"

    id = Column(
    Integer,
    primary_key=True,
    )

    equipment_id = Column(
        Integer,
        ForeignKey("equipment.id"),
        nullable=False,
    )

    temperature = Column(
        Float,
        nullable=False,
    )

    vibration = Column(
        Float,
        nullable=False,
    )

    pressure = Column(
        Float,
        nullable=False,
    )

    rpm = Column(
        Integer,
        nullable=False,
    )

    voltage = Column(
        Float,
        nullable=False,
    )

    current = Column(
        Float,
        nullable=False,
    )

    load = Column(
        Float,
        nullable=False,
    )

    humidity = Column(
        Float,
        nullable=False,
    )

    recorded_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    equipment = relationship(
        "Equipment",
        back_populates="telemetry_records",
    )