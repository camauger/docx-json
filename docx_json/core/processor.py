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
        Traite les instructions intégrées et les applique aux éléments suivants.

        Args:
            elements: Liste des éléments du document

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
            if element.type == "instruction":
                # Vérifier que l'élément est bien une Instruction avant d'accéder à content
                if isinstance(element, Instruction):
                    instruction = element.content.strip()
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
                        current_block = Block(block_type)

                    # Fin d'un bloc
                    elif " end" in instruction:
                        if current_block:
                            result.append(current_block)
                            current_block = None

                    # Instruction HTML brut
                    elif instruction.startswith("html "):
                        html_content = instruction[5:].strip()
                        result.append(RawHTML(html_content))

            # Traitement des marqueurs de composants pédagogiques
            elif element.type == "component_marker":
                # Vérifier que l'élément est bien un ComponentMarker avant d'accéder à component_type
                if isinstance(element, ComponentMarker):
                    component_type = element.component_type
                    logging.debug(f"Début de composant: {component_type}")

                    current_component = Component(component_type)

                    # Rechercher le contenu du composant jusqu'à [Fin] ou un autre composant
                    j = i + 1
                    while j < len(elements):
                        next_element = elements[j]

                        # Si on trouve un marqueur de fin pour ce composant
                        if (
                            next_element.type == "component_end"
                            and isinstance(next_element, ComponentEnd)
                            and next_element.component_type == component_type
                        ):
                            i = j  # On avance jusqu'à la fin du composant
                            break
                        # Si on trouve un autre marqueur de composant, on s'arrête aussi
                        elif next_element.type == "component_marker":
                            i = j - 1  # On s'arrête juste avant le nouveau composant
                            break
                        # Sinon, on ajoute l'élément au contenu du composant
                        else:
                            current_component.add_element(next_element)
                        j += 1

                    # Ajouter le composant au résultat
                    result.append(current_component)
                    current_component = None

            # Traitement des marqueurs de fin (sans marqueur de début correspondant)
            elif element.type == "component_end":
                # Vérifier que l'élément est bien un ComponentEnd avant d'accéder à component_type
                if isinstance(element, ComponentEnd):
                    logging.warning(
                        f"Marqueur de fin '{element.component_type}' sans marqueur de début correspondant"
                    )

            else:
                # Appliquer les classes et ID en attente
                if pending_classes:
                    element.html_class = " ".join(pending_classes)
                    pending_classes = []

                if pending_id:
                    element.html_id = pending_id
                    pending_id = None

                # Ajouter l'élément au bloc courant ou aux résultats
                if current_block:
                    current_block.add_element(element)
                elif current_component:
                    current_component.add_element(element)
                else:
                    result.append(element)

            i += 1

        # Ajouter le dernier bloc s'il existe encore
        if current_block:
            result.append(current_block)
            logging.warning("Un bloc n'a pas été fermé dans le document.")

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
