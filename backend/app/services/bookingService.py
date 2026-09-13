from datetime import datetime, timezone
from typing import List, Optional, Sequence

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.booking import (
    Booking,
    BookingStatusEnum as ModelBookingStatusEnum
)

from app.models.user import (
    User,
    UserRole
)

from app.repositories.bookingRepo import BookingRepository
from app.repositories.eventRepo import EventRepository
from app.repositories.seatRepo import SeatRepository

from app.schemas.booking import (
    BookingCreate,
    BookingStatusEnum as SchemaBookingStatusEnum
)

from app.core.exceptions import (
    BaseAppException,
    NotFoundException,
    ValidationException,
    ForbiddenException,
    SeatAlreadyBookedException,
)

from app.services.redisService import RedisService


class BookingService:

    def __init__(
        self,
        db: Session
    ):
        self.db = db

        self.booking_repo = BookingRepository(db)
        self.event_repo = EventRepository(db)
        self.seat_repo = SeatRepository(db)

    def create_booking(
        self,
        user: User,
        booking_in: BookingCreate
    ) -> Booking:

        event = self.event_repo.get_by_id(
            booking_in.event_id
        )

        if not event:

            raise NotFoundException(
                message=(
                    f"Event {booking_in.event_id} not found"
                )
            )
        now = datetime.now(timezone.utc)

        if event.start_time <= now:

            raise ValidationException(
                message=(
                    "Cannot book seats for an event "
                    "that has already started"
                )
            )

        if not booking_in.seat_ids:

            raise ValidationException(
                message=(
                    "At least one seat must be selected"
                )
            )

        if len(booking_in.seat_ids) != len(
            set(booking_in.seat_ids)
        ):

            raise ValidationException(
                message=(
                    "Duplicate seat IDs are not allowed"
                )
            )
        event_venue_ids = {
            venue.id
            for venue in event.venues
        }
        seats = []

        for seat_id in booking_in.seat_ids:

            seat = self.seat_repo.get_by_id(
                seat_id
            )

            if not seat:

                raise NotFoundException(
                    message=(
                        f"Seat {seat_id} not found"
                    )
                )

            if seat.venue_id not in event_venue_ids:

                raise ValidationException(
                    message=(
                        f"Seat {seat.id} does not belong "
                        f"to any venue associated with "
                        f"event {event.id}"
                    )
                )

            seats.append(seat)

        for seat in seats:

            active_booking = (
                self.booking_repo
                .get_active_booking_for_seat(
                    event_id=booking_in.event_id,
                    seat_id=seat.id
                )
            )

            if active_booking:

                raise SeatAlreadyBookedException(
                    seat_id=seat.id,
                    event_id=event.id
                )
        locked_seats = []

        try:

            booking = (
                self.booking_repo
                .create_booking(
                    user_id=user.id,
                    booking_in=booking_in,
                    price_per_seat=event.base_price
                )
            )

            self.db.flush()

            for seat in seats:

                lock_acquired = (
                    RedisService.lock_seat(
                        event_id=event.id,
                        seat_id=seat.id,
                        booking_id=booking.id,
                        ttl_seconds=300
                    )
                )

                if not lock_acquired:

                    raise SeatAlreadyBookedException(
                        seat_id=seat.id,
                        event_id=event.id
                    )

                locked_seats.append(
                    seat.id
                )
            self.db.commit()
            self.db.refresh(booking)

            return booking

        except IntegrityError as e:

            self.db.rollback()
            for seat_id in locked_seats:

                RedisService.release_seat(
                    event_id=event.id,
                    seat_id=seat_id,
                    booking_id=booking.id
                )

            error_text = str(e.orig)

            if "uq_event_seat_booking" in error_text:

                raise ValidationException(
                    message=(
                        "One or more selected seats were booked "
                        "by another user. Please select "
                        "different seats."
                    )
                )

            raise BaseAppException(
                message="Failed to create booking",
                details={
                    "raw_error": str(e)
                }
            )
        except BaseAppException:

            self.db.rollback()
            for seat_id in locked_seats:

                RedisService.release_seat(
                    event_id=event.id,
                    seat_id=seat_id,
                    booking_id=booking.id
                )

            raise
        except Exception as e:

            self.db.rollback()

            for seat_id in locked_seats:

                RedisService.release_seat(
                    event_id=event.id,
                    seat_id=seat_id,
                    booking_id=booking.id
                )

            raise BaseAppException(
                message=(
                    "An unexpected error occurred "
                    "while creating booking"
                ),
                details={
                    "raw_error": str(e)
                }
            )

    def get_booking_by_id(
        self,
        booking_id: int,
        user: Optional[User] = None
    ) -> Booking:

        booking = self.booking_repo.get_by_id(
            booking_id
        )

        if not booking:

            raise NotFoundException(
                message=(
                    f"Booking {booking_id} not found"
                )
            )

        if user is not None:

            if (
                booking.user_id != user.id
                and user.role != UserRole.ADMIN
            ):

                raise ForbiddenException(
                    message=(
                        "You are not allowed to "
                        "access this booking"
                    )
                )

        return booking

    def get_user_bookings(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 20,
        status: Optional[
            SchemaBookingStatusEnum
        ] = None
    ) -> Sequence[Booking]:

        model_status = None

        if status is not None:

            model_status = ModelBookingStatusEnum(
                status.value
            )

        return self.booking_repo.get_user_bookings(
            user_id=user_id,
            skip=skip,
            limit=limit,
            status=model_status
        )

    def cancel_booking(
        self,
        booking_id: int,
        user: User
    ) -> Booking:

        booking = self.get_booking_by_id(
            booking_id=booking_id,
            user=user
        )

        if booking.status == ModelBookingStatusEnum.CANCELLED:

            raise ValidationException(
                message=(
                    "Booking is already cancelled"
                )
            )

        try:

            updated_booking = (
                self.booking_repo
                .update_status_booking(
                    booking=booking,
                    new_status=(
                        ModelBookingStatusEnum.CANCELLED
                    )
                )
            )

            for booking_seat in booking.booking_seats:

                booking_seat.is_active = False

            for booking_seat in booking.booking_seats:

                RedisService.release_seat(
                    event_id=booking.event_id,
                    seat_id=booking_seat.seat_id,
                    booking_id=booking.id
                )

            self.db.commit()
            self.db.refresh(updated_booking)

            return updated_booking

        except BaseAppException:

            self.db.rollback()

            raise

        except Exception as e:

            self.db.rollback()

            raise BaseAppException(
                message=(
                    "An unexpected error occurred "
                    "while cancelling the booking"
                ),
                details={
                    "raw_error": str(e)
                }
            )

    def get_event_booked_seats(
    self,
    event_id: int,
    venue_id: int
    ) -> List[int]:
        return self.booking_repo.get_event_booked_seat_ids(
            event_id=event_id,
            venue_id=venue_id
        )

    def get_all_bookings(
        self,
        skip: int = 0,
        limit: int = 20,
        status: Optional[
            SchemaBookingStatusEnum
        ] = None
    ) -> Sequence[Booking]:

        model_status = None

        if status is not None:

            model_status = ModelBookingStatusEnum(
                status.value
            )

        return self.booking_repo.get_all_bookings(
            skip=skip,
            limit=limit,
            status=model_status
        )

    def admin_update_booking_status(
        self,
        booking_id: int,
        new_status: SchemaBookingStatusEnum
    ) -> Booking:

        booking = self.booking_repo.get_by_id(
            booking_id
        )

        if not booking:

            raise NotFoundException(
                message=(
                    f"Booking {booking_id} not found"
                )
            )

        target_status = ModelBookingStatusEnum(
            new_status.value
        )

        current_status = booking.status

        if (
            current_status
            == ModelBookingStatusEnum.PENDING
            and target_status
            == ModelBookingStatusEnum.CONFIRMED
        ):

            pass

        elif (
            current_status
            == ModelBookingStatusEnum.PENDING
            and target_status
            == ModelBookingStatusEnum.CANCELLED
        ):

            pass

        elif (
            current_status== ModelBookingStatusEnum.CONFIRMED and target_status == ModelBookingStatusEnum.CANCELLED
        ):

            pass

        elif current_status == target_status:

            raise ValidationException(
                message=(
                    f"Booking is already in "
                    f"{current_status.value} status"
                )
            )

        else:

            raise ValidationException(
                message=(
                    f"Invalid booking status transition: "
                    f"{current_status.value} -> "
                    f"{target_status.value}"
                )
            )

        try:

            updated_booking = (
                self.booking_repo
                .update_status_booking(
                    booking=booking,
                    new_status=target_status
                )
            )
            if (
                target_status
                == ModelBookingStatusEnum.CONFIRMED
            ):

                for booking_seat in booking.booking_seats:

                    booking_seat.is_active = True

                    RedisService.release_seat(
                        event_id=booking.event_id,
                        seat_id=booking_seat.seat_id,
                        booking_id=booking.id
                    )

            elif (
                target_status
                == ModelBookingStatusEnum.CANCELLED
            ):

                for booking_seat in booking.booking_seats:

                    booking_seat.is_active = False

                    RedisService.release_seat(
                        event_id=booking.event_id,
                        seat_id=booking_seat.seat_id,
                        booking_id=booking.id
                    )
            self.db.commit()
            self.db.refresh(updated_booking)

            return updated_booking

        except BaseAppException:

            self.db.rollback()

            raise

        except Exception as e:

            self.db.rollback()

            raise BaseAppException(
                message=(
                    "An unexpected error occurred "
                    "while updating booking status"
                ),
                details={
                    "raw_error": str(e)
                }
            )

    def expire_pending_bookings(self) -> int:

        expired_count = (
            self.booking_repo
            .expire_pending_bookings()
        )

        self.db.commit()

        return expired_count