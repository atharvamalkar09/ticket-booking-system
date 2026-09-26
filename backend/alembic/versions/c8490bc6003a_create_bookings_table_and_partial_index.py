"""create_bookings_table_and_partial_index

Revision ID: c8490bc6003a
Revises: e29ef4c6d54b
Create Date: 2026-08-29

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "c8490bc6003a"
down_revision: Union[str, None] = "e29ef4c6d54b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# PostgreSQL ENUM type
booking_status_enum = postgresql.ENUM(
    "PENDING",
    "CONFIRMED",
    "CANCELLED",
    name="booking_status_enum",
)


def upgrade() -> None:
    # 1. Create the new enum type.
    booking_status_enum.create(
        op.get_bind(),
        checkfirst=True,
    )

    # 2. Drop the old unique constraint if it exists.
    op.execute(
        """
        ALTER TABLE bookings
        DROP CONSTRAINT IF EXISTS uq_event_seat_booking
        """
    )

    # 3. Drop the partial index created by the previous
    #    reconstructed migration.
    op.execute(
        """
        DROP INDEX IF EXISTS uq_active_event_seat_booking
        """
    )

    # 4. Convert the status column from the old enum
    #    bookingstatus to the new enum booking_status_enum.
    op.execute(
        """
        ALTER TABLE bookings
        ALTER COLUMN status TYPE booking_status_enum
        USING status::text::booking_status_enum
        """
    )

    # 5. Re-create the partial unique index using the new enum.
    op.create_index(
        "uq_active_event_seat_booking",
        "bookings",
        ["event_id", "seat_id"],
        unique=True,
        postgresql_where=sa.text(
            "status IN ('PENDING', 'CONFIRMED')"
        ),
    )

    # 6. Drop the old enum type.
    op.execute(
        """
        DROP TYPE IF EXISTS bookingstatus
        """
    )


def downgrade() -> None:
    # 1. Create the old enum type.
    old_enum = postgresql.ENUM(
        "PENDING",
        "CONFIRMED",
        "CANCELLED",
        name="bookingstatus",
    )

    old_enum.create(
        op.get_bind(),
        checkfirst=True,
    )

    # 2. Drop the partial unique index.
    op.execute(
        """
        DROP INDEX IF EXISTS uq_active_event_seat_booking
        """
    )

    # 3. Convert status back to the old enum.
    op.execute(
        """
        ALTER TABLE bookings
        ALTER COLUMN status TYPE bookingstatus
        USING status::text::bookingstatus
        """
    )

    # 4. Restore the original unique constraint.
    op.create_unique_constraint(
        "uq_event_seat_booking",
        "bookings",
        ["event_id", "seat_id"],
    )

    # 5. Drop the newer enum.
    booking_status_enum.drop(
        op.get_bind(),
        checkfirst=True,
    )
