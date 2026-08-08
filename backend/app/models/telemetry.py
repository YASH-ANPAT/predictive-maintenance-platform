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

    air_temperature = Column(
        Float,
        nullable=False,
    )

    process_temperature = Column(
        Float,
        nullable=False,
    )

    rotational_speed = Column(
        Integer,
        nullable=False,
    )

    torque = Column(
        Float,
        nullable=False,
    )

    tool_wear = Column(
        Integer,
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
