"""
Module contenant le renderer pour les sauts de page.
"""

from typing import Any, Dict, List

from .base import ElementRenderer


class PageBreakRenderer(ElementRenderer):
    """Classe pour le rendu des sauts de page."""

    def render(self, element: Dict[str, Any], indent_level: int = 0) -> List[str]:
        """
        Génère le HTML pour un saut de page.

        Args:
            element: Dictionnaire représentant l'élément de saut de page
            indent_level: Niveau d'indentation

        Returns:
            Liste de chaînes de caractères HTML avec un marqueur de saut de page
        """
        indent = " " * indent_level
        # Utilise un commentaire spécial et une div avec une classe spéciale pour le saut de page
        return [
            f"{indent}<!-- PAGE_BREAK_MARKER -->",
            f'{indent}<div class="page-break" data-page-break="true"></div>',
        ]
