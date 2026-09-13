from typing import Sequence

from fastapi import APIRouter, HTTPException, status

from app.api.deps import DBSession, CurrentUser, CurrentAdmin
from app.models.user import UserRole
from app.schemas.user import UserResponse, UserStatusUpdate, UserUpdate
from app.services.userService import UserService


router = APIRouter(prefix="/users",tags=["Users"])

@router.get(
    "/me",
    response_model=UserResponse
)
def get_current_user_profile(
    current_user: CurrentUser
):
    return current_user


@router.patch(
    "/me",
    response_model=UserResponse
)
def update_current_user_profile(
    user_in: UserUpdate,
    current_user: CurrentUser,
    db: DBSession
):
    user_service = UserService(db)

    return user_service.update_user(
        user_id=current_user.id,
        user_in=user_in
    )


@router.get(
    "",
    response_model=Sequence[UserResponse]
)
def get_all_users(
    current_admin: CurrentAdmin,
    db: DBSession,
    skip: int = 0,
    limit: int = 20
):
    user_service = UserService(db)

    return user_service.get_users_paginated(
        skip=skip,
        limit=limit
    )

@router.patch(
    "/{user_id}/status",
    response_model=UserResponse
)
def update_user_status(
    user_id: int,
    status_in: UserStatusUpdate,
    current_admin: CurrentAdmin,
    db: DBSession
):
    user_service = UserService(db)

    return user_service.update_user_status(
        user_id=user_id,
        is_active=status_in.is_active
    )

@router.get(
    "/{user_id}",
    response_model=UserResponse
)
def get_user_by_id(
    user_id: int,
    current_user: CurrentUser,
    db: DBSession
):
    if (
        current_user.role != UserRole.ADMIN
        and current_user.id != user_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own profile"
        )

    user_service = UserService(db)

    return user_service.get_user_by_id(user_id)


@router.patch(
    "/{user_id}",
    response_model=UserResponse
)
def update_user_by_id(
    user_id: int,
    user_in: UserUpdate,
    current_user: CurrentUser,
    db: DBSession
):
    if (
        current_user.role != UserRole.ADMIN
        and current_user.id != user_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own profile"
        )

    user_service = UserService(db)

    return user_service.update_user(
        user_id=user_id,
        user_in=user_in
    )


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_user_by_id(
    user_id: int,
    current_user: CurrentUser,
    db: DBSession
):
    if (
        current_user.role != UserRole.ADMIN
        and current_user.id != user_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own account"
        )

    user_service = UserService(db)

    user_service.delete_user(user_id)

    return None

