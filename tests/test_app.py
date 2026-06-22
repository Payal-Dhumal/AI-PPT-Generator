"""Tests for AI PPT Generator."""

import json
import os
import tempfile
from io import BytesIO

import pytest
from PIL import Image

from app.models.presentation import PresentationRequest, PresentationResponse
from app.models.slide import SlideData
from app.services.image_service import ImageManager
from app.services.groq_service import GroqService
from app.services.ppt_service import PPTGenerator
from app.utils.helpers import extract_json_from_response, sanitize_filename
from app.utils.validators import ValidationError, validate_topic, validate_slide_count
from app.templates import get_template_config


class TestValidators:
    def test_validate_topic_empty(self):
        with pytest.raises(ValidationError):
            validate_topic("")

    def test_validate_topic_valid(self):
        assert validate_topic("  AI  ") == "AI"

    def test_validate_slide_count_invalid(self):
        with pytest.raises(ValidationError):
            validate_slide_count(1)
        with pytest.raises(ValidationError):
            validate_slide_count(50)

    def test_validate_slide_count_valid(self):
        assert validate_slide_count(10) == 10


class TestHelpers:
    def test_sanitize_filename(self):
        assert sanitize_filename("My Presentation!") == "My_Presentation!"
        assert sanitize_filename("") == "presentation"

    def test_extract_json_from_response(self):
        raw = '```json\n{"title": "Test", "slides": []}\n```'
        result = extract_json_from_response(raw)
        assert result["title"] == "Test"

    def test_extract_json_plain(self):
        raw = '{"presentation_title": "AI", "slides": []}'
        result = extract_json_from_response(raw)
        assert result["presentation_title"] == "AI"


class TestTemplates:
    def test_all_templates_exist(self):
        for name in ["Professional", "Modern", "Academic", "Creative", "Minimal"]:
            config = get_template_config(name)
            assert config.name == name
            assert config.title_font
            assert config.background_color.startswith("#")


class TestImageManager:
    def _create_test_image(self) -> bytes:
        img = Image.new("RGB", (100, 100), color="red")
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        return buffer.getvalue()

    def test_upload_and_list(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ImageManager(uploads_dir=tmpdir)
            content = self._create_test_image()
            metadata = manager.upload_image(content, "test.png")
            assert metadata.image_name.endswith(".png")
            assert metadata.width == 100
            assert len(manager.list_images()) == 1

    def test_unsupported_format(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ImageManager(uploads_dir=tmpdir)
            with pytest.raises(ValidationError):
                manager.upload_image(b"data", "test.gif")


class TestGroqService:
    def test_build_prompt_includes_images(self):
        service = GroqService(api_key="test-key")
        request = PresentationRequest(
            topic="AI",
            slide_count=5,
            selected_images=["robot.png", "brain.jpg"],
        )
        prompt = service.build_prompt(request)
        assert "AI" in prompt
        assert "robot.png" in prompt
        assert "brain.jpg" in prompt
        assert "5" in prompt

    def test_parse_response(self):
        service = GroqService(api_key="test-key")
        raw = json.dumps({
            "presentation_title": "Test",
            "slides": [{
                "slide_number": 1,
                "slide_type": "title",
                "title": "Hello",
                "content": [],
                "images": [],
            }],
        })
        result = service.parse_response(raw)
        assert result.presentation_title == "Test"
        assert len(result.slides) == 1


class TestPPTGenerator:
    def test_generate_presentation(self):
        with tempfile.TemporaryDirectory() as upload_dir, tempfile.TemporaryDirectory() as gen_dir:
            manager = ImageManager(uploads_dir=upload_dir)
            generator = PPTGenerator(image_manager=manager, generated_dir=gen_dir)

            presentation = PresentationResponse(
                presentation_title="Test Presentation",
                slides=[
                    SlideData(slide_number=1, slide_type="title", title="Test", subtitle="Demo"),
                    SlideData(
                        slide_number=2,
                        slide_type="content",
                        title="Intro",
                        content=["Point 1", "Point 2"],
                    ),
                    SlideData(slide_number=3, slide_type="conclusion", title="Summary", content=["Done"]),
                    SlideData(slide_number=4, slide_type="thank_you", title="Thank You"),
                ],
            )

            file_path = generator.generate_presentation(presentation, "Professional")
            assert os.path.isfile(file_path)
            assert file_path.endswith(".pptx")
