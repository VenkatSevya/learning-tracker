"""What the API accepts and returns (validated automatically by Pydantic)."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class EntryCreate(BaseModel):
    topic: str = Field(min_length=1, max_length=200)
    notes: str = Field(default="", max_length=5000)
    hours: float = Field(default=1.0, gt=0, le=24)


class EntryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    topic: str
    notes: str
    hours: float
    created_at: datetime


class Stats(BaseModel):
    entries: int
    total_hours: float
    top_topic: str | None
