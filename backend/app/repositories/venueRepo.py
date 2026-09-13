from typing import Optional, Sequence
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.models.venue import Venue
from app.schemas.venue import VenueCreate, VenueUpdate


class VenueRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, venue_id: int) -> Optional[Venue]:
        stmt = select(Venue).where(
            Venue.id == venue_id,
            Venue.is_active.is_(True)
        )

        return self.db.scalars(stmt).first()

    def get_by_name_and_location(self, name: str, location: str) -> Optional[Venue]:
        stmt = select(Venue).where(
            func.lower(Venue.name) == func.lower(name),
            func.lower(Venue.location) == func.lower(location),
            Venue.is_active.is_(True)
        )
        return self.db.scalars(stmt).first()

    def exists_by_name_and_location(self, name: str, location: str) -> bool:
        stmt = select(
            select(Venue.id)
            .where(
                func.lower(Venue.name) == func.lower(name),
                func.lower(Venue.location) == func.lower(location),
                Venue.is_active.is_(True)
            )
            .exists()
        )
        return bool(self.db.scalar(stmt))

    def create_venue(self, venue_in: VenueCreate) -> Venue:
        venue = Venue(
            name=venue_in.name,
            location=venue_in.location,
            capacity=venue_in.capacity,
            description=venue_in.description
        )
        self.db.add(venue)
        # self.db.commit()
        # self.db.refresh(venue)
        self.db.flush()
        return venue

    def update_venue(self, venue: Venue, venue_in: VenueUpdate) -> Venue:
        update_data = venue_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(venue, field, value)
            
        self.db.add(venue)
        # self.db.commit()
        self.db.flush()
        return venue

    def get_paginated_venues(
        self, 
        skip: int = 0, 
        limit: int = 20, 
        location: Optional[str] = None
    ) -> Sequence[Venue]:
        stmt = select(Venue)

        stmt = stmt.where(
            Venue.is_active.is_(True)
        )

        if location:
            stmt = stmt.where(func.lower(Venue.location).contains(func.lower(location)))
        stmt = stmt.order_by(Venue.id.asc()).offset(skip).limit(limit)
        return self.db.scalars(stmt).all()

    def count_venues(self, location: Optional[str] = None) -> int:
        stmt = select(func.count()).select_from(Venue)

        stmt = stmt.where(
            Venue.is_active.is_(True)
        )

        if location:
            stmt = stmt.where(func.lower(Venue.location).contains(func.lower(location)))
        return self.db.scalar(stmt) or 0