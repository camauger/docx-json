#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module pour l'extraction et l'analyse des documents DOCX
--------------------------------------------------------
"""

import base64
import logging
import os
from typing import Any, Dict, List, Optional

from docx import Document
from docx.oxml.table import CT_Tbl
from docx.oxml.text.paragraph import CT_P
from docx.table import Table as DocxTable
from docx.text.paragraph import Paragraph as DocxParagraph

from docx_json.models import (
    Block,
    Component,
    ComponentEnd,
    ComponentMarker,
    DocumentElement,
    Heading,
    Image,
    Instruction,
    ListItem,
    Paragraph,
    RawHTML,
    Table,
    TextRun,
)


class DocxParser:
    """
    Classe pour l'extraction et l'analyse des éléments d'un document DOCX.
    """

    def __init__(
        self, docx_path: str, output_dir: str, save_images_to_disk: bool = True
    ):
        """
        Initialise le parser.

        Args:
            docx_path: Chemin vers le fichier .docx
            output_dir: Répertoire de sortie pour les fichiers générés
            save_images_to_disk: Si True, sauvegarde les images sur disque. Sinon, encode en base64.
        """
        self._docx_path = docx_path
        self._output_dir = output_dir
        self._save_images_to_disk = save_images_to_disk
        self._document = None
        self._images = {}
        self._rels_dict = {}

    def load_document(self) -> None:
        """Charge le document DOCX."""
        logging.info(f"Chargement du document: {self._docx_path}")
        self._document = Document(self._docx_path)

    def extract_images(self) -> Dict[str, str]:
        """
        Extrait les images du document .docx.

        Returns:
            Un dictionnaire {nom_image: chemin_relatif} ou {nom_image: donnees_base64}
        """
        logging.info("Extraction des images...")

        # S'assurer que le document est chargé
        if self._document is None:
            self.load_document()
            if self._document is None:
                logging.error("Impossible de charger le document")
                return {}

        rels = self._document.part.rels

        # Si on sauvegarde sur disque, créer le dossier images
        if self._save_images_to_disk:
            images_dir = os.path.join(self._output_dir, "images")
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

                    if self._save_images_to_disk:
                        # Chemin de sortie pour l'image
                        image_path = os.path.join(images_dir, image_name)

                        # Sauvegarder l'image
                        with open(image_path, "wb") as f:
                            f.write(image_data)

                        # Stocker le chemin relatif dans le dictionnaire
                        self._images[image_name] = f"images/{image_name}"
                        logging.debug(f"Image extraite et sauvegardée: {image_path}")
                    else:
                        # Encoder en base64
                        encoded_image = base64.b64encode(image_data).decode("utf-8")
                        # Stocker dans le dictionnaire
                        self._images[image_name] = encoded_image
                        logging.debug(
                            f"Image extraite et encodée en base64: {image_name}"
                        )

                except Exception as e:
                    logging.warning(
                        f"Impossible d'extraire l'image {rel.target_ref}: {str(e)}"
                    )

        # S'assurer que self._document n'est pas None avant d'accéder à part
        if self._document is not None:
            # Créer un dictionnaire des relations pour associer les rIds aux chemins d'images
            for rel in self._document.part.rels.values():
                if "image" in rel.target_ref:
                    try:
                        image_name = os.path.basename(rel.target_ref)
                        if image_name in self._images:
                            if self._save_images_to_disk:
                                self._rels_dict[rel.rId] = self._images[image_name]
                            else:
                                # Pour les images en base64
                                self._rels_dict[rel.rId] = (
                                    f"data:image/png;base64,{self._images[image_name]}"
                                )
                    except Exception as e:
                        logging.warning(
                            f"Impossible de traiter la relation {rel.rId}: {str(e)}"
                        )

        return self._images

    def parse_paragraph(self, paragraph: DocxParagraph) -> DocumentElement:
        """
        Convertit un paragraphe en élément de document.

        Args:
            paragraph: L'objet Paragraph de python-docx

        Returns:
            Un élément de document (Paragraph, Heading, ListItem, etc.)
        """
        # Vérifier si le paragraphe contient une image
        for run in paragraph.runs:
            if hasattr(run, "_element"):
                # Recherche de l'élément inline (indiquant une image)
                inline_elem = None

                # Essayer différentes approches pour trouver les éléments d'image
                try:
                    # Méthode 1: Recherche directe avec le préfixe wp (si disponible)
                    if "wp" in run._element.nsmap:
                        inline_elem = run._element.find(
                            ".//wp:inline", namespaces=run._element.nsmap
                        )
                except Exception:
                    logging.debug(
                        "Impossible de trouver wp:inline avec les espaces de noms disponibles"
                    )

                # Si pas trouvé, essayer d'autres méthodes
                if inline_elem is None:
                    try:
                        # Méthode 2: Recherche pour n'importe quel élément inline sans préfixe spécifique
                        for child in run._element.iter(
                            "*"
                        ):  # Utiliser '*' pour tous les tags
                            if child.tag.endswith("inline"):
                                inline_elem = child
                                break
                    except Exception:
                        logging.debug(
                            "Impossible de rechercher un élément 'inline' générique"
                        )

                # Si on a trouvé une image
                if inline_elem is not None:
                    # Essayer de trouver l'attribut rId
                    rId = None
                    try:
                        # Rechercher l'élément blip et son attribut r:embed
                        for child in inline_elem.iter():
                            if child.tag.endswith("blip"):
                                # Chercher tous les attributs qui pourraient contenir l'ID de relation
                                for attrib_name, value in child.attrib.items():
                                    if attrib_name.endswith("embed"):
                                        rId = value
                                        break
                                if rId:
                                    break
                    except Exception as e:
                        logging.debug(
                            f"Impossible de récupérer l'ID de relation: {str(e)}"
                        )

                    # Créer l'élément image
                    image_element = Image(paragraph.text.strip() or "Image")

                    # Ajouter l'ID de relation s'il a été trouvé
                    if rId:
                        image_element.rId = rId
                        # Ajouter le chemin d'image s'il est disponible
                        if rId in self._rels_dict:
                            image_element.image_path = self._rels_dict[rId]

                    return image_element

        # Déterminer le type (paragraphe normal, titre, etc.)
        style_name = (
            paragraph.style.name if paragraph.style else ""
        )  # Utiliser une chaîne vide si None

        # Vérifier si c'est une instruction intégrée (commençant par ":::")
        text = paragraph.text.strip()
        if text.startswith(":::"):
            return Instruction(text[3:].strip())  # Retirer les ":::" du début

        # Vérifier si c'est un marqueur de composant pédagogique
        component_types = [
            "Vidéo",
            "Audio",
            "Accordéon",
            "Carrousel",
            "Onglets",
            "Défilement",
        ]
        if text.startswith("[") and any(
            text.startswith(f"[{comp}") for comp in component_types
        ):
            component_type = text[1:].split("]")[0] if "]" in text else "Unknown"
            return ComponentMarker(component_type)

        # Vérifier si c'est un marqueur de fin de composant
        if text.startswith("[Fin ") and "]" in text:
            component_type = text[5:].split("]")[0]
            return ComponentEnd(component_type)

        # Détecter si c'est un titre (Heading)
        if style_name and style_name.startswith("Heading"):
            level = (
                int(style_name.split(" ")[1]) if len(style_name.split(" ")) > 1 else 1
            )
            heading = Heading(level)

            # Extraire les runs (morceaux de texte avec style)
            for run in paragraph.runs:
                run_obj = TextRun(
                    text=run.text,
                    bold=bool(run.bold),  # Convertir en booléen strict
                    italic=bool(run.italic),  # Convertir en booléen strict
                    underline=bool(run.underline),  # Convertir en booléen strict
                )
                heading.add_run(run_obj)

            return heading

        # Vérifier si c'est un élément de liste
        if paragraph.paragraph_format.left_indent:
            list_item = ListItem()

            # Extraire les runs
            for run in paragraph.runs:
                run_obj = TextRun(
                    text=run.text,
                    bold=bool(run.bold),  # Convertir en booléen strict
                    italic=bool(run.italic),  # Convertir en booléen strict
                    underline=bool(run.underline),  # Convertir en booléen strict
                )
                list_item.add_run(run_obj)

            return list_item

        # C'est un paragraphe normal
        para = Paragraph()

        # Extraire les runs
        for run in paragraph.runs:
            run_obj = TextRun(
                text=run.text,
                bold=bool(run.bold),  # Convertir en booléen strict
                italic=bool(run.italic),  # Convertir en booléen strict
                underline=bool(run.underline),  # Convertir en booléen strict
            )
            para.add_run(run_obj)

        return para

    def parse_table(self, table: DocxTable) -> Table:
        """
        Convertit une table en élément Table.

        Args:
            table: L'objet Table de python-docx

        Returns:
            Un élément Table
        """
        table_element = Table()

        for row in table.rows:
            row_content = []
            for cell in row.cells:
                # Une cellule peut contenir plusieurs paragraphes
                cell_content = []
                for paragraph in cell.paragraphs:
                    para_element = self.parse_paragraph(paragraph)
                    # Ignorer les instructions dans les cellules
                    if para_element.type != "instruction":
                        cell_content.append(para_element)
                row_content.append(cell_content)
            table_element.add_row(row_content)

        return table_element

    def get_document_elements(self) -> List[DocumentElement]:
        """
        Extrait tous les éléments du document DOCX.

        Returns:
            Liste des éléments du document.
        """
        # S'assurer que le document est chargé
        if self._document is None:
            self.load_document()
            if self._document is None:
                logging.error("Impossible de charger le document")
                return []

        # Extraire les images si pas déjà fait
        if not self._images:
            self.extract_images()

        # Extraire le contenu en respectant l'ordre
        logging.info("Extraction du contenu...")
        elements = []

        # Vérifier que document est chargé et a un attribut element
        if hasattr(self._document, "element") and hasattr(
            self._document.element, "body"
        ):
            body = self._document.element.body

            # Parcourir les éléments du corps du document (paragraphes et tables)
            for child in body.iterchildren():
                if isinstance(child, CT_P):
                    # S'assurer que self._document n'est pas None pour le constructeur DocxParagraph
                    paragraph = DocxParagraph(child, self._document)
                    para_element = self.parse_paragraph(paragraph)
                    elements.append(para_element)
                elif isinstance(child, CT_Tbl):
                    # S'assurer que self._document n'est pas None pour le constructeur DocxTable
                    table = DocxTable(child, self._document)
                    table_element = self.parse_table(table)
                    elements.append(table_element)
        else:
            logging.error("Le document n'a pas de corps valide")
            return []

        return elements

    def get_images(self) -> Dict[str, str]:
        """
        Renvoie le dictionnaire des images extraites.

        Returns:
            Dictionnaire des images extraites
        """
        return self._images
