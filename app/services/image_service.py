"""Image upload and metadata management."""

import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from PIL import Image

from app.models.image import ImageMetadata
from app.utils.constants import MAX_IMAGE_SIZE_BYTES, UPLOADS_DIR
from app.utils.validators import ValidationError, validate_image_format


class ImageManager:
    """Handles image uploads, storage, and metadata."""

    def __init__(self, uploads_dir: str = UPLOADS_DIR):
        self.uploads_dir = uploads_dir
        self._registry: Dict[str, ImageMetadata] = {}
        os.makedirs(self.uploads_dir, exist_ok=True)

    def upload_image(self, file_content: bytes, original_filename: str) -> ImageMetadata:
        validate_image_format(original_filename)

        if len(file_content) > MAX_IMAGE_SIZE_BYTES:
            raise ValidationError(
                f"Image exceeds maximum size of {MAX_IMAGE_SIZE_BYTES // (1024 * 1024)} MB."
            )

        safe_name = self._generate_unique_name(original_filename)
        file_path = os.path.join(self.uploads_dir, safe_name)

        with open(file_path, "wb") as f:
            f.write(file_content)

        try:
            with Image.open(file_path) as img:
                width, height = img.size
                img.verify()
        except Exception as exc:
            os.remove(file_path)
            raise ValidationError(f"Corrupted or invalid image: {original_filename}") from exc

        metadata = ImageMetadata(
            image_name=safe_name,
            display_name=original_filename,
            path=file_path,
            width=width,
            height=height,
            upload_timestamp=datetime.now(timezone.utc),
        )
        self._registry[safe_name] = metadata
        return metadata

    def get_image(self, image_name: str) -> Optional[ImageMetadata]:
        if image_name in self._registry:
            return self._registry[image_name]
        file_path = os.path.join(self.uploads_dir, image_name)
        if os.path.isfile(file_path):
            return self._load_metadata_from_disk(image_name, file_path)
        return None

    def list_images(self) -> List[ImageMetadata]:
        self._sync_from_disk()
        return list(self._registry.values())

    def get_image_path(self, image_name: str) -> str:
        metadata = self.get_image(image_name)
        if not metadata:
            raise ValidationError(f"Image not found: {image_name}")
        return metadata.path

    def delete_image(self, image_name: str) -> bool:
        metadata = self.get_image(image_name)
        if not metadata:
            return False
        if os.path.isfile(metadata.path):
            os.remove(metadata.path)
        self._registry.pop(image_name, None)
        return True

    def _generate_unique_name(self, original_filename: str) -> str:
        extension = Path(original_filename).suffix.lower()
        return f"{uuid.uuid4().hex[:12]}{extension}"

    def _sync_from_disk(self) -> None:
        if not os.path.isdir(self.uploads_dir):
            return
        for filename in os.listdir(self.uploads_dir):
            if filename in self._registry:
                continue
            file_path = os.path.join(self.uploads_dir, filename)
            if os.path.isfile(file_path):
                try:
                    validate_image_format(filename)
                    self._load_metadata_from_disk(filename, file_path)
                except ValidationError:
                    continue

    def _load_metadata_from_disk(self, filename: str, file_path: str) -> ImageMetadata:
        with Image.open(file_path) as img:
            width, height = img.size
        metadata = ImageMetadata(
            image_name=filename,
            display_name=filename,
            path=file_path,
            width=width,
            height=height,
            upload_timestamp=datetime.fromtimestamp(os.path.getmtime(file_path)),
        )
        self._registry[filename] = metadata
        return metadata
