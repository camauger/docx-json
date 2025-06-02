#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module pour le traitement des instructions et des éléments du document
---------------------------------------------------------------------
"""

import logging
from typing import Any, Dict, List, cast

from docx_json.utils.comment_filter import filter_comments_from_json

logger = logging.getLogger(__name__)

from docx_json.models import (
    Block,
    Component,
    ComponentEnd,
    ComponentMarker,
    DocumentElement,
    Instruction,
    RawHTML,
)
from docx_json.models.text import Paragraph


class DocumentProcessor:
    """
    Classe pour le traitement des éléments du document.
    """

    @staticmethod
    def process_instructions(elements: List[DocumentElement]) -> List[DocumentElement]:
        """
        Traite les marqueurs d'instructions dans le document pour créer des composants.

        Args:
            elements: Liste d'éléments de document

        Returns:
            Liste d'éléments avec les composants traités
        """
        # Dictionnaire pour stocker les composants en cours de construction
        components_by_type = {}

        # Liste pour les éléments processés
        processed_elements = []

        # Compteurs de composants
        component_counts = {
            "Accordéon": 0,
            "Onglets": 0,
            "Carrousel": 0,
            "Audio": 0,
            "Vidéo": 0,
            "Consignes": 0,
        }

        # Première passe - Identifier les paragraphes qui sont des marqueurs de composant
        # mais qui n'ont pas été détectés comme tels (ex: paragraphes contenant [Consignes])
        i = 0
        while i < len(elements):
            element = elements[i]

            # Vérifier si c'est un paragraphe
            if element.type == "paragraph" and isinstance(element, Paragraph):
                full_text = "".join([run.text for run in element.runs]).strip()

                # Vérifier si c'est un marqueur de début de composant
                if full_text in [
                    "[Consignes]",
                    "[Audio]",
                    "[Vidéo]",
                    "[Accordéon]",
                    "[Carrousel]",
                    "[Onglets]",
                    "[Défilement]",
                ]:
                    # Remplacer le paragraphe par un marqueur de composant
                    component_type = full_text[1:-1]  # Enlever les []
                    logging.debug(
                        f"Paragraphe converti en marqueur de début de composant: {component_type}"
                    )
                    elements[i] = ComponentMarker(component_type=component_type)

                # Vérifier si c'est un marqueur de fin de composant
                elif full_text.startswith("[Fin ") and full_text.endswith("]"):
                    component_type = full_text[5:-1]  # Enlever [Fin et ]
                    logging.debug(
                        f"Paragraphe converti en marqueur de fin de composant: {component_type}"
                    )
                    elements[i] = ComponentEnd(component_type=component_type)

            i += 1

        # Deuxième passe - Traiter les composants
        i = 0
        while i < len(elements):
            element = elements[i]

            # Cas 1: Élément de type component_marker (début de composant)
            if element.type == "component_marker":
                marker = cast(ComponentMarker, element)
                component_type = (
                    marker.component_type
                )  # Maintenant c'est le type de base

                # Chercher le marqueur de fin correspondant
                j = i + 1
                end_index = -1

                while j < len(elements):
                    if (
                        elements[j].type == "component_end"
                        and cast(ComponentEnd, elements[j]).component_type
                        == component_type
                    ):
                        end_index = j
                        break
                    j += 1

                if end_index > i:
                    # Créer un nouveau composant
                    component = Component(component_type)
                    component_counts[component_type] += 1

                    # Transférer les attributs du marqueur
                    if hasattr(marker, "attributes") and isinstance(
                        marker.attributes, dict
                    ):
                        for key, value in marker.attributes.items():
                            component.add_attribute(key, value)
                            logging.debug(
                                f"Attribut ajouté à {component_type}: {key}={value}"
                            )

                    # Cas spécifique pour les Consignes
                    if component_type == "Consignes":
                        component.html_class = "consignes"
                        logging.info(
                            f"Classe 'consignes' ajoutée au composant {component_type}"
                        )

                    # Ajouter le contenu du composant
                    component.content = elements[i + 1 : end_index]

                    # Ajouter le composant à la liste des éléments traités
                    processed_elements.append(component)

                    # Passer directement après le marqueur de fin
                    i = end_index + 1
                else:
                    # Si pas de marqueur de fin, ignorer ce marqueur
                    logging.warning(
                        f"Pas de marqueur de fin trouvé pour '{component_type}'"
                    )
                    i += 1

            # Cas 2: Élément de type component_end (fin de composant sans début)
            elif element.type == "component_end":
                logging.warning(
                    f"Marqueur de fin '{cast(ComponentEnd, element).component_type}' sans début correspondant"
                )
                i += 1

            # Cas 3: Autre élément (ajouter tel quel)
            else:
                processed_elements.append(element)
                i += 1

        # Afficher les statistiques des composants traités
        for component_type, count in component_counts.items():
            if count > 0:
                logging.info(
                    f"Composant trouvé: {component_type} avec {count} éléments"
                )

        return processed_elements

    @staticmethod
    def process_document(
        json_data: Dict[str, Any], filter_comments: bool = True
    ) -> Dict[str, Any]:
        """
        Applique différentes transformations au document JSON.

        Args:
            json_data: Les données JSON du document
            filter_comments: Si True, filtre les commentaires délimités par ###

        Returns:
            Dict: Les données JSON transformées
        """
        processed_json = json_data

        # Filtrer les commentaires si demandé
        if filter_comments:
            logging.info("Filtrage des commentaires (délimités par ###)...")
            processed_json = filter_comments_from_json(processed_json)

        return processed_json


def generate_markdown(json_data: Dict[str, Any], output_path: str) -> None:
    """
    Génère un fichier Markdown à partir des données JSON.

    Args:
        json_data: Les données JSON du document.
        output_path: Le chemin où enregistrer le fichier Markdown.
    """
    from docx_json.core.markdown_generator import MarkdownGenerator

    generator = MarkdownGenerator(json_data)
    markdown_content = generator.generate()

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(markdown_content)

    logger.info(f"Fichier Markdown créé: '{output_path}'")
