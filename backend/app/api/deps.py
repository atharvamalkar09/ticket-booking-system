from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.database import get_db
from app.models.user import User, UserRole
from app.schemas.token import TokenPayload
from app.repositories.userRepo import UserRepository

from app.models.user import User, UserRole
from app.schemas.token import TokenPayload
from app.repositories.userRepo import UserRepository

oauth2_scheme = OAuth2PasswordBearer( tokenUrl=f"{settings.API_V1_STR}/auth/login")

DBSession = Annotated[Session, Depends(get_db)]

def get_current_user(db: DBSession,token: Annotated[str, Depends(oauth2_scheme)]) -> User:

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={
            "WWW-Authenticate": "Bearer"
        },
    )

    try:

        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        user_id: str | None = payload.get("sub")

        if user_id is None:
            raise credentials_exception

        token_data = TokenPayload(
            sub=int(user_id)
        )

    except (JWTError,ValidationError,ValueError):
        raise credentials_exception

    user_repo = UserRepository(db)

    user = user_repo.get_by_id(
    user_id=token_data.sub)

    if not user:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )

    # Release the DB connection immediately after authentication.
    
    # The user object is detached because the route may still need current_user after this session is closed.

    db.expunge(user)
    db.close()

    return user


CurrentUser = Annotated[
    User,
    Depends(get_current_user)
]


class RoleChecker:
    def __init__(self,allowed_roles: list[UserRole]):
        self.allowed_roles = allowed_roles

    def __call__(self,current_user: CurrentUser) -> User:

        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "Operation not permitted: "
                    "Insufficient privileges"
                ),
            )

        return current_user

require_admin = RoleChecker(
    [UserRole.ADMIN]
)

require_user_or_admin = RoleChecker([
        UserRole.USER,
        UserRole.ADMIN]
)

CurrentAdmin = Annotated[
    User,
    Depends(require_admin)
]