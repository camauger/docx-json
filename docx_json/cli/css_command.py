#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Intégration de la génération CSS dans l'interface en ligne de commande
---------------------------------------------------------------------

Ce module ajoute les options de ligne de commande pour la génération de CSS
et implémente les fonctions nécessaires pour traiter ces options.
"""

import argparse
import logging
import os
import sys
from typing import Dict, Optional, Set

from docx_json.utils.css_generator import load_custom_styles, process_json_file


def add_css_arguments(parser: argparse.ArgumentParser) -> None:
    """
    Ajoute les arguments de ligne de commande pour la génération de CSS.

    Args:
        parser: L'analyseur d'arguments auquel ajouter les options
    """
    css_group = parser.add_argument_group("Options de génération CSS")

    css_group.add_argument(
        "--generate-css",
        action="store_true",
        help="Générer un fichier CSS pour les classes personnalisées trouvées dans le document",
    )

    css_group.add_argument(
        "--css-output",
        type=str,
        metavar="FICHIER",
        help="Chemin du fichier CSS à générer (par défaut: même nom que le JSON avec extension .css)",
    )

    css_group.add_argument(
        "--css-styles",
        type=str,
        metavar="FICHIER",
        help="Chemin vers un fichier JSON contenant des styles CSS personnalisés",
    )


def handle_css_generation(
    args: argparse.Namespace, json_path: str
) -> Optional[Set[str]]:
    """
    Traite les options de génération CSS si elles sont activées.

    Args:
        args: Les arguments de ligne de commande analysés
        json_path: Le chemin du fichier JSON généré

    Returns:
        Un ensemble des classes CSS trouvées dans le document, ou None si
        la génération CSS n'est pas activée
    """
    if not args.generate_css:
        return None

    # Déterminer le chemin du fichier CSS de sortie
    css_path = args.css_output
    if not css_path:
        css_path = os.path.splitext(json_path)[0] + ".css"

    # Charger les styles personnalisés si spécifiés
    custom_styles = None
    if args.css_styles:
        custom_styles = load_custom_styles(args.css_styles)

    # Générer le CSS
    try:
        classes = process_json_file(json_path, css_path, custom_styles)
        logging.info(f"CSS généré avec succès: {css_path}")
        print(f"CSS généré avec succès: {css_path}")

        # Afficher un résumé des classes trouvées
        if classes:
            class_list = ", ".join(sorted(classes))
            logging.info(f"Classes trouvées: {class_list}")
            if args.verbose:
                print(f"Classes trouvées: {class_list}")
        else:
            logging.info("Aucune classe personnalisée trouvée dans le document")
            if args.verbose:
                print("Aucune classe personnalisée trouvée dans le document")

        return classes

    except Exception as e:
        logging.error(f"Erreur lors de la génération du CSS: {str(e)}")
        print(f"Erreur lors de la génération du CSS: {str(e)}")
        return None


def create_example_styles_file(path: str) -> None:
    """
    Crée un fichier d'exemple de styles CSS personnalisés.

    Args:
        path: Le chemin où enregistrer le fichier d'exemple
    """
    example_styles = {
        "hero": """
        font-size: 3rem;
        font-weight: bold;
        color: #007bff;
        margin-bottom: 2rem;
        text-align: center;
        text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.2);
        """,
        "card": """
        background-color: #fff;
        border-radius: 0.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        padding: 2rem;
        margin-bottom: 2rem;
        transition: transform 0.3s ease;
        """,
    }

    import json

    with open(path, "w", encoding="utf-8") as f:
        json.dump(example_styles, f, indent=2)

    print(f"Fichier d'exemple de styles créé: {path}")
    print("Vous pouvez modifier ce fichier puis l'utiliser avec --css-styles")
