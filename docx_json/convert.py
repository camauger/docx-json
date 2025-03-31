#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module principal pour la conversion de fichiers DOCX en JSON/HTML
"""

import sys
import os
import json
import re
import base64
import logging
from typing import Dict, List, Any, Optional, Union

from docx import Document
from docx.oxml.text.paragraph import CT_P
from docx.oxml.table import CT_Tbl
from docx.table import Table
from docx.text.paragraph import Paragraph


# Configuration du logging
def setup_logging(verbose: bool = False) -> None:
    """Configure le système de logging.

    Args:
        verbose: Si True, affiche les messages de debug
    """
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )


def extract_images(document: Document) -> Dict[str, str]:
    """
    Extrait les images du document .docx et les encode en base64

    Args:
        document: L'objet Document de python-docx

    Returns:
        Un dictionnaire {nom_image: données_base64}
    """
    images = {}
    rels = document.part.rels

    for rel in rels.values():
        if "image" in rel.target_ref:
            # Obtenir le nom de l'image depuis le chemin
            image_name = os.path.basename(rel.target_ref)

            # Récupérer les données binaires
            image_data = rel.target_part.blob

            # Encoder en base64
            encoded_image = base64.b64encode(image_data).decode('utf-8')

            # Stocker dans le dictionnaire
            images[image_name] = encoded_image
            logging.debug(f"Image extraite: {image_name}")

    return images


def get_paragraph_json(paragraph: Paragraph) -> Dict[str, Any]:
    """
    Convertit un paragraphe en structure JSON

    Args:
        paragraph: L'objet Paragraph de python-docx

    Returns:
        Un dictionnaire représentant le paragraphe
    """
    # Déterminer le type (paragraphe normal, titre, etc.)
    para_type = "paragraph"

    style_name = paragraph.style.name if paragraph.style else "Normal"
    level = 0

    # Détecter si c'est un titre (Heading)
    if style_name.startswith("Heading"):
        para_type = "heading"
        level = int(style_name.split(" ")[1]) if len(
            style_name.split(" ")) > 1 else 1

    # Vérifier si c'est un élément de liste
    if paragraph.paragraph_format.left_indent:
        para_type = "list_item"

    # Extraire les runs (morceaux de texte avec style)
    runs = []
    for run in paragraph.runs:
        run_info = {
            "text": run.text,
            "bold": run.bold,
            "italic": run.italic,
            "underline": run.underline
        }
        runs.append(run_info)

    # Vérifier si c'est une instruction intégrée (commençant par ":::")
    text = paragraph.text.strip()
    if text.startswith(":::"):
        return {
            "type": "instruction",
            "content": text[3:].strip()  # Retirer les ":::" du début
        }

    # Structure de base du JSON pour un paragraphe
    para_json = {
        "type": para_type,
        "runs": runs,
    }

    # Ajouter le niveau si c'est un titre
    if para_type == "heading":
        para_json["level"] = level

    return para_json


def get_table_json(table: Table) -> Dict[str, Any]:
    """
    Convertit une table en structure JSON

    Args:
        table: L'objet Table de python-docx

    Returns:
        Un dictionnaire représentant la table
    """
    rows = []
    for row in table.rows:
        cells = []
        for cell in row.cells:
            # Une cellule peut contenir plusieurs paragraphes
            cell_content = []
            for paragraph in cell.paragraphs:
                para_json = get_paragraph_json(paragraph)
                # Ignorer les instructions dans les cellules
                if para_json["type"] != "instruction":
                    cell_content.append(para_json)
            cells.append(cell_content)
        rows.append(cells)

    return {
        "type": "table",
        "rows": rows
    }


def process_instructions(elements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Traite les instructions intégrées et les applique aux éléments suivants

    Args:
        elements: Liste des éléments JSON du document

    Returns:
        Liste des éléments modifiés selon les instructions
    """
    result = []
    current_block = None
    skip_next = False

    # Classes et ID à appliquer au prochain élément
    pending_classes = []
    pending_id = None

    for i, element in enumerate(elements):
        # Si on doit ignorer cet élément (suite à une instruction "ignore")
        if skip_next:
            skip_next = False
            continue

        if element["type"] == "instruction":
            instruction = element["content"].strip()
            logging.debug(f"Traitement de l'instruction: {instruction}")

            # Instruction classe CSS
            if instruction.startswith("class "):
                class_names = instruction[6:].strip()
                pending_classes.extend(class_names.split())

            # Instruction ID
            elif instruction.startswith("id "):
                pending_id = instruction[3:].strip()

            # Instruction ignore
            elif instruction == "ignore":
                skip_next = True

            # Instruction bloc (pour wrapper des éléments)
            elif " start" in instruction:
                block_type = instruction.split()[0]
                current_block = {"type": "block",
                                 "block_type": block_type, "content": []}

            # Fin d'un bloc
            elif " end" in instruction:
                if current_block:
                    result.append(current_block)
                    current_block = None

            # Instruction HTML brut
            elif instruction.startswith("html "):
                html_content = instruction[5:].strip()
                result.append({"type": "raw_html", "content": html_content})

        else:
            # Appliquer les classes et ID en attente
            if pending_classes:
                element["html_class"] = " ".join(pending_classes)
                pending_classes = []

            if pending_id:
                element["html_id"] = pending_id
                pending_id = None

            # Ajouter l'élément au bloc courant ou aux résultats
            if current_block:
                current_block["content"].append(element)
            else:
                result.append(element)

    # Ajouter le dernier bloc s'il existe encore
    if current_block:
        result.append(current_block)
        logging.warning("Un bloc n'a pas été fermé dans le document.")

    return result


def get_document_json(docx_path: str) -> Dict[str, Any]:
    """
    Convertit un document .docx complet en structure JSON

    Args:
        docx_path: Chemin vers le fichier .docx

    Returns:
        Un dictionnaire représentant le document
    """
    logging.info(f"Chargement du document: {docx_path}")
    document = Document(docx_path)

    # Extraire les images
    logging.info("Extraction des images...")
    images = extract_images(document)

    # Extraire le contenu en respectant l'ordre
    logging.info("Extraction du contenu...")
    elements = []
    body = document.element.body

    # Parcourir les éléments du corps du document (paragraphes et tables)
    for child in body.iterchildren():
        if isinstance(child, CT_P):
            paragraph = Paragraph(child, document)
            para_json = get_paragraph_json(paragraph)
            elements.append(para_json)
        elif isinstance(child, CT_Tbl):
            table = Table(child, document)
            table_json = get_table_json(table)
            elements.append(table_json)

    # Traiter les instructions intégrées
    logging.info("Traitement des instructions...")
    processed_elements = process_instructions(elements)

    # Créer la structure JSON complète
    file_name = os.path.basename(docx_path)
    result = {
        "meta": {
            "title": file_name
        },
        "content": processed_elements,
        "images": images
    }

    return result


def generate_html(json_data: Dict[str, Any]) -> str:
    """
    Génère un document HTML à partir de la structure JSON

    Args:
        json_data: Dictionnaire représentant le document

    Returns:
        Une chaîne de caractères contenant le HTML
    """
    logging.info("Génération du HTML...")
    html = ['<!DOCTYPE html>',
            '<html lang="fr">',
            '<head>',
            f'<title>{json_data["meta"]["title"]}</title>',
            '<meta charset="UTF-8">',
            '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
            '</head>',
            '<body>']

    # Fonction récursive pour générer le HTML des éléments
    def generate_element_html(element: Dict[str, Any]) -> List[str]:
        element_html = []

        if element["type"] == "paragraph":
            attrs = []
            if "html_class" in element:
                attrs.append(f'class="{element["html_class"]}"')
            if "html_id" in element:
                attrs.append(f'id="{element["html_id"]}"')

            attrs_str = " ".join(attrs)
            attrs_str = f" {attrs_str}" if attrs_str else ""

            element_html.append(f'<p{attrs_str}>')
            for run in element["runs"]:
                text = run["text"]
                if run["bold"]:
                    text = f'<strong>{text}</strong>'
                if run["italic"]:
                    text = f'<em>{text}</em>'
                if run["underline"]:
                    text = f'<u>{text}</u>'
                element_html.append(text)
            element_html.append('</p>')

        elif element["type"] == "heading":
            attrs = []
            if "html_class" in element:
                attrs.append(f'class="{element["html_class"]}"')
            if "html_id" in element:
                attrs.append(f'id="{element["html_id"]}"')

            attrs_str = " ".join(attrs)
            attrs_str = f" {attrs_str}" if attrs_str else ""

            level = element["level"]
            element_html.append(f'<h{level}{attrs_str}>')
            for run in element["runs"]:
                text = run["text"]
                if run["bold"]:
                    text = f'<strong>{text}</strong>'
                if run["italic"]:
                    text = f'<em>{text}</em>'
                if run["underline"]:
                    text = f'<u>{text}</u>'
                element_html.append(text)
            element_html.append(f'</h{level}>')

        elif element["type"] == "list_item":
            # Note: ceci est simplifié et ne gère pas les listes imbriquées correctement
            element_html.append('<li>')
            for run in element["runs"]:
                text = run["text"]
                if run["bold"]:
                    text = f'<strong>{text}</strong>'
                if run["italic"]:
                    text = f'<em>{text}</em>'
                if run["underline"]:
                    text = f'<u>{text}</u>'
                element_html.append(text)
            element_html.append('</li>')

        elif element["type"] == "table":
            element_html.append('<table>')
            for row in element["rows"]:
                element_html.append('<tr>')
                for cell in row:
                    element_html.append('<td>')
                    for para in cell:
                        element_html.extend(generate_element_html(para))
                    element_html.append('</td>')
                element_html.append('</tr>')
            element_html.append('</table>')

        elif element["type"] == "raw_html":
            element_html.append(element["content"])

        elif element["type"] == "block":
            block_type = element["block_type"]
            if block_type == "quote":
                element_html.append('<blockquote>')
                for content_elem in element["content"]:
                    element_html.extend(generate_element_html(content_elem))
                element_html.append('</blockquote>')
            elif block_type == "aside":
                element_html.append('<aside>')
                for content_elem in element["content"]:
                    element_html.extend(generate_element_html(content_elem))
                element_html.append('</aside>')
            # Ajoutez d'autres types de blocs au besoin

        return element_html

    # Générer le HTML pour chaque élément
    for element in json_data["content"]:
        html.extend(generate_element_html(element))

    # Ajouter les images à la fin
    for img_name, img_data in json_data["images"].items():
        img_tag = f'<img src="data:image/png;base64,{img_data}" alt="{img_name}" />'
        html.append(img_tag)

    html.append('</body>')
    html.append('</html>')

    return '\n'.join(html)


def parse_args() -> Dict[str, Any]:
    """
    Parse les arguments de la ligne de commande

    Returns:
        Un dictionnaire contenant les options
    """
    args = {
        "docx_path": None,
        "generate_json": False,
        "generate_html": False,
        "verbose": False
    }

    if len(sys.argv) < 2 or "--help" in sys.argv or "-h" in sys.argv:
        print(
            "Usage: python convert.py <fichier.docx> [--json] [--html] [--verbose]")
        print("\nOptions:")
        print("  --json     Génère un fichier JSON")
        print("  --html     Génère un fichier HTML")
        print("  --verbose  Affiche des messages de debug")
        print("\nExemple:")
        print("  python convert.py mon-document.docx --json --html")
        sys.exit(0 if "--help" in sys.argv or "-h" in sys.argv else 1)

    # Le premier argument est le chemin du fichier
    args["docx_path"] = sys.argv[1]

    # Options
    args["generate_json"] = "--json" in sys.argv
    args["generate_html"] = "--html" in sys.argv
    args["verbose"] = "--verbose" in sys.argv

    return args


def main() -> None:
    """
    Fonction principale: traite les arguments de ligne de commande et
    effectue la conversion
    """
    # Traiter les arguments
    args = parse_args()

    # Configurer le logging
    setup_logging(args["verbose"])

    docx_path = args["docx_path"]
    generate_json = args["generate_json"]
    generate_html_output = args["generate_html"]

    # Vérifier que le fichier existe et a l'extension .docx
    if not os.path.exists(docx_path):
        logging.error(f"Le fichier '{docx_path}' n'existe pas.")
        print(f"Erreur: Le fichier '{docx_path}' n'existe pas.")
        sys.exit(1)

    if not docx_path.lower().endswith(".docx"):
        logging.error(f"Le fichier '{docx_path}' n'est pas un fichier .docx.")
        print(f"Erreur: Le fichier '{docx_path}' n'est pas un fichier .docx.")
        sys.exit(1)

    # Noms des fichiers de sortie
    base_name = os.path.splitext(docx_path)[0]
    json_path = f"{base_name}.json"
    html_path = f"{base_name}.html"

    try:
        # Convertir le document en JSON
        logging.info(f"Traitement du fichier '{docx_path}'...")
        print(f"Traitement du fichier '{docx_path}'...")
        json_data = get_document_json(docx_path)

        # Générer et sauvegarder le JSON si demandé
        if generate_json or not generate_html_output:  # Par défaut, génère le JSON si aucune option n'est spécifiée
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, ensure_ascii=False, indent=2)
            logging.info(f"Fichier JSON créé: '{json_path}'")
            print(f"Fichier JSON créé: '{json_path}'")

        # Générer et sauvegarder le HTML si demandé
        if generate_html_output:
            html_content = generate_html(json_data)
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            logging.info(f"Fichier HTML créé: '{html_path}'")
            print(f"Fichier HTML créé: '{html_path}'")

        logging.info("Conversion terminée avec succès!")
        print("Conversion terminée avec succès!")

    except Exception as e:
        logging.exception("Erreur lors de la conversion")
        print(f"Erreur lors de la conversion: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
