from typing import List, Optional, Sequence
from fastapi import APIRouter, Query, status

from app.api.deps import DBSession, CurrentUser, CurrentAdmin
from app.schemas.seat import SeatCreate, SeatResponse, SeatCategoryEnum
from app.services.seatService import SeatService
from app.schemas.seat import (
    SeatCreate,
    SeatBulkCreate,
    SeatResponse,
    SeatCategoryEnum
)
router = APIRouter(prefix="/seats", tags=["Seats"])


@router.post("", response_model=SeatResponse, status_code=status.HTTP_201_CREATED)
def create_seat(
    seat_in: SeatCreate,
    current_admin: CurrentAdmin,
    db: DBSession
):
    seat_service = SeatService(db)
    return seat_service.create_seat(seat_in)


@router.post("/bulk/venue/{venue_id}", response_model=List[SeatResponse], status_code=status.HTTP_201_CREATED)
def create_bulk_seats(
    venue_id: int,
    seats_in: List[SeatBulkCreate],
    current_admin: CurrentAdmin,
    db: DBSession
):
    seat_service = SeatService(db)
    return seat_service.create_bulk_seats(venue_id=venue_id, seats_in=seats_in)


@router.get("/venue/{venue_id}", response_model=Sequence[SeatResponse])
def get_seats_by_venue(
    venue_id: int,
    # current_user: CurrentUser,
    db: DBSession,
    category: Optional[SeatCategoryEnum] = Query(None, description="Filter seats by category"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500)
):
    seat_service = SeatService(db)
    return seat_service.get_seats_by_venue(
        venue_id=venue_id,
        category=category,
        skip=skip,
        limit=limit
    )


@router.get("/{seat_id}", response_model=SeatResponse)
def get_seat(
    seat_id: int,
    # current_user: CurrentUser,
    db: DBSession
):
    seat_service = SeatService(db)
    return seat_service.get_seat_by_id(seat_id)


@router.delete("/{seat_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_seat(
    seat_id: int,
    current_admin: CurrentAdmin,
    db: DBSession
):
    seat_service = SeatService(db)
    seat_service.delete_seat(seat_id)
    return None