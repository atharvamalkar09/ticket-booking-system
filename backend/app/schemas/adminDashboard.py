from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class RecentBookingResponse(BaseModel):
    id: int
    user_id: int
    username: str
    event_id: int
    event_title: str
    total_price: Decimal
    status: str
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )

class AdminDashboardResponse(BaseModel):
    total_users: int
    active_users: int
    inactive_users: int

    total_events: int

    total_venues: int

    total_bookings: int
    confirmed_bookings: int
    pending_bookings: int
    cancelled_bookings: int

    recent_bookings: list[RecentBookingResponse]