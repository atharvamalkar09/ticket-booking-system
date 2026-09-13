from pydantic import BaseModel, ConfigDict, Field, computed_field
from enum import Enum

from app.schemas.venue import VenueResponse


class SeatCategoryEnum(str, Enum):
    STANDARD = "STANDARD"
    PREMIUM = "PREMIUM"
    VIP = "VIP"


class SeatBase(BaseModel):
    row: str = Field(
        ...,
        min_length=1,
        max_length=10,
        example="A"
    )

    number: int = Field(
        ...,
        gt=0,
        example=10
    )

    category: SeatCategoryEnum = Field(
        SeatCategoryEnum.STANDARD,
        example=SeatCategoryEnum.STANDARD
    )


class SeatCreate(SeatBase):
    venue_id: int = Field(
        ...,
        gt=0,
        example=1
    )


class SeatBulkCreate(SeatBase):
    pass


class SeatResponse(SeatBase):
    id: int
    venue_id: int
    number: int
    venue: VenueResponse

    @computed_field
    def label(self) -> str:
        return f"{self.row}{self.number}"

    model_config = ConfigDict(from_attributes=True)