"""
Renderer pour les images
"""

from typing import Any, Dict, List

from .base import ElementRenderer


class ImageRenderer(ElementRenderer):
    """
    Renderer pour les images HTML.
    """

    def render(self, element: Dict[str, Any], indent_level: int = 0) -> List[str]:
        """
        Génère le HTML pour une image.

        Args:
            element: Dictionnaire représentant l'image
            indent_level: Niveau d'indentation

        Returns:
            Liste de chaînes de caractères HTML
        """
        indent = " " * indent_level
        src = element["src"]
        image_data = self.html_generator._images[src]

        # Générer la balise img avec les données base64
        html = [
            f'{indent}<img src="data:image/png;base64,{image_data}" '
            f'class="img-fluid" alt="{src}">'
        ]

        return html
