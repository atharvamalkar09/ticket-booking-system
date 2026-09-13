from typing import List, Sequence, Optional

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.repositories.seatRepo import SeatRepository
from app.repositories.venueRepo import VenueRepository
from app.models.seat import Seat
from app.core.exceptions import (
    NotFoundException,
    ResourceConflictException,
    ValidationException,
)
from app.schemas.seat import (
    SeatCreate,
    SeatBulkCreate,
    SeatCategoryEnum
)


class SeatService:
    def __init__(self, db: Session):
        self.db = db
        self.seat_repo = SeatRepository(db)
        self.venue_repo = VenueRepository(db)

    def _verify_venue_exists(self, venue_id: int) -> None:
        venue = self.venue_repo.get_by_id(venue_id)

        if not venue:
            raise NotFoundException(
                message=f"Venue with ID {venue_id} not found"
            )

    def _verify_seat_capacity(
        self,
        venue_id: int,
        additional_seats: int = 1
    ) -> None:
        venue = self.venue_repo.get_by_id(venue_id)

        if not venue:
            raise NotFoundException(
                message=f"Venue with ID {venue_id} not found"
            )

        current_seat_count = self.seat_repo.count_by_venue(
            venue_id=venue_id
        )

        if current_seat_count + additional_seats > venue.capacity:
            raise ValidationException(
                message=(
                    f"Cannot create {additional_seats} seat(s). "
                    f"Venue capacity is {venue.capacity}, "
                    f"but {current_seat_count} seat(s) already exist."
                )
            )

    def create_seat(self, seat_in: SeatCreate) -> Seat:
        self._verify_venue_exists(seat_in.venue_id)

        self._verify_seat_capacity(
            venue_id=seat_in.venue_id,
            additional_seats=1
        )

        existing_seat = self.seat_repo.get_by_venue_row_number(
            venue_id=seat_in.venue_id,
            row=seat_in.row,
            number=seat_in.number
        )

        if existing_seat:
            raise ResourceConflictException(
                message=(
                    f"Seat {seat_in.row.upper()}-{seat_in.number} "
                    f"already exists for venue ID {seat_in.venue_id}"
                )
            )

        try:
            seat = self.seat_repo.create_seat(seat_in)
            self.db.commit()
            return seat

        except IntegrityError:
            self.db.rollback()
            raise ResourceConflictException(
                message=(
                    f"Seat {seat_in.row.upper()}-{seat_in.number} "
                    f"already exists for venue ID {seat_in.venue_id}"
                )
            )

        except Exception:
            self.db.rollback()
            raise

    def create_bulk_seats(
        self,
        venue_id: int,
        seats_in: List[SeatBulkCreate]
    ) -> List[Seat]:
        self._verify_venue_exists(venue_id)

        if not seats_in:
            raise ValidationException(
                message="Seat payload list cannot be empty"
            )

        self._verify_seat_capacity(
            venue_id=venue_id,
            additional_seats=len(seats_in)
        )

        payload_designations = []
        seen_in_payload = set()

        for seat_item in seats_in:
            key = (
                seat_item.row.upper(),
                seat_item.number
            )

            if key in seen_in_payload:
                raise ValidationException(
                    message=(
                        f"Duplicate seat designation "
                        f"{key[0]}-{key[1]} supplied in payload"
                    )
                )

            seen_in_payload.add(key)
            payload_designations.append(key)

        existing_collisions = (
            self.seat_repo.get_existing_designations(
                venue_id=venue_id,
                designations=payload_designations
            )
        )

        if existing_collisions:
            sample_collision = next(iter(existing_collisions))

            raise ResourceConflictException(
                message=(
                    f"Seat {sample_collision[0]}-{sample_collision[1]} "
                    f"already exists in venue ID {venue_id}"
                )
            )

        try:
            created_seats = self.seat_repo.create_bulk_seat(
                venue_id,
                seats_in
            )

            self.db.commit()
            return created_seats

        except IntegrityError:
            self.db.rollback()
            raise ResourceConflictException(
                message="One or more seats already exist for this venue"
            )

        except Exception:
            self.db.rollback()
            raise

    def get_seat_by_id(self, seat_id: int) -> Seat:
        seat = self.seat_repo.get_by_id(seat_id)

        if not seat:
            raise NotFoundException(
                message=f"Seat with ID {seat_id} not found"
            )

        return seat

    def get_seats_by_venue(
        self,
        venue_id: int,
        category: Optional[SeatCategoryEnum] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Sequence[Seat]:
        self._verify_venue_exists(venue_id)

        return self.seat_repo.get_by_venue(
            venue_id=venue_id,
            category=category,
            skip=skip,
            limit=limit
        )

    def count_seats_by_venue(
        self,
        venue_id: int,
        category: Optional[SeatCategoryEnum] = None
    ) -> int:
        self._verify_venue_exists(venue_id)

        return self.seat_repo.count_by_venue(
            venue_id=venue_id,
            category=category
        )

    def delete_seat(self, seat_id: int) -> None:
        seat = self.get_seat_by_id(seat_id)

        try:
            self.seat_repo.delete_seat(seat)
            self.db.commit()

        except Exception:
            self.db.rollback()
            raise