"""
Générateur HTML principal
"""

import os
from typing import Any, Dict, List, Optional

from .block import BlockRenderer
from .component import ComponentRenderer
from .image import ImageRenderer
from .page_break import PageBreakRenderer
from .raw_html import RawHTMLRenderer
from .table import TableRenderer
from .text import TextElementRenderer


class HTMLGenerator:
    """
    Générateur HTML principal qui coordonne les différents renderers.
    """

    BOOTSTRAP_CSS = (
        '<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" '
        'rel="stylesheet" integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" '
        'crossorigin="anonymous">'
    )

    BOOTSTRAP_JS = (
        '<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js" '
        'integrity="sha384-YvpcrYf0tY3lHB60NNkmXc5s9fDVZLESaAA55NDzOxhy9GkcIdslK1eN7N6jIeHz" '
        'crossorigin="anonymous"></script>'
    )

    PAGE_BREAK_CSS = """
    @media print {
      .page-break {
        page-break-after: always;
        break-after: page;
      }
    }"""

    def __init__(self, json_data: Dict[str, Any]):
        """
        Initialise le générateur HTML.

        Args:
            json_data: Dictionnaire représentant le document
        """
        self._json_data = json_data
        self._images = json_data["images"]

        # Initialisation des renderers
        self._text_renderer = TextElementRenderer(self)
        self._table_renderer = TableRenderer(self)
        self._block_renderer = BlockRenderer(self)
        self._component_renderer = ComponentRenderer(self)
        self._image_renderer = ImageRenderer(self)
        self._raw_html_renderer = RawHTMLRenderer(self)
        self._page_break_renderer = PageBreakRenderer(self)

        # Mappage des types d'éléments aux renderers
        self._renderers = {
            "paragraph": self._text_renderer,
            "heading": self._text_renderer,
            "list_item": self._text_renderer,
            "table": self._table_renderer,
            "block": self._block_renderer,
            "component": self._component_renderer,
            "image": self._image_renderer,
            "raw_html": self._raw_html_renderer,
            "page_break": self._page_break_renderer,
        }

    def generate(self, custom_css: Optional[str] = None) -> str:
        """
        Génère le document HTML complet. Si des sauts de page sont présents, génère un fichier HTML unique
        avec des marqueurs de saut de page qui peuvent être interprétés ultérieurement.

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

        # Ajouter le CSS
        if custom_css:
            html.extend(["  <style>", f"    {custom_css}", "  </style>"])
        else:
            html.append(f"  {self.BOOTSTRAP_CSS}")

        # Ajouter le CSS pour les sauts de page
        html.extend(
            [
                "  <style>",
                f"    {self.PAGE_BREAK_CSS}",
                "  </style>",
                "</head>",
                "<body>",
                '  <div class="container py-4">',  # Ajouter un padding vertical
            ]
        )

        # Générer le contenu
        for element in self._json_data["content"]:
            element_html = self._generate_element_html(element, indent_level=4)
            html.extend(element_html)

        # Fermer les balises principales
        html.append("  </div>")  # Fermer le container

        # Ajouter les scripts Bootstrap si nécessaire
        if not custom_css:
            html.append(f"  {self.BOOTSTRAP_JS}")

        html.extend(["</body>", "</html>"])

        return "\n".join(html)

    def generate_multi_page(
        self, output_dir: str, base_filename: str, custom_css: Optional[str] = None
    ) -> List[str]:
        """
        Génère plusieurs fichiers HTML en séparant le document aux sauts de page.

        Args:
            output_dir: Répertoire de sortie pour les fichiers HTML
            base_filename: Nom de base pour les fichiers (sans extension)
            custom_css: CSS personnalisé à utiliser (optionnel)

        Returns:
            Liste des chemins des fichiers HTML générés
        """
        # Vérifier que le répertoire de sortie est valide
        if not output_dir or not isinstance(output_dir, str):
            raise ValueError(
                "Le répertoire de sortie doit être une chaîne de caractères non vide"
            )

        # Vérifier que le nom de base est valide
        if not base_filename or not isinstance(base_filename, str):
            raise ValueError(
                "Le nom de base doit être une chaîne de caractères non vide"
            )

        # Nettoyer les chemins
        output_dir = os.path.abspath(output_dir)
        base_filename = os.path.basename(
            base_filename
        )  # Enlever les chemins du nom de base

        # S'assurer que le répertoire de sortie existe
        try:
            os.makedirs(output_dir, exist_ok=True)
        except Exception as e:
            raise ValueError(f"Impossible de créer le répertoire de sortie: {str(e)}")

        # Générer le HTML complet
        full_html = self.generate(custom_css)

        # Diviser aux sauts de page
        pages = full_html.split("<!-- page-break -->")
        files = []

        # Générer un fichier par page
        for i, page in enumerate(pages):
            filename = f"{base_filename}_{i}.html" if i > 0 else f"{base_filename}.html"
            filepath = os.path.join(output_dir, filename)

            try:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(page.strip())
                files.append(filepath)
            except Exception as e:
                raise ValueError(f"Impossible d'écrire le fichier {filepath}: {str(e)}")

        return files

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

        Raises:
            KeyError: Si le type d'élément n'est pas supporté
        """
        element_type = element["type"]
        try:
            renderer = self._renderers[element_type]
            return renderer.render(element, indent_level)
        except KeyError:
            raise KeyError(f"Type d'élément non supporté : {element_type}")
