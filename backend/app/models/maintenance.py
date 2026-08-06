from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.orm import relationship

from app.database.base import Base


class Maintenance(Base):
    """Database record for scheduled and completed equipment maintenance."""

    __tablename__ = "maintenance"

    id = Column(Integer, primary_key=True)
    equipment_id = Column(
        Integer,
        ForeignKey("equipment.id"),
        nullable=False,
        index=True,
    )
    maintenance_type = Column(String(100), nullable=False)
    description = Column(String(1000), nullable=False)
    technician = Column(String(100), nullable=False)
    cost = Column(Numeric(12, 2), nullable=False)
    scheduled_date = Column(Date, nullable=False)
    completed_date = Column(Date, nullable=True)
    status = Column(String(30), nullable=False, default="Scheduled")
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    equipment = relationship("Equipment", back_populates="maintenance_records")
