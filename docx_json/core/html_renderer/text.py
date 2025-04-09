"""
Module contenant le renderer pour les éléments textuels.
"""

from typing import Any, Dict, List

from .base import ElementRenderer


class TextElementRenderer(ElementRenderer):
    """Classe pour le rendu des éléments textuels (paragraphes, titres, listes)."""

    def render(self, element: Dict[str, Any], indent_level: int = 0) -> List[str]:
        if element["type"] == "paragraph":
            return self._render_paragraph(element, indent_level)
        elif element["type"] == "heading":
            return self._render_heading(element, indent_level)
        elif element["type"] == "list_item":
            return self._render_list_item(element, indent_level)
        return []

    def _render_paragraph(
        self, element: Dict[str, Any], indent_level: int
    ) -> List[str]:
        # Vérifier si le paragraphe contient du texte non-vide
        has_content = False
        for run in element["runs"]:
            if run["text"].strip():
                has_content = True
                break

        # Ne pas générer de HTML pour les paragraphes vides
        if not has_content:
            return []

        attrs = []
        if "html_class" in element:
            attrs.append(f'class="{element["html_class"]}"')
        if "html_id" in element:
            attrs.append(f'id="{element["html_id"]}"')

        attrs_str = " ".join(attrs)
        attrs_str = f" {attrs_str}" if attrs_str else ""
        indent = " " * indent_level

        content = self._format_runs(element["runs"])
        if content:
            return [f"{indent}<p{attrs_str}>{''.join(content)}</p>"]
        return []

    def _render_heading(self, element: Dict[str, Any], indent_level: int) -> List[str]:
        attrs = []
        if "html_class" in element:
            attrs.append(f'class="{element["html_class"]}"')
        if "html_id" in element:
            attrs.append(f'id="{element["html_id"]}"')

        attrs_str = " ".join(attrs)
        attrs_str = f" {attrs_str}" if attrs_str else ""
        indent = " " * indent_level
        level = element["level"]

        content = self._format_runs(element["runs"])
        if "".join(content).strip():
            return [f"{indent}<h{level}{attrs_str}>{''.join(content)}</h{level}>"]
        return []

    def _render_list_item(
        self, element: Dict[str, Any], indent_level: int
    ) -> List[str]:
        # Vérifier si l'élément de liste contient du texte non-vide
        has_content = False
        for run in element["runs"]:
            if run["text"].strip():
                has_content = True
                break

        # Ne pas générer de HTML pour les éléments de liste vides
        if not has_content:
            return []

        indent = " " * indent_level
        content = self._format_runs(element["runs"])
        return [f"{indent}<li>{''.join(content)}</li>"]
