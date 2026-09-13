from typing import List, Optional, Sequence
from fastapi import APIRouter, Depends, Query, status
from app.api.deps import DBSession, CurrentUser,CurrentAdmin
from app.schemas.booking import (BookingCreate,BookingResponse,BookingStatusEnum,BookingStatusUpdate)

from app.services.bookingService import BookingService


router = APIRouter(prefix="/bookings",tags=["Bookings"])

# CREATE BOOKING
@router.post("",response_model=BookingResponse,status_code=status.HTTP_201_CREATED)
def create_booking(booking_in: BookingCreate,current_user: CurrentUser,db: DBSession):

    booking_service = BookingService(db)
    return booking_service.create_booking(
        user=current_user,
        booking_in=booking_in
    )

# GET MY BOOKINGS
@router.get("/me",response_model=Sequence[BookingResponse])
def get_my_bookings(current_user: CurrentUser,db: DBSession,skip: int = Query(0,ge=0),
    limit: int = Query(20,ge=1,le=100),
    status: Optional[BookingStatusEnum] = Query(
        None,
        description="Filter by booking status"
    )
):

    booking_service = BookingService(db)

    return booking_service.get_user_bookings(
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        status=status
    )

# GET BOOKED SEATS FOR EVENT
@router.get("/event/{event_id}/venue/{venue_id}/booked-seats",response_model=List[int])
def get_event_booked_seats(event_id: int,venue_id: int,db: DBSession):

    booking_service = BookingService(db)
    return booking_service.get_event_booked_seats(
        event_id=event_id,
        venue_id=venue_id
    )

# ADMIN
@router.get("/admin",response_model=Sequence[BookingResponse])
def get_all_bookings(current_admin: CurrentAdmin,db: DBSession,skip: int = Query(0,ge=0),
    limit: int = Query(20,ge=1,le=100),
    status: Optional[BookingStatusEnum] = Query(
        None,
        description="Filter bookings by status"
    )
):

    booking_service = BookingService(db)
    return booking_service.get_all_bookings(
        skip=skip,
        limit=limit,
        status=status
    )

@router.patch("/admin/{booking_id}/status",response_model=BookingResponse)
def admin_update_booking_status(booking_id: int,booking_in: BookingStatusUpdate,current_admin: CurrentAdmin,db: DBSession):

    booking_service = BookingService(db)
    return booking_service.admin_update_booking_status(
        booking_id=booking_id,
        new_status=booking_in.status
    )

@router.get("/{booking_id}",response_model=BookingResponse)
def get_booking(booking_id: int,current_user: CurrentUser,db: DBSession):

    booking_service = BookingService(db)
    return booking_service.get_booking_by_id(
        booking_id=booking_id,
        user=current_user
    )

@router.patch("/{booking_id}/cancel",response_model=BookingResponse)
def cancel_booking(booking_id: int,current_user: CurrentUser,db: DBSession):

    booking_service = BookingService(db)
    return booking_service.cancel_booking(
        booking_id=booking_id,
        user=current_user
    )