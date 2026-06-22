"""Image metadata models."""

from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field


class ImageMetadata(BaseModel):
    image_name: str
    display_name: str
    path: str
    width: int
    height: int
    upload_timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ImageReference(BaseModel):
    image_name: str
    position: str = "right"
