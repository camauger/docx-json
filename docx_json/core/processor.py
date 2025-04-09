#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module pour le traitement des instructions et des éléments du document
---------------------------------------------------------------------
"""

import logging
from typing import Any, Dict, List

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


class DocumentProcessor:
    """
    Classe pour le traitement des éléments du document.
    """

    @staticmethod
    def process_instructions(elements: List[DocumentElement]) -> List[DocumentElement]:
        """
        Traite les instructions et composants spéciaux dans une liste d'éléments.

        Cette méthode :
        1. Gère les instructions et les remplace par les éléments appropriés
        2. Regroupe les éléments entre marqueurs de composants
        3. Traite les attributs HTML (classes, ID)

        Args:
            elements: Liste des éléments de document à traiter

        Returns:
            Liste des éléments traités
        """
        result = []
        i = 0
        current_block = None
        current_component = None
        pending_classes = []
        pending_id = None

        while i < len(elements):
            element = elements[i]

            # Traitement des instructions
            if isinstance(element, Instruction):
                instruction = element.content.strip()
                logging.debug(f"Instruction trouvée: {instruction}")

                # Traitement des instructions comme les classes et IDs
                if instruction.startswith("class "):
                    class_names = instruction[6:].strip()
                    pending_classes.extend(class_names.split())
                elif instruction.startswith("id "):
                    pending_id = instruction[3:].strip()
                elif " begin" in instruction:
                    block_type = instruction.split()[0]
                    current_block = Block(block_type)
                # Autres instructions omises pour la concision

            # Traitement des marqueurs de composants pédagogiques
            elif element.type == "component_marker":
                if isinstance(element, ComponentMarker):
                    component_type = element.component_type
                    logging.debug(f"Marqueur de composant trouvé: {component_type}")

                    # Créer un nouveau composant
                    current_component = Component(component_type)

                    # Rechercher jusqu'au marqueur de fin correspondant
                    j = i + 1
                    found_end_marker = False

                    while j < len(elements):
                        next_element = elements[j]

                        # Si on trouve le marqueur de fin correspondant
                        if (
                            next_element.type == "component_end"
                            and isinstance(next_element, ComponentEnd)
                            and next_element.component_type == component_type
                        ):
                            i = j  # On avance jusqu'à la fin du composant
                            found_end_marker = True
                            break
                        # Si c'est un autre marqueur de composant, on s'arrête
                        elif next_element.type == "component_marker":
                            i = j - 1
                            break
                        # Sinon, on ajoute au contenu du composant
                        else:
                            current_component.add_element(next_element)

                        j += 1

                    # Ajouter le composant au résultat
                    result.append(current_component)
                    logging.debug(
                        f"Composant '{component_type}' ajouté avec {len(current_component.content)} éléments de contenu"
                    )
                    current_component = None

                    # Si on n'a pas trouvé de marqueur de fin
                    if not found_end_marker:
                        logging.warning(
                            f"Pas de marqueur de fin trouvé pour le composant '{component_type}'"
                        )

            # Traitement des marqueurs de fin sans marqueur de début correspondant
            elif element.type == "component_end":
                if isinstance(element, ComponentEnd):
                    logging.warning(
                        f"Marqueur de fin '{element.component_type}' sans marqueur de début correspondant"
                    )

            # Tout autre élément
            else:
                # Ajouter aux résultats en tenant compte du contexte
                if pending_classes:
                    element.html_class = " ".join(pending_classes)
                    pending_classes = []

                if pending_id:
                    element.html_id = pending_id
                    pending_id = None

                if current_block:
                    current_block.add_element(element)
                else:
                    result.append(element)

            i += 1

        # Ajouter le dernier bloc s'il n'a pas été fermé
        if current_block:
            result.append(current_block)
            logging.warning("Un bloc n'a pas été fermé dans le document")

        return result


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
