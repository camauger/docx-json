#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module pour la génération de Markdown à partir de la structure JSON
------------------------------------------------------------------
"""

from typing import Any, Dict, List


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

    def generate(self) -> str:
        """
        Génère le document Markdown complet.

        Returns:
            Une chaîne de caractères contenant le Markdown
        """
        markdown = []

        # Titre du document
        title = self._json_data["meta"]["title"]
        markdown.append(f"# {title}\n")

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
            element_md.append(f"{'#' * level} {''.join(line)}")

            # Ajouter les attributs HTML comme commentaires
            attrs = []
            if "html_class" in element:
                attrs.append(f'class="{element["html_class"]}"')
            if "html_id" in element:
                attrs.append(f'id="{element["html_id"]}"')
            if attrs:
                element_md.append(f"<!-- {' '.join(attrs)} -->")

        elif element["type"] == "list_item":
            # Note: ceci ne gère pas les listes imbriquées correctement
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

            # On utilise des tirets par défaut (Markdown supporte *, +, -)
            element_md.append(f"- {''.join(line)}")

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
                # Pour les autres types de blocs, utiliser une balise HTML avec commentaire
                element_md.append(f'<div class="{block_type}">')

                for content_elem in element["content"]:
                    lines = self._generate_element_markdown(content_elem)
                    element_md.extend(lines)

                element_md.append("</div>")

        elif element["type"] == "component":
            component_type = element["component_type"]

            # En Markdown, nous utilisons la syntaxe de bloc personnalisée de fenced divs
            element_md.append(f":::{component_type}")

            for content_elem in element["content"]:
                lines = self._generate_element_markdown(content_elem)
                element_md.extend(lines)

            element_md.append(":::")

        elif element["type"] == "image" and "image_path" in element:
            img_path = element["image_path"]
            img_alt = element.get("alt_text", "Image")
            element_md.append(f"![{img_alt}]({img_path})")

        return element_md
