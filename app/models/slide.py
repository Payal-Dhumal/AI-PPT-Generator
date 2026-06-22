"""Slide data models."""

from typing import List, Optional

from pydantic import BaseModel, Field

from app.models.image import ImageReference


class SlideData(BaseModel):
    slide_number: int
    slide_type: str = "content"
    title: str
    content: List[str] = Field(default_factory=list)
    images: List[ImageReference] = Field(default_factory=list)
    subtitle: Optional[str] = None
    left_section: Optional[List[str]] = None
    right_section: Optional[List[str]] = None
    timeline_items: Optional[List[str]] = None
