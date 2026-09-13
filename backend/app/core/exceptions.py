from typing import Any, Dict, Optional


class BaseAppException(Exception):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class NotFoundException(BaseAppException):
    pass

class ResourceConflictException(BaseAppException):
    pass

class ValidationException(BaseAppException):
    pass

class UnauthorizedException(BaseAppException):
    pass

class ForbiddenException(BaseAppException):
    pass

class UserAlreadyExistsException(ResourceConflictException):
    def __init__(self, field: str, value: str):
        super().__init__(
            f"{field} '{value}' is already registered"
        )

class SeatAlreadyBookedException(ResourceConflictException):
    def __init__(self, seat_id: int, event_id: int):
        super().__init__(
            f"Seat ID {seat_id} is already reserved or booked for event ID {event_id}"
        )
        
class SeatVenueMismatchException(ValidationException):
    def __init__(self, seat_id: int, venue_id: int):
        super().__init__(
            f"Seat ID {seat_id} does not belong to venue ID {venue_id}"
        )