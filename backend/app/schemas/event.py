from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator
)

from typing import Optional
from datetime import datetime
from decimal import Decimal

from app.schemas.venue import VenueSummary


class EventBase(BaseModel):

    title: str = Field(
        ...,
        min_length=2,
        max_length=150,
        example="Coldplay Live in Concert"
    )

    description: Optional[str] = Field(
        None,
        max_length=1000,
        example="World Tour 2026"
    )

    category: str = Field(
        ...,
        min_length=2,
        max_length=50,
        example="Concert"
    )

    start_time: datetime = Field(
        ...,
        example="2026-10-15T19:00:00Z"
    )

    end_time: datetime = Field(
        ...,
        example="2026-10-15T22:00:00Z"
    )

    base_price: Decimal = Field(
        ...,
        gt=0,
        max_digits=10,
        decimal_places=2,
        example=500.00
    )

    @model_validator(mode="after")
    def validate_event_times(
        self
    ) -> "EventBase":

        if self.end_time <= self.start_time:

            raise ValueError(
                "end_time must be chronologically "
                "strictly after start_time"
            )

        return self


class EventCreate(EventBase):

    venue_ids: list[int] = Field(
        ...,
        min_length=1,
        example=[1, 2, 3]
    )

class EventUpdate(BaseModel):

    title: Optional[str] = Field(
        None,
        min_length=2,
        max_length=150
    )

    description: Optional[str] = Field(
        None,
        max_length=1000
    )

    category: Optional[str] = Field(
        None,
        min_length=2,
        max_length=50
    )

    start_time: Optional[datetime] = None

    end_time: Optional[datetime] = None

    base_price: Optional[Decimal] = Field(
        None,
        gt=0,
        max_digits=10,
        decimal_places=2
    )

    venue_ids: Optional[list[int]] = Field(
        None,
        min_length=1,
        example=[1, 2, 3]
    )

    @model_validator(mode="after")
    def validate_update_times(
        self
    ) -> "EventUpdate":

        if (
            self.start_time is not None
            and self.end_time is not None
        ):

            if self.end_time <= self.start_time:

                raise ValueError(
                    "end_time must be chronologically "
                    "strictly after start_time"
                )

        return self


class EventResponse(EventBase):

    id: int
    venues: list[VenueSummary]

    model_config = ConfigDict(
        from_attributes=True
    )

