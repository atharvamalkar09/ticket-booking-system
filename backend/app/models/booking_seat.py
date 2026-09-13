from decimal import Decimal

from sqlalchemy import (
    ForeignKey,
    Integer,
    Numeric,
    Index,
    Boolean,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class BookingSeat(Base):
    __tablename__ = "booking_seats"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    booking_id: Mapped[int] = mapped_column(
        ForeignKey(
            "bookings.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    event_id: Mapped[int] = mapped_column(
        ForeignKey(
            "events.id",
            ondelete="RESTRICT"
        ),
        nullable=False
    )

    seat_id: Mapped[int] = mapped_column(
        ForeignKey(
            "seats.id",
            ondelete="RESTRICT"
        ),
        nullable=False
    )

    price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=text("true")
    )
    booking = relationship(
        "Booking",
        back_populates="booking_seats"
    )

    event = relationship(
        "Event"
    )

    seat = relationship(
        "Seat",
        back_populates="booking_seats"
    )

    __table_args__ = (
        Index(
            "uq_event_seat_booking",
            "event_id",
            "seat_id",
            unique=True,
            postgresql_where=text("is_active = true"),
        ),
    )
