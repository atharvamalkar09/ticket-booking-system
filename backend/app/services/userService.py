from typing import Dict, List, Sequence

from sqlalchemy.orm import Session

from app.core import security
from app.core.exceptions import (
    NotFoundException,
    UnauthorizedException,
    UserAlreadyExistsException,
)
from app.models.user import User, UserRole
from app.repositories.userRepo import UserRepository
from app.schemas.user import UserCreate, UserLogin, UserUpdate


class UserService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)

    def register_user(self, user_in: UserCreate) -> User:
        if self.user_repo.get_by_email(user_in.email):
            raise UserAlreadyExistsException(
                field="Email",
                value=user_in.email
            )

        if self.user_repo.get_by_username(user_in.username):
            raise UserAlreadyExistsException(
                field="Username",
                value=user_in.username
            )

        if self.user_repo.get_by_phone(user_in.phone_no):
            raise UserAlreadyExistsException(
                field="Phone number",
                value=user_in.phone_no
            )

        hashed_pwd = security.hash_password(user_in.password)

        try:
            user = self.user_repo.create(
                user_in,
                hashed_password=hashed_pwd
            )

            self.db.commit()
            return user

        except Exception:
            self.db.rollback()
            raise

    def authenticate_user(
        self,
        login_data: UserLogin
    ) -> Dict[str, str]:
        user = self.user_repo.get_by_email(login_data.email)

        if not user or not security.verify_password(
            login_data.password,
            user.hashed_password
        ):
            raise UnauthorizedException(
                message="Incorrect email or password"
            )

        if not user.is_active:
            raise UnauthorizedException(
                message="Your account has been deactivated"
            )

        access_token = security.create_access_token(
            subject=user.id,
            role=user.role.value
        )

        return {
            "access_token": access_token,
            "token_type": "bearer"
        }

    def get_user_by_id(self, user_id: int) -> User:
        user = self.user_repo.get_by_id(user_id)

        if not user:
            raise NotFoundException(
                message=f"User with ID {user_id} not found"
            )

        return user

    def get_users_paginated(
        self,
        skip: int = 0,
        limit: int = 20
    ) -> Sequence[User]:
        return self.user_repo.get_paginated(
            skip=skip,
            limit=limit
        )

    def get_user_count(self) -> int:
        return self.user_repo.count()

    def update_user(
        self,
        user_id: int,
        user_in: UserUpdate
    ) -> User:
        user = self.get_user_by_id(user_id)

        if user_in.email or user_in.username:
            new_email = user_in.email or user.email
            new_username = user_in.username or user.username

            existing = self.user_repo.get_by_email_or_username(
                new_email,
                new_username
            )

            if existing and existing.id != user_id:
                raise UserAlreadyExistsException(
                    identifier=f"{new_email} / {new_username}"
                )

        update_data = user_in.model_dump(
            exclude_unset=True
        )

        if "password" in update_data and update_data["password"]:
            update_data["hashed_password"] = (
                security.hash_password(
                    update_data.pop("password")
                )
            )

        try:
            updated_user = self.user_repo.update(
                user,
                update_data
            )

            self.db.commit()
            return updated_user

        except Exception:
            self.db.rollback()
            raise

    def update_user_status(
        self,
        user_id: int,
        is_active: bool
    ) -> User:
        user = self.get_user_by_id(user_id)

        try:
            user.is_active = is_active

            self.db.commit()
            self.db.refresh(user)

            return user

        except Exception:
            self.db.rollback()
            raise

    def delete_user(self, user_id: int) -> None:
        user = self.get_user_by_id(user_id)

        try:
            self.user_repo.delete(user)
            self.db.commit()

        except Exception:
            self.db.rollback()
            raise

    def logout_user(
        self,
        token: str
    ) -> Dict[str, str]:
        return {
            "message": "Successfully logged out"
        }