"""
Module contenant la classe de base pour tous les renderers HTML.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class ElementRenderer(ABC):
    """Classe abstraite pour le rendu des éléments HTML."""

    def __init__(self, html_generator):
        """
        Initialise le renderer.

        Args:
            html_generator: Instance du générateur HTML principal
        """
        self.html_generator = html_generator

    @abstractmethod
    def render(self, element: Dict[str, Any], indent_level: int = 0) -> List[str]:
        """
        Génère le HTML pour un élément spécifique.

        Args:
            element: Dictionnaire représentant l'élément
            indent_level: Niveau d'indentation

        Returns:
            Liste de chaînes de caractères HTML
        """
        pass

    def _format_runs(self, runs: List[Dict[str, Any]]) -> List[str]:
        """
        Formate une liste de runs en appliquant les styles.

        Args:
            runs: Liste des runs à formater

        Returns:
            Liste des textes formatés
        """
        content = []
        for run in runs:
            text = run["text"]
            if run.get("bold", False):
                text = f"<strong>{text}</strong>"
            if run.get("italic", False):
                text = f"<em>{text}</em>"
            if run.get("underline", False):
                text = f"<u>{text}</u>"
            content.append(text)
        return content
