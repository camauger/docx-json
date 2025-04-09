#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module pour l'extraction et l'analyse des documents DOCX
--------------------------------------------------------
"""

import base64
import logging
import os
import re
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
    DocumentList,
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
        self.NAMESPACES = {
            "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
            "wp": "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing",
            "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
            "pic": "http://schemas.openxmlformats.org/drawingml/2006/picture",
        }
        self._load_relationships()

    def _load_relationships(self) -> None:
        """
        Charge les relations entre les éléments du document DOCX.
        """
        logging.info("Chargement des relations...")
        self._document = Document(self._docx_path)
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

    def _get_runs(self, paragraph: DocxParagraph) -> List[Dict[str, Any]]:
        """
        Extraire les runs (morceaux de texte avec style) d'un paragraphe.
        """
        runs = []
        for run in paragraph.runs:
            runs.append(
                {
                    "text": run.text,
                    "bold": bool(run.bold),
                    "italic": bool(run.italic),
                    "underline": bool(run.underline),
                }
            )
        return runs

    def _parse_image(self, paragraph: DocxParagraph) -> Dict[str, Any]:
        """
        Parse une image dans un paragraphe.
        """
        for run in paragraph.runs:
            if run._element is not None:
                # Vérifier si le run contient une image
                if (
                    run._element.find(".//pic:pic", namespaces=self.NAMESPACES)
                    is not None
                ):
                    # Extraire l'ID de l'image
                    blip = run._element.find(".//a:blip", namespaces=self.NAMESPACES)
                    if blip is not None and hasattr(blip, "attrib"):
                        rId = blip.attrib.get(
                            "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed"
                        )
                        if rId:
                            return {
                                "type": "image",
                                "alt_text": paragraph.text.strip() or "Image",
                                "rId": rId,
                                "image_path": self._rels_dict.get(rId),
                            }

        return {"type": "image", "alt_text": paragraph.text.strip() or "Image"}

    def _group_consecutive_lists(
        self, elements: List[DocumentElement]
    ) -> List[DocumentElement]:
        """
        Regroupe les éléments de liste consécutifs en un seul DocumentList.
        """
        grouped_elements = []
        current_list = None

        for element in elements:
            if isinstance(element, DocumentList):
                if current_list is None:
                    current_list = element
                else:
                    # Ajouter les éléments de la liste courante à la liste en cours
                    for item in element.items:
                        current_list.add_item(item)
            else:
                if current_list is not None:
                    grouped_elements.append(current_list)
                    current_list = None
                grouped_elements.append(element)

        # Ajouter la dernière liste si elle existe
        if current_list is not None:
            grouped_elements.append(current_list)

        return grouped_elements

    def parse_paragraph(self, paragraph: DocxParagraph) -> DocumentElement:
        """
        Convertit un paragraphe en élément de document.
        """
        # Vérifier si c'est un marqueur de composant
        text = paragraph.text.strip()
        if text.startswith("[") and text.endswith("]"):
            # Extraire le type de composant et les attributs HTML
            component_pattern = r"\[([\w\s]+)(?:\s+(.+))?\]"
            match = re.match(component_pattern, text)
            if match:
                component_type = match.group(1).strip()
                attributes_str = match.group(2) or ""

                # Vérifier si c'est un marqueur de début ou de fin de composant
                if component_type in [
                    "Vidéo",
                    "Audio",
                    "Accordéon",
                    "Carrousel",
                    "Onglets",
                    "Défilement",
                ]:
                    logging.debug(
                        f"Marqueur de début de composant détecté: {component_type}"
                    )

                    # Extraire les attributs si présents (format: attr='value' attr2="value2")
                    component_marker = ComponentMarker(component_type=component_type)

                    if attributes_str:
                        # Pattern pour extraire les attributs au format key='value' ou key="value"
                        attr_pattern = r"(\w+)=(['\"])(.*?)\2"
                        for attr_match in re.finditer(attr_pattern, attributes_str):
                            attr_name = attr_match.group(1)
                            attr_value = attr_match.group(3)
                            # Stocker l'attribut dans l'objet ComponentMarker
                            setattr(component_marker, attr_name, attr_value)
                            logging.debug(
                                f"  Attribut détecté: {attr_name}={attr_value}"
                            )

                    return component_marker
                elif component_type.startswith("Fin "):
                    # Extraire le type de composant sans le "Fin "
                    end_component_type = component_type[4:].strip()
                    logging.debug(
                        f"Marqueur de fin de composant détecté: {end_component_type}"
                    )
                    return ComponentEnd(component_type=end_component_type)

        # Vérifier si c'est une image
        if any(
            run._element.find(".//pic:pic", namespaces=self.NAMESPACES) is not None
            for run in paragraph.runs
        ):
            image_data = self._parse_image(paragraph)
            image = Image(alt_text=image_data["alt_text"])
            if "rId" in image_data:
                image.rId = image_data["rId"]
            if "image_path" in image_data:
                image.image_path = image_data["image_path"]
            return image

        # Vérifier si c'est une instruction
        if paragraph.text.strip().startswith("{{") and paragraph.text.strip().endswith(
            "}}"
        ):
            return Instruction(content=paragraph.text.strip()[2:-2])

        # Vérifier si c'est un titre
        if (
            paragraph.style is not None
            and paragraph.style.name is not None
            and paragraph.style.name.startswith("Heading")
        ):
            level = int(paragraph.style.name[-1])
            heading = Heading(level=level)
            for run in paragraph.runs:
                heading.add_run(
                    TextRun(
                        text=run.text,
                        bold=bool(run.bold),
                        italic=bool(run.italic),
                        underline=bool(run.underline),
                    )
                )
            return heading

        # Vérifier si c'est un élément de liste
        if (
            paragraph.paragraph_format.left_indent is not None
            and paragraph.paragraph_format.left_indent > 0
        ):
            is_ordered = False
            if paragraph.style and paragraph.style.name == "List Number":
                is_ordered = True
            elif paragraph.text.strip() and re.match(r"^\d+\.", paragraph.text.strip()):
                is_ordered = True

            # Créer un DocumentList avec les attributs appropriés
            doc_list = DocumentList(ordered=is_ordered)

            # Créer un ListItem et y ajouter les runs
            list_item = ListItem()
            for run in paragraph.runs:
                list_item.add_run(
                    TextRun(
                        text=run.text,
                        bold=bool(run.bold),
                        italic=bool(run.italic),
                        underline=bool(run.underline),
                    )
                )

            # Ajouter l'élément à la liste
            doc_list.add_item(list_item)
            return doc_list

        # Paragraphe normal
        para = Paragraph()
        for run in paragraph.runs:
            para.add_run(
                TextRun(
                    text=run.text,
                    bold=bool(run.bold),
                    italic=bool(run.italic),
                    underline=bool(run.underline),
                )
            )
        return para

    def parse_table(self, table: DocxTable) -> Table:
        """
        Parse une table Word et retourne un élément Table.

        Args:
            table: Table Word à parser

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
                    if para_element is not None and not isinstance(
                        para_element, Instruction
                    ):
                        cell_content.append(para_element)
                row_content.append(cell_content)
            table_element.add_row(row_content)

        return table_element

    def parse(self) -> List[DocumentElement]:
        """
        Parse a Word document and return a list of document elements.
        """
        if not self._document:
            raise ValueError("No document loaded")

        elements = []
        for paragraph in self._document.paragraphs:
            para_element = self.parse_paragraph(paragraph)
            if para_element is not None and not isinstance(para_element, Instruction):
                elements.append(para_element)

        # Group consecutive list elements
        elements = self._group_consecutive_lists(elements)
        return elements

    def get_images(self) -> Dict[str, str]:
        """
        Renvoie le dictionnaire des images extraites.

        Returns:
            Dictionnaire des images extraites
        """
        return self._images
