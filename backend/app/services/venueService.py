from typing import Optional, Sequence

from sqlalchemy.orm import Session

from app.core.exceptions import (
    NotFoundException,
    ResourceConflictException,
    ValidationException,
)
from app.models.venue import Venue
from app.repositories.venueRepo import VenueRepository
from app.schemas.venue import VenueCreate, VenueUpdate
from app.repositories.seatRepo import SeatRepository


class VenueService:
    def __init__(self, db: Session):
        self.db = db
        self.venue_repo = VenueRepository(db)
        self.seat_repo = SeatRepository(db)

    def create_venue(self, venue_in: VenueCreate) -> Venue:
        if self.venue_repo.exists_by_name_and_location(
            venue_in.name,
            venue_in.location
        ):
            raise ResourceConflictException(
                message=(
                    f"Venue '{venue_in.name}' already exists at "
                    f"location '{venue_in.location}'"
                )
            )

        if venue_in.capacity <= 0:
            raise ValidationException(
                message="Venue capacity must be greater than zero"
            )

        try:
            venue = self.venue_repo.create_venue(venue_in)
            self.db.commit()
            self.db.refresh(venue)
            return venue
        except Exception:
            self.db.rollback()
            raise

    def get_venue_by_id(self, venue_id: int) -> Venue:
        venue = self.venue_repo.get_by_id(venue_id)

        if not venue:
            raise NotFoundException(
                message=f"Venue with ID {venue_id} not found"
            )

        return venue

    def get_paginated_venues(
        self,
        skip: int = 0,
        limit: int = 20,
        location: Optional[str] = None
    ) -> Sequence[Venue]:
        return self.venue_repo.get_paginated_venues(
            skip=skip,
            limit=limit,
            location=location
        )

    def count_venues(
        self,
        location: Optional[str] = None
    ) -> int:
        return self.venue_repo.count_venues(
            location=location
        )

    def update_venue(
        self,
        venue_id: int,
        venue_in: VenueUpdate
    ) -> Venue:
        venue = self.get_venue_by_id(venue_id)

        update_data = venue_in.model_dump(
            exclude_unset=True
        )

        if "name" in update_data or "location" in update_data:
            check_name = update_data.get(
                "name",
                venue.name
            )
            check_location = update_data.get(
                "location",
                venue.location
            )

            existing_venue = (
                self.venue_repo.get_by_name_and_location(
                    check_name,
                    check_location
                )
            )

            if existing_venue and existing_venue.id != venue_id:
                raise ResourceConflictException(
                    message=(
                        f"Venue '{check_name}' already exists at "
                        f"location '{check_location}'"
                    )
                )

        if "capacity" in update_data:
            new_capacity = update_data["capacity"]

            if new_capacity <= 0:
                raise ValidationException(
                    message="Venue capacity must be greater than zero"
                )

            current_seat_count = self.seat_repo.count_by_venue(
                venue_id=venue_id
            )

            if new_capacity < current_seat_count:
                raise ValidationException(
                    message=(
                        f"Venue capacity cannot be reduced below the "
                        f"current number of seats ({current_seat_count})"
                    )
                )

        try:
            updated_venue = self.venue_repo.update_venue(
                venue,
                venue_in
            )

            self.db.commit()
            return updated_venue

        except Exception:
            self.db.rollback()
            raise

    def delete_venue(self, venue_id: int) -> None:
        venue = self.get_venue_by_id(venue_id)

        if not venue.is_active:
            raise ResourceConflictException(
                message=f"Venue '{venue.name}' is already inactive"
            )

        try:
            venue.is_active = False

            self.db.commit()
            self.db.refresh(venue)

        except Exception:
            self.db.rollback()
            raise