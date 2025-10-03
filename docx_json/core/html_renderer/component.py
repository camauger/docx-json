"""
Module contenant le renderer pour les composants interactifs.
"""

import logging
import re
from typing import Any, Dict, List

from .base import ElementRenderer

logger = logging.getLogger(__name__)


class ComponentRenderer(ElementRenderer):
    """Classe pour le rendu des composants interactifs."""

    def __init__(self, html_generator):
        self.html_generator = html_generator
        self.component_renderers = {
            "Vidéo": self._render_video,
            "Audio": self._render_audio,
            "Accordéon": self._render_accordion,
            "Carrousel": self._render_carousel,
            "Onglets": self._render_tabs,
            "Défilement": self._render_scrollspy,
            "Consignes": self._render_consignes,
        }

    def render(self, element: Dict[str, Any], indent_level: int = 0) -> List[str]:
        """
        Rend un composant en HTML.

        Args:
            element: Données du composant
            indent_level: Niveau d'indentation

        Returns:
            Liste de lignes HTML
        """
        # Si c'est un composant complet avec un type défini
        if element["type"] == "component" and "component_type" in element:
            component_type = element["component_type"]

            # Si le type contient des espaces, extraire juste le type de base
            base_component_type = (
                component_type.split()[0] if " " in component_type else component_type
            )

            renderer = self.component_renderers.get(base_component_type)

            if renderer:
                # Afficher des informations de débogage
                if base_component_type == "Vidéo" and "video_id" in element:
                    logger.debug(
                        "Rendu de composant vidéo avec ID: %s", element["video_id"]
                    )

                if base_component_type == "Consignes":
                    logger.debug("Rendu de composant Consignes")

                return renderer(element, indent_level)

        # Si c'est un marqueur de début de composant
        elif element["type"] == "component_marker" and "component_type" in element:
            component_type = element.get("component_type")

            # Cas spécial pour les Consignes
            if component_type == "Consignes":
                logger.debug("Traitement marqueur de début de Consignes")

                # Simuler un composant Consignes complet
                consignes_component = {
                    "type": "component",
                    "component_type": "Consignes",
                    "content": [],
                }

                # Chercher dans le JSON complet le contenu du composant Consignes
                # en parcourant les éléments après ce marqueur jusqu'au marqueur de fin
                doc_content = self.html_generator._json_data.get("content", [])

                # Trouver notre position dans le contenu
                for i, content_item in enumerate(doc_content):
                    if (
                        content_item["type"] == "component_marker"
                        and content_item.get("component_type") == "Consignes"
                    ):
                        # Collecter tous les éléments jusqu'au marqueur de fin
                        for j in range(i + 1, len(doc_content)):
                            if (
                                doc_content[j]["type"] == "component_end"
                                and doc_content[j].get("component_type") == "Consignes"
                            ):
                                break
                            consignes_component["content"].append(doc_content[j])
                        break

                # Utiliser le renderer de Consignes pour ce composant
                renderer = self.component_renderers.get("Consignes")
                if renderer and consignes_component["content"]:
                    return renderer(consignes_component, indent_level)

            # Pour les autres marqueurs seuls, on ne rend rien (ils seront traités par process_instructions)
            return []

        # Si c'est un marqueur de fin de composant
        elif element["type"] == "component_end" and "component_type" in element:
            # Pour les marqueurs de fin seuls, on ne rend rien
            return []

        # Rendu générique pour les composants non reconnus
        return self._render_generic(element, indent_level)

    def _render_video(
        self, element: Dict[str, Any], indent_level: int = 0
    ) -> List[str]:
        """
        Rend un composant Vidéo en HTML (lecteur Vimeo).

        Args:
            element: Données du composant
            indent_level: Niveau d'indentation

        Returns:
            Liste de lignes HTML pour le lecteur vidéo
        """
        indent = " " * indent_level

        # Déterminer l'ID de la vidéo (valeur par défaut si non spécifiée)
        video_id = "1069341210"  # Vidéo par défaut

        # Essayer différentes façons d'accéder à l'ID de la vidéo
        # 1. D'abord vérifier dans les attributs directs du composant
        if "video_id" in element:
            video_id = element["video_id"]
            logger.debug("Trouvé video_id dans element: %s", video_id)

        # 2. Ensuite vérifier dans les attributs personnalisés
        elif "attributes" in element and isinstance(element["attributes"], dict):
            attributes = element["attributes"]
            if "video_id" in attributes:
                video_id = attributes["video_id"]
                logger.debug("Trouvé video_id dans attributes: %s", video_id)

        # 3. Vérifier si le type du composant contient un ID (pour la rétrocompatibilité)
        elif "component_type" in element and " " in element["component_type"]:
            # Extraire l'ID de la vidéo du type de composant
            component_type = element["component_type"]
            if "video_id=" in component_type:
                # Pattern pour extraire les attributs au format key='value' ou key="value"
                attr_pattern = r'video_id=(["\'])(.*?)\1'
                match = re.search(attr_pattern, component_type)
                if match:
                    video_id = match.group(2)
                    logger.debug("Extrait video_id du type de composant: %s", video_id)

        # Construire la sortie HTML
        return [
            f'{indent}<section class="video-component">',
            f'{indent}  <div class="video-container">',
            f'{indent}    <iframe src="https://player.vimeo.com/video/{video_id}" width="640" height="360" frameborder="0" ',
            f'{indent}      allow="autoplay; fullscreen; picture-in-picture" allowfullscreen></iframe>',
            f"{indent}  </div>",
            f'{indent}  <script src="https://player.vimeo.com/api/player.js"></script>',
            f"{indent}</section>",
        ]

    def _render_audio(self, element: Dict[str, Any], indent_level: int) -> List[str]:
        """
        Rend un composant Audio en HTML.

        Args:
            element: Données du composant
            indent_level: Niveau d'indentation

        Returns:
            Liste de lignes HTML
        """
        indent = " " * indent_level
        element_html = [
            f'{indent}<section class="audio-component">',
            f'{indent}  <div class="card shadow-sm my-4 border-0">',
            f'{indent}    <div class="card-body">',
            f'{indent}      <audio controls class="w-100 mb-3">',
            f'{indent}        <source src="#" type="audio/mpeg">',
            f"{indent}        Votre navigateur ne supporte pas l'élément audio.",
            f"{indent}      </audio>",
        ]

        has_content = False
        # S'assurer que l'élément a du contenu
        if "content" in element and element["content"]:
            for content_elem in element["content"]:
                # Générer le HTML pour l'élément de contenu
                content_html = self.html_generator._generate_element_html(
                    content_elem, indent_level=indent_level + 6
                )

                # S'assurer que le contenu est une liste de chaînes
                if content_html and isinstance(content_html, list):
                    has_content = True
                    # N'ajouter que les éléments valides
                    for item in content_html:
                        if isinstance(item, str):
                            element_html.append(item)

        element_html.append(f"{indent}    </div>")
        element_html.append(f"{indent}  </div>")
        element_html.append(f"{indent}</section>")
        return element_html

    def _render_accordion(
        self, element: Dict[str, Any], indent_level: int
    ) -> List[str]:
        """
        Rend un composant Accordéon en HTML.

        Args:
            element: Données du composant
            indent_level: Niveau d'indentation

        Returns:
            Liste de lignes HTML
        """
        indent = " " * indent_level
        accordion_id = element.get("html_id", f"accordion-{id(element)}")

        # Commencer l'accordéon avec des classes améliorées
        element_html = [
            f'{indent}<section class="accordion-component">',
            f'{indent}  <div class="accordion accordion-flush my-4 shadow-sm border" id="{accordion_id}">',
        ]

        # Parcourir les éléments pour créer les items de l'accordéon
        current_item = None
        item_count = 0
        item_content = []

        # Vérifier que l'élément a du contenu
        if "content" in element and element["content"]:
            for content_elem in element["content"]:
                if content_elem["type"] == "heading":
                    # Si nous avons un item en cours, l'ajouter à l'accordéon
                    if current_item and item_content:
                        item_count += 1
                        element_html.extend(
                            self._create_accordion_item(
                                accordion_id,
                                item_count,
                                current_item,
                                item_content,
                                indent + "  ",
                            )
                        )
                        item_content = []

                    # Commencer un nouvel item avec le titre du heading
                    if "runs" in content_elem:
                        current_item = "".join(self._format_runs(content_elem["runs"]))
                else:
                    # Générer le HTML pour l'élément de contenu
                    content_html = self.html_generator._generate_element_html(
                        content_elem, indent_level=indent_level + 8
                    )

                    # S'assurer que le contenu est une liste de chaînes
                    if content_html and isinstance(content_html, list):
                        item_content.extend(content_html)

            # Ajouter le dernier item s'il existe
            if current_item and item_content:
                item_count += 1
                element_html.extend(
                    self._create_accordion_item(
                        accordion_id,
                        item_count,
                        current_item,
                        item_content,
                        indent + "  ",
                    )
                )

        element_html.append(f"{indent}  </div>")
        element_html.append(f"{indent}</section>")
        return element_html

    def _create_accordion_item(
        self,
        accordion_id: str,
        item_count: int,
        title: str,
        content_items: List[str],
        indent: str,
    ) -> List[str]:
        """
        Crée un élément d'accordéon.

        Args:
            accordion_id: ID de l'accordéon
            item_count: Numéro de l'élément
            title: Titre de l'élément
            content_items: Liste des éléments de contenu
            indent: Indentation

        Returns:
            Liste de lignes HTML
        """
        item_id = f"{accordion_id}-item-{item_count}"

        # S'assurer que tous les éléments de contenu sont des chaînes
        final_content = []
        for item in content_items:
            if isinstance(item, str):
                final_content.append(item)

        return [
            f'{indent}    <div class="accordion-item">',
            f'{indent}      <h2 class="accordion-header" id="heading-{item_id}">',
            f'{indent}        <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapse-{item_id}" aria-expanded="false" aria-controls="collapse-{item_id}">',
            f"{indent}          {title}",
            f"{indent}        </button>",
            f"{indent}      </h2>",
            f'{indent}      <div id="collapse-{item_id}" class="accordion-collapse collapse" aria-labelledby="heading-{item_id}" data-bs-parent="#{accordion_id}">',
            f'{indent}        <div class="accordion-body">',
            *final_content,
            f"{indent}        </div>",
            f"{indent}      </div>",
            f"{indent}    </div>",
        ]

    def _render_tabs(self, element: Dict[str, Any], indent_level: int) -> List[str]:
        """
        Rend un composant Onglets en HTML.

        Args:
            element: Données du composant
            indent_level: Niveau d'indentation

        Returns:
            Liste de lignes HTML
        """
        indent = " " * indent_level
        tabs_id = element.get("html_id", "mainTabs")

        # Commencer les onglets avec des classes améliorées
        element_html = [
            f'{indent}<section class="tabs-component">',
            f'{indent}  <div class="tabs-container card border-0 shadow-sm">',
            f'{indent}    <div class="card-header bg-white">',
            f'{indent}      <ul class="nav nav-tabs card-header-tabs" id="{tabs_id}" role="tablist">',
        ]

        # Collecter les onglets
        tabs = []
        current_tab = None
        tab_content = []

        # S'assurer que l'élément a du contenu
        if "content" in element and element["content"]:
            for content_elem in element["content"]:
                if content_elem["type"] == "heading":
                    if current_tab and tab_content:
                        tabs.append((current_tab, tab_content))
                        tab_content = []

                    if "runs" in content_elem:
                        current_tab = "".join(self._format_runs(content_elem["runs"]))
                else:
                    # Générer le HTML pour l'élément de contenu
                    content_html = self.html_generator._generate_element_html(
                        content_elem, indent_level=indent_level + 6
                    )

                    # S'assurer que le contenu est une liste de chaînes
                    if content_html and isinstance(content_html, list):
                        tab_content.extend(content_html)

            # Ajouter le dernier onglet
            if current_tab and tab_content:
                tabs.append((current_tab, tab_content))

            # Générer les boutons d'onglets
            for i, (title, _) in enumerate(tabs):
                tab_id = f"{tabs_id}-tab-{i}"
                active = " active" if i == 0 else ""
                selected = "true" if i == 0 else "false"
                element_html.append(
                    f'{indent}        <li class="nav-item" role="presentation">',
                )
                element_html.append(
                    f'{indent}          <button class="nav-link{active}" id="{tab_id}" data-bs-toggle="tab" data-bs-target="#{tab_id}-pane" type="button" role="tab" aria-controls="{tab_id}-pane" aria-selected="{selected}">{title}</button>',
                )
                element_html.append(
                    f"{indent}        </li>",
                )

            element_html.append(f"{indent}      </ul>")
            element_html.append(f"{indent}    </div>")
            element_html.append(f'{indent}    <div class="card-body">')
            element_html.append(
                f'{indent}      <div class="tab-content" id="{tabs_id}-content">'
            )

            # Générer le contenu des onglets
            for i, (title, content) in enumerate(tabs):
                tab_id = f"{tabs_id}-tab-{i}"
                active = " show active" if i == 0 else ""

                # Filtrer les éléments invalides
                filtered_content = []
                for item in content:
                    if isinstance(item, str):
                        filtered_content.append(item)

                element_html.extend(
                    [
                        f'{indent}        <div class="tab-pane fade{active}" id="{tab_id}-pane" role="tabpanel" aria-labelledby="{tab_id}" tabindex="0">',
                        f'{indent}          <div class="py-3">',
                        *filtered_content,
                        f"{indent}          </div>",
                        f"{indent}        </div>",
                    ]
                )

        element_html.extend(
            [
                f"{indent}      </div>",
                f"{indent}    </div>",
                f"{indent}  </div>",
                f"{indent}</section>",
            ]
        )

        return element_html

    def _render_carousel(self, element: Dict[str, Any], indent_level: int) -> List[str]:
        """
        Rend un composant Carrousel en HTML.

        Args:
            element: Données du composant
            indent_level: Niveau d'indentation

        Returns:
            Liste de lignes HTML
        """
        indent = " " * indent_level
        carousel_id = element.get("html_id", "mainCarousel")

        logger.debug("Rendu du carrousel: %s", carousel_id)

        # Ajouter des styles CSS pour améliorer l'apparence du carousel
        element_html = [
            f'{indent}<section class="carousel-component">',
            f"{indent}  <style>",
            f"{indent}    #{carousel_id} .carousel-control-prev-icon, #{carousel_id} .carousel-control-next-icon {{",
            f"{indent}      background-color: rgba(0, 0, 0, 0.5);",
            f"{indent}      border-radius: 50%;",
            f"{indent}      padding: 10px;",
            f"{indent}    }}",
            f"{indent}    #{carousel_id} .carousel-indicators button {{",
            f"{indent}      background-color: rgba(0, 0, 0, 0.6);",
            f"{indent}      width: 30px;",
            f"{indent}      height: 3px;",
            f"{indent}      margin-right: 3px;",
            f"{indent}      margin-left: 3px;",
            f"{indent}    }}",
            f"{indent}    #{carousel_id} .carousel-item img {{",
            f"{indent}      max-width: 100%;",
            f"{indent}      height: auto;",
            f"{indent}      margin: 0 auto;",
            f"{indent}      display: block;",
            f"{indent}    }}",
            f"{indent}  </style>",
            f'{indent}  <div id="{carousel_id}" class="carousel slide shadow">',
        ]

        # Vérifier que l'élément a du contenu
        slides = []
        slide_titles = []
        slide_contents = []
        slide_images = []

        if "content" in element and element["content"]:
            current_slide_content = []
            current_slide_title = None
            current_slide_image = None

            # Parcourir les éléments pour extraire les slides
            for content_elem in element["content"]:
                logger.debug("Élément carousel: %s", content_elem.get("type"))

                if content_elem["type"] == "heading":
                    # Si on a déjà un titre pour cette diapositive, c'est une nouvelle diapositive
                    if current_slide_title is not None:
                        slide_titles.append(current_slide_title)
                        slide_contents.append(current_slide_content)
                        slide_images.append(current_slide_image)
                        current_slide_content = []
                        current_slide_image = None

                    # Récupérer le titre de la diapositive
                    if "runs" in content_elem:
                        current_slide_title = "".join(
                            self._format_runs(content_elem["runs"])
                        )

                    # Vérifier si le titre contient une image
                    if "image" in content_elem:
                        current_slide_image = content_elem["image"].get("path", "")
                        logger.debug(
                            "Image trouvée dans heading (image): %s",
                            current_slide_image,
                        )
                    elif "images" in content_elem and content_elem["images"]:
                        current_slide_image = content_elem["images"][0].get("path", "")
                        logger.debug(
                            "Image trouvée dans heading (images): %s",
                            current_slide_image,
                        )

                elif content_elem["type"] == "image":
                    # Stocker l'image pour cette diapositive
                    current_slide_image = content_elem.get("image_path", "")
                    logger.debug("Image trouvée (type=image): %s", current_slide_image)
                elif "image" in content_elem:
                    # Si l'élément a une image directement
                    current_slide_image = content_elem["image"].get("path", "")
                    logger.debug("Image trouvée (attr image): %s", current_slide_image)
                elif "images" in content_elem and content_elem["images"]:
                    # Si l'élément a des images
                    current_slide_image = content_elem["images"][0].get("path", "")
                    logger.debug("Image trouvée (attr images): %s", current_slide_image)
                elif content_elem["type"] == "paragraph":
                    # Générer le HTML pour le paragraphe
                    content_html = self.html_generator._generate_element_html(
                        content_elem, indent_level=0
                    )
                    if content_html:
                        current_slide_content.extend(content_html)

                    # Vérifier si le paragraphe contient une image
                    if not current_slide_image:
                        # Vérifier toutes les façons possibles d'avoir une image
                        if "image" in content_elem:
                            current_slide_image = content_elem["image"].get("path", "")
                            logger.debug(
                                "Image trouvée dans paragraphe (image): %s",
                                current_slide_image,
                            )
                        elif "images" in content_elem and content_elem["images"]:
                            current_slide_image = content_elem["images"][0].get(
                                "path", ""
                            )
                            logger.debug(
                                "Image trouvée dans paragraphe (images): %s",
                                current_slide_image,
                            )
                        elif (
                            "attributes" in content_elem
                            and "images" in content_elem["attributes"]
                        ):
                            # Images stockées dans les attributs
                            images = content_elem["attributes"]["images"]
                            if images and len(images) > 0:
                                current_slide_image = images[0].get("path", "")
                                logger.debug(
                                    "Image trouvée dans attributs: %s",
                                    current_slide_image,
                                )

                        # Vérifier dans les runs s'ils contiennent des images
                        if "runs" in content_elem:
                            for run in content_elem["runs"]:
                                if "image" in run:
                                    current_slide_image = run["image"].get("path", "")
                                    logger.debug(
                                        "Image trouvée dans run: %s",
                                        current_slide_image,
                                    )
                                    break
                else:
                    # Générer le HTML pour l'élément de contenu
                    content_html = self.html_generator._generate_element_html(
                        content_elem, indent_level=0
                    )
                    if content_html:
                        current_slide_content.extend(content_html)

            # Ajouter la dernière diapositive
            if current_slide_title is not None:
                slide_titles.append(current_slide_title)
                slide_contents.append(current_slide_content)
                slide_images.append(current_slide_image)

        # Génération des images depuis le document
        if not slide_images or all(img is None or img == "" for img in slide_images):
            logger.debug("Aucune image n'a été trouvée pour ce carrousel")

        # Générer les indicateurs de diapositive
        element_html.append(f'{indent}  <div class="carousel-indicators">')
        for i in range(len(slide_titles)):
            active = "active" if i == 0 else ""
            element_html.append(
                f'{indent}    <button type="button" data-bs-target="#{carousel_id}" data-bs-slide-to="{i}" class="{active}"></button>'
            )
        element_html.append(f"{indent}  </div>")

        # Générer les diapositives
        element_html.append(f'{indent}  <div class="carousel-inner rounded">')
        for i, (title, content, image) in enumerate(
            zip(slide_titles, slide_contents, slide_images)
        ):
            active = "active" if i == 0 else ""
            element_html.append(f'{indent}    <div class="carousel-item {active}">')
            element_html.append(
                f'{indent}      <div class="carousel-content p-4 bg-light">'
            )
            element_html.append(
                f'{indent}        <h4 class="mb-3 text-primary">{title}</h4>'
            )

            # Ajouter le contenu
            for line in content:
                element_html.append(f"{indent}      {line}")

            # Ajouter l'image si elle existe
            if image:
                logger.debug("Ajout de l'image %s à la diapositive %d", image, i + 1)
                element_html.append(f'{indent}        <div class="text-center mt-3">')
                element_html.append(
                    f'{indent}          <img src="{image}" class="img-fluid rounded" alt="{title}">'
                )
                element_html.append(f"{indent}        </div>")

            element_html.append(f"{indent}      </div>")
            element_html.append(f"{indent}    </div>")
        element_html.append(f"{indent}  </div>")

        # Ajouter les contrôles
        element_html.extend(
            [
                f'{indent}  <button class="carousel-control-prev" type="button" data-bs-target="#{carousel_id}" data-bs-slide="prev">',
                f'{indent}    <span class="carousel-control-prev-icon" aria-hidden="true"></span>',
                f'{indent}    <span class="visually-hidden">Précédent</span>',
                f"{indent}  </button>",
                f'{indent}  <button class="carousel-control-next" type="button" data-bs-target="#{carousel_id}" data-bs-slide="next">',
                f'{indent}    <span class="carousel-control-next-icon" aria-hidden="true"></span>',
                f'{indent}    <span class="visually-hidden">Suivant</span>',
                f"{indent}  </button>",
            ]
        )
        element_html.append(f"{indent}</div>")

        # Ajouter un script pour initialiser manuellement le carousel
        element_html.extend(
            [
                f"{indent}  <script>",
                f"{indent}    document.addEventListener('DOMContentLoaded', function() {{",
                f"{indent}      setTimeout(function() {{",
                f"{indent}        var carousel = document.getElementById('{carousel_id}');",
                f"{indent}        if (carousel) {{",
                f"{indent}          new bootstrap.Carousel(carousel, {{",
                f"{indent}            interval: 5000,",
                f"{indent}            keyboard: true,",
                f"{indent}            pause: 'hover',",
                f"{indent}            wrap: true",
                f"{indent}          }});",
                f"{indent}        }}",
                f"{indent}      }}, 100);",
                f"{indent}    }});",
                f"{indent}  </script>",
                f"{indent}</section>",
            ]
        )

        return element_html

    def _render_scrollspy(
        self, element: Dict[str, Any], indent_level: int
    ) -> List[str]:
        indent = " " * indent_level
        scrollspy_id = f"scrollspy-{id(element)}"
        element_html = [
            f'{indent}<section class="scrollspy-component">',
            f'{indent}  <div class="row my-4">',
            f'{indent}    <div class="col-4">',
            f'{indent}      <nav id="{scrollspy_id}" class="navbar navbar-light bg-light flex-column align-items-stretch p-3">',
            f'{indent}        <nav class="nav nav-pills flex-column">',
        ]

        # Créer les liens de navigation
        nav_items = []
        has_items = False

        for i, content_elem in enumerate(element["content"]):
            if content_elem["type"] == "heading":
                item_id = f"{scrollspy_id}-item-{i}"
                item_title = "".join([run["text"] for run in content_elem["runs"]])

                if item_title.strip():
                    has_items = True
                    active = " active" if i == 0 else ""
                    element_html.append(
                        f'{indent}          <a class="nav-link{active}" href="#{item_id}">{item_title}</a>'
                    )
                    nav_items.append((item_id, content_elem, []))
            elif len(nav_items) > 0:
                # Ajouter au contenu de la dernière section
                content = self.html_generator._generate_element_html(
                    content_elem, indent_level=indent_level + 8
                )
                if content:
                    nav_items[-1][2].extend(content)

        # Ne pas générer de HTML pour les défilements sans éléments
        if not has_items:
            return []

        element_html.extend(
            [
                f"{indent}        </nav>",
                f"{indent}      </nav>",
                f"{indent}    </div>",
                f'{indent}    <div class="col-8">',
                f'{indent}      <div data-bs-spy="scroll" data-bs-target="#{scrollspy_id}" data-bs-offset="0" class="scrollspy-example-2" tabindex="0" style="height: 400px; overflow-y: scroll;">',
            ]
        )

        # Ajouter le contenu des sections
        for item_id, heading, content_elems in nav_items:
            heading_text = " ".join([run["text"] for run in heading["runs"]])
            if heading_text.strip():
                element_html.append(
                    f'{indent}        <h4 id="{item_id}">{heading_text}</h4>'
                )

            if content_elems:
                element_html.extend(content_elems)

        element_html.extend(
            [
                f"{indent}      </div>",
                f"{indent}    </div>",
                f"{indent}  </div>",
                f"{indent}</section>",
            ]
        )

        return element_html

    def _render_generic(self, element: Dict[str, Any], indent_level: int) -> List[str]:
        indent = " " * indent_level
        # Extraire le type de composant du texte du premier run
        component_type = element["runs"][0]["text"].strip("[]")
        element_html = [
            f'{indent}<section class="component-generic">',
            f'{indent}  <div class="component-{component_type.lower()} p-3 my-3 border">',
            f"{indent}    <h3>{component_type}</h3>",
        ]

        has_content = False
        for content_elem in element["content"]:
            content = self.html_generator._generate_element_html(
                content_elem, indent_level=indent_level + 4
            )
            if content:
                has_content = True
                element_html.extend(content)

        # Ne pas générer de HTML pour les composants sans contenu
        if not has_content:
            return []

        element_html.append(f"{indent}  </div>")
        element_html.append(f"{indent}</section>")
        return element_html

    def _render_consignes(
        self, element: Dict[str, Any], indent_level: int
    ) -> List[str]:
        """
        Rend un composant Consignes en HTML.

        Args:
            element: Données du composant
            indent_level: Niveau d'indentation

        Returns:
            Liste de lignes HTML
        """
        indent = " " * indent_level
        element_html = [
            f'{indent}<section class="consignes-component">',
            f'{indent}  <div class="card my-4 border-0 shadow-sm">',
            f'{indent}    <div class="card-body consignes" style="background-color: #fffde7; border-left: 4px solid #fb8c00; font-style: italic; padding: 1rem;">',
        ]

        has_content = False
        # S'assurer que l'élément a du contenu
        if "content" in element and element["content"]:
            for content_elem in element["content"]:
                # Générer le HTML pour l'élément de contenu
                content_html = self.html_generator._generate_element_html(
                    content_elem, indent_level=indent_level + 6
                )

                # S'assurer que le contenu est une liste de chaînes
                if content_html and isinstance(content_html, list):
                    has_content = True
                    # N'ajouter que les éléments valides
                    for item in content_html:
                        if isinstance(item, str):
                            element_html.append(item)

        element_html.append(f"{indent}    </div>")
        element_html.append(f"{indent}  </div>")
        element_html.append(f"{indent}</section>")
        return element_html
