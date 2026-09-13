from typing import List, Optional, Sequence
from datetime import datetime

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, func, and_

from app.models.event import Event
from app.schemas.event import EventCreate, EventUpdate
from app.models.venue import Venue


class EventRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(
        self,
        event_id: int,
        include_venues: bool = True
    ) -> Optional[Event]:

        stmt = select(Event).where(
            Event.id == event_id
        )
        if include_venues:

            stmt = stmt.options(
                joinedload(
                    Event.venues.and_(
                        Venue.is_active.is_(True)
                    )
                )
            )

        return (
            self.db
            .scalars(stmt)
            .unique()
            .first()
        )

    def has_overlapping_event(
        self,
        venue_ids: list[int],
        start_time: datetime,
        end_time: datetime,
        exclude_event_id: Optional[int] = None
    ) -> bool:

        stmt = (
            select(Event.id)
            .where(
                Event.venues.any(
                    Venue.id.in_(venue_ids)
                ),
                Event.start_time < end_time,
                Event.end_time > start_time
            )
        )
        if exclude_event_id is not None:

            stmt = stmt.where(
                Event.id != exclude_event_id
            )

        return (
            self.db.scalar(
                stmt.limit(1)
            )
            is not None
        )
    def create_event(
        self,
        event_in: EventCreate,
        venues: list[Venue]
    ) -> Event:

        event = Event(
            title=event_in.title,
            description=event_in.description,
            category=event_in.category,
            start_time=event_in.start_time,
            end_time=event_in.end_time,
            base_price=event_in.base_price
        )
        event.venues = venues

        self.db.add(event)
        self.db.flush()

        return event

    def update_event(
        self,
        event: Event,
        event_in: EventUpdate,
        venues: list[Venue]
    ) -> Event:

        update_data = event_in.model_dump(
            exclude_unset=True
        )

        for field, value in update_data.items():
            if field == "venue_ids":
                continue

            setattr(
                event,
                field,
                value
            )

        event.venues = venues

        self.db.add(event)

        self.db.flush()

        return event

    def delete_event(
        self,
        event: Event
    ) -> None:

        self.db.delete(event)

    def get_paginated_events(
        self,
        skip: int = 0,
        limit: int = 20,
        venue_id: Optional[int] = None,
        category: Optional[str] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        upcoming_only: bool = False
    ) -> Sequence[Event]:

        stmt = (
            select(Event)
            .options(
                joinedload(
                    Event.venues.and_(
                        Venue.is_active.is_(True)
                    )
                )
            )
        )

        filters = [
                Event.venues.any(
                    Venue.is_active.is_(True)
                )
            ]

        if venue_id is not None:

            filters.append(
                Event.venues.any(
                    Venue.id == venue_id
                )
            )

        if category:

            filters.append(
                func.lower(Event.category)
                ==
                func.lower(category)
            )

        if upcoming_only:

            filters.append(
                Event.start_time >= func.now()
            )

        else:

            if from_date:

                filters.append(
                    Event.start_time >= from_date
                )

            if to_date:

                filters.append(
                    Event.end_time <= to_date
                )

        if filters:

            stmt = stmt.where(
                and_(*filters)
            )

        stmt = (
            stmt
            .order_by(
                Event.start_time.asc(),
                Event.id.asc()
            )
            .offset(skip)
            .limit(limit)
        )

        return (
            self.db
            .scalars(stmt)
            .unique()
            .all()
        )

    def count_event(
        self,
        venue_id: Optional[int] = None,
        category: Optional[str] = None,
        upcoming_only: bool = False
    ) -> int:

        stmt = (
            select(
                func.count(Event.id)
            )
            .select_from(Event)
        )

        filters = [
            Event.venues.any(
                Venue.is_active.is_(True)
            )
        ]


        if venue_id is not None:

            filters.append(
                Event.venues.any(
                    Venue.id == venue_id
                )
            )

        if category:

            filters.append(
                func.lower(Event.category)
                ==
                func.lower(category)
            )

        if upcoming_only:

            filters.append(
                Event.start_time >= func.now()
            )

        if filters:

            stmt = stmt.where(
                and_(*filters)
            )

        return (
            self.db.scalar(stmt)
            or 0
        )
