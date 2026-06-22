"""Base template configuration."""

from dataclasses import dataclass


@dataclass(frozen=True)
class TemplateConfig:
    name: str
    background_color: str
    title_color: str
    heading_color: str
    content_color: str
    accent_color: str
    title_font: str
    heading_font: str
    body_font: str
    title_size: int
    heading_size: int
    content_size: int
    subtitle_size: int
