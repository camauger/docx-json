"""
Module contenant le renderer pour le HTML brut.
"""

from typing import Any, Dict, List

from .base import ElementRenderer


class RawHTMLRenderer(ElementRenderer):
    """Classe pour le rendu du HTML brut."""

    def render(self, element: Dict[str, Any], indent_level: int = 0) -> List[str]:
        indent = " " * indent_level
        return [f"{indent}{element['content']}"]
