"""Input validation utilities."""

import os
from pathlib import Path
from typing import List, Optional

from app.utils.constants import (
    MAX_SLIDES,
    MIN_SLIDES,
    PRESENTATION_TYPES,
    SUPPORTED_IMAGE_FORMATS,
    TEMPLATE_NAMES,
)


class ValidationError(Exception):
    """Raised when input validation fails."""


def validate_topic(topic: str) -> str:
    if not topic or not topic.strip():
        raise ValidationError("Topic cannot be empty.")
    return topic.strip()


def validate_slide_count(slide_count: int) -> int:
    if slide_count < MIN_SLIDES or slide_count > MAX_SLIDES:
        raise ValidationError(
            f"Slide count must be between {MIN_SLIDES} and {MAX_SLIDES}."
        )
    return slide_count


def validate_presentation_type(presentation_type: str) -> str:
    if presentation_type not in PRESENTATION_TYPES:
        raise ValidationError(f"Invalid presentation type: {presentation_type}")
    return presentation_type


def validate_template_name(template_name: str) -> str:
    if template_name not in TEMPLATE_NAMES:
        raise ValidationError(f"Invalid template: {template_name}")
    return template_name


def validate_image_format(filename: str) -> str:
    extension = Path(filename).suffix.lower()
    if extension not in SUPPORTED_IMAGE_FORMATS:
        raise ValidationError(
            f"Unsupported image format: {extension}. "
            f"Supported: {', '.join(sorted(SUPPORTED_IMAGE_FORMATS))}"
        )
    return extension


def validate_image_exists(image_path: str) -> None:
    if not os.path.isfile(image_path):
        raise ValidationError(f"Image not found: {image_path}")


def validate_selected_images(
    selected_images: List[str], available_images: List[str]
) -> List[str]:
    missing = [name for name in selected_images if name not in available_images]
    if missing:
        raise ValidationError(f"Selected images not found: {', '.join(missing)}")
    return selected_images


def validate_api_key(api_key: Optional[str]) -> str:
    if not api_key or not api_key.strip():
        raise ValidationError("Groq API key is required. Set GROQ_API_KEY in .env")
    return api_key.strip()
