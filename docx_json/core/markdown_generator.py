#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module pour la génération de Markdown à partir de la structure JSON
------------------------------------------------------------------
"""

import datetime
from typing import Any, Dict, List, Optional, Tuple


class MarkdownGenerator:
    """
    Classe pour générer du Markdown à partir de la structure JSON.
    """

    def __init__(self, json_data: Dict[str, Any]):
        """
        Initialise le générateur Markdown.

        Args:
            json_data: Dictionnaire représentant le document
        """
        self._json_data = json_data
        self._images = json_data["images"]
        self._list_stack = []  # Pour suivre les listes imbriquées
        self._component_level = 0  # Pour suivre l'imbrication des composants

    def generate(self) -> str:
        """
        Génère le document Markdown complet.

        Returns:
            Une chaîne de caractères contenant le Markdown
        """
        markdown = []

        # Ajout d'un frontmatter YAML
        markdown.append("---")
        markdown.append(f"title: {self._json_data['meta']['title']}")
        markdown.append("author: Généré automatiquement")
        markdown.append("date: " + datetime.datetime.now().strftime("%Y-%m-%d"))
        markdown.append("---")
        markdown.append("")  # Ligne vide après les métadonnées

        # Générer le Markdown pour chaque élément
        for element in self._json_data["content"]:
            markdown.extend(self._generate_element_markdown(element))
            # Ajouter une ligne vide entre les éléments
            markdown.append("")

        return "\n".join(markdown)

    def _generate_element_markdown(self, element: Dict[str, Any]) -> List[str]:
        """
        Génère le Markdown pour un élément spécifique.

        Args:
            element: Dictionnaire représentant l'élément

        Returns:
            Liste de chaînes de caractères Markdown
        """
        element_md = []

        if element["type"] == "paragraph":
            line = []
            for run in element["runs"]:
                text = run["text"]
                # Appliquer les styles
                if run["bold"]:
                    text = f"**{text}**"
                if run["italic"]:
                    text = f"*{text}*"
                if run["underline"]:
                    text = (
                        f"<u>{text}</u>"  # Markdown pur ne supporte pas le soulignement
                    )
                line.append(text)
            element_md.append("".join(line))

            # Ajouter les attributs HTML comme commentaires
            attrs = []
            if "html_class" in element:
                attrs.append(f'class="{element["html_class"]}"')
            if "html_id" in element:
                attrs.append(f'id="{element["html_id"]}"')
            if attrs:
                element_md.append(f"<!-- {' '.join(attrs)} -->")

        elif element["type"] == "heading":
            level = element["level"]
            line = []
            for run in element["runs"]:
                text = run["text"]
                # Appliquer les styles
                if run["bold"]:
                    text = f"**{text}**"
                if run["italic"]:
                    text = f"*{text}*"
                if run["underline"]:
                    text = f"<u>{text}</u>"
                line.append(text)

            heading_text = "".join(line)

            # Utiliser des styles de titres plus visuels pour les niveaux 1 et 2
            if level == 1:
                element_md.append(heading_text)
                element_md.append("=" * len(heading_text))
            elif level == 2:
                element_md.append(heading_text)
                element_md.append("-" * len(heading_text))
            else:
                # Pour les niveaux 3+, utiliser la notation #
                element_md.append(f"{'#' * level} {heading_text}")

            # Ajouter les attributs HTML comme commentaires
            attrs = []
            if "html_class" in element:
                attrs.append(f'class="{element["html_class"]}"')
            if "html_id" in element:
                attrs.append(f'id="{element["html_id"]}"')
            if attrs:
                element_md.append(f"<!-- {' '.join(attrs)} -->")

        elif element["type"] == "list_item":
            # Déterminer le niveau d'imbrication et le type de liste
            list_level = self._determine_list_level(element)
            list_marker = self._get_list_marker(element, list_level)

            line = []
            for run in element["runs"]:
                text = run["text"]
                # Appliquer les styles
                if run["bold"]:
                    text = f"**{text}**"
                if run["italic"]:
                    text = f"*{text}*"
                if run["underline"]:
                    text = f"<u>{text}</u>"
                line.append(text)

            # Indentation en fonction du niveau d'imbrication
            indent = "  " * list_level
            element_md.append(f"{indent}{list_marker} {''.join(line)}")

        elif element["type"] == "table":
            # Créer l'en-tête de tableau si la première ligne existe
            if element["rows"]:
                # Créer le tableau - première ligne comme en-tête
                header_cells = []
                for cell in element["rows"][0]:
                    # Extraire le texte des paragraphes dans la cellule
                    cell_text = []
                    for para in cell:
                        for run in para.get("runs", []):
                            cell_text.append(run["text"])
                    header_cells.append(" ".join(cell_text).strip())

                element_md.append("| " + " | ".join(header_cells) + " |")

                # Ligne de séparation après l'en-tête
                element_md.append("| " + " | ".join(["---"] * len(header_cells)) + " |")

                # Ajouter les autres lignes du tableau
                for row in element["rows"][1:]:
                    row_cells = []
                    for cell in row:
                        # Extraire le texte des paragraphes dans la cellule
                        cell_text = []
                        for para in cell:
                            for run in para.get("runs", []):
                                cell_text.append(run["text"])
                        row_cells.append(" ".join(cell_text).strip())

                    element_md.append("| " + " | ".join(row_cells) + " |")

        elif element["type"] == "raw_html":
            # Encapsuler le HTML brut dans un bloc de code Markdown
            element_md.append(f"```html\n{element['content']}\n```")

        elif element["type"] == "block":
            block_type = element["block_type"]
            if block_type == "quote":
                # Citations en Markdown
                for content_elem in element["content"]:
                    lines = self._generate_element_markdown(content_elem)
                    # Préfixer chaque ligne avec >
                    for line in lines:
                        element_md.append(f"> {line}")

            else:
                # Pour les autres types de blocs, utiliser une syntaxe plus expressive
                element_md.append(f"::: {block_type}")

                for content_elem in element["content"]:
                    lines = self._generate_element_markdown(content_elem)
                    element_md.extend(lines)

                element_md.append(":::")

        elif element["type"] == "component":
            component_type = element["component_type"]

            # Augmenter le niveau d'imbrication
            self._component_level += 1

            # En Markdown, nous utilisons la syntaxe de bloc personnalisée de fenced divs
            element_md.append(f":::{component_type}")

            for content_elem in element["content"]:
                lines = self._generate_element_markdown(content_elem)
                element_md.extend(lines)

            element_md.append(":::")

            # Diminuer le niveau d'imbrication
            self._component_level -= 1

        elif element["type"] == "image" and "image_path" in element:
            img_path = element["image_path"]
            img_alt = element.get("alt_text", "Image")

            # Ajouter une légende si disponible
            caption = element.get("caption", "")
            if caption:
                element_md.append(f"![{img_alt}]({img_path})\n*{caption}*")
            else:
                element_md.append(f"![{img_alt}]({img_path})")

        return element_md

    def _determine_list_level(self, element: Dict[str, Any]) -> int:
        """
        Détermine le niveau d'imbrication d'un élément de liste.

        Args:
            element: L'élément de liste à analyser

        Returns:
            Le niveau d'imbrication (0 pour le premier niveau)
        """
        # Dans une implémentation réelle, on pourrait utiliser des attributs dans l'élément
        # pour déterminer le niveau d'imbrication. Ici, on retourne 0 par défaut.
        return element.get("list_level", 0)

    def _get_list_marker(self, element: Dict[str, Any], level: int) -> str:
        """
        Retourne le marqueur approprié pour un élément de liste.

        Args:
            element: L'élément de liste
            level: Le niveau d'imbrication

        Returns:
            Le marqueur de liste (-, *, +, 1., etc.)
        """
        list_type = element.get("list_type", "unordered")

        if list_type == "ordered":
            return "1."
        else:
            # Alterner les marqueurs selon le niveau d'imbrication
            markers = ["-", "*", "+"]
            return markers[level % len(markers)]
