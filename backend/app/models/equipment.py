from sqlalchemy import Column, Date, DateTime, Integer, String
from sqlalchemy.sql import func

from sqlalchemy.orm import relationship

from app.database.base import Base


class Equipment(Base):
    __tablename__ = "equipment"

    id = Column(
    Integer,
    primary_key=True,
    )

    equipment_code = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )

    name = Column(
        String(100),
        nullable=False,
    )

    category = Column(
        String(50),
        nullable=False,
    )

    machine_type = Column(
        String(1),
        nullable=False,
    )

    manufacturer = Column(
        String(100),
        nullable=True,
    )

    model_number = Column(
        String(100),
        nullable=True,
    )

    installation_date = Column(
        Date,
        nullable=True,
    )

    status = Column(
        String(30),
        nullable=False,
        default="Active",
    )

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
    
    telemetry_records = relationship(
    "Telemetry",
    back_populates="equipment",
    cascade="all, delete-orphan",
    )

    maintenance_records = relationship(
        "Maintenance",
        back_populates="equipment",
        cascade="all, delete-orphan",
    )
    
