#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Gestion des arguments de la ligne de commande
--------------------------------------------
"""

import argparse
from typing import Any, Dict, Tuple


def parse_args() -> argparse.Namespace:
    """
    Parse les arguments de la ligne de commande avec argparse

    Returns:
        argparse.Namespace: Un objet Namespace contenant les options
    """
    parser = argparse.ArgumentParser(
        description="Convertit des fichiers DOCX en formats JSON, HTML et/ou Markdown",
        epilog="Exemple: python -m docx_json mon-document.docx --json --html --md",
    )

    parser.add_argument(
        "input_file",
        help="Chemin vers le fichier d'entrée (.docx) ou dossier si --batch est utilisé",
    )

    # Formats de sortie
    output_group = parser.add_argument_group("Formats de sortie")
    output_group.add_argument(
        "--json", action="store_true", help="Génère un fichier JSON"
    )
    output_group.add_argument(
        "--html", action="store_true", help="Génère un fichier HTML"
    )
    output_group.add_argument(
        "--md", action="store_true", help="Génère un fichier Markdown"
    )

    # Options avancées
    advanced_group = parser.add_argument_group("Options avancées")
    advanced_group.add_argument(
        "--output-dir",
        help="Dossier de destination (par défaut: même dossier que le fichier source)",
    )
    advanced_group.add_argument(
        "--output-prefix", help="Préfixe pour les fichiers de sortie"
    )
    advanced_group.add_argument(
        "--output-suffix", help="Suffixe pour les fichiers de sortie"
    )
    advanced_group.add_argument(
        "--no-save-images",
        action="store_true",
        help="Encode les images en base64 au lieu de les sauvegarder comme fichiers",
    )
    advanced_group.add_argument(
        "--css", help="Fichier CSS à utiliser pour le HTML généré"
    )
    advanced_group.add_argument(
        "--batch",
        action="store_true",
        help="Traite tous les fichiers .docx du dossier source",
    )
    advanced_group.add_argument(
        "--recursive",
        action="store_true",
        help="En mode batch, recherche récursivement dans les sous-dossiers",
    )
    advanced_group.add_argument(
        "--quiet",
        action="store_true",
        help="Mode silencieux (n'affiche que les erreurs)",
    )
    advanced_group.add_argument(
        "--skip-existing",
        action="store_true",
        help="Ignore les fichiers déjà convertis (basé sur les dates de modification)",
    )
    advanced_group.add_argument(
        "--force",
        action="store_true",
        help="Force la conversion même si les fichiers de sortie existent déjà",
    )

    parser.add_argument(
        "--verbose", action="store_true", help="Affiche des messages de debug détaillés"
    )

    args = parser.parse_args()

    # Si aucun format de sortie n'est spécifié, activer JSON par défaut
    if not (args.json or args.html or args.md):
        args.json = True

    return args


def get_conversion_formats(args: argparse.Namespace) -> Tuple[bool, bool, bool]:
    """
    Extrait les formats demandés des arguments de l'utilisateur

    Args:
        args: Arguments de la ligne de commande

    Returns:
        Tuple de booléens (json, html, markdown)
    """
    return (args.json, args.html, args.md)
