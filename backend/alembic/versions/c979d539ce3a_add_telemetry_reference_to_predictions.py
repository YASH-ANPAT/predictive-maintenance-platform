"""add telemetry reference to predictions

Revision ID: c979d539ce3a
Revises: a8c9d1e2f3b4
Create Date: 2026-09-08 23:11:41.892947
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c979d539ce3a"
down_revision: Union[str, Sequence[str], None] = "a8c9d1e2f3b4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "predictions",
        sa.Column("telemetry_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "fk_predictions_telemetry_id",
        "predictions",
        "telemetry",
        ["telemetry_id"],
        ["id"],
    )
    op.create_index(
        "ix_predictions_telemetry_id",
        "predictions",
        ["telemetry_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_predictions_telemetry_id",
        table_name="predictions",
    )
    op.drop_constraint(
        "fk_predictions_telemetry_id",
        "predictions",
        type_="foreignkey",
    )
    op.drop_column("predictions", "telemetry_id")
