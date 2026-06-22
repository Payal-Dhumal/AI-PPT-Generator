"""Central configuration constants for the AI PPT Generator."""

MAX_SLIDES = 30
MIN_SLIDES = 3
DEFAULT_SLIDE_COUNT = 10

SUPPORTED_IMAGE_FORMATS = {".png", ".jpg", ".jpeg", ".webp"}
MAX_IMAGE_SIZE_MB = 10
MAX_IMAGE_SIZE_BYTES = MAX_IMAGE_SIZE_MB * 1024 * 1024

UPLOADS_DIR = "uploads"
GENERATED_DIR = "generated"
ASSETS_DIR = "assets"

# Typography (points)
DEFAULT_FONT_SIZE = 18
TITLE_FONT_SIZE = 44
SECTION_HEADING_FONT_SIZE = 32
CONTENT_FONT_SIZE = 18
SUBTITLE_FONT_SIZE = 24
CAPTION_FONT_SIZE = 14

# Spacing (inches)
TITLE_MARGIN = 0.75
CONTENT_MARGIN = 0.5
IMAGE_MARGIN = 0.4
SLIDE_PADDING = 0.6
BULLET_INDENT = 0.25

# Image placement
IMAGE_PADDING = 0.2

PRESENTATION_TYPES = [
    "Academic Presentation",
    "Business Presentation",
    "Project Report",
    "Seminar Presentation",
    "Research Presentation",
    "Product Pitch",
]

TEMPLATE_NAMES = [
    "Professional",
    "Modern",
    "Academic",
    "Creative",
    "Minimal",
]

SLIDE_TYPES = [
    "title",
    "content",
    "two_column",
    "image_focus",
    "comparison",
    "timeline",
    "conclusion",
    "thank_you",
]

IMAGE_POSITIONS = ["left", "right", "center", "top", "bottom", "background"]

GROQ_MODEL = "llama-3.3-70b-versatile"
