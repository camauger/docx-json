#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Point d'entrée principal du package docx_json
---------------------------------------------
"""

import sys
import os
import json
import logging
import argparse
from typing import Dict, Any

from docx_json.core.converter import DocxConverter


def setup_logging(verbose: bool = False) -> None:
    """Configure le système de logging.

    Args:
        verbose: Si True, affiche les messages de debug
    """
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )


def parse_args() -> Dict[str, Any]:
    """Parse les arguments de la ligne de commande.

    Returns:
        Un dictionnaire contenant les options
    """
    parser = argparse.ArgumentParser(
        description="Convertit un fichier DOCX en JSON et/ou HTML"
    )

    parser.add_argument(
        "docx_path",
        help="Chemin vers le fichier .docx à convertir"
    )

    parser.add_argument(
        "--json",
        action="store_true",
        help="Génère un fichier JSON"
    )

    parser.add_argument(
        "--html",
        action="store_true",
        help="Génère un fichier HTML"
    )

    parser.add_argument(
        "--no-save-images",
        action="store_true",
        help="Ne sauvegarde pas les images (utilise base64 à la place)"
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Affiche des messages de debug"
    )

    args = parser.parse_args()

    # Si aucune option de sortie n'est spécifiée, générer le JSON par défaut
    if not args.json and not args.html:
        args.json = True

    return {
        "docx_path": args.docx_path,
        "generate_json": args.json,
        "generate_html": args.html,
        "save_images": not args.no_save_images,
        "verbose": args.verbose
    }


def main() -> None:
    """Fonction principale: traite les arguments et effectue la conversion."""
    # Traiter les arguments
    args = parse_args()

    # Configurer le logging
    setup_logging(args["verbose"])

    docx_path = args["docx_path"]
    generate_json = args["generate_json"]
    generate_html = args["generate_html"]
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

    # Obtenir le répertoire de sortie (même répertoire que le fichier .docx)
    output_dir = os.path.dirname(os.path.abspath(docx_path))
    if not output_dir:
        output_dir = "."

    # Noms des fichiers de sortie
    base_name = os.path.splitext(docx_path)[0]
    json_path = f"{base_name}.json"
    html_path = f"{base_name}.html"

    try:
        # Créer le convertisseur
        converter = DocxConverter(docx_path, output_dir, save_images)

        # Convertir le document en JSON
        logging.info(f"Traitement du fichier '{docx_path}'...")
        print(f"Traitement du fichier '{docx_path}'...")
        json_data = converter.convert()

        # Générer et sauvegarder le JSON si demandé
        if generate_json:
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, ensure_ascii=False, indent=2)
            logging.info(f"Fichier JSON créé: '{json_path}'")
            print(f"Fichier JSON créé: '{json_path}'")

        # Générer et sauvegarder le HTML si demandé
        if generate_html:
            html_content = converter.generate_html(json_data)
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            logging.info(f"Fichier HTML créé: '{html_path}'")
            print(f"Fichier HTML créé: '{html_path}'")

        logging.info("Conversion terminée avec succès!")
        print("Conversion terminée avec succès!")

    except Exception as e:
        logging.exception("Erreur lors de la conversion")
        print(f"Erreur lors de la conversion: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
