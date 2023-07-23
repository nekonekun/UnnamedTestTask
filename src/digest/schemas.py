"""Schemas, used in project."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PostDTO(BaseModel):
    """Single Post representation."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    subscription_id: int
    content: str
    popularity: int


class DigestDTO(BaseModel):
    """Full Digest representation."""

    id: int
    user_id: int
    timestamp: datetime
    posts: list[PostDTO]
