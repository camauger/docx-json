#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Générateur de CSS pour les classes personnalisées
-------------------------------------------------

Ce module analyse le document JSON intermédiaire pour extraire
les classes personnalisées ajoutées via les instructions :::class
et génère un fichier CSS avec des styles par défaut.
"""

import json
import logging
import os
from typing import Any, Dict, List, Optional, Set

# Dictionnaire de styles prédéfinis pour les classes courantes
DEFAULT_STYLES = {
    # Styles de texte et mise en évidence
    "hero": """
    font-size: 2.5rem;
    font-weight: bold;
    color: #0056b3;
    margin-bottom: 1.5rem;
    text-align: center;
    """,
    "lead": """
    font-size: 1.25rem;
    font-weight: 300;
    """,
    "emphasis": """
    color: #0056b3;
    font-weight: 500;
    """,
    # Notifications et alertes
    "info": """
    background-color: #e8f4fd;
    border-left: 4px solid #0d6efd;
    padding: 1rem;
    margin: 1rem 0;
    border-radius: 0.25rem;
    """,
    "warning": """
    background-color: #fff3cd;
    border-left: 4px solid #ffc107;
    padding: 1rem;
    margin: 1rem 0;
    border-radius: 0.25rem;
    """,
    "danger": """
    background-color: #f8d7da;
    border-left: 4px solid #dc3545;
    padding: 1rem;
    margin: 1rem 0;
    border-radius: 0.25rem;
    """,
    "success": """
    background-color: #d1e7dd;
    border-left: 4px solid #198754;
    padding: 1rem;
    margin: 1rem 0;
    border-radius: 0.25rem;
    """,
    # Conteneurs
    "card": """
    background-color: #fff;
    border: 1px solid #dee2e6;
    border-radius: 0.375rem;
    padding: 1.5rem;
    box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
    margin-bottom: 1.5rem;
    """,
    "panel": """
    background-color: #f8f9fa;
    border: 1px solid #dee2e6;
    border-radius: 0.375rem;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    """,
    # Marges et espacement
    "mt-large": "margin-top: 3rem;",
    "mb-large": "margin-bottom: 3rem;",
    "p-large": "padding: 3rem;",
    # Couleurs de texte
    "text-primary": "color: #0d6efd;",
    "text-secondary": "color: #6c757d;",
    "text-success": "color: #198754;",
    "text-warning": "color: #ffc107;",
    "text-danger": "color: #dc3545;",
    # Alignement
    "text-center": "text-align: center;",
    "text-right": "text-align: right;",
    "text-justify": "text-align: justify;",
    # Bordures
    "border": "border: 1px solid #dee2e6;",
    "border-top": "border-top: 1px solid #dee2e6;",
    "border-bottom": "border-bottom: 1px solid #dee2e6;",
    "rounded": "border-radius: 0.375rem;",
    # Espacement
    "p-0": "padding: 0;",
    "p-1": "padding: 0.25rem;",
    "p-2": "padding: 0.5rem;",
    "p-3": "padding: 1rem;",
    "p-4": "padding: 1.5rem;",
    "p-5": "padding: 3rem;",
    "m-0": "margin: 0;",
    "m-1": "margin: 0.25rem;",
    "m-2": "margin: 0.5rem;",
    "m-3": "margin: 1rem;",
    "m-4": "margin: 1.5rem;",
    "m-5": "margin: 3rem;",
    # Autres
    "shadow": "box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);",
    "shadow-sm": "box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);",
    "shadow-lg": "box-shadow: 0 1rem 3rem rgba(0, 0, 0, 0.175);",
}


def extract_custom_classes(json_data: Dict[str, Any]) -> Set[str]:
    """
    Extrait toutes les classes CSS personnalisées du document JSON.

    Args:
        json_data: Le document JSON généré par le convertisseur

    Returns:
        Un ensemble de noms de classes uniques
    """
    custom_classes = set()

    def process_item(item: Dict[str, Any]) -> None:
        """Traite récursivement un élément du JSON pour extraire les classes."""
        if not isinstance(item, dict):
            return

        # Extraire les classes HTML de l'élément courant
        if "html_class" in item and item["html_class"]:
            classes = item["html_class"].split()
            for cls in classes:
                custom_classes.add(cls)

        # Traiter récursivement les éléments enfants
        if "content" in item and isinstance(item["content"], list):
            for child in item["content"]:
                process_item(child)

        # Traiter récursivement les éléments d'un tableau
        if "cells" in item and isinstance(item["cells"], list):
            for row in item["cells"]:
                if isinstance(row, list):
                    for cell in row:
                        process_item(cell)

    # Traiter tous les éléments de contenu
    for item in json_data.get("content", []):
        process_item(item)

    return custom_classes


def generate_css(
    classes: Set[str], css_path: str, custom_styles: Optional[Dict[str, str]] = None
) -> None:
    """
    Génère un fichier CSS pour les classes personnalisées.

    Args:
        classes: Ensemble des noms de classes à inclure
        css_path: Chemin du fichier CSS à générer
        custom_styles: Dictionnaire de styles personnalisés à utiliser
                      à la place des styles par défaut
    """
    # Fusionner les styles par défaut et personnalisés
    styles = DEFAULT_STYLES.copy()
    if custom_styles:
        styles.update(custom_styles)

    # Générer le contenu CSS
    css_content = [
        "/**",
        " * Styles générés automatiquement pour les classes personnalisées",
        " * Généré par docx-json",
        " */",
        "",
        "/* Styles pour les classes personnalisées */",
        "",
    ]

    # Ajouter les styles pour chaque classe trouvée
    for cls in sorted(classes):
        if cls in styles:
            css_content.append(f".{cls} {{")
            for line in styles[cls].strip().split("\n"):
                css_content.append(f"    {line.strip()}")
            css_content.append("}")
            css_content.append("")
        else:
            css_content.append(f".{cls} {{")
            css_content.append("    /* Classe personnalisée, ajoutez vos styles ici */")
            css_content.append("}")
            css_content.append("")

    # Écrire le fichier CSS
    os.makedirs(os.path.dirname(os.path.abspath(css_path)), exist_ok=True)
    with open(css_path, "w", encoding="utf-8") as f:
        f.write("\n".join(css_content))

    logging.info(f"Fichier CSS généré: {css_path}")


def process_json_file(
    json_path: str, css_path: str, custom_styles: Optional[Dict[str, str]] = None
) -> Set[str]:
    """
    Traite un fichier JSON pour générer le CSS correspondant.

    Args:
        json_path: Chemin du fichier JSON à analyser
        css_path: Chemin du fichier CSS à générer
        custom_styles: Dictionnaire de styles personnalisés à utiliser

    Returns:
        Ensemble des classes CSS trouvées dans le document
    """
    # Charger le JSON
    with open(json_path, "r", encoding="utf-8") as f:
        json_data = json.load(f)

    # Extraire les classes et générer le CSS
    classes = extract_custom_classes(json_data)
    generate_css(classes, css_path, custom_styles)

    return classes


def load_custom_styles(styles_path: str) -> Dict[str, str]:
    """
    Charge des styles personnalisés depuis un fichier JSON.

    Args:
        styles_path: Chemin du fichier JSON contenant les styles

    Returns:
        Dictionnaire des styles personnalisés
    """
    if not os.path.exists(styles_path):
        logging.warning(f"Fichier de styles personnalisés non trouvé: {styles_path}")
        return {}

    try:
        with open(styles_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        logging.error(f"Erreur de format dans le fichier de styles: {styles_path}")
        return {}
