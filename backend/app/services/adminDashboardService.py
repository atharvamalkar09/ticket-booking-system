from sqlalchemy.orm import Session

from app.repositories.adminDashboardRepo import (
    AdminDashboardRepository
)

from app.schemas.adminDashboard import (
    AdminDashboardResponse,
    RecentBookingResponse
)


class AdminDashboardService:
    def __init__(self, db: Session):
        self.db = db
        self.dashboard_repo = AdminDashboardRepository(
            db
        )

    def get_dashboard(self) -> AdminDashboardResponse:
        total_users = (
            self.dashboard_repo.count_users()
        )
        active_users = (
            self.dashboard_repo.count_active_users()
        )
        inactive_users = (
            self.dashboard_repo.count_inactive_users()
        )
        total_events = (
            self.dashboard_repo.count_events()
        )
        total_venues = (
            self.dashboard_repo.count_venues()
        )
        total_bookings = (
            self.dashboard_repo.count_bookings()
        )
        confirmed_bookings = (
            self.dashboard_repo.count_confirmed_bookings()
        )
        pending_bookings = (
            self.dashboard_repo.count_pending_bookings()
        )
        cancelled_bookings = (
            self.dashboard_repo.count_cancelled_bookings()
        )
        bookings = (
            self.dashboard_repo.get_recent_bookings(
                limit=5
            )
        )
        recent_bookings = [
            RecentBookingResponse(
                id=booking.id,
                user_id=booking.user_id,
                username=booking.user.username,
                event_id=booking.event_id,
                event_title=booking.event.title,
                total_price=booking.total_price,
                status=booking.status.value,
                created_at=booking.created_at
            )
            for booking in bookings
        ]

        return AdminDashboardResponse(
            total_users=total_users,
            active_users=active_users,
            inactive_users=inactive_users,
            total_events=total_events,
            total_venues=total_venues,
            total_bookings=total_bookings,
            confirmed_bookings=confirmed_bookings,
            pending_bookings=pending_bookings,
            cancelled_bookings=cancelled_bookings,
            recent_bookings=recent_bookings
        )