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
revision: str = 'c8490bc6003a'
down_revision: Union[str, None] = 'e29ef4c6d54b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Declare new PostgreSQL ENUM object
booking_status_enum = postgresql.ENUM(
    'PENDING', 'CONFIRMED', 'CANCELLED', 
    name='booking_status_enum'
)

def upgrade() -> None:
    # 1. Create the new enum type if it doesn't exist
    booking_status_enum.create(op.get_bind(), checkfirst=True)

    # 2. Drop old full constraint if it exists
    op.execute("ALTER TABLE bookings DROP CONSTRAINT IF EXISTS uq_event_seat_booking")

    # 3. Alter column using text intermediate casting (status::text::booking_status_enum)
    op.alter_column(
        'bookings', 
        'status',
        existing_type=sa.Enum('PENDING', 'CONFIRMED', 'CANCELLED', name='bookingstatus'),
        type_=booking_status_enum,
        postgresql_using='status::text::booking_status_enum',
        existing_nullable=False
    )

    # 4. Create Partial Unique Index for concurrent double-booking protection
    op.create_index(
        'uq_active_event_seat_booking',
        'bookings',
        ['event_id', 'seat_id'],
        unique=True,
        postgresql_where=sa.text("status IN ('PENDING', 'CONFIRMED')")
    )

    # 5. Drop the old enum type from PostgreSQL
    op.execute("DROP TYPE IF EXISTS bookingstatus")


def downgrade() -> None:
    old_enum = postgresql.ENUM('PENDING', 'CONFIRMED', 'CANCELLED', name='bookingstatus')
    old_enum.create(op.get_bind(), checkfirst=True)

    op.drop_index(
        'uq_active_event_seat_booking', 
        table_name='bookings',
        postgresql_where=sa.text("status IN ('PENDING', 'CONFIRMED')")
    )

    op.alter_column(
        'bookings', 
        'status',
        existing_type=booking_status_enum,
        type_=old_enum,
        postgresql_using='status::text::bookingstatus',
        existing_nullable=False
    )

    op.create_unique_constraint(
        'uq_event_seat_booking', 
        'bookings', 
        ['event_id', 'seat_id']
    )

    booking_status_enum.drop(op.get_bind(), checkfirst=True)