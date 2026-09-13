from enum import Enum

from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.venue import Venue


class SeatCategory(str, Enum):
    STANDARD = "STANDARD"
    PREMIUM = "PREMIUM"
    VIP = "VIP"


class Seat(Base):
    __tablename__ = "seats"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    venue_id: Mapped[int] = mapped_column(
        ForeignKey("venues.id", ondelete="CASCADE"),
        nullable=False
    )

    row: Mapped[str] = mapped_column(
        String(10),
        nullable=False
    )

    number: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    category: Mapped[SeatCategory] = mapped_column(
        SQLEnum(SeatCategory),
        default=SeatCategory.STANDARD,
        nullable=False
    )

    venue: Mapped["Venue"] = relationship(
    "Venue",
    back_populates="seats"
    )

    booking_seats = relationship(
        "BookingSeat",
        back_populates="seat"
    )

    __table_args__ = (
        UniqueConstraint(
            "venue_id",
            "row",
            "number",
            name="uq_venue_row_number"
        ),
    )