#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Gestion des arguments de la ligne de commande
--------------------------------------------
"""

import argparse
from typing import Any, Dict


def parse_args() -> Dict[str, Any]:
    """Parse les arguments de la ligne de commande.

    Returns:
        Un dictionnaire contenant les options
    """
    parser = argparse.ArgumentParser(
        description="Convertit un fichier DOCX en JSON et/ou HTML"
    )

    parser.add_argument("docx_path", help="Chemin vers le fichier .docx à convertir")

    parser.add_argument("--json", action="store_true", help="Génère un fichier JSON")

    parser.add_argument("--html", action="store_true", help="Génère un fichier HTML")

    parser.add_argument("--md", action="store_true", help="Génère un fichier Markdown")

    parser.add_argument(
        "--no-save-images",
        action="store_true",
        help="Ne sauvegarde pas les images (utilise base64 à la place)",
    )

    parser.add_argument(
        "--verbose", action="store_true", help="Affiche des messages de debug"
    )

    args = parser.parse_args()

    # Si aucune option de sortie n'est spécifiée, générer le JSON par défaut
    if not args.json and not args.html and not args.md:
        args.json = True

    return {
        "docx_path": args.docx_path,
        "generate_json": args.json,
        "generate_html": args.html,
        "generate_markdown": args.md,
        "save_images": not args.no_save_images,
        "verbose": args.verbose,
    }
