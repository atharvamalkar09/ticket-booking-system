"""add active status to booking seats

Revision ID: e53a19bdf4f1
Revises: 34f1f946e0df
Create Date: 2026-09-07 13:32:50.990341

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e53a19bdf4f1'
down_revision: Union[str, Sequence[str], None] = '34f1f946e0df'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    # 1. Add column initially with a server default
    op.add_column(
        "booking_seats",
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true")
        )
    )

    # 2. Existing cancelled bookings must become inactive
    op.execute("""
        UPDATE booking_seats
        SET is_active = false
        WHERE booking_id IN (
            SELECT id
            FROM bookings
            WHERE status = 'CANCELLED'
        )
    """)

    # 3. Existing PENDING and CONFIRMED remain active
    op.execute("""
        UPDATE booking_seats
        SET is_active = true
        WHERE booking_id IN (
            SELECT id
            FROM bookings
            WHERE status IN ('PENDING', 'CONFIRMED')
        )
    """)

    # 4. Remove old unique index
    op.drop_index(
        "uq_event_seat_booking",
        table_name="booking_seats"
    )

    # 5. Create new unique index ONLY for active seats
    op.create_index(
        "uq_event_seat_booking",
        "booking_seats",
        ["event_id", "seat_id"],
        unique=True,
        postgresql_where=sa.text("is_active = true")
    )


def downgrade() -> None:

    # Remove partial unique index
    op.drop_index(
        "uq_event_seat_booking",
        table_name="booking_seats"
    )

    # Recreate original unique index
    op.create_index(
        "uq_event_seat_booking",
        "booking_seats",
        ["event_id", "seat_id"],
        unique=True
    )

    # Remove column
    op.drop_column(
        "booking_seats",
        "is_active"
    )
