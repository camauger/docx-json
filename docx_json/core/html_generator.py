#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module pour la génération de HTML à partir de la structure JSON
--------------------------------------------------------------
"""

from typing import Any, Dict, List, Optional


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
            f'<title>{self._json_data["meta"]["title"]}</title>',
            '<meta charset="UTF-8">',
            '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
        ]

        # Utiliser le CSS personnalisé s'il est fourni, sinon Bootstrap
        if custom_css:
            html.append(f"<style>{custom_css}</style>")
        else:
            html.append(
                '<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" crossorigin="anonymous">'
            )

        html.append("</head>")
        html.append("<body>")
        html.append('<div class="container">')

        # Générer le HTML pour chaque élément
        for element in self._json_data["content"]:
            html.extend(self._generate_element_html(element))

        # Fin du document HTML
        html.append("</div>")  # Fermer le container

        # N'inclure le script Bootstrap que si on utilise Bootstrap (pas de CSS personnalisé)
        if not custom_css:
            html.append(
                '<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-YvpcrYf0tY3lHB60NNkmXc5s9fDVZLESaAA55NDzOxhy9GkcIdslK1eN7N6jIeHz" crossorigin="anonymous"></script>'
            )

        html.append("</body>")
        html.append("</html>")

        return "\n".join(html)

    def _generate_element_html(self, element: Dict[str, Any]) -> List[str]:
        """
        Génère le HTML pour un élément spécifique.

        Args:
            element: Dictionnaire représentant l'élément

        Returns:
            Liste de chaînes de caractères HTML
        """
        element_html = []

        if element["type"] == "paragraph":
            attrs = []
            if "html_class" in element:
                attrs.append(f'class="{element["html_class"]}"')
            if "html_id" in element:
                attrs.append(f'id="{element["html_id"]}"')

            attrs_str = " ".join(attrs)
            attrs_str = f" {attrs_str}" if attrs_str else ""

            element_html.append(f"<p{attrs_str}>")
            for run in element["runs"]:
                text = run["text"]
                if run["bold"]:
                    text = f"<strong>{text}</strong>"
                if run["italic"]:
                    text = f"<em>{text}</em>"
                if run["underline"]:
                    text = f"<u>{text}</u>"
                element_html.append(text)
            element_html.append("</p>")

        elif element["type"] == "heading":
            attrs = []
            if "html_class" in element:
                attrs.append(f'class="{element["html_class"]}"')
            if "html_id" in element:
                attrs.append(f'id="{element["html_id"]}"')

            attrs_str = " ".join(attrs)
            attrs_str = f" {attrs_str}" if attrs_str else ""

            level = element["level"]
            element_html.append(f"<h{level}{attrs_str}>")
            for run in element["runs"]:
                text = run["text"]
                if run["bold"]:
                    text = f"<strong>{text}</strong>"
                if run["italic"]:
                    text = f"<em>{text}</em>"
                if run["underline"]:
                    text = f"<u>{text}</u>"
                element_html.append(text)
            element_html.append(f"</h{level}>")

        elif element["type"] == "list_item":
            # Note: ceci est simplifié et ne gère pas les listes imbriquées correctement
            element_html.append("<li>")
            for run in element["runs"]:
                text = run["text"]
                if run["bold"]:
                    text = f"<strong>{text}</strong>"
                if run["italic"]:
                    text = f"<em>{text}</em>"
                if run["underline"]:
                    text = f"<u>{text}</u>"
                element_html.append(text)
            element_html.append("</li>")

        elif element["type"] == "table":
            element_html.append('<table class="table table-bordered">')
            for row in element["rows"]:
                element_html.append("<tr>")
                for cell in row:
                    element_html.append("<td>")
                    for para in cell:
                        element_html.extend(self._generate_element_html(para))
                    element_html.append("</td>")
                element_html.append("</tr>")
            element_html.append("</table>")

        elif element["type"] == "raw_html":
            element_html.append(element["content"])

        elif element["type"] == "block":
            block_type = element["block_type"]
            if block_type == "quote":
                element_html.append('<blockquote class="blockquote">')
                for content_elem in element["content"]:
                    element_html.extend(self._generate_element_html(content_elem))
                element_html.append("</blockquote>")
            elif block_type == "aside":
                element_html.append('<aside class="border p-3 my-3">')
                for content_elem in element["content"]:
                    element_html.extend(self._generate_element_html(content_elem))
                element_html.append("</aside>")
            # Ajoutez d'autres types de blocs au besoin

        elif element["type"] == "component":
            component_type = element["component_type"]

            if component_type == "Vidéo":
                # Template pour une vidéo (exemple)
                element_html.append('<div class="ratio ratio-16x9 my-4">')
                element_html.append(
                    '  <iframe src="https://www.youtube.com/embed/dQw4w9WgXcQ" title="Video" allowfullscreen></iframe>'
                )
                element_html.append("</div>")
                element_html.append('<div class="mt-2 mb-4">')
                for content_elem in element["content"]:
                    element_html.extend(self._generate_element_html(content_elem))
                element_html.append("</div>")

            elif component_type == "Audio":
                # Template pour audio
                element_html.append('<div class="my-4">')
                element_html.append('  <audio controls class="w-100">')
                element_html.append('    <source src="#" type="audio/mpeg">')
                element_html.append(
                    "    Votre navigateur ne supporte pas l'élément audio."
                )
                element_html.append("  </audio>")
                element_html.append("</div>")
                element_html.append('<div class="mt-2 mb-4">')
                for content_elem in element["content"]:
                    element_html.extend(self._generate_element_html(content_elem))
                element_html.append("</div>")

            elif component_type == "Accordéon":
                # Template pour accordéon
                accordion_id = f"accordion-{id(element)}"
                element_html.append(f'<div class="accordion my-4" id="{accordion_id}">')

                # Parcourir le contenu pour créer les éléments d'accordéon
                item_count = 0
                title = "Accordéon"
                content_html = []

                for content_elem in element["content"]:
                    if content_elem["type"] == "heading":
                        # Si on a déjà un titre et du contenu, créer un item d'accordéon
                        if item_count > 0 and content_html:
                            item_id = f"{accordion_id}-item-{item_count}"
                            element_html.append(f'  <div class="accordion-item">')
                            element_html.append(
                                f'    <h2 class="accordion-header" id="heading-{item_id}">'
                            )
                            element_html.append(
                                f'      <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapse-{item_id}" aria-expanded="false" aria-controls="collapse-{item_id}">'
                            )
                            element_html.append(f"        {title}")
                            element_html.append(f"      </button>")
                            element_html.append(f"    </h2>")
                            element_html.append(
                                f'    <div id="collapse-{item_id}" class="accordion-collapse collapse" aria-labelledby="heading-{item_id}" data-bs-parent="#{accordion_id}">'
                            )
                            element_html.append(f'      <div class="accordion-body">')
                            element_html.extend(content_html)
                            element_html.append(f"      </div>")
                            element_html.append(f"    </div>")
                            element_html.append(f"  </div>")

                            # Réinitialiser
                            content_html = []

                        # Nouveau titre d'accordéon
                        title = "".join([run["text"] for run in content_elem["runs"]])
                        item_count += 1
                    else:
                        # Ajouter au contenu en cours
                        content_html.extend(self._generate_element_html(content_elem))

                # Ajouter le dernier item s'il existe
                if item_count > 0 and content_html:
                    item_id = f"{accordion_id}-item-{item_count}"
                    element_html.append(f'  <div class="accordion-item">')
                    element_html.append(
                        f'    <h2 class="accordion-header" id="heading-{item_id}">'
                    )
                    element_html.append(
                        f'      <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapse-{item_id}" aria-expanded="false" aria-controls="collapse-{item_id}">'
                    )
                    element_html.append(f"        {title}")
                    element_html.append(f"      </button>")
                    element_html.append(f"    </h2>")
                    element_html.append(
                        f'    <div id="collapse-{item_id}" class="accordion-collapse collapse" aria-labelledby="heading-{item_id}" data-bs-parent="#{accordion_id}">'
                    )
                    element_html.append(f'      <div class="accordion-body">')
                    element_html.extend(content_html)
                    element_html.append(f"      </div>")
                    element_html.append(f"    </div>")
                    element_html.append(f"  </div>")

                element_html.append("</div>")

            elif component_type == "Carrousel":
                # Template pour carrousel
                carousel_id = f"carousel-{id(element)}"
                element_html.append(
                    f'<div id="{carousel_id}" class="carousel slide my-4" data-bs-ride="carousel">'
                )
                element_html.append('  <div class="carousel-inner">')

                # Ajouter les éléments du carrousel
                for i, content_elem in enumerate(element["content"]):
                    active = " active" if i == 0 else ""
                    element_html.append(f'    <div class="carousel-item{active}">')
                    element_html.extend(self._generate_element_html(content_elem))
                    element_html.append("    </div>")

                element_html.append("  </div>")
                element_html.append(
                    f'  <button class="carousel-control-prev" type="button" data-bs-target="#{carousel_id}" data-bs-slide="prev">'
                )
                element_html.append(
                    '    <span class="carousel-control-prev-icon" aria-hidden="true"></span>'
                )
                element_html.append(
                    '    <span class="visually-hidden">Précédent</span>'
                )
                element_html.append("  </button>")
                element_html.append(
                    f'  <button class="carousel-control-next" type="button" data-bs-target="#{carousel_id}" data-bs-slide="next">'
                )
                element_html.append(
                    '    <span class="carousel-control-next-icon" aria-hidden="true"></span>'
                )
                element_html.append('    <span class="visually-hidden">Suivant</span>')
                element_html.append("  </button>")
                element_html.append("</div>")

            elif component_type == "Onglets":
                # Template pour onglets
                tabs_id = f"tabs-{id(element)}"
                element_html.append('<div class="my-4">')
                element_html.append('  <ul class="nav nav-tabs" role="tablist">')

                # Créer les onglets
                tab_contents = []
                for i, content_elem in enumerate(element["content"]):
                    if content_elem["type"] == "heading":
                        tab_id = f"{tabs_id}-tab-{i}"
                        active = " active" if i == 0 else ""
                        selected = "true" if i == 0 else "false"

                        # Le titre de l'onglet
                        tab_title = "".join(
                            [run["text"] for run in content_elem["runs"]]
                        )
                        element_html.append(
                            f'    <li class="nav-item" role="presentation">'
                        )
                        element_html.append(
                            f'      <button class="nav-link{active}" id="{tab_id}-button" data-bs-toggle="tab" data-bs-target="#{tab_id}" type="button" role="tab" aria-controls="{tab_id}" aria-selected="{selected}">{tab_title}</button>'
                        )
                        element_html.append("    </li>")

                        # Préparer le contenu de l'onglet (à ajouter plus tard)
                        tab_contents.append((tab_id, active, []))
                    elif len(tab_contents) > 0:
                        # Ajouter au contenu du dernier onglet
                        tab_contents[-1][2].extend(
                            self._generate_element_html(content_elem)
                        )

                element_html.append("  </ul>")
                element_html.append('  <div class="tab-content">')

                # Ajouter le contenu des onglets
                for tab_id, active, content in tab_contents:
                    element_html.append(
                        f'    <div class="tab-pane fade show{active}" id="{tab_id}" role="tabpanel" aria-labelledby="{tab_id}-button">'
                    )
                    element_html.extend(content)
                    element_html.append("    </div>")

                element_html.append("  </div>")
                element_html.append("</div>")

            elif component_type == "Défilement":
                # Template pour scrollspy
                scrollspy_id = f"scrollspy-{id(element)}"
                element_html.append('<div class="row my-4">')
                element_html.append('  <div class="col-4">')
                element_html.append(
                    f'    <nav id="{scrollspy_id}" class="navbar navbar-light bg-light flex-column align-items-stretch p-3">'
                )
                element_html.append('      <nav class="nav nav-pills flex-column">')

                # Créer les liens de navigation
                nav_items = []
                for i, content_elem in enumerate(element["content"]):
                    if content_elem["type"] == "heading":
                        item_id = f"{scrollspy_id}-item-{i}"
                        item_title = "".join(
                            [run["text"] for run in content_elem["runs"]]
                        )
                        active = " active" if i == 0 else ""

                        element_html.append(
                            f'        <a class="nav-link{active}" href="#{item_id}">{item_title}</a>'
                        )
                        nav_items.append((item_id, content_elem, []))
                    elif len(nav_items) > 0:
                        # Ajouter au contenu de la dernière section
                        nav_items[-1][2].append(content_elem)

                element_html.append("      </nav>")
                element_html.append("    </nav>")
                element_html.append("  </div>")

                element_html.append('  <div class="col-8">')
                element_html.append(
                    f'    <div data-bs-spy="scroll" data-bs-target="#{scrollspy_id}" data-bs-offset="0" class="scrollspy-example-2" tabindex="0" style="height: 400px; overflow-y: scroll;">'
                )

                # Ajouter le contenu des sections
                for item_id, heading, content_elems in nav_items:
                    element_html.append(
                        f'      <h4 id="{item_id}">{" ".join([run["text"] for run in heading["runs"]])}</h4>'
                    )
                    for content_elem in content_elems:
                        element_html.extend(self._generate_element_html(content_elem))

                element_html.append("    </div>")
                element_html.append("  </div>")
                element_html.append("</div>")

            else:
                # Pour les autres types de composants, juste englober dans un div
                element_html.append(
                    f'<div class="component-{component_type.lower()} p-3 my-3 border">'
                )
                element_html.append(f"<h3>{component_type}</h3>")
                for content_elem in element["content"]:
                    element_html.extend(self._generate_element_html(content_elem))
                element_html.append("</div>")

        # Vérifier si l'élément a une référence d'image associée
        elif element["type"] == "image" and "image_path" in element:
            img_path = element["image_path"]
            img_alt = element.get("alt_text", "Image")
            element_html.append(
                f'<img src="{img_path}" alt="{img_alt}" class="img-fluid my-3" />'
            )

        return element_html
