# app/schemas/user.py
import re
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.models.user import UserRole

ALLOWED_EMAIL_REGEX = r"^[\w\.-]+@(gmail\.com|yahoo\.com|outlook\.com)$"


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, json_schema_extra={"example": "john_doe"})
    email: EmailStr = Field(..., json_schema_extra={"example": "john@gmail.com"})
    phone_no: str = Field(..., min_length=10, max_length=15, json_schema_extra={"example": "+1234567890"})
    address: Optional[str] = Field(None, max_length=255)
    city: str = Field(..., min_length=2, max_length=100, json_schema_extra={"example": "Mumbai"})

    @field_validator("email")
    @classmethod
    def validate_allowed_email_domains(cls, value: str) -> str:
        value_lower = value.strip().lower()
        if not re.match(ALLOWED_EMAIL_REGEX, value_lower):
            raise ValueError(
                "Email must belong to one of the allowed providers: gmail.com, yahoo.com, or outlook.com"
            )
        return value_lower


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100, json_schema_extra={"example": "StrongPass123!"})


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50, json_schema_extra={"example": "john_doe_updated"})
    email: Optional[EmailStr] = Field(None, json_schema_extra={"example": "john.updated@gmail.com"})
    phone_no: Optional[str] = Field(None, min_length=10, max_length=15, json_schema_extra={"example": "+9876543210"})
    address: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, min_length=2, max_length=100, json_schema_extra={"example": "Pune"})
    password: Optional[str] = Field(None, min_length=8, max_length=100, json_schema_extra={"example": "NewStrongPass123!"})

    @field_validator("email")
    @classmethod
    def validate_allowed_email_domains(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        value_lower = value.strip().lower()
        if not re.match(ALLOWED_EMAIL_REGEX, value_lower):
            raise ValueError(
                "Email must belong to one of the allowed providers: gmail.com, yahoo.com, or outlook.com"
            )
        return value_lower


class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserStatusUpdate(BaseModel):
    is_active: bool


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    phone_no: str
    address: Optional[str] = None
    city: str
    role: UserRole
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
