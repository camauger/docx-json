#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module principal pour la conversion de fichiers DOCX en JSON/HTML
Ce module fournit une compatibilité avec l'ancienne API tout en utilisant
la nouvelle implémentation orientée objet.
"""

import json
import logging
import os
import sys
from typing import Any, Dict, List, Optional

# Importer les fonctions de compatibilité
from docx_json.core.compatibility import (
    create_element_from_dict,
    extract_images,
    generate_html,
    get_document_json,
    get_paragraph_json,
    get_table_json,
    process_instructions,
)
from docx_json.utils.logging import setup_logging


def parse_args() -> Dict[str, Any]:
    """
    Parse les arguments de la ligne de commande

    Returns:
        Un dictionnaire contenant les options
    """
    args = {
        "docx_path": None,
        "generate_json": False,
        "generate_html": False,
        "generate_markdown": False,
        "save_images": True,  # Par défaut, les images sont sauvegardées
        "verbose": False,
    }

    if len(sys.argv) < 2 or "--help" in sys.argv or "-h" in sys.argv:
        print(
            "Usage: python convert.py <fichier.docx> [--json] [--html] [--md] [--no-save-images] [--verbose]"
        )
        print("\nOptions:")
        print("  --json           Génère un fichier JSON")
        print("  --html           Génère un fichier HTML")
        print("  --md             Génère un fichier Markdown")
        print(
            "  --no-save-images Encode les images en base64 au lieu de les sauvegarder comme fichiers"
        )
        print("  --verbose        Affiche des messages de debug")
        print("\nExemple:")
        print("  python convert.py mon-document.docx --json --html --md")
        sys.exit(0 if "--help" in sys.argv or "-h" in sys.argv else 1)

    # Le premier argument est le chemin du fichier
    args["docx_path"] = sys.argv[1]

    # Options
    args["generate_json"] = "--json" in sys.argv
    args["generate_html"] = "--html" in sys.argv
    args["generate_markdown"] = "--md" in sys.argv
    args["verbose"] = "--verbose" in sys.argv
    args["save_images"] = "--no-save-images" not in sys.argv

    # Si aucune option de sortie n'est spécifiée, générer le JSON par défaut
    if (
        not args["generate_json"]
        and not args["generate_html"]
        and not args["generate_markdown"]
    ):
        args["generate_json"] = True

    return args


def main() -> None:
    """
    Fonction principale: traite les arguments de ligne de commande et
    effectue la conversion
    """
    # Traiter les arguments
    args = parse_args()

    # Configurer le logging
    setup_logging(args["verbose"])

    docx_path = args["docx_path"]
    generate_json = args["generate_json"]
    generate_html_output = args["generate_html"]
    generate_markdown = args["generate_markdown"]
    save_images = args["save_images"]

    # Vérifier que le fichier existe et a l'extension .docx
    if not os.path.exists(docx_path):
        logging.error(f"Le fichier '{docx_path}' n'existe pas.")
        print(f"Erreur: Le fichier '{docx_path}' n'existe pas.")
        sys.exit(1)

    if not docx_path.lower().endswith(".docx"):
        logging.error(f"Le fichier '{docx_path}' n'est pas un fichier .docx.")
        print(f"Erreur: Le fichier '{docx_path}' n'est pas un fichier .docx.")
        sys.exit(1)

    # Noms des fichiers de sortie
    base_name = os.path.splitext(docx_path)[0]
    json_path = f"{base_name}.json"
    html_path = f"{base_name}.html"
    markdown_path = f"{base_name}.md"
    output_dir = os.path.dirname(os.path.abspath(docx_path))

    try:
        # Convertir le document
        logging.info(f"Traitement du fichier '{docx_path}'...")
        print(f"Traitement du fichier '{docx_path}'...")
        json_data = get_document_json(docx_path, output_dir, save_images)

        # Générer et sauvegarder le JSON si demandé
        if (
            generate_json or not generate_html_output
        ):  # Par défaut, génère le JSON si aucune option n'est spécifiée
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(json_data, f, ensure_ascii=False, indent=2)
            logging.info(f"Fichier JSON créé: '{json_path}'")
            print(f"Fichier JSON créé: '{json_path}'")

        # Générer et sauvegarder le HTML si demandé
        if generate_html_output:
            html_content = generate_html(json_data)
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            logging.info(f"Fichier HTML créé: '{html_path}'")
            print(f"Fichier HTML créé: '{html_path}'")

        # Générer et sauvegarder le Markdown si demandé
        if generate_markdown:
            markdown_content = generate_markdown(json_data)
            with open(markdown_path, "w", encoding="utf-8") as f:
                f.write(markdown_content)
            logging.info(f"Fichier Markdown créé: '{markdown_path}'")
            print(f"Fichier Markdown créé: '{markdown_path}'")

        logging.info("Conversion terminée avec succès!")
        print("Conversion terminée avec succès!")

    except Exception as e:
        logging.exception("Erreur lors de la conversion")
        print(f"Erreur lors de la conversion: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
