from typing import Sequence, Optional
from datetime import datetime

from sqlalchemy.orm import Session

from app.repositories.eventRepo import EventRepository
from app.repositories.venueRepo import VenueRepository

from app.schemas.event import (
    EventCreate,
    EventUpdate
)

from app.models.event import Event

from app.core.exceptions import (
    NotFoundException,
    ValidationException,
    ResourceConflictException,
)


class EventService:

    def __init__(
        self,
        db: Session
    ):
        self.db = db

        self.event_repo = EventRepository(db)
        self.venue_repo = VenueRepository(db)

    def _verify_venue_exists(
        self,
        venue_id: int
    ) -> None:

        venue = self.venue_repo.get_by_id(
            venue_id
        )

        if not venue:

            raise NotFoundException(
                message=(
                    f"Venue with ID {venue_id} not found"
                )
            )

    def create_event(
        self,
        event_in: EventCreate
    ) -> Event:

        if event_in.end_time <= event_in.start_time:

            raise ValidationException(
                message=(
                    "Event end_time must be "
                    "chronologically after start_time"
                )
            )
        if not event_in.venue_ids:

            raise ValidationException(
                message=(
                    "At least one venue must be selected"
                )
            )

        if len(event_in.venue_ids) != len(
            set(event_in.venue_ids)
        ):

            raise ValidationException(
                message=(
                    "Duplicate venue IDs are not allowed"
                )
            )

        venues = []

        for venue_id in event_in.venue_ids:

            venue = self.venue_repo.get_by_id(
                venue_id
            )

            if not venue:

                raise NotFoundException(
                    message=(
                        f"Venue with ID {venue_id} not found"
                    )
                )

            venues.append(venue)

        if self.event_repo.has_overlapping_event(
            venue_ids=event_in.venue_ids,
            start_time=event_in.start_time,
            end_time=event_in.end_time
        ):

            raise ResourceConflictException(
                message=(
                    "One or more selected venues already "
                    "have an event scheduled during this "
                    "time window"
                )
            )
        try:

            event = self.event_repo.create_event(
                event_in=event_in,
                venues=venues
            )

            self.db.commit()

            # Refresh event after commit
            self.db.refresh(event)

            return event

        except Exception:

            self.db.rollback()

            raise

    def get_event_by_id(
        self,
        event_id: int
    ) -> Event:

        event = self.event_repo.get_by_id(
            event_id=event_id,
            include_venues=True
        )

        if not event:

            raise NotFoundException(
                message=(
                    f"Event with ID {event_id} not found"
                )
            )

        return event

    def get_events(
        self,
        skip: int = 0,
        limit: int = 20,
        venue_id: Optional[int] = None,
        category: Optional[str] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        upcoming_only: bool = False
    ) -> Sequence[Event]:

        if venue_id is not None:

            self._verify_venue_exists(
                venue_id
            )

        return self.event_repo.get_paginated_events(
            skip=skip,
            limit=limit,
            venue_id=venue_id,
            category=category,
            from_date=from_date,
            to_date=to_date,
            upcoming_only=upcoming_only
        )

    def count_events(
        self,
        venue_id: Optional[int] = None,
        category: Optional[str] = None,
        upcoming_only: bool = False
    ) -> int:

        if venue_id is not None:

            self._verify_venue_exists(
                venue_id
            )

        return self.event_repo.count_event(
            venue_id=venue_id,
            category=category,
            upcoming_only=upcoming_only
        )

    def update_event(
        self,
        event_id: int,
        event_in: EventUpdate
    ) -> Event:

        event = self.get_event_by_id(
            event_id
        )
        update_data = event_in.model_dump(
            exclude_unset=True
        )

        start_time = update_data.get(
            "start_time",
            event.start_time
        )

        end_time = update_data.get(
            "end_time",
            event.end_time
        )

        if end_time <= start_time:

            raise ValidationException(
                message=(
                    "Event end_time must be "
                    "chronologically after start_time"
                )
            )

        if "venue_ids" in update_data:

            venue_ids = update_data["venue_ids"]

            if not venue_ids:

                raise ValidationException(
                    message=(
                        "At least one venue must be selected"
                    )
                )

            if len(venue_ids) != len(
                set(venue_ids)
            ):

                raise ValidationException(
                    message=(
                        "Duplicate venue IDs are not allowed"
                    )
                )

            venues = []

            for venue_id in venue_ids:

                venue = self.venue_repo.get_by_id(
                    venue_id
                )

                if not venue:

                    raise NotFoundException(
                        message=(
                            f"Venue with ID {venue_id} "
                            f"not found"
                        )
                    )

                venues.append(venue)

        else:

            venues = event.venues

            venue_ids = [
                venue.id
                for venue in venues
            ]

        if self.event_repo.has_overlapping_event(
            venue_ids=venue_ids,
            start_time=start_time,
            end_time=end_time,
            exclude_event_id=event_id
        ):

            raise ResourceConflictException(
                message=(
                    "One or more selected venues already "
                    "have an overlapping event scheduled "
                    "during this time window"
                )
            )
        try:

            updated_event = (
                self.event_repo.update_event(
                    event=event,
                    event_in=event_in,
                    venues=venues
                )
            )

            self.db.commit()

            self.db.refresh(updated_event)

            return updated_event

        except Exception:

            self.db.rollback()

            raise

    def delete_event(
        self,
        event_id: int
    ) -> None:

        event = self.get_event_by_id(
            event_id
        )

        try:

            self.event_repo.delete_event(
                event
            )

            self.db.commit()

        except Exception:

            self.db.rollback()

            raise

