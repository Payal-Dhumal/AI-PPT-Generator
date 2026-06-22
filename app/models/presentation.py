"""Presentation data models."""

from typing import List, Optional

from pydantic import BaseModel, Field

from app.models.slide import SlideData


class PresentationRequest(BaseModel):
    topic: str
    prompt: str = ""
    slide_count: int = 10
    presentation_type: str = "Business Presentation"
    template_name: str = "Professional"
    selected_images: List[str] = Field(default_factory=list)


class PresentationResponse(BaseModel):
    presentation_title: str
    slides: List[SlideData]


class GenerationResult(BaseModel):
    success: bool
    message: str
    file_path: Optional[str] = None
    presentation_title: Optional[str] = None
