from decimal import Decimal
from datetime import datetime

from sqlalchemy import Numeric, String, Integer, DateTime, Text, Table, Column, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


event_venues = Table(
    "event_venues",
    Base.metadata,
    Column(
        "event_id",
        ForeignKey("events.id", ondelete="CASCADE"),
        primary_key=True
    ),
    Column(
        "venue_id",
        ForeignKey("venues.id", ondelete="CASCADE"),
        primary_key=True
    )
)


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    title: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    category: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    start_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )

    end_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )

    base_price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False
    )

    venues = relationship(
        "Venue",
        secondary=event_venues,
        back_populates="events"
    )

    bookings = relationship(
        "Booking",
        back_populates="event"
    )