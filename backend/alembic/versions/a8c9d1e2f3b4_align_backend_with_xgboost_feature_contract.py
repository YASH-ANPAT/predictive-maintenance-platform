"""align backend with xgboost feature contract

Revision ID: a8c9d1e2f3b4
Revises: f7b3a1d9e602
Create Date: 2026-08-08 00:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "a8c9d1e2f3b4"
down_revision: Union[str, Sequence[str], None] = "f7b3a1d9e602"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _table_has_rows(table_name: str) -> bool:
    """Return whether a table contains data."""
    bind = op.get_bind()
    result = bind.execute(
        sa.text(f"SELECT EXISTS (SELECT 1 FROM {table_name})")
    )
    return bool(result.scalar())


def upgrade() -> None:
    """Apply the final XGBoost feature contract."""

    if _table_has_rows("telemetry"):
        raise RuntimeError(
            "Cannot replace legacy telemetry measurements while telemetry "
            "rows exist. Export or migrate existing telemetry explicitly "
            "before applying this revision."
        )

    op.add_column(
        "equipment",
        sa.Column("machine_type", sa.String(length=1), nullable=True),
    )

    op.execute(
        sa.text(
            "UPDATE equipment "
            "SET machine_type = 'M' "
            "WHERE machine_type IS NULL"
        )
    )

    op.alter_column(
        "equipment",
        "machine_type",
        nullable=False,
    )

    op.create_check_constraint(
        "ck_equipment_machine_type",
        "equipment",
        "machine_type IN ('L', 'M', 'H')",
    )

    op.add_column(
        "telemetry",
        sa.Column("air_temperature", sa.Float(), nullable=True),
    )
    op.add_column(
        "telemetry",
        sa.Column("process_temperature", sa.Float(), nullable=True),
    )
    op.add_column(
        "telemetry",
        sa.Column("rotational_speed", sa.Integer(), nullable=True),
    )
    op.add_column(
        "telemetry",
        sa.Column("torque", sa.Float(), nullable=True),
    )
    op.add_column(
        "telemetry",
        sa.Column("tool_wear", sa.Integer(), nullable=True),
    )

    op.drop_column("telemetry", "temperature")
    op.drop_column("telemetry", "vibration")
    op.drop_column("telemetry", "pressure")
    op.drop_column("telemetry", "rpm")
    op.drop_column("telemetry", "voltage")
    op.drop_column("telemetry", "current")
    op.drop_column("telemetry", "load")
    op.drop_column("telemetry", "humidity")

    op.alter_column(
        "telemetry",
        "air_temperature",
        nullable=False,
    )
    op.alter_column(
        "telemetry",
        "process_temperature",
        nullable=False,
    )
    op.alter_column(
        "telemetry",
        "rotational_speed",
        nullable=False,
    )
    op.alter_column(
        "telemetry",
        "torque",
        nullable=False,
    )
    op.alter_column(
        "telemetry",
        "tool_wear",
        nullable=False,
    )


def downgrade() -> None:
    """Restore the legacy telemetry contract."""

    if _table_has_rows("telemetry"):
        raise RuntimeError(
            "Cannot downgrade telemetry while telemetry rows exist because "
            "the XGBoost feature values would be lost."
        )

    op.add_column(
        "telemetry",
        sa.Column("humidity", sa.Float(), nullable=True),
    )
    op.add_column(
        "telemetry",
        sa.Column("load", sa.Float(), nullable=True),
    )
    op.add_column(
        "telemetry",
        sa.Column("current", sa.Float(), nullable=True),
    )
    op.add_column(
        "telemetry",
        sa.Column("voltage", sa.Float(), nullable=True),
    )
    op.add_column(
        "telemetry",
        sa.Column("rpm", sa.Integer(), nullable=True),
    )
    op.add_column(
        "telemetry",
        sa.Column("pressure", sa.Float(), nullable=True),
    )
    op.add_column(
        "telemetry",
        sa.Column("vibration", sa.Float(), nullable=True),
    )
    op.add_column(
        "telemetry",
        sa.Column("temperature", sa.Float(), nullable=True),
    )

    op.drop_column("telemetry", "tool_wear")
    op.drop_column("telemetry", "torque")
    op.drop_column("telemetry", "rotational_speed")
    op.drop_column("telemetry", "process_temperature")
    op.drop_column("telemetry", "air_temperature")

    op.drop_constraint(
        "ck_equipment_machine_type",
        "equipment",
        type_="check",
    )

    op.drop_column("equipment", "machine_type")