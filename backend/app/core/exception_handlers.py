from fastapi import Request, status
from fastapi.responses import JSONResponse
from app.core.exceptions import (
    BaseAppException,
    NotFoundException,
    ResourceConflictException,
    ValidationException,
    UnauthorizedException,
    ForbiddenException,
)


def create_error_response(status_code: int, error_type: str, message: str, details: dict = None):
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "type": error_type,
                "message": message,
                "details": details or {}
            }
        }
    )


async def app_exception_handler(request: Request, exc: BaseAppException):
    if isinstance(exc, NotFoundException):
        return create_error_response(
            status.HTTP_404_NOT_FOUND, "NOT_FOUND", exc.message, exc.details
        )
    
    if isinstance(exc, ResourceConflictException):
        return create_error_response(
            status.HTTP_409_CONFLICT, "RESOURCE_CONFLICT", exc.message, exc.details
        )
        
    if isinstance(exc, ValidationException):
        return create_error_response(
            status.HTTP_400_BAD_REQUEST, "BAD_REQUEST", exc.message, exc.details
        )
        
    if isinstance(exc, UnauthorizedException):
        return create_error_response(
            status.HTTP_401_UNAUTHORIZED, "UNAUTHORIZED", exc.message, exc.details
        )

    if isinstance(exc, ForbiddenException):
        return create_error_response(
            status.HTTP_403_FORBIDDEN, "FORBIDDEN", exc.message, exc.details
        )
    
    return create_error_response(
        status.HTTP_500_INTERNAL_SERVER_ERROR, "INTERNAL_SERVER_ERROR", exc.message, exc.details
    )