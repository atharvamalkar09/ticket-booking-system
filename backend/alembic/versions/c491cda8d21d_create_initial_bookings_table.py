"""create initial bookings table

Revision ID: c491cda8d21d
Revises: d75123bda9c7
Create Date: 2026-09-25

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c491cda8d21d"
down_revision: Union[str, Sequence[str], None] = "d75123bda9c7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bookingstatus = sa.Enum(
        "PENDING",
        "CONFIRMED",
        "CANCELLED",
        name="bookingstatus",
    )

    op.create_table(
        "bookings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("event_id", sa.Integer(), nullable=False),
        sa.Column("seat_id", sa.Integer(), nullable=False),
        sa.Column(
            "price",
            sa.Numeric(precision=10, scale=2),
            nullable=False,
        ),
        sa.Column(
            "status",
            bookingstatus,
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=True,
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
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_bookings_id"),
        "bookings",
        ["id"],
        unique=False,
    )

    op.create_index(
        "uq_active_event_seat_booking",
        "bookings",
        ["event_id", "seat_id"],
        unique=True,
        postgresql_where=sa.text(
            "status IN ('PENDING', 'CONFIRMED')"
        ),
    )


def downgrade() -> None:
    op.drop_index(
        "uq_active_event_seat_booking",
        table_name="bookings",
    )

    op.drop_index(
        op.f("ix_bookings_id"),
        table_name="bookings",
    )

    op.drop_table("bookings")