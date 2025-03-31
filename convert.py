#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
DOCX to JSON/HTML Converter
---------------------------
Un script Python en ligne de commande pour convertir des fichiers .docx en
fichiers .json structurés ou .html sémantiques.
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


def extract_images(document: Document, output_dir: str, save_to_disk: bool = True) -> Dict[str, str]:
    """
    Extrait les images du document .docx et les sauvegarde dans un dossier ou les encode en base64

    Args:
        document: L'objet Document de python-docx
        output_dir: Répertoire de sortie pour les fichiers générés
        save_to_disk: Si True, sauvegarde les images sur disque. Sinon, encode en base64.

    Returns:
        Un dictionnaire {nom_image: chemin_relatif} ou {nom_image: donnees_base64}
    """
    images = {}
    rels = document.part.rels

    # Si on sauvegarde sur disque, créer le dossier images
    if save_to_disk:
        images_dir = os.path.join(output_dir, 'images')
        if not os.path.exists(images_dir):
            os.makedirs(images_dir)
            logging.info(f"Dossier images créé: {images_dir}")

    for rel in rels.values():
        if "image" in rel.target_ref:
            try:
                # Obtenir le nom de l'image depuis le chemin
                image_name = os.path.basename(rel.target_ref)

                # Vérifier si c'est une image externe
                if rel.is_external:
                    logging.warning(f"Image externe ignorée: {rel.target_ref}")
                    continue

                # Récupérer les données binaires
                image_data = rel.target_part.blob

                if save_to_disk:
                    # Chemin de sortie pour l'image
                    image_path = os.path.join(images_dir, image_name)

                    # Sauvegarder l'image
                    with open(image_path, 'wb') as f:
                        f.write(image_data)

                    # Stocker le chemin relatif dans le dictionnaire
                    images[image_name] = f'images/{image_name}'
                    logging.debug(
                        f"Image extraite et sauvegardée: {image_path}")
                else:
                    # Encoder en base64
                    encoded_image = base64.b64encode(
                        image_data).decode('utf-8')
                    # Stocker dans le dictionnaire
                    images[image_name] = encoded_image
                    logging.debug(
                        f"Image extraite et encodée en base64: {image_name}")

            except Exception as e:
                logging.warning(
                    f"Impossible d'extraire l'image {rel.target_ref}: {str(e)}")

    return images


def get_paragraph_json(paragraph: Paragraph) -> Dict[str, Any]:
    """
    Convertit un paragraphe en structure JSON

    Args:
        paragraph: L'objet Paragraph de python-docx

    Returns:
        Un dictionnaire représentant le paragraphe
    """
    # Vérifier si le paragraphe contient une image
    for run in paragraph.runs:
        if hasattr(run, '_element'):
            # Recherche de l'élément inline (indiquant une image)
            inline_elem = None

            # Essayer différentes approches pour trouver les éléments d'image
            try:
                # Méthode 1: Recherche directe avec le préfixe wp (si disponible)
                if 'wp' in run._element.nsmap:
                    inline_elem = run._element.find(
                        './/wp:inline', namespaces=run._element.nsmap)
            except Exception:
                logging.debug(
                    "Impossible de trouver wp:inline avec les espaces de noms disponibles")

            # Si pas trouvé, essayer d'autres méthodes
            if inline_elem is None:
                try:
                    # Méthode 2: Recherche pour n'importe quel élément inline sans préfixe spécifique
                    for child in run._element.iter():
                        if child.tag.endswith('inline'):
                            inline_elem = child
                            break
                except Exception:
                    logging.debug(
                        "Impossible de rechercher un élément 'inline' générique")

            # Si on a trouvé une image
            if inline_elem is not None:
                # Essayer de trouver l'attribut rId
                rId = None
                try:
                    # Rechercher l'élément blip et son attribut r:embed
                    for child in inline_elem.iter():
                        if child.tag.endswith('blip'):
                            # Chercher tous les attributs qui pourraient contenir l'ID de relation
                            for attrib_name, value in child.attrib.items():
                                if attrib_name.endswith('embed'):
                                    rId = value
                                    break
                            if rId:
                                break
                except Exception as e:
                    logging.debug(
                        f"Impossible de récupérer l'ID de relation: {str(e)}")

                # Créer l'élément image
                image_json = {
                    "type": "image",
                    "alt_text": paragraph.text.strip() or "Image"
                }

                # Ajouter l'ID de relation s'il a été trouvé
                if rId:
                    image_json["rId"] = rId

                return image_json

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

    # Vérifier si c'est un marqueur de composant pédagogique
    component_types = ["Vidéo", "Audio", "Accordéon",
                       "Carrousel", "Onglets", "Défilement"]
    if text.startswith("[") and any(text.startswith(f"[{comp}") for comp in component_types):
        component_type = text[1:].split("]")[0] if "]" in text else "Unknown"
        return {
            "type": "component_marker",
            "component_type": component_type
        }

    # Vérifier si c'est un marqueur de fin de composant
    if text.startswith("[Fin ") and "]" in text:
        component_type = text[5:].split("]")[0]
        return {
            "type": "component_end",
            "component_type": component_type
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
    current_component = None
    skip_next = False

    # Classes et ID à appliquer au prochain élément
    pending_classes = []
    pending_id = None

    i = 0
    while i < len(elements):
        element = elements[i]

        # Si on doit ignorer cet élément (suite à une instruction "ignore")
        if skip_next:
            skip_next = False
            i += 1
            continue

        # Traitement des instructions spéciales :::
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

        # Traitement des marqueurs de composants pédagogiques
        elif element["type"] == "component_marker":
            component_type = element["component_type"]
            logging.debug(f"Début de composant: {component_type}")

            current_component = {
                "type": "component",
                "component_type": component_type,
                "content": []
            }

            # Rechercher le contenu du composant jusqu'à [Fin] ou un autre composant
            j = i + 1
            while j < len(elements):
                next_element = elements[j]

                # Si on trouve un marqueur de fin pour ce composant
                if next_element.get("type") == "component_end" and next_element.get("component_type") == component_type:
                    i = j  # On avance jusqu'à la fin du composant
                    break
                # Si on trouve un autre marqueur de composant, on s'arrête aussi
                elif next_element.get("type") == "component_marker":
                    i = j - 1  # On s'arrête juste avant le nouveau composant
                    break
                # Sinon, on ajoute l'élément au contenu du composant
                else:
                    current_component["content"].append(next_element)
                j += 1

            # Ajouter le composant au résultat
            result.append(current_component)
            current_component = None

        # Traitement des marqueurs de fin (sans marqueur de début correspondant)
        elif element["type"] == "component_end":
            logging.warning(
                f"Marqueur de fin '{element['component_type']}' sans marqueur de début correspondant")

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
            elif current_component:
                current_component["content"].append(element)
            else:
                result.append(element)

        i += 1

    # Ajouter le dernier bloc s'il existe encore
    if current_block:
        result.append(current_block)
        logging.warning("Un bloc n'a pas été fermé dans le document.")

    return result


def get_document_json(docx_path: str, output_dir: str, save_images_to_disk: bool = True) -> Dict[str, Any]:
    """
    Convertit un document .docx complet en structure JSON

    Args:
        docx_path: Chemin vers le fichier .docx
        output_dir: Répertoire de sortie pour les fichiers générés
        save_images_to_disk: Si True, sauvegarde les images sur disque. Sinon, encode en base64.

    Returns:
        Un dictionnaire représentant le document
    """
    logging.info(f"Chargement du document: {docx_path}")
    document = Document(docx_path)

    # Extraire les images
    logging.info("Extraction des images...")
    images = extract_images(document, output_dir, save_images_to_disk)

    # Créer un dictionnaire des relations pour associer les rId aux chemins d'images
    rels_dict = {}
    for rel in document.part.rels.values():
        if "image" in rel.target_ref:
            try:
                image_name = os.path.basename(rel.target_ref)
                if image_name in images:
                    if save_images_to_disk:
                        rels_dict[rel.rId] = images[image_name]
                    else:
                        # Pour les images en base64
                        rels_dict[rel.rId] = f"data:image/png;base64,{images[image_name]}"
            except Exception as e:
                logging.warning(
                    f"Impossible de traiter la relation {rel.rId}: {str(e)}")

    # Extraire le contenu en respectant l'ordre
    logging.info("Extraction du contenu...")
    elements = []
    body = document.element.body

    # Parcourir les éléments du corps du document (paragraphes et tables)
    for child in body.iterchildren():
        if isinstance(child, CT_P):
            paragraph = Paragraph(child, document)
            para_json = get_paragraph_json(paragraph)

            # Si c'est une image, ajouter le chemin d'image
            if para_json["type"] == "image" and "rId" in para_json:
                rId = para_json["rId"]
                if rId in rels_dict:
                    para_json["image_path"] = rels_dict[rId]
                # Supprimer l'attribut rId car il n'est plus nécessaire
                del para_json["rId"]

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
            '<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" crossorigin="anonymous">',
            '</head>',
            '<body>',
            '<div class="container">']

    # Images disponibles dans le document
    images = json_data["images"]

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
            element_html.append('<table class="table table-bordered">')
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
                element_html.append('<blockquote class="blockquote">')
                for content_elem in element["content"]:
                    element_html.extend(generate_element_html(content_elem))
                element_html.append('</blockquote>')
            elif block_type == "aside":
                element_html.append('<aside class="border p-3 my-3">')
                for content_elem in element["content"]:
                    element_html.extend(generate_element_html(content_elem))
                element_html.append('</aside>')
            # Ajoutez d'autres types de blocs au besoin

        elif element["type"] == "component":
            component_type = element["component_type"]

            if component_type == "Vidéo":
                # Template pour une vidéo (exemple)
                element_html.append('<div class="ratio ratio-16x9 my-4">')
                element_html.append(
                    '  <iframe src="https://www.youtube.com/embed/dQw4w9WgXcQ" title="Video" allowfullscreen></iframe>')
                element_html.append('</div>')
                element_html.append('<div class="mt-2 mb-4">')
                for content_elem in element["content"]:
                    element_html.extend(generate_element_html(content_elem))
                element_html.append('</div>')

            elif component_type == "Audio":
                # Template pour audio
                element_html.append('<div class="my-4">')
                element_html.append('  <audio controls class="w-100">')
                element_html.append('    <source src="#" type="audio/mpeg">')
                element_html.append(
                    '    Votre navigateur ne supporte pas l\'élément audio.')
                element_html.append('  </audio>')
                element_html.append('</div>')
                element_html.append('<div class="mt-2 mb-4">')
                for content_elem in element["content"]:
                    element_html.extend(generate_element_html(content_elem))
                element_html.append('</div>')

            elif component_type == "Accordéon":
                # Template pour accordéon
                accordion_id = f"accordion-{id(element)}"
                element_html.append(
                    f'<div class="accordion my-4" id="{accordion_id}">')

                # Parcourir le contenu pour créer les éléments d'accordéon
                item_count = 0
                title = "Accordéon"
                content_html = []

                for content_elem in element["content"]:
                    if content_elem["type"] == "heading":
                        # Si on a déjà un titre et du contenu, créer un item d'accordéon
                        if item_count > 0 and content_html:
                            item_id = f"{accordion_id}-item-{item_count}"
                            element_html.append(
                                f'  <div class="accordion-item">')
                            element_html.append(
                                f'    <h2 class="accordion-header" id="heading-{item_id}">')
                            element_html.append(
                                f'      <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapse-{item_id}" aria-expanded="false" aria-controls="collapse-{item_id}">')
                            element_html.append(f'        {title}')
                            element_html.append(f'      </button>')
                            element_html.append(f'    </h2>')
                            element_html.append(
                                f'    <div id="collapse-{item_id}" class="accordion-collapse collapse" aria-labelledby="heading-{item_id}" data-bs-parent="#{accordion_id}">')
                            element_html.append(
                                f'      <div class="accordion-body">')
                            element_html.extend(content_html)
                            element_html.append(f'      </div>')
                            element_html.append(f'    </div>')
                            element_html.append(f'  </div>')

                            # Réinitialiser
                            content_html = []

                        # Nouveau titre d'accordéon
                        title = "".join([run["text"]
                                        for run in content_elem["runs"]])
                        item_count += 1
                    else:
                        # Ajouter au contenu en cours
                        content_html.extend(
                            generate_element_html(content_elem))

                # Ajouter le dernier item s'il existe
                if item_count > 0 and content_html:
                    item_id = f"{accordion_id}-item-{item_count}"
                    element_html.append(f'  <div class="accordion-item">')
                    element_html.append(
                        f'    <h2 class="accordion-header" id="heading-{item_id}">')
                    element_html.append(
                        f'      <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapse-{item_id}" aria-expanded="false" aria-controls="collapse-{item_id}">')
                    element_html.append(f'        {title}')
                    element_html.append(f'      </button>')
                    element_html.append(f'    </h2>')
                    element_html.append(
                        f'    <div id="collapse-{item_id}" class="accordion-collapse collapse" aria-labelledby="heading-{item_id}" data-bs-parent="#{accordion_id}">')
                    element_html.append(f'      <div class="accordion-body">')
                    element_html.extend(content_html)
                    element_html.append(f'      </div>')
                    element_html.append(f'    </div>')
                    element_html.append(f'  </div>')

                element_html.append('</div>')

            elif component_type == "Carrousel":
                # Template pour carrousel
                carousel_id = f"carousel-{id(element)}"
                element_html.append(
                    f'<div id="{carousel_id}" class="carousel slide my-4" data-bs-ride="carousel">')
                element_html.append('  <div class="carousel-inner">')

                # Ajouter les éléments du carrousel
                for i, content_elem in enumerate(element["content"]):
                    active = " active" if i == 0 else ""
                    element_html.append(
                        f'    <div class="carousel-item{active}">')
                    element_html.extend(generate_element_html(content_elem))
                    element_html.append('    </div>')

                element_html.append('  </div>')
                element_html.append(
                    f'  <button class="carousel-control-prev" type="button" data-bs-target="#{carousel_id}" data-bs-slide="prev">')
                element_html.append(
                    '    <span class="carousel-control-prev-icon" aria-hidden="true"></span>')
                element_html.append(
                    '    <span class="visually-hidden">Précédent</span>')
                element_html.append('  </button>')
                element_html.append(
                    f'  <button class="carousel-control-next" type="button" data-bs-target="#{carousel_id}" data-bs-slide="next">')
                element_html.append(
                    '    <span class="carousel-control-next-icon" aria-hidden="true"></span>')
                element_html.append(
                    '    <span class="visually-hidden">Suivant</span>')
                element_html.append('  </button>')
                element_html.append('</div>')

            elif component_type == "Onglets":
                # Template pour onglets
                tabs_id = f"tabs-{id(element)}"
                element_html.append('<div class="my-4">')
                element_html.append(
                    '  <ul class="nav nav-tabs" role="tablist">')

                # Créer les onglets
                tab_contents = []
                for i, content_elem in enumerate(element["content"]):
                    if content_elem["type"] == "heading":
                        tab_id = f"{tabs_id}-tab-{i}"
                        active = " active" if i == 0 else ""
                        selected = "true" if i == 0 else "false"

                        # Le titre de l'onglet
                        tab_title = "".join([run["text"]
                                            for run in content_elem["runs"]])
                        element_html.append(
                            f'    <li class="nav-item" role="presentation">')
                        element_html.append(
                            f'      <button class="nav-link{active}" id="{tab_id}-button" data-bs-toggle="tab" data-bs-target="#{tab_id}" type="button" role="tab" aria-controls="{tab_id}" aria-selected="{selected}">{tab_title}</button>')
                        element_html.append('    </li>')

                        # Préparer le contenu de l'onglet (à ajouter plus tard)
                        tab_contents.append((tab_id, active, []))
                    elif len(tab_contents) > 0:
                        # Ajouter au contenu du dernier onglet
                        tab_contents[-1][2].extend(
                            generate_element_html(content_elem))

                element_html.append('  </ul>')
                element_html.append('  <div class="tab-content">')

                # Ajouter le contenu des onglets
                for tab_id, active, content in tab_contents:
                    element_html.append(
                        f'    <div class="tab-pane fade show{active}" id="{tab_id}" role="tabpanel" aria-labelledby="{tab_id}-button">')
                    element_html.extend(content)
                    element_html.append('    </div>')

                element_html.append('  </div>')
                element_html.append('</div>')

            elif component_type == "Défilement":
                # Template pour scrollspy
                scrollspy_id = f"scrollspy-{id(element)}"
                element_html.append('<div class="row my-4">')
                element_html.append('  <div class="col-4">')
                element_html.append(
                    f'    <nav id="{scrollspy_id}" class="navbar navbar-light bg-light flex-column align-items-stretch p-3">')
                element_html.append(
                    '      <nav class="nav nav-pills flex-column">')

                # Créer les liens de navigation
                nav_items = []
                for i, content_elem in enumerate(element["content"]):
                    if content_elem["type"] == "heading":
                        item_id = f"{scrollspy_id}-item-{i}"
                        item_title = "".join([run["text"]
                                             for run in content_elem["runs"]])
                        active = " active" if i == 0 else ""

                        element_html.append(
                            f'        <a class="nav-link{active}" href="#{item_id}">{item_title}</a>')
                        nav_items.append((item_id, content_elem, []))
                    elif len(nav_items) > 0:
                        # Ajouter au contenu de la dernière section
                        nav_items[-1][2].append(content_elem)

                element_html.append('      </nav>')
                element_html.append('    </nav>')
                element_html.append('  </div>')

                element_html.append('  <div class="col-8">')
                element_html.append(
                    f'    <div data-bs-spy="scroll" data-bs-target="#{scrollspy_id}" data-bs-offset="0" class="scrollspy-example-2" tabindex="0" style="height: 400px; overflow-y: scroll;">')

                # Ajouter le contenu des sections
                for item_id, heading, content_elems in nav_items:
                    element_html.append(
                        f'      <h4 id="{item_id}">{" ".join([run["text"] for run in heading["runs"]])}</h4>')
                    for content_elem in content_elems:
                        element_html.extend(
                            generate_element_html(content_elem))

                element_html.append('    </div>')
                element_html.append('  </div>')
                element_html.append('</div>')

            else:
                # Pour les autres types de composants, juste englober dans un div
                element_html.append(
                    f'<div class="component-{component_type.lower()} p-3 my-3 border">')
                element_html.append(f'<h3>{component_type}</h3>')
                for content_elem in element["content"]:
                    element_html.extend(generate_element_html(content_elem))
                element_html.append('</div>')

        # Vérifier si l'élément a une référence d'image associée
        elif element["type"] == "image" and "image_path" in element:
            img_path = element["image_path"]
            img_alt = element.get("alt_text", "Image")
            element_html.append(
                f'<img src="{img_path}" alt="{img_alt}" class="img-fluid my-3" />')

        return element_html

    # Générer le HTML pour chaque élément
    for element in json_data["content"]:
        html.extend(generate_element_html(element))

    # Fin du document HTML
    html.append('</div>')  # Fermer le container
    html.append('<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-YvpcrYf0tY3lHB60NNkmXc5s9fDVZLESaAA55NDzOxhy9GkcIdslK1eN7N6jIeHz" crossorigin="anonymous"></script>')
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
        "save_images": True,  # Par défaut, les images sont sauvegardées
        "verbose": False
    }

    if len(sys.argv) < 2 or "--help" in sys.argv or "-h" in sys.argv:
        print(
            "Usage: python convert.py <fichier.docx> [--json] [--html] [--no-save-images] [--verbose]")
        print("\nOptions:")
        print("  --json            Génère un fichier JSON")
        print("  --html            Génère un fichier HTML")
        print(
            "  --no-save-images  Ne sauvegarde pas les images (utilise base64 à la place)")
        print("  --verbose         Affiche des messages de debug")
        print("\nExemple:")
        print("  python convert.py mon-document.docx --json --html")
        sys.exit(0 if "--help" in sys.argv or "-h" in sys.argv else 1)

    # Le premier argument est le chemin du fichier
    args["docx_path"] = sys.argv[1]

    # Options
    args["generate_json"] = "--json" in sys.argv
    args["generate_html"] = "--html" in sys.argv
    args["save_images"] = "--no-save-images" not in sys.argv
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
    save_images = args["save_images"]

    # Vérifier que le fichier existe et a l'extension .docx
    if not os.path.exists(docx_path):
        logging.error(f"Le fichier '{docx_path}' n'existe pas.")
        print(f"Erreur: Le fichier '{docx_path}' n'existe pas.")
        sys.exit(1)

    if not docx_path.lower().endswith(".docx"):
        logging.error(f"Le fichier '{docx_path}' n'est pas un fichier .docx.")
        print(f"Erreur: Le fichier '{docx_path}' n'est pas un fichier .docx.")
        sys.exit(1)

    # Obtenir le répertoire de sortie (même répertoire que le fichier .docx)
    output_dir = os.path.dirname(os.path.abspath(docx_path))
    if not output_dir:
        output_dir = "."

    # Noms des fichiers de sortie
    base_name = os.path.splitext(docx_path)[0]
    json_path = f"{base_name}.json"
    html_path = f"{base_name}.html"

    try:
        # Convertir le document en JSON
        logging.info(f"Traitement du fichier '{docx_path}'...")
        print(f"Traitement du fichier '{docx_path}'...")
        json_data = get_document_json(docx_path, output_dir, save_images)

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
