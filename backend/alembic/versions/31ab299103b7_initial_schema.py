"""initial schema

Revision ID: 31ab299103b7
Revises:
Create Date: 2026-08-06 09:02:32.707909
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "31ab299103b7"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create the initial equipment table."""
    op.create_table(
        "equipment",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("equipment_code", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("category", sa.String(length=50), nullable=False),
        sa.Column("manufacturer", sa.String(length=100), nullable=True),
        sa.Column("model_number", sa.String(length=100), nullable=True),
        sa.Column("installation_date", sa.Date(), nullable=True),
        sa.Column(
            "status",
            sa.String(length=30),
            server_default=sa.text("'Active'"),
            nullable=False,
        ),
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
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("equipment_code"),
    )

    op.create_index(
        "ix_equipment_equipment_code",
        "equipment",
        ["equipment_code"],
        unique=True,
    )


def downgrade() -> None:
    """Remove the initial equipment table."""
    op.drop_index(
        "ix_equipment_equipment_code",
        table_name="equipment",
    )
    op.drop_table("equipment")