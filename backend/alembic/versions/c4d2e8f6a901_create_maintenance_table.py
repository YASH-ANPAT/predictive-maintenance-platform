"""create maintenance table

Revision ID: c4d2e8f6a901
Revises: 9af7becad804
Create Date: 2026-08-06 10:30:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "c4d2e8f6a901"
down_revision: Union[str, Sequence[str], None] = "9af7becad804"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create the maintenance table and its equipment lookup index."""
    op.create_table(
        "maintenance",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("equipment_id", sa.Integer(), nullable=False),
        sa.Column("maintenance_type", sa.String(length=100), nullable=False),
        sa.Column("description", sa.String(length=1000), nullable=False),
        sa.Column("technician", sa.String(length=100), nullable=False),
        sa.Column("cost", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("scheduled_date", sa.Date(), nullable=False),
        sa.Column("completed_date", sa.Date(), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["equipment_id"], ["equipment.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_maintenance_equipment_id", "maintenance", ["equipment_id"])


def downgrade() -> None:
    """Remove the maintenance table and its index."""
    op.drop_index("ix_maintenance_equipment_id", table_name="maintenance")
    op.drop_table("maintenance")
