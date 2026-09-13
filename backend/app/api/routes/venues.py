from typing import Optional, Sequence
from fastapi import APIRouter, Query, status

from app.api.deps import DBSession, CurrentUser, CurrentAdmin
from app.schemas.venue import VenueCreate, VenueResponse, VenueUpdate
from app.services.venueService import VenueService

router = APIRouter(prefix="/venues", tags=["Venues"])


@router.post("", response_model=VenueResponse, status_code=status.HTTP_201_CREATED)
def create_venue(
    venue_in: VenueCreate,
    current_admin: CurrentAdmin,
    db: DBSession
):
    venue_service = VenueService(db)
    return venue_service.create_venue(venue_in)


@router.get("", response_model=Sequence[VenueResponse])
def get_venues(
    # current_user: CurrentUser,
    db: DBSession,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    location: Optional[str] = Query(None, description="Filter venues by location")
):
    venue_service = VenueService(db)
    return venue_service.get_paginated_venues(skip=skip, limit=limit, location=location)


@router.get("/{venue_id}", response_model=VenueResponse)
def get_venue(
    venue_id: int,
    # current_user: CurrentUser,
    db: DBSession
):
    venue_service = VenueService(db)
    return venue_service.get_venue_by_id(venue_id)


@router.patch("/{venue_id}", response_model=VenueResponse)
def update_venue(
    venue_id: int,
    venue_in: VenueUpdate,
    current_admin: CurrentAdmin,
    db: DBSession
):
    venue_service = VenueService(db)
    return venue_service.update_venue(venue_id=venue_id, venue_in=venue_in)


@router.delete("/{venue_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_venue(
    venue_id: int,
    current_admin: CurrentAdmin,
    db: DBSession
):
    venue_service = VenueService(db)
    venue_service.delete_venue(venue_id)
    return None