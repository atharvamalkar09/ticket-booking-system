from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.services.bookingService import BookingService
from app.models.booking import BookingStatusEnum
from app.models.user import UserRole
from app.core.exceptions import (
    NotFoundException,
    ValidationException,
    ForbiddenException,
    SeatAlreadyBookedException,
)


@pytest.fixture
def service():
    db = MagicMock()

    service = BookingService.__new__(BookingService)

    service.db = db
    service.booking_repo = MagicMock()
    service.event_repo = MagicMock()
    service.seat_repo = MagicMock()

    return service


@pytest.fixture
def user():
    return SimpleNamespace(
        id=1,
        role=UserRole.USER
    )


@pytest.fixture
def future_event():
    return SimpleNamespace(
        id=1,
        start_time=datetime.now(timezone.utc) + timedelta(days=1),
        base_price=500,
        venues=[
            SimpleNamespace(id=10)
        ]
    )


def test_get_booking_by_id_success(service, user):

    booking = SimpleNamespace(
        id=1,
        user_id=1,
        status=BookingStatusEnum.PENDING
    )

    service.booking_repo.get_by_id.return_value = booking

    result = service.get_booking_by_id(
        booking_id=1,
        user=user
    )

    assert result == booking
    service.booking_repo.get_by_id.assert_called_once_with(1)


def test_get_booking_by_id_not_found(service, user):

    service.booking_repo.get_by_id.return_value = None

    with pytest.raises(NotFoundException):
        service.get_booking_by_id(
            booking_id=999,
            user=user
        )


def test_get_booking_by_id_forbidden(service, user):

    booking = SimpleNamespace(
        id=1,
        user_id=99,
        status=BookingStatusEnum.PENDING
    )

    service.booking_repo.get_by_id.return_value = booking

    with pytest.raises(ForbiddenException):
        service.get_booking_by_id(
            booking_id=1,
            user=user
        )


def test_create_booking_event_not_found(service, user):

    booking_in = SimpleNamespace(
        event_id=999,
        seat_ids=[1]
    )

    service.event_repo.get_by_id.return_value = None

    with pytest.raises(NotFoundException):
        service.create_booking(
            user=user,
            booking_in=booking_in
        )


def test_create_booking_event_already_started(
    service,
    user
):

    event = SimpleNamespace(
        id=1,
        start_time=datetime.now(timezone.utc) - timedelta(hours=1),
        base_price=500,
        venues=[]
    )

    service.event_repo.get_by_id.return_value = event

    booking_in = SimpleNamespace(
        event_id=1,
        seat_ids=[1]
    )

    with pytest.raises(ValidationException):
        service.create_booking(
            user=user,
            booking_in=booking_in
        )


def test_create_booking_without_seats(
    service,
    user,
    future_event
):

    service.event_repo.get_by_id.return_value = future_event

    booking_in = SimpleNamespace(
        event_id=1,
        seat_ids=[]
    )

    with pytest.raises(ValidationException):
        service.create_booking(
            user=user,
            booking_in=booking_in
        )


def test_create_booking_duplicate_seat_ids(
    service,
    user,
    future_event
):

    service.event_repo.get_by_id.return_value = future_event

    booking_in = SimpleNamespace(
        event_id=1,
        seat_ids=[1, 1]
    )

    with pytest.raises(ValidationException):
        service.create_booking(
            user=user,
            booking_in=booking_in
        )


def test_create_booking_seat_not_found(
    service,
    user,
    future_event
):

    service.event_repo.get_by_id.return_value = future_event
    service.seat_repo.get_by_id.return_value = None

    booking_in = SimpleNamespace(
        event_id=1,
        seat_ids=[999]
    )

    with pytest.raises(NotFoundException):
        service.create_booking(
            user=user,
            booking_in=booking_in
        )


def test_create_booking_seat_belongs_to_wrong_venue(
    service,
    user,
    future_event
):

    service.event_repo.get_by_id.return_value = future_event

    seat = SimpleNamespace(
        id=1,
        venue_id=999
    )

    service.seat_repo.get_by_id.return_value = seat

    booking_in = SimpleNamespace(
        event_id=1,
        seat_ids=[1]
    )

    with pytest.raises(ValidationException):
        service.create_booking(
            user=user,
            booking_in=booking_in
        )


def test_create_booking_seat_already_booked(
    service,
    user,
    future_event
):

    service.event_repo.get_by_id.return_value = future_event

    seat = SimpleNamespace(
        id=1,
        venue_id=10
    )

    service.seat_repo.get_by_id.return_value = seat

    service.booking_repo.get_active_booking_for_seat.return_value = (
        SimpleNamespace(id=100)
    )

    booking_in = SimpleNamespace(
        event_id=1,
        seat_ids=[1]
    )

    with pytest.raises(SeatAlreadyBookedException):
        service.create_booking(
            user=user,
            booking_in=booking_in
        )


def test_create_booking_success(
    service,
    user,
    future_event
):

    service.event_repo.get_by_id.return_value = future_event

    seat = SimpleNamespace(
        id=1,
        venue_id=10
    )

    service.seat_repo.get_by_id.return_value = seat

    service.booking_repo.get_active_booking_for_seat.return_value = None

    booking = SimpleNamespace(
        id=100,
        user_id=1,
        event_id=1,
        status=BookingStatusEnum.PENDING
    )

    service.booking_repo.create_booking.return_value = booking

    booking_in = SimpleNamespace(
        event_id=1,
        seat_ids=[1]
    )

    result = service.create_booking(
        user=user,
        booking_in=booking_in
    )

    assert result == booking

    service.booking_repo.create_booking.assert_called_once_with(
        user_id=1,
        booking_in=booking_in,
        price_per_seat=500
    )

    service.db.commit.assert_called_once()
    service.db.refresh.assert_called_once_with(booking)