"""
Générateur HTML principal
"""

import logging
import os
from typing import Any, Dict, List, Optional

from .block import BlockRenderer
from .component import ComponentRenderer
from .image import ImageRenderer
from .page_break import PageBreakRenderer
from .raw_html import RawHTMLRenderer
from .table import TableRenderer
from .text import TextElementRenderer
from .video import VideoRenderer


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
            "list": self._text_renderer,
            "table": self._table_renderer,
            "block": self._block_renderer,
            "component": self._component_renderer,
            "component_marker": self._component_renderer,
            "component_end": self._component_renderer,
            "image": self._image_renderer,
            "raw_html": self._raw_html_renderer,
            "page_break": self._page_break_renderer,
            "video": VideoRenderer(self),
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
            "  <link rel='stylesheet' href='https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css'>",
        ]

        # Ajouter le CSS
        if custom_css:
            html.extend(["  <style>", f"    {custom_css}", "  </style>"])
            html.append(f"  {self.BOOTSTRAP_CSS}")
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
                "  <!-- En-tête -->",
                '  <header class="bg-primary py-3 mb-4 shadow-sm">',
                '    <div class="container">',
                '      <div class="d-flex align-items-center">',
                f'        <h1 class="h4 mb-0">{self._json_data["meta"]["title"]}</h1>',
                '        <div class="ms-auto">',
                '          <button class="btn btn-outline-light btn-sm" id="theme-toggle">',
                '            <i class="bi bi-brightness-high" id="light-icon"></i>',
                '            <i class="bi bi-moon-stars d-none" id="dark-icon"></i>',
                "          </button>",
                "        </div>",
                "      </div>",
                "    </div>",
                "  </header>",
                "  <!-- Contenu principal -->",
                "  <main class='container'>",
                '    <div class="col-8 m-auto py-4">',  # Ajouter un padding vertical
            ]
        )

        # Générer le contenu
        for element in self._json_data["content"]:
            element_html = self._generate_element_html(element, indent_level=6)
            html.extend(element_html)

        # Fermer les balises principales
        html.extend(
            [
                "    </div>",  # Fermer le container
                "  </main>",
                "  <!-- Pied de page -->",
                '  <footer class="bg-light py-4 mt-5 border-top">',
                '    <div class="container">',
                '      <div class="row">',
                '        <div class="col-md-6">',
                '          <p class="mb-0 text-muted">© 2025 - TELUQ</p>',
                "        </div>",
                '        <div class="col-md-6 text-md-end">',
                '          <a href="#" class="text-decoration-none me-3"><i class="bi bi-github"></i> GitHub</a>',
                '          <a href="#" class="text-decoration-none"><i class="bi bi-book"></i> Documentation</a>',
                "        </div>",
                "      </div>",
                "    </div>",
                "  </footer>",
            ]
        )

        # Ajouter les scripts Bootstrap
        if not custom_css:
            html.append(f"  {self.BOOTSTRAP_JS}")
        else:
            html.append(f"  {self.BOOTSTRAP_JS}")

        # Ajouter le script pour le toggle de thème
        html.extend(
            [
                "  <script>",
                '    document.getElementById("theme-toggle").addEventListener("click", function() {',
                '      document.body.classList.toggle("bg-dark");',
                '      document.body.classList.toggle("text-white");',
                '      document.getElementById("light-icon").classList.toggle("d-none");',
                '      document.getElementById("dark-icon").classList.toggle("d-none");',
                '      const containers = document.querySelectorAll(".container");',
                "      containers.forEach(container => {",
                '        if (document.body.classList.contains("bg-dark")) {',
                '          container.style.backgroundColor = "#343a40";',
                '          container.style.color = "#fff";',
                "        } else {",
                '          container.style.backgroundColor = "#fff";',
                '          container.style.color = "#212529";',
                "        }",
                "      });",
                "    });",
                "  </script>",
                "</body>",
                "</html>",
            ]
        )

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
        Génère le HTML pour un élément spécifique.

        Args:
            element: Données de l'élément
            indent_level: Niveau d'indentation

        Returns:
            Liste de lignes HTML
        """
        element_html = []
        indent = "  " * indent_level

        try:
            element_type = element.get("type", "unknown")

            # Traitement spécial pour les composants vidéo
            if element_type == "component" and element.get("component_type") == "Vidéo":
                # Traitement spécial pour les composants vidéo
                return self._render_video_component(element, indent_level)

            # Vérifier si c'est un paragraphe avec un marqueur de vidéo
            if element_type == "paragraph" and "runs" in element:
                # Extraire le texte complet du paragraphe
                full_text = ""
                for run in element["runs"]:
                    full_text += run.get("text", "")

                # Vérifier si c'est un marqueur de vidéo
                if full_text.strip().startswith("[Vidéo") and "]" in full_text:
                    print(
                        f"DEBUG - Marqueur vidéo détecté dans le paragraphe: '{full_text}'"
                    )
                    # Utiliser le renderer vidéo pour traiter cet élément
                    video_renderer = self._renderers.get("video")
                    if video_renderer:
                        return video_renderer.render(element, indent_level)
                    else:
                        # Fallback au rendu direct si le renderer n'est pas disponible
                        return self._render_paragraph_video(full_text, indent_level)

            # Utiliser les renderers pour les autres types d'éléments
            renderer = self._renderers.get(element_type)
            if renderer:
                element_html = renderer.render(element, indent_level)
            else:
                # Si pas de renderer pour ce type, ajouter un commentaire d'erreur
                element_html.append(
                    f"{indent}<!-- Erreur lors du rendu : {element_type} -->"
                )
                element_html.append(
                    f'{indent}<div class="rendering-error">(Erreur de rendu)</div>'
                )

            return element_html

        except Exception as e:
            # En cas d'erreur, ajouter un commentaire et une div d'erreur
            error_message = str(e)
            logging.error(f"Erreur de rendu HTML: {error_message}")
            element_html.append(
                f"{indent}<!-- Erreur lors du rendu : {error_message} -->"
            )
            element_html.append(
                f'{indent}<div class="rendering-error">(Erreur de rendu)</div>'
            )

            return element_html

    def _render_video_component(
        self, element: Dict[str, Any], indent_level: int = 0
    ) -> List[str]:
        """
        Rend un composant vidéo en HTML.

        Args:
            element: Élément de composant vidéo
            indent_level: Niveau d'indentation

        Returns:
            Liste de lignes HTML
        """
        indent = "  " * indent_level

        # Obtenir l'ID de la vidéo à partir des attributs
        video_id = "1069341210"  # Valeur par défaut

        if "attributes" in element and isinstance(element["attributes"], dict):
            # Récupérer depuis les attributs du composant
            video_id = element["attributes"].get("video_id", video_id)
        elif hasattr(element, "get"):
            # Récupération directe si l'élément supporte get()
            video_id = element.get("video_id", video_id)

        print(f"DEBUG - Rendu de composant vidéo avec ID: {video_id}")

        # Générer le HTML pour la vidéo
        return [
            f'{indent}<section class="video-component">',
            f'{indent}  <div class="video-container">',
            f'{indent}    <iframe src="https://player.vimeo.com/video/{video_id}" width="640" height="360" frameborder="0" ',
            f'{indent}      allow="autoplay; fullscreen; picture-in-picture" allowfullscreen></iframe>',
            f"{indent}  </div>",
            f'{indent}  <script src="https://player.vimeo.com/api/player.js"></script>',
            f"{indent}</section>",
        ]

    def _render_paragraph_video(self, text: str, indent_level: int = 0) -> List[str]:
        """
        Rend un paragraphe contenant un marqueur de vidéo en HTML.

        Args:
            text: Texte du paragraphe contenant le marqueur de vidéo
            indent_level: Niveau d'indentation

        Returns:
            Liste de lignes HTML
        """
        indent = " " * indent_level

        # Valeur par défaut pour l'ID de vidéo
        video_id = "1069341210"

        # Rechercher l'ID de vidéo avec des quotes simples
        if "video_id='" in text:
            start_idx = text.find("video_id='") + 10
            end_idx = text.find("'", start_idx)
            if end_idx > start_idx:
                video_id = text[start_idx:end_idx]
                print(f"DEBUG - ID vidéo trouvé (quotes simples): '{video_id}'")

        # Rechercher l'ID de vidéo avec des quotes doubles
        elif 'video_id="' in text:
            start_idx = text.find('video_id="') + 10
            end_idx = text.find('"', start_idx)
            if end_idx > start_idx:
                video_id = text[start_idx:end_idx]
                print(f"DEBUG - ID vidéo trouvé (quotes doubles): '{video_id}'")

        print(f"DEBUG - Génération de l'iframe pour la vidéo avec ID: {video_id}")

        # Générer le HTML pour la vidéo Vimeo
        return [
            f'{indent}<div class="video-container">',
            f'{indent}  <iframe src="https://player.vimeo.com/video/{video_id}"',
            f'{indent}          style="width:100%;height:400px;"',
            f'{indent}          frameborder="0"',
            f'{indent}          allow="autoplay; fullscreen; picture-in-picture"',
            f"{indent}          allowfullscreen",
            f'{indent}          title="Vimeo Video Player">',
            f"{indent}  </iframe>",
            f"{indent}</div>",
            f'{indent}<script src="https://player.vimeo.com/api/player.js"></script>',
        ]
