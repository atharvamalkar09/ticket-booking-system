from typing import Sequence

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.user import User, UserRole
from app.models.event import Event
from app.models.venue import Venue
from app.models.booking import Booking, BookingStatusEnum


class AdminDashboardRepository:

    def __init__(self, db: Session):
        self.db = db

    def count_users(self) -> int:

        stmt = select(func.count(User.id)).where(
            User.role == UserRole.USER
        )

        return self.db.scalar(stmt) or 0


    def count_active_users(self) -> int:

        stmt = select(
            func.count(User.id)
        ).where(
            User.role == UserRole.USER,
            User.is_active.is_(True)
        )

        return self.db.scalar(stmt) or 0


    def count_inactive_users(self) -> int:

        stmt = select(
            func.count(User.id)
        ).where(
            User.role == UserRole.USER,
            User.is_active.is_(False)
        )

        return self.db.scalar(stmt) or 0

    def count_events(self) -> int:

        stmt = select(
            func.count(Event.id)
        )

        return self.db.scalar(stmt) or 0

    def count_venues(self) -> int:

        stmt = select(
            func.count(Venue.id)
        ).where(
            Venue.is_active.is_(True)
        )

        return self.db.scalar(stmt) or 0

    def count_bookings(self) -> int:

        stmt = select(
            func.count(Booking.id)
        )

        return self.db.scalar(stmt) or 0


    def count_confirmed_bookings(self) -> int:

        stmt = select(
            func.count(Booking.id)
        ).where(
            Booking.status == BookingStatusEnum.CONFIRMED
        )

        return self.db.scalar(stmt) or 0


    def count_pending_bookings(self) -> int:

        stmt = select(
            func.count(Booking.id)
        ).where(
            Booking.status == BookingStatusEnum.PENDING
        )

        return self.db.scalar(stmt) or 0


    def count_cancelled_bookings(self) -> int:

        stmt = select(
            func.count(Booking.id)
        ).where(
            Booking.status == BookingStatusEnum.CANCELLED
        )

        return self.db.scalar(stmt) or 0

    def get_recent_bookings(
        self,
        limit: int = 5
    ) -> Sequence[Booking]:

        stmt = (
            select(Booking)
            .join(User, Booking.user_id == User.id)
            .join(Event, Booking.event_id == Event.id)
            .order_by(
                Booking.created_at.desc(),
                Booking.id.desc()
            )
            .limit(limit)
        )

        return self.db.scalars(stmt).all()