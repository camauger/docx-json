"""
Module contenant le renderer pour les images.
"""

from typing import Any, Dict, List

from .base import ElementRenderer


class ImageRenderer(ElementRenderer):
    """Classe pour le rendu des images."""

    def render(self, element: Dict[str, Any], indent_level: int = 0) -> List[str]:
        if "image_path" not in element:
            return []

        indent = " " * indent_level
        img_path = element["image_path"]
        img_alt = element.get("alt_text", "Image")

        return [
            f'{indent}<img src="{img_path}" alt="{img_alt}" class="img-fluid my-3" />'
        ]
