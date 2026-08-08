"""create telemetry table

Revision ID: 9af7becad804
Revises: 31ab299103b7
Create Date: 2026-08-06 09:55:41.251019
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "9af7becad804"
down_revision: Union[str, Sequence[str], None] = "31ab299103b7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create the legacy telemetry table."""
    op.create_table(
        "telemetry",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("equipment_id", sa.Integer(), nullable=False),
        sa.Column("temperature", sa.Float(), nullable=False),
        sa.Column("vibration", sa.Float(), nullable=False),
        sa.Column("pressure", sa.Float(), nullable=False),
        sa.Column("rpm", sa.Integer(), nullable=False),
        sa.Column("voltage", sa.Float(), nullable=False),
        sa.Column("current", sa.Float(), nullable=False),
        sa.Column("load", sa.Float(), nullable=False),
        sa.Column("humidity", sa.Float(), nullable=False),
        sa.Column(
            "recorded_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["equipment_id"],
            ["equipment.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    """Remove the legacy telemetry table."""
    op.drop_table("telemetry")