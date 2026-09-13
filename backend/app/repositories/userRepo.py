from typing import Optional, Sequence

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.user import User, UserRole
from app.schemas.user import UserCreate


class UserRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int) -> Optional[User]:
        return self.db.get(User, user_id)

    def get_by_email(self, email: str) -> Optional[User]:
        stmt = select(User).where(
            func.lower(User.email) == func.lower(email)
        )
        return self.db.scalars(stmt).first()

    def get_by_email_or_username(
        self,
        email: str,
        username: str
    ) -> Optional[User]:

        stmt = select(User).where(
            or_(
                func.lower(User.email) == func.lower(email),
                func.lower(User.username) == func.lower(username)
            )
        )

        return self.db.scalars(stmt).first()

    def exists_by_email_or_username(
        self,
        email: str,
        username: str
    ) -> bool:

        stmt = select(User.id).where(
            or_(
                func.lower(User.email) == func.lower(email),
                func.lower(User.username) == func.lower(username)
            )
        ).limit(1)

        return self.db.scalar(stmt) is not None

    def get_by_phone(self, phone_no: str) -> Optional[User]:
        stmt = select(User).where(
            User.phone_no == phone_no
        )
        return self.db.scalars(stmt).first()

    def get_by_username(self, username: str) -> Optional[User]:
        stmt = select(User).where(
            func.lower(User.username) == func.lower(username)
        )
        return self.db.scalars(stmt).first()

    def create(
        self,
        user_in: UserCreate,
        hashed_password: str,
        role: UserRole = UserRole.USER
    ) -> User:

        user = User(
            username=user_in.username,
            email=user_in.email,
            phone_no=user_in.phone_no,
            address=user_in.address,
            city=user_in.city,
            hashed_password=hashed_password,
            role=role,
        )

        self.db.add(user)
        self.db.flush()
        self.db.refresh(user)

        return user

    def update(self, user: User, update_data: dict) -> User:

        for key, value in update_data.items():
            setattr(user, key, value)

        self.db.flush()
        self.db.refresh(user)

        return user

    def delete(self, user: User) -> None:

        self.db.delete(user)
        self.db.flush()

    def get_paginated(
        self,
        skip: int = 0,
        limit: int = 20
    ) -> Sequence[User]:

        stmt = (
            select(User)
            .order_by(User.id.asc())
            .offset(skip)
            .limit(limit)
        )

        return self.db.scalars(stmt).all()

    def count(self) -> int:

        stmt = select(func.count()).select_from(User)

        return self.db.scalar(stmt) or 0