from datetime import datetime
from typing import Optional, Sequence
from fastapi import APIRouter, Query, status

from app.api.deps import DBSession, CurrentUser, CurrentAdmin
from app.schemas.event import EventCreate, EventResponse, EventUpdate
from app.services.eventService import EventService

router = APIRouter(prefix="/events", tags=["Events"])


@router.post("", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
def create_event(
    event_in: EventCreate,
    current_admin: CurrentAdmin,
    db: DBSession
):
    event_service = EventService(db)
    return event_service.create_event(event_in)


@router.get("", response_model=Sequence[EventResponse])
def get_events(
    # current_user: CurrentUser,
    db: DBSession,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    venue_id: Optional[int] = Query(None, description="Filter events by venue ID"),
    category: Optional[str] = Query(None, description="Filter events by category"),
    from_date: Optional[datetime] = Query(None, description="Filter events starting on or after this date"),
    to_date: Optional[datetime] = Query(None, description="Filter events ending on or before this date"),
    upcoming_only: bool = Query(False, description="Filter for upcoming events only")
):
    event_service = EventService(db)
    return event_service.get_events(
        skip=skip,
        limit=limit,
        venue_id=venue_id,
        category=category,
        from_date=from_date,
        to_date=to_date,
        upcoming_only=upcoming_only
    )


@router.get("/{event_id}", response_model=EventResponse)
def get_event(event_id: int,db: DBSession):

    event_service = EventService(db)
    return event_service.get_event_by_id(event_id)


@router.patch("/{event_id}", response_model=EventResponse)
def update_event(event_id: int,event_in: EventUpdate,current_admin: CurrentAdmin,db: DBSession):

    event_service = EventService(db)
    return event_service.update_event(event_id=event_id, event_in=event_in)


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(event_id: int,current_admin: CurrentAdmin,db: DBSession):

    event_service = EventService(db)
    event_service.delete_event(event_id)
    return None