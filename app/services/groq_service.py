"""Groq API integration for presentation content generation."""

import json
import os
from typing import List, Optional

from groq import Groq

from app.models.presentation import PresentationRequest, PresentationResponse
from app.models.slide import SlideData
from app.models.image import ImageReference
from app.utils.constants import GROQ_MODEL, IMAGE_POSITIONS, SLIDE_TYPES
from app.utils.helpers import extract_json_from_response
from app.utils.validators import ValidationError, validate_api_key


class GroqService:
    """Handles AI communication for content planning and slide generation."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = validate_api_key(api_key or os.getenv("GROQ_API_KEY"))
        self.client = Groq(api_key=self.api_key)

    def build_prompt(self, request: PresentationRequest) -> str:
        image_list = ", ".join(request.selected_images) if request.selected_images else "None"

        return f"""You are an expert presentation designer. Create a complete presentation outline.

TOPIC: {request.topic}
DETAILED PROMPT: {request.prompt or "Create a comprehensive presentation on the topic."}
SLIDE COUNT: {request.slide_count}
PRESENTATION TYPE: {request.presentation_type}
TEMPLATE STYLE: {request.template_name}
SELECTED IMAGES: {image_list}

RULES:
1. Create exactly {request.slide_count} slides with slide-wise content.
2. Decide where images should appear based on content relevance.
3. Reference images ONLY by their exact provided names.
4. Maintain logical presentation flow from introduction to conclusion.
5. Keep formatting structured and professional.
6. First slide must be type "title", last slide must be type "thank_you".
7. Include a "conclusion" slide before the thank you slide.
8. Use varied slide types: title, content, two_column, image_focus, comparison, timeline, conclusion, thank_you.

Supported slide types: {", ".join(SLIDE_TYPES)}
Supported image positions: {", ".join(IMAGE_POSITIONS)}

For comparison slides, use "left_section" and "right_section" arrays.
For timeline slides, use "timeline_items" array.
For title slides, include "subtitle".

Return ONLY valid JSON in this exact structure:
{{
  "presentation_title": "Title Here",
  "slides": [
    {{
      "slide_number": 1,
      "slide_type": "title",
      "title": "Main Title",
      "subtitle": "Subtitle text",
      "content": [],
      "images": []
    }},
    {{
      "slide_number": 2,
      "slide_type": "content",
      "title": "Section Title",
      "content": ["Bullet point 1", "Bullet point 2"],
      "images": [
        {{"image_name": "exact_filename.png", "position": "right"}}
      ]
    }}
  ]
}}"""

    def generate_presentation(self, request: PresentationRequest) -> PresentationResponse:
        prompt = self.build_prompt(request)

        try:
            response = self.client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a presentation content generator. Always respond with valid JSON only.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=8000,
            )
        except Exception as exc:
            raise ValidationError(f"Groq API error: {exc}") from exc

        raw_content = response.choices[0].message.content
        if not raw_content:
            raise ValidationError("Empty response from Groq API.")

        return self.parse_response(raw_content)

    def parse_response(self, raw_content: str) -> PresentationResponse:
        try:
            data = extract_json_from_response(raw_content)
        except (ValueError, json.JSONDecodeError) as exc:
            raise ValidationError(f"Failed to parse Groq response: {exc}") from exc

        try:
            slides = []
            for slide_raw in data.get("slides", []):
                images = [
                    ImageReference(**img) for img in slide_raw.get("images", [])
                ]
                slides.append(
                    SlideData(
                        slide_number=slide_raw["slide_number"],
                        slide_type=slide_raw.get("slide_type", "content"),
                        title=slide_raw.get("title", ""),
                        content=slide_raw.get("content", []),
                        images=images,
                        subtitle=slide_raw.get("subtitle"),
                        left_section=slide_raw.get("left_section"),
                        right_section=slide_raw.get("right_section"),
                        timeline_items=slide_raw.get("timeline_items"),
                    )
                )

            return PresentationResponse(
                presentation_title=data.get("presentation_title", "Presentation"),
                slides=slides,
            )
        except (KeyError, TypeError) as exc:
            raise ValidationError(f"Invalid Groq response structure: {exc}") from exc
