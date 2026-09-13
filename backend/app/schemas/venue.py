from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field
from typing import Optional

class VenueBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, example="PVR Cinemas")
    location: str = Field(..., min_length=2, max_length=255, example="Lower Parel, Mumbai")
    capacity: int = Field(..., gt=0, examples=[200])
    description: Optional[str] = Field(None, max_length=500, example="Multi-screen cinema hall")

class VenueCreate(VenueBase):
    pass

class VenueUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    location: Optional[str] = Field(None, min_length=2, max_length=255)
    capacity: Optional[int] = Field(None,gt=0)
    description: Optional[str] = Field(None, max_length=500)


class VenueResponse(VenueBase):
    id: int
    created_at: datetime
    name: str
    location: str

    model_config = ConfigDict(from_attributes=True)

class VenueSummary(BaseModel):
    id: int
    name: str
    location: str

    model_config = ConfigDict(from_attributes=True)