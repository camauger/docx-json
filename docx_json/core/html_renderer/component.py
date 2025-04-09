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
            renderer = self.component_renderers.get(component_type)

            if renderer:
                return renderer(element, indent_level)

        # Si c'est un marqueur de début de composant
        elif element["type"] == "component_marker" and "component_type" in element:
            # Pour les marqueurs seuls, on ne rend rien (ils seront traités par process_instructions)
            return []

        # Si c'est un marqueur de fin de composant
        elif element["type"] == "component_end" and "component_type" in element:
            # Pour les marqueurs de fin seuls, on ne rend rien
            return []

        # Rendu générique pour les composants non reconnus
        return self._render_generic(element, indent_level)

    def _render_video(self, element: Dict[str, Any], indent_level: int) -> List[str]:
        """
        Rend un composant Vidéo en HTML.

        Args:
            element: Données du composant
            indent_level: Niveau d'indentation

        Returns:
            Liste de lignes HTML
        """
        indent = " " * indent_level
        element_html = [
            f'{indent}<div class="ratio ratio-16x9 my-4">',
            f'{indent}  <iframe src="https://www.youtube.com/embed/dQw4w9WgXcQ" title="Video" allowfullscreen></iframe>',
            f"{indent}</div>",
            f'{indent}<div class="mt-2 mb-4">',
        ]

        has_content = False
        # S'assurer que l'élément a du contenu
        if "content" in element and element["content"]:
            for content_elem in element["content"]:
                # Générer le HTML pour l'élément de contenu
                content_html = self.html_generator._generate_element_html(
                    content_elem, indent_level=indent_level + 2
                )

                # S'assurer que le contenu est une liste de chaînes
                if content_html and isinstance(content_html, list):
                    has_content = True
                    # N'ajouter que les éléments valides
                    for item in content_html:
                        if isinstance(item, str):
                            element_html.append(item)

        element_html.append(f"{indent}</div>")
        return element_html

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
            f'{indent}<div class="my-4">',
            f'{indent}  <audio controls class="w-100">',
            f'{indent}    <source src="#" type="audio/mpeg">',
            f"{indent}    Votre navigateur ne supporte pas l'élément audio.",
            f"{indent}  </audio>",
            f"{indent}</div>",
            f'{indent}<div class="mt-2 mb-4">',
        ]

        has_content = False
        # S'assurer que l'élément a du contenu
        if "content" in element and element["content"]:
            for content_elem in element["content"]:
                # Générer le HTML pour l'élément de contenu
                content_html = self.html_generator._generate_element_html(
                    content_elem, indent_level=indent_level + 2
                )

                # S'assurer que le contenu est une liste de chaînes
                if content_html and isinstance(content_html, list):
                    has_content = True
                    # N'ajouter que les éléments valides
                    for item in content_html:
                        if isinstance(item, str):
                            element_html.append(item)

        element_html.append(f"{indent}</div>")
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

        # Commencer l'accordéon
        element_html = [
            f'{indent}<div class="accordion my-4" id="{accordion_id}">',
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
                                indent,
                            )
                        )
                        item_content = []

                    # Commencer un nouvel item avec le titre du heading
                    if "runs" in content_elem:
                        current_item = "".join(self._format_runs(content_elem["runs"]))
                else:
                    # Générer le HTML pour l'élément de contenu
                    content_html = self.html_generator._generate_element_html(
                        content_elem, indent_level=indent_level + 6
                    )

                    # S'assurer que le contenu est une liste de chaînes
                    if content_html and isinstance(content_html, list):
                        item_content.extend(content_html)

            # Ajouter le dernier item s'il existe
            if current_item and item_content:
                item_count += 1
                element_html.extend(
                    self._create_accordion_item(
                        accordion_id, item_count, current_item, item_content, indent
                    )
                )

        element_html.append(f"{indent}</div>")
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
            f'{indent}  <div class="accordion-item">',
            f'{indent}    <h2 class="accordion-header" id="heading-{item_id}">',
            f'{indent}      <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapse-{item_id}" aria-expanded="false" aria-controls="collapse-{item_id}">',
            f"{indent}        {title}",
            f"{indent}      </button>",
            f"{indent}    </h2>",
            f'{indent}    <div id="collapse-{item_id}" class="accordion-collapse collapse" aria-labelledby="heading-{item_id}" data-bs-parent="#{accordion_id}">',
            f'{indent}      <div class="accordion-body">',
            *final_content,
            f"{indent}      </div>",
            f"{indent}    </div>",
            f"{indent}  </div>",
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

        # Commencer les onglets
        element_html = [
            f'{indent}<div class="tabs-container">',
            f'{indent}  <ul class="nav nav-tabs" id="{tabs_id}" role="tablist">',
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
                    f'{indent}    <li class="nav-item" role="presentation">',
                )
                element_html.append(
                    f'{indent}      <button class="nav-link{active}" id="{tab_id}" data-bs-toggle="tab" data-bs-target="#{tab_id}-pane" type="button" role="tab" aria-controls="{tab_id}-pane" aria-selected="{selected}">{title}</button>',
                )
                element_html.append(
                    f"{indent}    </li>",
                )

            element_html.append(f"{indent}  </ul>")
            element_html.append(
                f'{indent}  <div class="tab-content" id="{tabs_id}-content">'
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
                        f'{indent}    <div class="tab-pane fade{active}" id="{tab_id}-pane" role="tabpanel" aria-labelledby="{tab_id}" tabindex="0">',
                        f'{indent}      <div class="p-4">',
                        *filtered_content,
                        f"{indent}      </div>",
                        f"{indent}    </div>",
                    ]
                )

        element_html.extend([f"{indent}  </div>", f"{indent}</div>"])

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

        # Commencer le carrousel
        element_html = [
            f'{indent}<div id="{carousel_id}" class="carousel slide" data-bs-ride="carousel">',
        ]

        # Collecter les diapositives
        slides = []
        current_slide = None
        slide_content = []

        # S'assurer que l'élément a du contenu
        if "content" in element and element["content"]:
            for content_elem in element["content"]:
                if content_elem["type"] == "heading":
                    if current_slide and slide_content:
                        slides.append((current_slide, slide_content))
                        slide_content = []

                    if "runs" in content_elem:
                        current_slide = "".join(self._format_runs(content_elem["runs"]))
                else:
                    # Générer le HTML pour l'élément de contenu
                    content_html = self.html_generator._generate_element_html(
                        content_elem, indent_level=indent_level + 6
                    )

                    # S'assurer que le contenu est une liste de chaînes
                    if content_html and isinstance(content_html, list):
                        slide_content.extend(content_html)

            # Ajouter la dernière diapositive
            if current_slide and slide_content:
                slides.append((current_slide, slide_content))

            # Générer les indicateurs
            element_html.append(f'{indent}  <div class="carousel-indicators">')
            for i, (title, _) in enumerate(slides):
                active = " active" if i == 0 else ""
                element_html.append(
                    f'{indent}    <button type="button" data-bs-target="#{carousel_id}" data-bs-slide-to="{i}"{active} aria-label="{title}"></button>'
                )
            element_html.append(f"{indent}  </div>")

            # Générer le contenu du carrousel
            element_html.append(f'{indent}  <div class="carousel-inner">')
            for i, (title, content) in enumerate(slides):
                active = " active" if i == 0 else ""

                # Filtrer les éléments invalides
                filtered_content = []
                for item in content:
                    if isinstance(item, str):
                        filtered_content.append(item)

                element_html.extend(
                    [
                        f'{indent}    <div class="carousel-item{active}">',
                        f'{indent}      <div class="carousel-content p-4">',
                        f"{indent}        <h4>{title}</h4>",
                        *filtered_content,
                        f"{indent}      </div>",
                        f"{indent}    </div>",
                    ]
                )
            element_html.append(f"{indent}  </div>")

            # Ajouter les contrôles de navigation
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
        # Extraire le type de composant du texte du premier run
        component_type = element["runs"][0]["text"].strip("[]")
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
