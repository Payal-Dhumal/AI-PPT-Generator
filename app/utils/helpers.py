"""General helper utilities."""

import json
import re
from typing import Any, Dict


def sanitize_filename(name: str) -> str:
    sanitized = re.sub(r'[<>:"/\\|?*]', "_", name)
    sanitized = re.sub(r"\s+", "_", sanitized.strip())
    return sanitized[:100] if sanitized else "presentation"


def extract_json_from_response(text: str) -> Dict[str, Any]:
    """Extract JSON object from Groq response, handling markdown fences."""
    text = text.strip()

    if text.startswith("```"):
        lines = text.split("\n")
        json_lines = []
        in_block = False
        for line in lines:
            if line.startswith("```") and not in_block:
                in_block = True
                continue
            if line.startswith("```") and in_block:
                break
            if in_block:
                json_lines.append(line)
        text = "\n".join(json_lines)

    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("No JSON object found in response.")

    return json.loads(text[start : end + 1])
