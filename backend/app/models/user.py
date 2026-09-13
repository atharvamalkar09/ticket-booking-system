import enum

from sqlalchemy import Boolean, String,Integer,DateTime,Enum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from app.db.base import Base
from app.models.booking import Booking


class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    USER = "USER"

class User(Base):
    __tablename__ = "users"

    id:Mapped[int] = mapped_column(primary_key=True,index=True)
    username:Mapped[str] = mapped_column(String(50),unique=True,index=True,nullable=False)
    email:Mapped[str] = mapped_column(String(255),unique=True,nullable=False,index=True)
    hashed_password:Mapped[str] = mapped_column(String(255),nullable=False)
    phone_no:Mapped[str] = mapped_column(String(15),unique=True,nullable=False)
    address:Mapped[str] = mapped_column(String(255),unique=False,nullable=True)
    city:Mapped[str] = mapped_column(String(255),unique=False,nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole),default=UserRole.USER,nullable=False)

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True),
    server_default=func.now(),
    nullable=False
)

    bookings:Mapped[list["Booking"]] = relationship("Booking", back_populates="user")
 