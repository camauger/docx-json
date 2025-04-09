"""
Module contenant le renderer pour les tables.
"""

from typing import Any, Dict, List

from .base import ElementRenderer


class TableRenderer(ElementRenderer):
    """Classe pour le rendu des tables."""

    def __init__(self, html_generator):
        """
        Initialise le renderer.

        Args:
            html_generator: Instance du générateur HTML principal
        """
        super().__init__(html_generator)

    def render(self, element: Dict[str, Any], indent_level: int = 0) -> List[str]:
        """
        Génère le HTML pour un tableau.

        Args:
            element: Dictionnaire représentant le tableau
            indent_level: Niveau d'indentation

        Returns:
            Liste de chaînes de caractères HTML
        """
        indent = " " * indent_level
        html = [f'{indent}<table class="table table-bordered">', f"{indent}  <tbody>"]

        # Générer les lignes
        for row in element["rows"]:
            html.append(f"{indent}    <tr>")
            for cell in row:
                html.append(f"{indent}      <td>")
                # Si la cellule est une liste d'éléments
                if isinstance(cell, list):
                    # Générer le contenu pour chaque élément de la cellule
                    for cell_element in cell:
                        cell_content = self.html_generator._generate_element_html(
                            cell_element, indent_level + 8
                        )
                        html.extend(cell_content)
                # Si la cellule est un élément unique
                else:
                    cell_content = self.html_generator._generate_element_html(
                        cell, indent_level + 8
                    )
                    html.extend(cell_content)
                html.append(f"{indent}      </td>")
            html.append(f"{indent}    </tr>")

        html.extend([f"{indent}  </tbody>", f"{indent}</table>"])

        return html
