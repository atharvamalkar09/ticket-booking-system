from typing import List, Optional, Sequence, Set, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import select, func, tuple_

from app.models.seat import Seat
from app.schemas.seat import SeatCreate, SeatCategoryEnum


class SeatRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, seat_id: int) -> Optional[Seat]:
        return self.db.get(Seat, seat_id)

    def get_by_venue_row_number(
        self, 
        venue_id: int, 
        row: str, 
        number: int
    ) -> Optional[Seat]:
        stmt = select(Seat).where(
            Seat.venue_id == venue_id,
            func.upper(Seat.row) == row.upper(),
            Seat.number == number
        )
        return self.db.scalars(stmt).first()

    def get_existing_designations(
        self, 
        venue_id: int, 
        designations: List[Tuple[str, int]]
    ) -> Set[Tuple[str, int]]:
        if not designations:
            return set()
        formatted_tuples = [
            (row.upper(), number) for row, number in designations
        ]

        stmt = select(func.upper(Seat.row), Seat.number).where(
            Seat.venue_id == venue_id,
            tuple_(func.upper(Seat.row), Seat.number).in_(formatted_tuples)
        )

        results = self.db.execute(stmt).all()
        return {(row_str, num) for row_str, num in results}

    def create_seat(self, seat_in: SeatCreate) -> Seat:
        seat = Seat(
            venue_id=seat_in.venue_id,
            row=seat_in.row.upper(),
            number=seat_in.number,
            category=seat_in.category
        )
        self.db.add(seat)
        self.db.flush()
        self.db.refresh(seat)
        return seat

    def create_bulk_seat(self, venue_id: int, seats_in: List[SeatCreate]) -> List[Seat]:
        seat_objects = [
            Seat(
                venue_id=venue_id,
                row=s.row.upper(),
                number=s.number,
                category=s.category
            )
            for s in seats_in
        ]
        self.db.add_all(seat_objects)
        self.db.flush()
        
        for seat in seat_objects:
            self.db.refresh(seat)
            
        return seat_objects

    def get_by_venue(
        self, 
        venue_id: int, 
        category: Optional[SeatCategoryEnum] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Sequence[Seat]:
        stmt = select(Seat).where(Seat.venue_id == venue_id)

        if category:
            stmt = stmt.where(Seat.category == category)

        stmt = stmt.order_by(Seat.row.asc(), Seat.number.asc()).offset(skip).limit(limit)
        return self.db.scalars(stmt).all()

    def count_by_venue(
        self, 
        venue_id: int, 
        category: Optional[SeatCategoryEnum] = None
    ) -> int:
        stmt = select(func.count()).select_from(Seat).where(Seat.venue_id == venue_id)
        if category:
            stmt = stmt.where(Seat.category == category)
        return self.db.scalar(stmt) or 0

    def delete_seat(self, seat: Seat) -> None:
        self.db.delete(seat)
        self.db.flush()