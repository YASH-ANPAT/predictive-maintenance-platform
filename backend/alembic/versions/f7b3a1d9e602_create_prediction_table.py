"""create prediction table

Revision ID: f7b3a1d9e602
Revises: c4d2e8f6a901
Create Date: 2026-08-06 11:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "f7b3a1d9e602"
down_revision: Union[str, Sequence[str], None] = "c4d2e8f6a901"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create the predictions table and equipment lookup index."""
    op.create_table(
        "predictions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("equipment_id", sa.Integer(), nullable=False),
        sa.Column("failure_probability", sa.Float(), nullable=False),
        sa.Column("predicted_failure", sa.Boolean(), nullable=False),
        sa.Column(
            "prediction_time",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("model_version", sa.String(length=100), nullable=False),
        sa.Column("recommendation", sa.String(length=1000), nullable=False),
        sa.ForeignKeyConstraint(["equipment_id"], ["equipment.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_predictions_equipment_id", "predictions", ["equipment_id"])


def downgrade() -> None:
    """Remove the predictions table and its equipment index."""
    op.drop_index("ix_predictions_equipment_id", table_name="predictions")
    op.drop_table("predictions")
