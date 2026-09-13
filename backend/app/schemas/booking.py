from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum

from app.schemas.event import EventResponse


class BookingStatusEnum(str, Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    PAYMENT_FAILED = "PAYMENT_FAILED"
    CANCELLED = "CANCELLED"


class BookingCreate(BaseModel):
    event_id: int = Field(
        ...,
        description="Target event ID"
    )

    seat_ids: List[int] = Field(
        ...,
        min_length=1,
        description="List of selected seat IDs"
    )


class BookingStatusUpdate(BaseModel):
    status: BookingStatusEnum

class SeatSummary(BaseModel):
    id: int
    row: str
    number: int

    class Config:
        from_attributes = True


class VenueSummary(BaseModel):
    id: int
    name: str
    location: str

    class Config:
        from_attributes = True


class EventSummary(BaseModel):
    id: int
    title: str
    start_time: datetime

    venues: List[VenueSummary] = []

    class Config:
        from_attributes = True


class VenueResponse(BaseModel):
    id: int
    name: str
    location: str

    model_config = {
        "from_attributes": True
    }


class SeatResponse(BaseModel):
    id: int
    row: str
    number: int
    venue: VenueResponse

    model_config = {
        "from_attributes": True
    }

class UserSummary(BaseModel):
    username: str
    email: str
    phone_no: Optional[str] = None

    class Config:
        from_attributes = True

class BookingSeatResponse(BaseModel):
    id: int
    seat_id: int
    price: float
    seat: SeatResponse

    class Config:
        from_attributes = True

class BookingResponse(BaseModel):
    id: int
    user_id: int
    event_id: int
    total_price: float
    status: BookingStatusEnum
    created_at: datetime
    user: UserSummary | None = None
    event: EventResponse | None = None
    booking_seats: List[BookingSeatResponse]

    class Config:
        from_attributes = True