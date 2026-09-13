import redis
import app.services.redisService as redis_service_module

from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.services.paymentService import PaymentService
from app.models.booking import BookingStatusEnum
from app.models.payment import PaymentStatusEnum
from app.core.exceptions import (
    NotFoundException,
    ForbiddenException,
    ResourceConflictException,
    ValidationException,
)


test_redis_client = redis.Redis(
    host="localhost",
    port=6379,
    db=0,
    decode_responses=True,
)

redis_service_module.redis_client = test_redis_client


@pytest.fixture
def service():
    db = MagicMock()

    service = PaymentService.__new__(PaymentService)

    service.db = db
    service.booking_repository = MagicMock()
    service.payment_repository = MagicMock()
    service.client = MagicMock()

    return service


def test_create_order_booking_not_found(service):

    service.booking_repository.get_by_id.return_value = None

    with pytest.raises(NotFoundException):
        service.create_order(
            user_id=1,
            booking_id=999
        )


def test_create_order_forbidden(service):

    booking = SimpleNamespace(
        id=1,
        user_id=99,
        status=BookingStatusEnum.PENDING,
        total_price=Decimal("500.00"),
    )

    service.booking_repository.get_by_id.return_value = booking

    with pytest.raises(ForbiddenException):
        service.create_order(
            user_id=1,
            booking_id=1
        )


def test_create_order_non_pending_booking(service):

    booking = SimpleNamespace(
        id=1,
        user_id=1,
        status=BookingStatusEnum.CONFIRMED,
        total_price=Decimal("500.00"),
    )

    service.booking_repository.get_by_id.return_value = booking

    with pytest.raises(ValidationException):
        service.create_order(
            user_id=1,
            booking_id=1
        )


def test_create_order_duplicate_payment(service):

    booking = SimpleNamespace(
        id=1,
        user_id=1,
        status=BookingStatusEnum.PENDING,
        total_price=Decimal("500.00"),
    )

    service.booking_repository.get_by_id.return_value = booking

    service.payment_repository.get_by_booking_id.return_value = (
        SimpleNamespace(id=10)
    )

    with pytest.raises(ResourceConflictException):
        service.create_order(
            user_id=1,
            booking_id=1
        )


def test_create_order_success(service):

    booking = SimpleNamespace(
        id=1,
        user_id=1,
        status=BookingStatusEnum.PENDING,
        total_price=Decimal("500.00"),
    )

    service.booking_repository.get_by_id.return_value = booking
    service.payment_repository.get_by_booking_id.return_value = None

    service.client.order.create.return_value = {
        "id": "order_test_123"
    }

    payment = SimpleNamespace(
        id=10,
        booking_id=1,
        status=PaymentStatusEnum.CREATED
    )

    service.payment_repository.create_payment.return_value = payment

    result = service.create_order(
        user_id=1,
        booking_id=1
    )

    assert result["payment_id"] == 10
    assert result["razorpay_order_id"] == "order_test_123"
    assert result["amount"] == Decimal("500.00")
    assert result["amount_in_paise"] == 50000
    assert result["currency"] == "INR"

    service.client.order.create.assert_called_once()
    service.payment_repository.create_payment.assert_called_once()
    service.db.commit.assert_called_once()


def test_verify_payment_not_found(service):

    service.payment_repository.get_by_razorpay_order_id.return_value = None

    payment_data = SimpleNamespace(
        razorpay_order_id="order_test",
        razorpay_payment_id="pay_test",
        razorpay_signature="signature"
    )

    with pytest.raises(NotFoundException):
        service.verify_payment(
            payment_data=payment_data,
            user_id=1
        )


def test_verify_payment_forbidden(service):

    payment = SimpleNamespace(
        booking_id=1,
        status=PaymentStatusEnum.CREATED
    )

    booking = SimpleNamespace(
        id=1,
        user_id=99,
        status=BookingStatusEnum.PENDING
    )

    service.payment_repository.get_by_razorpay_order_id.return_value = payment
    service.booking_repository.get_by_id.return_value = booking

    payment_data = SimpleNamespace(
        razorpay_order_id="order_test",
        razorpay_payment_id="pay_test",
        razorpay_signature="signature"
    )

    with pytest.raises(ForbiddenException):
        service.verify_payment(
            payment_data=payment_data,
            user_id=1
        )


def test_verify_payment_already_successful(service):

    payment = SimpleNamespace(
        booking_id=1,
        status=PaymentStatusEnum.SUCCESS
    )

    booking = SimpleNamespace(
        id=1,
        user_id=1,
        status=BookingStatusEnum.CONFIRMED
    )

    service.payment_repository.get_by_razorpay_order_id.return_value = payment
    service.booking_repository.get_by_id.return_value = booking

    payment_data = SimpleNamespace(
        razorpay_order_id="order_test",
        razorpay_payment_id="pay_test",
        razorpay_signature="signature"
    )

    result = service.verify_payment(
        payment_data=payment_data,
        user_id=1
    )

    assert result == payment


def test_verify_payment_success(service):

    payment = SimpleNamespace(
        id=10,
        booking_id=1,
        status=PaymentStatusEnum.CREATED
    )

    booking_seat = SimpleNamespace(
        seat_id=101
    )

    booking = SimpleNamespace(
        id=1,
        user_id=1,
        event_id=1,
        status=BookingStatusEnum.PENDING,
        booking_seats=[booking_seat]
    )

    service.payment_repository.get_by_razorpay_order_id.return_value = payment
    service.booking_repository.get_by_id.return_value = booking

    service.client.utility.verify_payment_signature.return_value = None

    payment_data = SimpleNamespace(
        razorpay_order_id="order_test",
        razorpay_payment_id="pay_test",
        razorpay_signature="valid_signature"
    )

    result = service.verify_payment(
        payment_data=payment_data,
        user_id=1
    )

    assert result == payment

    service.payment_repository.mark_success.assert_called_once_with(
        payment=payment,
        razorpay_payment_id="pay_test"
    )

    service.booking_repository.update_status_booking.assert_called_once_with(
        booking=booking,
        new_status=BookingStatusEnum.CONFIRMED
    )

    service.db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_webhook_invalid_signature(service):

    from razorpay.errors import SignatureVerificationError

    service.client.utility.verify_webhook_signature.side_effect = (
        SignatureVerificationError
    )

    request = MagicMock()
    request.body = AsyncMock(
        return_value=b"{}"
    )

    with pytest.raises(ValidationException):
        await service.handle_webhook(
            request=request,
            signature="invalid"
        )


@pytest.mark.asyncio
async def test_webhook_unsupported_event(service):

    body = b'{"event": "payment.authorized"}'

    request = MagicMock()
    request.body = AsyncMock(
        return_value=body
    )

    result = await service.handle_webhook(
        request=request,
        signature="valid"
    )

    assert result["status"] == "ignored"
    assert result["event"] == "payment.authorized"


@pytest.mark.asyncio
async def test_webhook_payment_failed_releases_seats(service):

    body = (
        b'{"event": "payment.failed",'
        b' "payload": {"payment": {"entity": {'
        b'"id": "pay_failed",'
        b'"order_id": "order_failed"'
        b'}}}}'
    )

    request = MagicMock()
    request.body = AsyncMock(
        return_value=body
    )

    payment = SimpleNamespace(
        id=10,
        booking_id=1,
        status=PaymentStatusEnum.CREATED
    )

    service.payment_repository.update_status.side_effect = (
        lambda payment, status: setattr(
            payment,
            "status",
            status
        )
    )

    booking_seat_1 = SimpleNamespace(
        seat_id=101,
        is_active=True
    )

    booking_seat_2 = SimpleNamespace(
        seat_id=102,
        is_active=True
    )

    booking = SimpleNamespace(
        id=1,
        event_id=1,
        status=BookingStatusEnum.PENDING,
        booking_seats=[
            booking_seat_1,
            booking_seat_2
        ]
    )

    service.booking_repository.update_status_booking.side_effect = (
        lambda booking, new_status: setattr(
            booking,
            "status",
            new_status
        )
    )

    service.payment_repository.get_by_razorpay_order_id.return_value = payment
    service.booking_repository.get_by_id.return_value = booking

    result = await service.handle_webhook(
        request=request,
        signature="valid"
    )

    assert result["status"] == "processed"
    assert payment.status == PaymentStatusEnum.FAILED
    assert booking.status == BookingStatusEnum.PAYMENT_FAILED
    assert booking_seat_1.is_active is False
    assert booking_seat_2.is_active is False

    service.db.commit.assert_called_once()