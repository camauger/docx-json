"""
Module contenant le renderer pour les tables.
"""

from typing import Any, Dict, List

from .base import ElementRenderer


class TableRenderer(ElementRenderer):
    """Classe pour le rendu des tables."""

    def __init__(self, html_generator):
        self.html_generator = html_generator

    def render(self, element: Dict[str, Any], indent_level: int = 0) -> List[str]:
        # Vérifier si la table n'est pas vide
        has_content = False
        for row in element["rows"]:
            if row:  # Si la ligne contient au moins une cellule
                has_content = True
                break

        # Ne pas générer de HTML pour les tables vides
        if not has_content:
            return []

        indent = " " * indent_level
        element_html = [f'{indent}<table class="table table-bordered">']

        for row in element["rows"]:
            element_html.append(f"{indent}  <tr>")
            for cell in row:
                element_html.append(f"{indent}    <td>")
                for para in cell:
                    cell_content = self.html_generator._generate_element_html(
                        para, indent_level=indent_level + 6
                    )
                    if cell_content:  # Ajouter uniquement si la cellule n'est pas vide
                        element_html.extend(cell_content)
                element_html.append(f"{indent}    </td>")
            element_html.append(f"{indent}  </tr>")

        element_html.append(f"{indent}</table>")
        return element_html
