#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module pour le traitement des instructions et des éléments du document
---------------------------------------------------------------------
"""

import logging
from typing import Any, Dict, List, cast

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
        result = []
        pending_markers = {}  # Stocke les marqueurs par type
        component_counts = {
            "Accordéon": 0,
            "Onglets": 0,
            "Carrousel": 0,
            "Audio": 0,
            "Vidéo": 0,
        }

        for element in elements:
            # Si c'est un marqueur de début de composant
            if element.type == "component_marker":
                marker = cast(ComponentMarker, element)
                component_type = marker.component_type

                # Stocker le marqueur pour traitement ultérieur
                if component_type not in pending_markers:
                    pending_markers[component_type] = []
                pending_markers[component_type].append((len(result), marker))

            # Si c'est un marqueur de fin de composant
            elif element.type == "component_end":
                end_marker = cast(ComponentEnd, element)
                component_type = end_marker.component_type

                # Chercher le marqueur de début correspondant
                if (
                    component_type in pending_markers
                    and pending_markers[component_type]
                ):
                    start_index, start_marker = pending_markers[component_type].pop(0)

                    # Logger pour le débogage
                    print(
                        f"Création d'un composant {component_type} entre les indices {start_index} et {len(result)}"
                    )

                    # Créer un composant avec tout le contenu entre les marqueurs
                    component = Component(component_type)
                    component_counts[component_type] += 1

                    # Pour les vidéos, récupérer les attributs personnalisés
                    if component_type == "Vidéo" and hasattr(
                        start_marker, "attributes"
                    ):
                        # Transférer les attributs du ComponentMarker vers le Component
                        for key, value in start_marker.attributes.items():
                            # Utiliser la méthode add_attribute au lieu d'accéder directement à custom_attributes
                            component.add_attribute(key, value)
                            print(f"Attribut vidéo ajouté: {key}={value}")

                    # Ajouter le contenu entre les marqueurs au composant
                    component.content = result[start_index : len(result)]

                    # Remplacer tous les éléments entre les marqueurs par le composant
                    result = result[:start_index] + [component]
                else:
                    # Si pas de marqueur de début, ajouter un avertissement
                    logging.warning(
                        f"Marqueur de fin '{component_type}' sans marqueur de début correspondant"
                    )
                    result.append(element)
            else:
                # Vérifier si c'est un paragraphe contenant un marqueur [Vidéo] directement
                if element.type == "paragraph" and isinstance(element, Paragraph):
                    # Extraire le texte complet du paragraphe
                    full_text = ""
                    for run in element.runs:
                        full_text += run.text

                    # Vérifier si c'est un marqueur de vidéo
                    if full_text.startswith("[Vidéo") and "]" in full_text:
                        # Créer un composant vidéo
                        print(
                            f"Création d'un composant Vidéo à partir du marqueur: {full_text}"
                        )
                        component = Component("Vidéo")

                        # Extraire l'ID de vidéo
                        video_id = None

                        # Rechercher video_id avec quotes simples
                        if "video_id='" in full_text:
                            start_idx = full_text.find("video_id='") + 10
                            end_idx = full_text.find("'", start_idx)
                            if end_idx > start_idx:
                                video_id = full_text[start_idx:end_idx]

                        # Rechercher video_id avec quotes doubles
                        elif 'video_id="' in full_text:
                            start_idx = full_text.find('video_id="') + 10
                            end_idx = full_text.find('"', start_idx)
                            if end_idx > start_idx:
                                video_id = full_text[start_idx:end_idx]

                        # Ajouter l'ID comme attribut
                        if video_id:
                            component.add_attribute("video_id", video_id)

                        # Ajouter au résultat
                        result.append(component)
                        continue

                # Si ce n'est pas un marqueur de vidéo, ajouter normalement
                result.append(element)

        # Si des marqueurs de début restent sans fin correspondante, les ajouter au résultat
        for component_type, markers in pending_markers.items():
            for _, marker in markers:
                logging.warning(
                    f"Marqueur de début '{component_type}' sans marqueur de fin correspondant"
                )
                result.append(marker)

        # Afficher les statistiques des composants
        for component_type, count in component_counts.items():
            if count > 0:
                print(f"Composant trouvé: {component_type} avec {count} éléments")

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
