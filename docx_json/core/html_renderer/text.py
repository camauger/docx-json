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
        elif element["type"] == "list":
            return self._render_list(element, indent_level)
        return []

    def _render_paragraph(
        self, element: Dict[str, Any], indent_level: int
    ) -> List[str]:
        """
        Génère le HTML pour un paragraphe.

        Args:
            element: Dictionnaire représentant le paragraphe.
            indent_level: Niveau d'indentation.

        Returns:
            Liste de lignes HTML.
        """
        indent = " " * indent_level

        # Ajouter des classes Bootstrap pour les paragraphes
        classes = element.get("html_class", "")
        if not classes:
            classes = "mb-3 lead"

        class_attr = f' class="{classes}"' if classes else ""
        id_attr = f' id="{element["html_id"]}"' if "html_id" in element else ""

        # Ouvrir la balise avec les attributs appropriés
        opening_tag = f"{indent}<p{class_attr}{id_attr}>"

        # Formater le contenu
        content = self._format_runs(element.get("runs", []))

        # Ne pas générer de HTML pour les paragraphes vides
        if not content:
            return []

        # Assembler le HTML
        return [f"{opening_tag}{''.join(content)}</p>"]

    def _render_heading(self, element: Dict[str, Any], indent_level: int) -> List[str]:
        """
        Génère le HTML pour un titre.

        Args:
            element: Dictionnaire représentant le titre.
            indent_level: Niveau d'indentation.

        Returns:
            Liste de lignes HTML.
        """
        level = element.get("level", 1)
        indent = " " * indent_level

        # Ajouter des classes Bootstrap selon le niveau
        classes = element.get("html_class", "")
        if level == 1:
            classes += " display-4 fw-bold mb-4"
        elif level == 2:
            classes += " border-start border-4 border-success ps-2 mb-3 mt-4"
        elif level == 3:
            classes += " text-primary mb-3"
        elif level == 4:
            classes += " text-secondary fst-italic mb-2"

        class_attr = f' class="{classes.strip()}"' if classes.strip() else ""
        id_attr = f' id="{element["html_id"]}"' if "html_id" in element else ""

        # Construire la balise avec les attributs appropriés
        opening_tag = f"{indent}<h{level}{class_attr}{id_attr}>"
        closing_tag = f"</h{level}>"

        # Formater le contenu
        content = self._format_runs(element.get("runs", []))

        # Ne pas générer de HTML pour les titres vides
        if not content:
            return []

        # Assembler le HTML
        return [f"{opening_tag}{''.join(content)}{closing_tag}"]

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
        if content:
            return [f"{indent}<li>{''.join(content)}</li>"]
        return []

    def _render_list(self, element: Dict[str, Any], indent_level: int) -> List[str]:
        # Vérifier si la liste contient des éléments
        if not element.get("items"):
            return []

        indent = " " * indent_level
        list_tag = "ol" if element.get("ordered", False) else "ul"

        # Ajouter les attributs HTML si présents
        attrs = []
        if "html_class" in element:
            attrs.append(f'class="{element["html_class"]}"')
        if "html_id" in element:
            attrs.append(f'id="{element["html_id"]}"')

        attrs_str = " ".join(attrs)
        attrs_str = f" {attrs_str}" if attrs_str else ""

        element_html = [f"{indent}<{list_tag}{attrs_str}>"]

        # Ajouter chaque élément de la liste
        for item in element["items"]:
            item_html = self._render_list_item(item, indent_level + 2)
            if item_html:
                element_html.extend(item_html)

        element_html.append(f"{indent}</{list_tag}>")
        return element_html
