from decimal import Decimal
import json

import razorpay
from fastapi import Request
from razorpay.errors import SignatureVerificationError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import (
    ForbiddenException,
    NotFoundException,
    ResourceConflictException,
    ValidationException,
)
from app.models.booking import BookingStatusEnum
from app.models.payment import PaymentStatusEnum
from app.repositories.bookingRepo import BookingRepository
from app.repositories.paymentRepo import PaymentRepository
from app.schemas.payment import PaymentVerifyRequest
from app.services.redisService import RedisService


class PaymentService:

    def __init__(self, db: Session):
        self.db = db

        self.booking_repository = BookingRepository(db)
        self.payment_repository = PaymentRepository(db)

        self.client = razorpay.Client(
            auth=(
                settings.RAZORPAY_KEY_ID,
                settings.RAZORPAY_KEY_SECRET,
            )
        )

    def create_order(
        self,
        user_id: int,
        booking_id: int
    ):
        booking = self.booking_repository.get_by_id(
            booking_id
        )

        if booking is None:
            raise NotFoundException(
                f"Booking with ID {booking_id} not found"
            )

        if booking.user_id != user_id:
            raise ForbiddenException(
                "You are not allowed to pay for this booking"
            )

        if booking.status != BookingStatusEnum.PENDING:
            raise ValidationException(
                "Only pending bookings can be paid for"
            )

        existing_payment = (
            self.payment_repository.get_by_booking_id(
                booking_id
            )
        )

        if existing_payment is not None:
            raise ResourceConflictException(
                f"Payment already exists for booking ID {booking_id}"
            )

        amount = booking.total_price

        if amount is None or amount <= Decimal("0.00"):
            raise ValidationException(
                "Invalid booking amount"
            )

        amount_in_paise = int(
            amount * Decimal("100")
        )

        try:
            razorpay_order = self.client.order.create(
                {
                    "amount": amount_in_paise,
                    "currency": "INR",
                    "receipt": f"booking_{booking.id}",
                    "notes": {
                        "booking_id": str(booking.id),
                        "user_id": str(user_id),
                    },
                }
            )

        except Exception as e:
            raise ValidationException(
                "Unable to create Razorpay order",
                details={
                    "booking_id": booking.id
                },
            ) from e

        payment = self.payment_repository.create_payment(
            booking_id=booking.id,
            razorpay_order_id=razorpay_order["id"],
            amount=amount,
            currency="INR",
        )

        self.db.commit()

        return {
            "payment_id": payment.id,
            "razorpay_order_id": razorpay_order["id"],
            "amount": amount,
            "amount_in_paise": amount_in_paise,
            "currency": "INR",
            "razorpay_key_id": settings.RAZORPAY_KEY_ID,
        }

    def verify_payment(
        self,
        payment_data: PaymentVerifyRequest,
        user_id: int,
    ):
        payment = (
            self.payment_repository
            .get_by_razorpay_order_id(
                payment_data.razorpay_order_id
            )
        )

        if payment is None:
            raise NotFoundException(
                "Payment record not found"
            )

        booking = self.booking_repository.get_by_id(
            payment.booking_id
        )

        if booking is None:
            raise NotFoundException(
                "Associated booking not found"
            )

        if booking.user_id != user_id:
            raise ForbiddenException(
                "You are not allowed to verify this payment"
            )

        if payment.status == PaymentStatusEnum.SUCCESS:
            return payment

        try:
            self.client.utility.verify_payment_signature(
                {
                    "razorpay_order_id":
                        payment_data.razorpay_order_id,

                    "razorpay_payment_id":
                        payment_data.razorpay_payment_id,

                    "razorpay_signature":
                        payment_data.razorpay_signature,
                }
            )

        except SignatureVerificationError as e:
            self.payment_repository.update_status(
                payment=payment,
                status=PaymentStatusEnum.FAILED,
            )

            self.db.commit()

            raise ValidationException(
                "Payment signature verification failed"
            ) from e

        self.payment_repository.mark_success(
            payment=payment,
            razorpay_payment_id=
                payment_data.razorpay_payment_id,
        )

        if booking.status == BookingStatusEnum.PENDING:
            self.booking_repository.update_status_booking(
                booking=booking,
                new_status=BookingStatusEnum.CONFIRMED,
            )

        self.db.commit()

        for booking_seat in booking.booking_seats:
            RedisService.release_seat(
                event_id=booking.event_id,
                seat_id=booking_seat.seat_id,
                booking_id=booking.id
            )

        return payment

    async def handle_webhook(
        self,
        request: Request,
        signature: str
    ):
        body = await request.body()

        try:
            self.client.utility.verify_webhook_signature(
                body.decode("utf-8"),
                signature,
                settings.RAZORPAY_WEBHOOK_SECRET,
            )

        except SignatureVerificationError as e:
            raise ValidationException(
                "Invalid Razorpay webhook signature"
            ) from e

        try:
            payload = json.loads(body)

        except json.JSONDecodeError as e:
            raise ValidationException(
                "Invalid webhook payload"
            ) from e

        event = payload.get("event")

        print(
            f"RAZORPAY WEBHOOK EVENT: {event}"
        )

        supported_events = {
            "payment.captured",
            "order.paid",
            "payment.failed",
        }

        if event not in supported_events:
            return {
                "status": "ignored",
                "event": event,
            }

        payment_entity = (
            payload
            .get("payload", {})
            .get("payment", {})
            .get("entity", {})
        )

        razorpay_payment_id = payment_entity.get(
            "id"
        )

        razorpay_order_id = payment_entity.get(
            "order_id"
        )

        if not razorpay_order_id:
            order_entity = (
                payload
                .get("payload", {})
                .get("order", {})
                .get("entity", {})
            )

            razorpay_order_id = order_entity.get(
                "id"
            )

        print(
            "RAZORPAY PAYMENT:"
            f" payment_id={razorpay_payment_id},"
            f" order_id={razorpay_order_id}"
        )

        if not razorpay_order_id:
            return {
                "status": "ignored",
                "reason": "Missing Razorpay order ID",
            }

        payment = (
            self.payment_repository
            .get_by_razorpay_order_id(
                razorpay_order_id
            )
        )

        if payment is None:
            return {
                "status": "ignored",
                "reason": "Payment record not found",
            }

        booking = self.booking_repository.get_by_id(
            payment.booking_id
        )

        if booking is None:
            return {
                "status": "ignored",
                "reason": "Booking not found",
            }

        if event == "payment.failed":
            print(
                f"Payment FAILED for booking {booking.id}"
            )

            self.payment_repository.update_status(
                payment=payment,
                status=PaymentStatusEnum.FAILED,
            )

            if booking.status == BookingStatusEnum.PENDING:
                self.booking_repository.update_status_booking(
                    booking=booking,
                    new_status=BookingStatusEnum.PAYMENT_FAILED,
                )

                for booking_seat in booking.booking_seats:
                    booking_seat.is_active = False

            self.db.commit()

            for booking_seat in booking.booking_seats:
                RedisService.release_seat(
                    event_id=booking.event_id,
                    seat_id=booking_seat.seat_id,
                    booking_id=booking.id
                )

            return {
                "status": "processed",
                "event": event,
                "booking_id": booking.id,
                "payment_status":
                    payment.status.value,
                "booking_status":
                    booking.status.value,
            }

        if event == "payment.captured":
            print(
                f"Payment CAPTURED for booking "
                f"{booking.id}"
            )

            if payment.status != PaymentStatusEnum.SUCCESS:
                self.payment_repository.mark_success(
                    payment=payment,
                    razorpay_payment_id=
                        razorpay_payment_id,
                )

            if booking.status == BookingStatusEnum.PENDING:
                self.booking_repository.update_status_booking(
                    booking=booking,
                    new_status=BookingStatusEnum.CONFIRMED,
                )

            self.db.commit()

            for booking_seat in booking.booking_seats:
                RedisService.release_seat(
                    event_id=booking.event_id,
                    seat_id=booking_seat.seat_id,
                    booking_id=booking.id
                )

            return {
                "status": "processed",
                "event": event,
                "booking_id": booking.id,
                "payment_status":
                    payment.status.value,
                "booking_status":
                    booking.status.value,
            }

        if event == "order.paid":
            print(
                f"Order PAID for booking "
                f"{booking.id}"
            )

            if payment.status != PaymentStatusEnum.SUCCESS:
                self.payment_repository.mark_success(
                    payment=payment,
                    razorpay_payment_id=
                        razorpay_payment_id,
                )

            if booking.status == BookingStatusEnum.PENDING:
                self.booking_repository.update_status_booking(
                    booking=booking,
                    new_status=BookingStatusEnum.CONFIRMED,
                )

            self.db.commit()

            for booking_seat in booking.booking_seats:
                RedisService.release_seat(
                    event_id=booking.event_id,
                    seat_id=booking_seat.seat_id,
                    booking_id=booking.id
                )

            return {
                "status": "processed",
                "event": event,
                "booking_id": booking.id,
                "payment_status":
                    payment.status.value,
                "booking_status":
                    booking.status.value,
            }

        return {
            "status": "ignored",
            "event": event,
        }