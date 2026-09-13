"""add booking expiration

Revision ID: edf270a27c26
Revises: ff4f0952dc21
Create Date: 2026-09-09 08:06:17.024391

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "edf270a27c26"
down_revision: Union[str, Sequence[str], None] = "ff4f0952dc21"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.add_column(
        "bookings",
        sa.Column(
            "expires_at",
            sa.DateTime(timezone=True),
            nullable=True
        )
    )

    op.execute(
        """
        UPDATE bookings
        SET expires_at = created_at + INTERVAL '5 minutes'
        WHERE expires_at IS NULL
        """
    )

    op.alter_column(
        "bookings",
        "expires_at",
        nullable=False
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_column(
        "bookings",
        "expires_at"
    )