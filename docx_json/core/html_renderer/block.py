"""
Renderer pour les blocs
"""

from typing import Any, Dict, List

from .base import ElementRenderer


class BlockRenderer(ElementRenderer):
    """
    Renderer pour les blocs HTML (citations, encadrés, etc.).
    """

    def __init__(self, html_generator):
        """
        Initialise le renderer.

        Args:
            html_generator: Instance du générateur HTML principal
        """
        super().__init__(html_generator)

    def render(self, element: Dict[str, Any], indent_level: int = 0) -> List[str]:
        """
        Génère le HTML pour un bloc.

        Args:
            element: Dictionnaire représentant le bloc
            indent_level: Niveau d'indentation

        Returns:
            Liste de chaînes de caractères HTML
        """
        block_type = element["block_type"]
        if block_type == "quote":
            return self._render_quote(element, indent_level)
        elif block_type == "aside":
            return self._render_aside(element, indent_level)
        else:
            raise ValueError(f"Type de bloc inconnu : {block_type}")

    def _render_quote(self, element: Dict[str, Any], indent_level: int) -> List[str]:
        """
        Génère le HTML pour une citation.

        Args:
            element: Dictionnaire représentant la citation
            indent_level: Niveau d'indentation

        Returns:
            Liste de chaînes de caractères HTML
        """
        indent = " " * indent_level
        html = [f"{indent}<blockquote>"]

        # Générer le contenu de la citation
        for content_element in element["content"]:
            content_html = self.html_generator._generate_element_html(
                content_element, indent_level + 2
            )
            html.extend(content_html)

        html.append(f"{indent}</blockquote>")
        return html

    def _render_aside(self, element: Dict[str, Any], indent_level: int) -> List[str]:
        """
        Génère le HTML pour un encadré.

        Args:
            element: Dictionnaire représentant l'encadré
            indent_level: Niveau d'indentation

        Returns:
            Liste de chaînes de caractères HTML
        """
        indent = " " * indent_level
        html = [f'{indent}<aside class="alert alert-info">']

        # Générer le contenu de l'encadré
        for content_element in element["content"]:
            content_html = self.html_generator._generate_element_html(
                content_element, indent_level + 2
            )
            html.extend(content_html)

        html.append(f"{indent}</aside>")
        return html
