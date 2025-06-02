#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Module contenant l'interface en ligne de commande pour docx-json."""

import argparse
import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, cast

from docx_json import __version__
from docx_json.core.compatibility import generate_html, generate_markdown
from docx_json.core.converter import DocxConverter
from docx_json.core.converter_functions import convert_docx_to_markdown
from docx_json.core.html_renderer import HTMLGenerator
from docx_json.exceptions import DocxValidationError


def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse les arguments de la ligne de commande."""
    parser = argparse.ArgumentParser(
        description="Convertit des fichiers DOCX en JSON, HTML ou Markdown"
    )
    parser.add_argument(
        "docx_files",
        nargs="+",
        help="Fichier(s) DOCX à convertir ou dossier(s) si --recursive est utilisé",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Génère un fichier JSON",
    )
    parser.add_argument(
        "--html",
        action="store_true",
        help="Génère un fichier HTML",
    )
    parser.add_argument(
        "--md",
        action="store_true",
        help="Génère un fichier Markdown",
    )
    parser.add_argument(
        "--output-dir",
        default=".",
        help="Répertoire de sortie pour les fichiers générés",
    )
    parser.add_argument(
        "--no-save-images",
        action="store_true",
        help="Encode les images en base64 au lieu de les sauvegarder",
    )
    parser.add_argument(
        "--standalone",
        action="store_true",
        help="Génère un document Markdown autonome avec métadonnées",
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Convertit récursivement tous les fichiers DOCX des dossiers spécifiés",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Affiche des messages de debug détaillés",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    return parser.parse_args(args)


def get_docx_files(paths: List[str], recursive: bool = False) -> List[str]:
    """
    Récupère la liste des fichiers DOCX à partir des chemins spécifiés.

    Args:
        paths: Liste des chemins (fichiers ou dossiers)
        recursive: Si True, recherche récursivement dans les dossiers

    Returns:
        Liste des chemins des fichiers DOCX
    """
    docx_files = []

    for path in paths:
        path_obj = Path(path)
        if path_obj.is_file() and path_obj.suffix.lower() == ".docx":
            docx_files.append(str(path_obj))
        elif path_obj.is_dir() and recursive:
            # Recherche récursive des fichiers DOCX
            for docx_file in path_obj.rglob("*.docx"):
                docx_files.append(str(docx_file))
        elif path_obj.is_dir():
            # Recherche non récursive des fichiers DOCX
            for docx_file in path_obj.glob("*.docx"):
                docx_files.append(str(docx_file))

    return docx_files


def main(args: Optional[List[str]] = None) -> int:
    """Point d'entrée principal du programme."""
    parsed_args = parse_args(args)

    # Configurer le logging
    log_level = logging.DEBUG if parsed_args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(levelname)s: %(message)s",
    )

    # Vérifier qu'au moins un format de sortie est spécifié
    if not any([parsed_args.json, parsed_args.html, parsed_args.md]):
        logging.error(
            "Veuillez spécifier au moins un format de sortie (--json, --html, ou --md)"
        )
        return 1

    # Créer le répertoire de sortie s'il n'existe pas
    os.makedirs(parsed_args.output_dir, exist_ok=True)

    # Récupérer la liste des fichiers DOCX à convertir
    docx_files = get_docx_files(parsed_args.docx_files, parsed_args.recursive)

    if not docx_files:
        logging.error("Aucun fichier DOCX trouvé dans les chemins spécifiés")
        return 1

    # Traiter chaque fichier DOCX
    for docx_file in docx_files:
        try:
            # Créer un sous-dossier de sortie basé sur le chemin relatif du fichier
            if parsed_args.recursive:
                rel_path = os.path.relpath(
                    os.path.dirname(docx_file),
                    os.path.commonpath(parsed_args.docx_files),
                )
                file_output_dir = os.path.join(parsed_args.output_dir, rel_path)
                os.makedirs(file_output_dir, exist_ok=True)
            else:
                file_output_dir = parsed_args.output_dir

            base_name = os.path.splitext(os.path.basename(docx_file))[0]

            # Conversion en JSON
            converter = DocxConverter(
                docx_file, file_output_dir, not parsed_args.no_save_images
            )
            json_data = converter.convert()

            if parsed_args.json:
                json_path = os.path.join(file_output_dir, f"{base_name}.json")
                with open(json_path, "w", encoding="utf-8") as f:
                    json.dump(json_data, f, ensure_ascii=False, indent=2)
                logging.info(f"Fichier JSON généré: {json_path}")

            # Conversion en HTML
            if parsed_args.html:
                html_path = os.path.join(file_output_dir, f"{base_name}.html")
                html_generator = HTMLGenerator(json_data)
                html_content = html_generator.generate()
                with open(html_path, "w", encoding="utf-8") as f:
                    f.write(html_content)
                logging.info(f"Fichier HTML généré: {html_path}")

            # Conversion en Markdown
            if parsed_args.md:
                md_path = os.path.join(file_output_dir, f"{base_name}.md")
                convert_docx_to_markdown(
                    docx_file,
                    output_path=md_path,
                    standalone=parsed_args.standalone,
                    extract_images=not parsed_args.no_save_images,
                )
                logging.info(f"Fichier Markdown généré: {md_path}")

        except DocxValidationError as e:
            logging.error(f"Erreur de validation pour {docx_file}: {str(e)}")
            return 1
        except Exception as e:
            logging.error(f"Erreur lors du traitement de {docx_file}: {str(e)}")
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
