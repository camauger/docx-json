"""
Module principal pour la génération de HTML.
"""

from typing import Any, Dict, List, Optional

from .base import ElementRenderer
from .block import BlockRenderer
from .component import ComponentRenderer
from .image import ImageRenderer
from .raw_html import RawHTMLRenderer
from .table import TableRenderer
from .text import TextElementRenderer


class HTMLGenerator:
    """
    Classe pour générer du HTML à partir de la structure JSON.
    """

    def __init__(self, json_data: Dict[str, Any]):
        """
        Initialise le générateur HTML.

        Args:
            json_data: Dictionnaire représentant le document
        """
        self._json_data = json_data
        self._images = json_data["images"]

        # Initialisation des renderers
        self._text_renderer = TextElementRenderer()
        self._table_renderer = TableRenderer(self)
        self._block_renderer = BlockRenderer(self)
        self._component_renderer = ComponentRenderer(self)
        self._image_renderer = ImageRenderer()
        self._raw_html_renderer = RawHTMLRenderer()

        # Mapping des types d'éléments vers les renderers appropriés
        self._renderers = {
            "paragraph": self._text_renderer,
            "heading": self._text_renderer,
            "list_item": self._text_renderer,
            "table": self._table_renderer,
            "block": self._block_renderer,
            "component": self._component_renderer,
            "image": self._image_renderer,
            "raw_html": self._raw_html_renderer,
        }

    def generate(self, custom_css: Optional[str] = None) -> str:
        """
        Génère le document HTML complet.

        Args:
            custom_css: CSS personnalisé à utiliser au lieu du Bootstrap par défaut (optionnel)

        Returns:
            Une chaîne de caractères contenant le HTML
        """
        html = [
            "<!DOCTYPE html>",
            '<html lang="fr">',
            "<head>",
            f'  <title>{self._json_data["meta"]["title"]}</title>',
            '  <meta charset="UTF-8">',
            '  <meta name="viewport" content="width=device-width, initial-scale=1.0">',
        ]

        # Utiliser le CSS personnalisé s'il est fourni, sinon Bootstrap
        if custom_css:
            html.append(f"  <style>{custom_css}</style>")
        else:
            html.append(
                '  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" crossorigin="anonymous">'
            )

        html.append("</head>")
        html.append("<body>")
        html.append('  <div class="container">')

        # Générer le HTML pour chaque élément, filtrer les listes vides
        for element in self._json_data["content"]:
            element_html = self._generate_element_html(element, indent_level=2)
            if element_html:  # Ne pas ajouter d'éléments vides
                html.extend(element_html)

        # Fin du document HTML
        html.append("  </div>")  # Fermer le container

        # N'inclure le script Bootstrap que si on utilise Bootstrap (pas de CSS personnalisé)
        if not custom_css:
            html.append(
                '  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-YvpcrYf0tY3lHB60NNkmXc5s9fDVZLESaAA55NDzOxhy9GkcIdslK1eN7N6jIeHz" crossorigin="anonymous"></script>'
            )

        html.append("</body>")
        html.append("</html>")

        return "\n".join(html)

    def _generate_element_html(
        self, element: Dict[str, Any], indent_level: int = 0
    ) -> List[str]:
        """
        Génère le HTML pour un élément spécifique en déléguant au renderer approprié.

        Args:
            element: Dictionnaire représentant l'élément
            indent_level: Niveau d'indentation

        Returns:
            Liste de chaînes de caractères HTML
        """
        element_type = element["type"]
        renderer = self._renderers.get(element_type)

        if renderer:
            return renderer.render(element, indent_level)

        # Type d'élément non reconnu
        return []
