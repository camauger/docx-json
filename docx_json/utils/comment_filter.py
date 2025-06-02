#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Filtre de commentaires pour docx-json
-------------------------------------

Ce module filtre les commentaires délimités par ### dans les documents Word.
Les paragraphes ou parties de texte entourés par ces délimiteurs ne seront
pas inclus dans la sortie JSON, HTML ou Markdown.
"""

import re
from typing import Any, Dict, List, Optional, Tuple


def is_comment_paragraph(text: str) -> bool:
    """
    Détermine si un paragraphe complet est un commentaire.

    Un paragraphe est considéré comme un commentaire s'il commence et se termine
    par ### ou s'il est entièrement encadré par ###.

    Args:
        text: Le texte du paragraphe à vérifier

    Returns:
        bool: True si le paragraphe est un commentaire, False sinon
    """
    # Vérifier si le texte commence et se termine par ###
    if text.strip().startswith("###") and text.strip().endswith("###"):
        return True

    # Vérifier si tout le texte est entre ### et ###
    if "###" in text:
        comment_parts = re.split(r"###", text)
        # Si le premier élément est vide (texte commence par ###)
        # et le dernier élément est vide (texte finit par ###)
        if (
            len(comment_parts) >= 3
            and not comment_parts[0].strip()
            and not comment_parts[-1].strip()
        ):
            return True

    return False


def filter_comment_from_text(text: str) -> str:
    """
    Filtre les commentaires d'un texte.

    Supprime toutes les parties de texte encadrées par ### ###.

    Args:
        text: Le texte à filtrer

    Returns:
        str: Le texte filtré sans les commentaires
    """
    # Si le paragraphe entier est un commentaire
    if is_comment_paragraph(text):
        return ""

    # Filtrer les commentaires à l'intérieur du texte
    # Trouve tous les segments entre ### et ### (non-greedy avec ? dans .*?)
    filtered_text = re.sub(r"###.*?###", "", text)

    return filtered_text


def filter_comments_from_paragraph(
    paragraph: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    """
    Filtre les commentaires d'un paragraphe.

    Si le paragraphe est entièrement un commentaire, retourne None.
    Sinon, filtre les commentaires dans les runs de texte.

    Args:
        paragraph: Le dictionnaire représentant un paragraphe

    Returns:
        Dict ou None: Le paragraphe filtré ou None si c'est un commentaire complet
    """
    if "runs" not in paragraph:
        return paragraph

    # Vérifier si l'ensemble du paragraphe est un commentaire
    full_text = "".join(run.get("text", "") for run in paragraph["runs"])
    if is_comment_paragraph(full_text):
        return None

    # Traitement des commentaires dans les runs individuels
    comment_started = False
    filtered_runs = []

    for run in paragraph["runs"]:
        text = run.get("text", "")
        if not text:
            filtered_runs.append(run)
            continue

        # Cas où le commentaire a commencé dans un run précédent
        if comment_started:
            if "###" in text:
                # Le commentaire se termine dans ce run
                comment_started = False
                remaining_text = text.split("###", 1)[1]
                if remaining_text:
                    new_run = run.copy()
                    new_run["text"] = remaining_text
                    filtered_runs.append(new_run)
            # Sinon, on ignore ce run qui fait partie du commentaire
            continue

        # Cas normal, recherche de commentaires dans ce run
        parts = text.split("###")
        if len(parts) % 2 == 0:
            # Nombre pair de '###' : le commentaire se termine dans un run suivant
            comment_started = True
            # Ajouter la partie avant le premier '###'
            if parts[0]:
                new_run = run.copy()
                new_run["text"] = parts[0]
                filtered_runs.append(new_run)
        else:
            # Nombre impair de '###' : au moins un commentaire complet dans ce run
            filtered_text = ""
            for i, part in enumerate(parts):
                if (
                    i % 2 == 0
                ):  # Les parties à l'indice pair sont en dehors des commentaires
                    filtered_text += part

            if filtered_text:
                new_run = run.copy()
                new_run["text"] = filtered_text
                filtered_runs.append(new_run)

    # Si tous les runs ont été filtrés, retourner None
    if not filtered_runs:
        return None

    # Créer un nouveau paragraphe avec les runs filtrés
    filtered_paragraph = paragraph.copy()
    filtered_paragraph["runs"] = filtered_runs
    return filtered_paragraph


def filter_comments_from_content(content: List[Any]) -> List[Any]:
    """
    Filtre les commentaires de tout le contenu du document.

    Parcourt récursivement la structure du document et filtre les commentaires.

    Args:
        content: La liste des éléments de contenu du document

    Returns:
        List: La liste des éléments filtrés
    """
    filtered_content = []

    for item in content:
        # Vérifier si l'élément est un dictionnaire ou un objet
        if isinstance(item, dict):
            item_type = item.get("type", "")
        else:
            # Si c'est un objet, utiliser l'attribut type
            item_type = getattr(item, "type", "")

        # Traiter les paragraphes
        if item_type == "paragraph":
            if isinstance(item, dict):
                filtered_item = filter_comments_from_paragraph(item)
                if filtered_item:
                    filtered_content.append(filtered_item)
            else:
                # Si c'est un objet, l'ajouter directement pour l'instant
                # (le filtrage des objets sera implémenté ultérieurement)
                filtered_content.append(item)

        # Traiter les composants (récursivement)
        elif item_type == "component":
            content_to_filter = None
            if isinstance(item, dict) and "content" in item:
                content_to_filter = item["content"]
            elif hasattr(item, "content") and item.content:
                content_to_filter = item.content

            if content_to_filter:
                filtered_component_content = filter_comments_from_content(
                    content_to_filter
                )

                if filtered_component_content:
                    if isinstance(item, dict):
                        filtered_item = item.copy()
                        filtered_item["content"] = filtered_component_content
                    else:
                        # Pour les objets, nous ne faisons pas encore de filtrage
                        # Cela nécessiterait d'implémenter une méthode de copie
                        filtered_item = item
                    filtered_content.append(filtered_item)

        # Traiter les blocs (récursivement)
        elif item_type == "block":
            content_to_filter = None
            if isinstance(item, dict) and "content" in item:
                content_to_filter = item["content"]
            elif hasattr(item, "content") and item.content:
                content_to_filter = item.content

            if content_to_filter:
                filtered_block_content = filter_comments_from_content(content_to_filter)

                if filtered_block_content:
                    if isinstance(item, dict):
                        filtered_item = item.copy()
                        filtered_item["content"] = filtered_block_content
                    else:
                        # Pour les objets, nous ne faisons pas encore de filtrage
                        filtered_item = item
                    filtered_content.append(filtered_item)

        # Les autres éléments sont conservés tels quels
        else:
            filtered_content.append(item)

    return filtered_content


def filter_comments_from_json(json_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Filtre les commentaires d'un document JSON.

    Args:
        json_data: Les données JSON du document

    Returns:
        Dict: Les données JSON filtrées
    """
    if "content" not in json_data:
        return json_data

    filtered_json = json_data.copy()

    # Vérifier si le contenu est une liste de dictionnaires ou une liste d'objets
    if json_data["content"] and isinstance(json_data["content"][0], dict):
        filtered_json["content"] = filter_comments_from_content(json_data["content"])
    else:
        # Si ce sont des objets, convertir d'abord en dict
        dict_content = []
        for item in json_data["content"]:
            if hasattr(item, "to_dict"):
                dict_content.append(item.to_dict())
            else:
                # Si l'objet n'a pas de méthode to_dict, l'ignorer pour l'instant
                # Une solution plus complète serait nécessaire
                dict_content.append({"type": getattr(item, "type", "unknown")})

        filtered_content = filter_comments_from_content(dict_content)
        filtered_json["content"] = filtered_content

    return filtered_json


def is_comment_text(text: str) -> bool:
    """
    Détermine si un texte est un commentaire délimité par ###.

    Utile pour les analyseurs de documents DOCX qui veulent
    écarter les paragraphes commentaires dès la phase d'analyse.

    Args:
        text: Le texte à analyser

    Returns:
        bool: True si le texte est un commentaire, False sinon
    """
    # Texte vide n'est pas un commentaire
    if not text or text.isspace():
        return False

    # Texte est entièrement entouré par ###
    if is_comment_paragraph(text):
        return True

    # Texte contient au moins une paire de ###
    return "###" in text and text.count("###") >= 2
