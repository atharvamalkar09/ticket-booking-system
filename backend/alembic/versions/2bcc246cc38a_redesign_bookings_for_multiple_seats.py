"""redesign bookings for multiple seats

Revision ID: 2bcc246cc38a
Revises: cc54d91a5953
Create Date: 2026-08-31 19:05:20.249843

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "2bcc246cc38a"
down_revision: Union[str, Sequence[str], None] = "cc54d91a5953"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Convert the old one-seat-per-booking structure
    into a booking + booking_seats structure.
    """

    # ---------------------------------------------------------
    # 1. Add total_price as nullable temporarily
    # ---------------------------------------------------------

    op.add_column(
        "bookings",
        sa.Column(
            "total_price",
            sa.Numeric(precision=10, scale=2),
            nullable=True,
        ),
    )

    # ---------------------------------------------------------
    # 2. Create booking_seats table
    # ---------------------------------------------------------

    op.create_table(
        "booking_seats",

        sa.Column(
            "id",
            sa.Integer(),
            autoincrement=True,
            nullable=False,
        ),

        sa.Column(
            "booking_id",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "event_id",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "seat_id",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "price",
            sa.Numeric(
                precision=10,
                scale=2,
            ),
            nullable=False,
        ),

        sa.ForeignKeyConstraint(
            ["booking_id"],
            ["bookings.id"],
            ondelete="CASCADE",
        ),

        sa.ForeignKeyConstraint(
            ["event_id"],
            ["events.id"],
            ondelete="RESTRICT",
        ),

        sa.ForeignKeyConstraint(
            ["seat_id"],
            ["seats.id"],
            ondelete="RESTRICT",
        ),

        sa.PrimaryKeyConstraint("id"),
    )

    # ---------------------------------------------------------
    # 3. Copy existing booking information
    #
    # Every old booking represented one seat.
    #
    # Therefore:
    #
    # bookings.seat_id
    #       ↓
    # booking_seats.seat_id
    #
    # bookings.price
    #       ↓
    # booking_seats.price
    #
    # bookings.event_id
    #       ↓
    # booking_seats.event_id
    # ---------------------------------------------------------

    op.execute(
        """
        INSERT INTO booking_seats
        (
            booking_id,
            event_id,
            seat_id,
            price
        )
        SELECT
            id,
            event_id,
            seat_id,
            price
        FROM bookings
        WHERE seat_id IS NOT NULL
        """
    )

    # ---------------------------------------------------------
    # 4. Copy old price into total_price
    # ---------------------------------------------------------

    op.execute(
        """
        UPDATE bookings
        SET total_price = price
        WHERE total_price IS NULL
        """
    )

    # ---------------------------------------------------------
    # 5. Make total_price NOT NULL
    # ---------------------------------------------------------

    op.alter_column(
        "bookings",
        "total_price",
        existing_type=sa.Numeric(
            precision=10,
            scale=2,
        ),
        nullable=False,
    )

    # ---------------------------------------------------------
    # 6. Add unique constraint
    #
    # Same seat cannot belong to two active bookings
    # for the same event in our current architecture.
    # ---------------------------------------------------------

    op.create_index(
        "uq_event_seat_booking",
        "booking_seats",
        ["event_id", "seat_id"],
        unique=True,
    )

    # ---------------------------------------------------------
    # 7. Remove old booking constraint
    # ---------------------------------------------------------

    op.drop_index(
        "uq_active_event_seat_booking",
        table_name="bookings",
    )

    # ---------------------------------------------------------
    # 8. Remove old seat foreign key
    # ---------------------------------------------------------

    op.drop_constraint(
        "bookings_seat_id_fkey",
        "bookings",
        type_="foreignkey",
    )

    # ---------------------------------------------------------
    # 9. Remove old columns
    # ---------------------------------------------------------

    op.drop_column(
        "bookings",
        "price",
    )

    op.drop_column(
        "bookings",
        "seat_id",
    )


def downgrade() -> None:
    """
    Restore the old one-seat-per-booking structure.
    """

    # ---------------------------------------------------------
    # 1. Re-add old columns
    # ---------------------------------------------------------

    op.add_column(
        "bookings",
        sa.Column(
            "seat_id",
            sa.Integer(),
            nullable=True,
        ),
    )

    op.add_column(
        "bookings",
        sa.Column(
            "price",
            sa.Numeric(
                precision=10,
                scale=2,
            ),
            nullable=True,
        ),
    )

    # ---------------------------------------------------------
    # 2. Restore first seat for each booking
    # ---------------------------------------------------------

    op.execute(
        """
        UPDATE bookings b
        SET
            seat_id = bs.seat_id,
            price = bs.price
        FROM booking_seats bs
        WHERE bs.booking_id = b.id
        """
    )

    # ---------------------------------------------------------
    # 3. Make old columns NOT NULL
    # ---------------------------------------------------------

    op.alter_column(
        "bookings",
        "seat_id",
        existing_type=sa.Integer(),
        nullable=False,
    )

    op.alter_column(
        "bookings",
        "price",
        existing_type=sa.Numeric(
            precision=10,
            scale=2,
        ),
        nullable=False,
    )

    # ---------------------------------------------------------
    # 4. Restore foreign key
    # ---------------------------------------------------------

    op.create_foreign_key(
        "bookings_seat_id_fkey",
        "bookings",
        "seats",
        ["seat_id"],
        ["id"],
        ondelete="RESTRICT",
    )

    # ---------------------------------------------------------
    # 5. Restore old unique index
    # ---------------------------------------------------------

    op.create_index(
        "uq_active_event_seat_booking",
        "bookings",
        ["event_id", "seat_id"],
        unique=True,
        postgresql_where=sa.text(
            "status IN ('PENDING', 'CONFIRMED')"
        ),
    )

    # ---------------------------------------------------------
    # 6. Remove new index
    # ---------------------------------------------------------

    op.drop_index(
        "uq_event_seat_booking",
        table_name="booking_seats",
    )

    # ---------------------------------------------------------
    # 7. Remove booking_seats
    # ---------------------------------------------------------

    op.drop_table(
        "booking_seats"
    )

    # ---------------------------------------------------------
    # 8. Remove total_price
    # ---------------------------------------------------------

    op.drop_column(
        "bookings",
        "total_price",
    )