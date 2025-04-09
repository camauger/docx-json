"""
Module contenant le renderer pour les blocs.
"""

from typing import Any, Dict, List

from .base import ElementRenderer


class BlockRenderer(ElementRenderer):
    """Classe pour le rendu des blocs (citations, encadrés...)."""

    def __init__(self, html_generator):
        self.html_generator = html_generator

    def render(self, element: Dict[str, Any], indent_level: int = 0) -> List[str]:
        block_type = element["block_type"]
        if block_type == "quote":
            return self._render_quote(element, indent_level)
        elif block_type == "aside":
            return self._render_aside(element, indent_level)
        # Autres types de blocs...
        return []

    def _render_quote(self, element: Dict[str, Any], indent_level: int) -> List[str]:
        indent = " " * indent_level
        element_html = [f'{indent}<blockquote class="blockquote">']

        has_content = False
        for content_elem in element["content"]:
            content = self.html_generator._generate_element_html(
                content_elem, indent_level=indent_level + 2
            )
            if content:
                has_content = True
                element_html.extend(content)

        if not has_content:
            return []

        element_html.append(f"{indent}</blockquote>")
        return element_html

    def _render_aside(self, element: Dict[str, Any], indent_level: int) -> List[str]:
        indent = " " * indent_level
        element_html = [f'{indent}<aside class="border p-3 my-3">']

        has_content = False
        for content_elem in element["content"]:
            content = self.html_generator._generate_element_html(
                content_elem, indent_level=indent_level + 2
            )
            if content:
                has_content = True
                element_html.extend(content)

        if not has_content:
            return []

        element_html.append(f"{indent}</aside>")
        return element_html
