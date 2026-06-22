"""Template registry."""

from app.templates.base import TemplateConfig


def get_template_config(template_name: str) -> TemplateConfig:
    from app.templates.academic import ACADEMIC_TEMPLATE
    from app.templates.creative import CREATIVE_TEMPLATE
    from app.templates.minimal import MINIMAL_TEMPLATE
    from app.templates.modern import MODERN_TEMPLATE
    from app.templates.professional import PROFESSIONAL_TEMPLATE

    templates = {
        "Professional": PROFESSIONAL_TEMPLATE,
        "Modern": MODERN_TEMPLATE,
        "Academic": ACADEMIC_TEMPLATE,
        "Creative": CREATIVE_TEMPLATE,
        "Minimal": MINIMAL_TEMPLATE,
    }
    return templates.get(template_name, PROFESSIONAL_TEMPLATE)
