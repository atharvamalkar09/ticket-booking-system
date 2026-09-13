from typing import Optional, Sequence

from decimal import Decimal

from sqlalchemy import or_, select
from sqlalchemy.orm import Session, joinedload
from datetime import datetime, timedelta, timezone
from app.models.booking import Booking, BookingStatusEnum
from app.models.booking_seat import BookingSeat
from app.models.seat import Seat
from app.schemas.booking import BookingCreate


class BookingRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(
        self,
        booking_id: int
    ) -> Optional[Booking]:

        stmt = (
            select(Booking)
            .options(
                joinedload(Booking.user),

                joinedload(
                    Booking.event
                ).joinedload(
                    Booking.event.property.mapper.class_.venues
                ),
                joinedload(
                    Booking.booking_seats
                )
                .joinedload(
                    BookingSeat.seat
                )
                .joinedload(
                    Seat.venue
                ),
            )
            .where(
                Booking.id == booking_id
            )
        )

        return (
            self.db
            .scalars(stmt)
            .unique()
            .first()
        )

    def get_active_booking_for_seat(
    self,
    event_id: int,
    seat_id: int
    ) -> Optional[BookingSeat]:

        now = datetime.now(timezone.utc)

        stmt = (
            select(BookingSeat)
            .join(
                Booking,
                Booking.id == BookingSeat.booking_id
            )
            .where(
                BookingSeat.event_id == event_id,
                BookingSeat.seat_id == seat_id,
                BookingSeat.is_active.is_(True),
                or_(
                    Booking.status == BookingStatusEnum.CONFIRMED,
                    (
                        (Booking.status == BookingStatusEnum.PENDING)
                        &
                        (Booking.expires_at > now)
                    )
                )
            )
        )

        return self.db.scalars(stmt).first()

    def create_booking(
    self,
    user_id: int,
    booking_in: BookingCreate,
    price_per_seat: Decimal
    ) -> Booking:

        total_price = (
            price_per_seat *
            len(booking_in.seat_ids)
        )

        expires_at = (
            datetime.now(timezone.utc)
            + timedelta(minutes=5)
        )

        booking = Booking(
            user_id=user_id,
            event_id=booking_in.event_id,
            total_price=total_price,
            status=BookingStatusEnum.PENDING,
            expires_at=expires_at
        )

        self.db.add(booking)
        self.db.flush()

        for seat_id in booking_in.seat_ids:
            booking_seat = BookingSeat(
                booking_id=booking.id,
                event_id=booking_in.event_id,
                seat_id=seat_id,
                price=price_per_seat,
                is_active=True
            )
            self.db.add(booking_seat)
        self.db.flush()
        return booking

    def update_status_booking(
        self,
        booking: Booking,
        new_status: BookingStatusEnum
    ) -> Booking:

        booking.status = new_status
        self.db.add(booking)
        self.db.flush()

        return booking

    def get_user_bookings(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 20,
        status: Optional[BookingStatusEnum] = None
    ) -> Sequence[Booking]:

        stmt = (
            select(Booking)
            .options(
                joinedload(
                    Booking.event
                ).joinedload(
                    Booking.event.property.mapper.class_.venues
                ),
                joinedload(
                    Booking.booking_seats
                )
                .joinedload(
                    BookingSeat.seat
                )
                .joinedload(
                    Seat.venue
                )
            )
            .where(
                Booking.user_id == user_id
            )
        )
        if status is not None:

            stmt = stmt.where(
                Booking.status == status
            )
        stmt = (
            stmt
            .order_by(
                Booking.created_at.desc(),
                Booking.id.desc()
            )
            .offset(skip)
            .limit(limit)
        )
        bookings = (
            self.db
            .scalars(stmt)
            .unique()
            .all()
        )
        for booking in bookings:
            booking.booking_seats.sort(
                key=lambda booking_seat: (
                    booking_seat.seat.row,
                    booking_seat.seat.number
                )
            )
        return bookings

    def get_event_booked_seat_ids(
    self,
    event_id: int,
    venue_id: int
    ) -> list[int]:

        now = datetime.now(timezone.utc)

        results = (
            self.db.query(Seat.id)
            .join(
                BookingSeat,
                BookingSeat.seat_id == Seat.id
            )
            .join(
                Booking,
                Booking.id == BookingSeat.booking_id
            )
            .filter(
                BookingSeat.event_id == event_id,
                Seat.venue_id == venue_id,
                BookingSeat.is_active.is_(True),

                or_(
                    Booking.status == BookingStatusEnum.CONFIRMED,

                    (
                        (Booking.status == BookingStatusEnum.PENDING)
                        &
                        (Booking.expires_at > now)
                    )
                )
            )
            .order_by(
                Seat.id.asc()
            )
            .all()
        )

        return [
            seat_id
            for (seat_id,) in results
        ]

    def get_all_bookings(
        self,
        skip: int = 0,
        limit: int = 20,
        status: Optional[BookingStatusEnum] = None
    ) -> Sequence[Booking]:

        stmt = (
            select(Booking)
            .options(
                joinedload(Booking.user),

                joinedload(
                    Booking.event
                ).joinedload(
                    Booking.event.property.mapper.class_.venues
                ),

                joinedload(
                    Booking.booking_seats
                )
                .joinedload(
                    BookingSeat.seat
                )
                .joinedload(
                    Seat.venue
                )
            )
        )
        if status is not None:
            stmt = stmt.where(
                Booking.status == status
            )
        stmt = (
            stmt
            .order_by(
                Booking.created_at.desc(),
                Booking.id.desc()
            )
            .offset(skip)
            .limit(limit)
        )
        bookings = (
            self.db
            .scalars(stmt)
            .unique()
            .all()
        )
        for booking in bookings:

            booking.booking_seats.sort(
                key=lambda booking_seat: (
                    booking_seat.seat.row,
                    booking_seat.seat.number
                )
            )
        return bookings

    def expire_pending_bookings(self) -> int:

        now = datetime.now(timezone.utc)
        stmt = (
            select(Booking)
            .where(
                Booking.status == BookingStatusEnum.PENDING,
                Booking.expires_at <= now
            )
        )
        expired_bookings = self.db.scalars(stmt).all()
        for booking in expired_bookings:
            booking.status = BookingStatusEnum.CANCELLED
            for booking_seat in booking.booking_seats:
                booking_seat.is_active = False
        self.db.flush()

        return len(expired_bookings)

