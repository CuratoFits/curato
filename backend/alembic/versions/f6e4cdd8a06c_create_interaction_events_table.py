"""create interaction events table

Revision ID: f6e4cdd8a06c
Revises: 25ea7d200c9a
Create Date: 2026-08-11 23:07:56.404758
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f6e4cdd8a06c"
down_revision: Union[str, Sequence[str], None] = "25ea7d200c9a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create interaction_events table."""

    op.create_table(
        "interaction_events",

        sa.Column(
            "event_id",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "user_id",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "product_id",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "event_type",
            sa.String(length=30),
            nullable=False,
        ),

        sa.Column(
            "session_id",
            sa.String(length=100),
            nullable=False,
        ),

        sa.Column(
            "time_spent_seconds",
            sa.Float(),
            nullable=False,
        ),

        sa.Column(
            "scroll_depth",
            sa.Float(),
            nullable=False,
        ),

        sa.Column(
            "source",
            sa.String(length=30),
            nullable=False,
        ),

        sa.Column(
            "quantity",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "timestamp",
            sa.DateTime(),
            nullable=False,
        ),

        sa.PrimaryKeyConstraint("event_id"),
    )

    op.create_index(
        "ix_interaction_events_user_id",
        "interaction_events",
        ["user_id"],
        unique=False,
    )

    op.create_index(
        "ix_interaction_events_product_id",
        "interaction_events",
        ["product_id"],
        unique=False,
    )

    op.create_index(
        "ix_interaction_events_timestamp",
        "interaction_events",
        ["timestamp"],
        unique=False,
    )


def downgrade() -> None:
    """Remove interaction_events table."""

    # The table did not exist when this migration was
    # previously marked as applied, so use IF EXISTS
    # to make the rollback safe.

    op.execute(
        "DROP TABLE IF EXISTS interaction_events CASCADE"
    )