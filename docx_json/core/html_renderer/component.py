"""
Module contenant le renderer pour les composants interactifs.
"""

from typing import Any, Dict, List

from .base import ElementRenderer


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
        }

    def render(self, element: Dict[str, Any], indent_level: int = 0) -> List[str]:
        component_type = element["component_type"]
        renderer = self.component_renderers.get(component_type)

        if renderer:
            return renderer(element, indent_level)
        else:
            return self._render_generic(element, indent_level)

    def _render_video(self, element: Dict[str, Any], indent_level: int) -> List[str]:
        indent = " " * indent_level
        element_html = [
            f'{indent}<div class="ratio ratio-16x9 my-4">',
            f'{indent}  <iframe src="https://www.youtube.com/embed/dQw4w9WgXcQ" title="Video" allowfullscreen></iframe>',
            f"{indent}</div>",
            f'{indent}<div class="mt-2 mb-4">',
        ]

        has_content = False
        for content_elem in element["content"]:
            content = self.html_generator._generate_element_html(
                content_elem, indent_level=indent_level + 2
            )
            if content:
                has_content = True
                element_html.extend(content)

        element_html.append(f"{indent}</div>")
        return element_html

    def _render_audio(self, element: Dict[str, Any], indent_level: int) -> List[str]:
        indent = " " * indent_level
        element_html = [
            f'{indent}<div class="my-4">',
            f'{indent}  <audio controls class="w-100">',
            f'{indent}    <source src="#" type="audio/mpeg">',
            f"{indent}    Votre navigateur ne supporte pas l'élément audio.",
            f"{indent}  </audio>",
            f"{indent}</div>",
            f'{indent}<div class="mt-2 mb-4">',
        ]

        has_content = False
        for content_elem in element["content"]:
            content = self.html_generator._generate_element_html(
                content_elem, indent_level=indent_level + 2
            )
            if content:
                has_content = True
                element_html.extend(content)

        element_html.append(f"{indent}</div>")
        return element_html

    def _render_accordion(
        self, element: Dict[str, Any], indent_level: int
    ) -> List[str]:
        indent = " " * indent_level
        accordion_id = f"accordion-{id(element)}"
        element_html = [f'{indent}<div class="accordion my-4" id="{accordion_id}">']

        # Parcourir le contenu pour créer les éléments d'accordéon
        item_count = 0
        title = "Accordéon"
        content_items = []

        for content_elem in element["content"]:
            if content_elem["type"] == "heading":
                # Si on a déjà un titre et du contenu, créer un item d'accordéon
                if item_count > 0 and content_items:
                    element_html.extend(
                        self._create_accordion_item(
                            accordion_id, item_count, title, content_items, indent
                        )
                    )
                    # Réinitialiser
                    content_items = []

                # Nouveau titre d'accordéon
                title = "".join([run["text"] for run in content_elem["runs"]])
                item_count += 1
            else:
                # Ajouter au contenu en cours
                content = self.html_generator._generate_element_html(
                    content_elem, indent_level=indent_level + 8
                )
                if content:
                    content_items.append(content)

        # Ajouter le dernier item s'il existe
        if item_count > 0 and content_items:
            element_html.extend(
                self._create_accordion_item(
                    accordion_id, item_count, title, content_items, indent
                )
            )

        element_html.append(f"{indent}</div>")
        return element_html

    def _create_accordion_item(
        self,
        accordion_id: str,
        item_count: int,
        title: str,
        content_items: List,
        indent: str,
    ) -> List[str]:
        item_id = f"{accordion_id}-item-{item_count}"
        return [
            f'{indent}  <div class="accordion-item">',
            f'{indent}    <h2 class="accordion-header" id="heading-{item_id}">',
            f'{indent}      <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapse-{item_id}" aria-expanded="false" aria-controls="collapse-{item_id}">',
            f"{indent}        {title}",
            f"{indent}      </button>",
            f"{indent}    </h2>",
            f'{indent}    <div id="collapse-{item_id}" class="accordion-collapse collapse" aria-labelledby="heading-{item_id}" data-bs-parent="#{accordion_id}">',
            f'{indent}      <div class="accordion-body">',
            *[item for sublist in content_items for item in sublist],
            f"{indent}      </div>",
            f"{indent}    </div>",
            f"{indent}  </div>",
        ]

    def _render_carousel(self, element: Dict[str, Any], indent_level: int) -> List[str]:
        indent = " " * indent_level
        carousel_id = f"carousel-{id(element)}"
        element_html = [
            f'{indent}<div id="{carousel_id}" class="carousel slide my-4" data-bs-ride="carousel">',
            f'{indent}  <div class="carousel-inner">',
        ]

        # Vérifier si le carrousel a du contenu
        has_slides = False

        # Ajouter les éléments du carrousel
        for i, content_elem in enumerate(element["content"]):
            active = " active" if i == 0 else ""
            slide_content = self.html_generator._generate_element_html(
                content_elem, indent_level=indent_level + 6
            )

            if slide_content:
                has_slides = True
                element_html.append(f'{indent}    <div class="carousel-item{active}">')
                element_html.extend(slide_content)
                element_html.append(f"{indent}    </div>")

        # Ne pas générer de HTML pour les carrousels sans diapositives
        if not has_slides:
            return []

        # Compléter avec les contrôles
        element_html.extend(
            [
                f"{indent}  </div>",
                f'{indent}  <button class="carousel-control-prev" type="button" data-bs-target="#{carousel_id}" data-bs-slide="prev">',
                f'{indent}    <span class="carousel-control-prev-icon" aria-hidden="true"></span>',
                f'{indent}    <span class="visually-hidden">Précédent</span>',
                f"{indent}  </button>",
                f'{indent}  <button class="carousel-control-next" type="button" data-bs-target="#{carousel_id}" data-bs-slide="next">',
                f'{indent}    <span class="carousel-control-next-icon" aria-hidden="true"></span>',
                f'{indent}    <span class="visually-hidden">Suivant</span>',
                f"{indent}  </button>",
                f"{indent}</div>",
            ]
        )

        return element_html

    def _render_tabs(self, element: Dict[str, Any], indent_level: int) -> List[str]:
        indent = " " * indent_level
        tabs_id = f"tabs-{id(element)}"
        element_html = [
            f'{indent}<div class="my-4">',
            f'{indent}  <ul class="nav nav-tabs" role="tablist">',
        ]

        # Créer les onglets
        tab_contents = []
        has_tabs = False

        for i, content_elem in enumerate(element["content"]):
            if content_elem["type"] == "heading":
                tab_id = f"{tabs_id}-tab-{i}"
                active = " active" if i == 0 else ""
                selected = "true" if i == 0 else "false"

                # Le titre de l'onglet (s'assurer qu'il n'est pas vide)
                tab_title = "".join([run["text"] for run in content_elem["runs"]])
                if tab_title.strip():
                    has_tabs = True
                    element_html.extend(
                        [
                            f'{indent}    <li class="nav-item" role="presentation">',
                            f'{indent}      <button class="nav-link{active}" id="{tab_id}-button" data-bs-toggle="tab" data-bs-target="#{tab_id}" type="button" role="tab" aria-controls="{tab_id}" aria-selected="{selected}">{tab_title}</button>',
                            f"{indent}    </li>",
                        ]
                    )

                    # Préparer le contenu de l'onglet
                    tab_contents.append((tab_id, active, []))
            elif len(tab_contents) > 0:
                # Ajouter au contenu du dernier onglet
                content = self.html_generator._generate_element_html(
                    content_elem, indent_level=indent_level + 6
                )
                if content:
                    tab_contents[-1][2].extend(content)

        # Ne pas générer de HTML pour les onglets sans titres
        if not has_tabs:
            return []

        element_html.append(f"{indent}  </ul>")
        element_html.append(f'{indent}  <div class="tab-content">')

        # Ajouter le contenu des onglets
        for tab_id, active, content in tab_contents:
            if content:  # N'ajouter que s'il y a du contenu réel
                element_html.append(
                    f'{indent}    <div class="tab-pane fade show{active}" id="{tab_id}" role="tabpanel" aria-labelledby="{tab_id}-button">'
                )
                element_html.extend(content)
                element_html.append(f"{indent}    </div>")

        element_html.append(f"{indent}  </div>")
        element_html.append(f"{indent}</div>")

        return element_html

    def _render_scrollspy(
        self, element: Dict[str, Any], indent_level: int
    ) -> List[str]:
        indent = " " * indent_level
        scrollspy_id = f"scrollspy-{id(element)}"
        element_html = [
            f'{indent}<div class="row my-4">',
            f'{indent}  <div class="col-4">',
            f'{indent}    <nav id="{scrollspy_id}" class="navbar navbar-light bg-light flex-column align-items-stretch p-3">',
            f'{indent}      <nav class="nav nav-pills flex-column">',
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
                        f'{indent}        <a class="nav-link{active}" href="#{item_id}">{item_title}</a>'
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
                f"{indent}      </nav>",
                f"{indent}    </nav>",
                f"{indent}  </div>",
                f'{indent}  <div class="col-8">',
                f'{indent}    <div data-bs-spy="scroll" data-bs-target="#{scrollspy_id}" data-bs-offset="0" class="scrollspy-example-2" tabindex="0" style="height: 400px; overflow-y: scroll;">',
            ]
        )

        # Ajouter le contenu des sections
        for item_id, heading, content_elems in nav_items:
            heading_text = " ".join([run["text"] for run in heading["runs"]])
            if heading_text.strip():
                element_html.append(
                    f'{indent}      <h4 id="{item_id}">{heading_text}</h4>'
                )

            if content_elems:
                element_html.extend(content_elems)

        element_html.extend(
            [f"{indent}    </div>", f"{indent}  </div>", f"{indent}</div>"]
        )

        return element_html

    def _render_generic(self, element: Dict[str, Any], indent_level: int) -> List[str]:
        indent = " " * indent_level
        component_type = element["component_type"]
        element_html = [
            f'{indent}<div class="component-{component_type.lower()} p-3 my-3 border">',
            f"{indent}  <h3>{component_type}</h3>",
        ]

        has_content = False
        for content_elem in element["content"]:
            content = self.html_generator._generate_element_html(
                content_elem, indent_level=indent_level + 2
            )
            if content:
                has_content = True
                element_html.extend(content)

        # Ne pas générer de HTML pour les composants sans contenu
        if not has_content:
            return []

        element_html.append(f"{indent}</div>")
        return element_html
