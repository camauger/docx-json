#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Point d'entrée principal pour la ligne de commande docx_json
-----------------------------------------------------------
"""

import argparse
import logging
import os
import sys
from typing import Tuple

from docx_json.cli.arguments import get_conversion_formats, parse_args
from docx_json.cli.batch import process_batch
from docx_json.cli.converter import convert_file
from docx_json.utils.logging import setup_logging


def main() -> int:
    """
    Fonction principale: traite les arguments de ligne de commande et
    effectue la conversion.

    Returns:
        int: Code de sortie (0 pour succès, 1 pour erreur)
    """
    # Traiter les arguments
    args: argparse.Namespace = parse_args()

    # Configurer le logging
    setup_logging(args.verbose)

    # Variables communes
    input_path: str = args.input_file
    output_dir: str = args.output_dir
    save_images: bool = not args.no_save_images
    formats: Tuple[bool, bool, bool] = get_conversion_formats(args)

    # Vérifier que le chemin d'entrée existe
    if not os.path.exists(input_path):
        logging.error(f"Le chemin '{input_path}' n'existe pas.")
        print(f"Erreur: Le chemin '{input_path}' n'existe pas.")
        return 1

    # Mode traitement par lot
    if args.batch:
        success_count, total_count = process_batch(
            input_path,
            output_dir=output_dir,
            prefix=args.output_prefix,
            suffix=args.output_suffix,
            formats=formats,
            save_images=save_images,
            css_path=args.css,
            skip_existing=args.skip_existing,
            force=args.force,
            recursive=args.recursive,
            quiet=args.quiet,
            multipage=args.multipage,
        )

        # Si aucun fichier trouvé, ce n'est pas forcément une erreur
        if total_count == 0:
            return 0

        # Si tous les fichiers ont été convertis avec succès, retourner 0
        return 0 if success_count == total_count else 1

    else:
        # Mode fichier unique
        if not os.path.isfile(input_path):
            logging.error(f"Le chemin '{input_path}' n'est pas un fichier.")
            print(f"Erreur: Le chemin '{input_path}' n'est pas un fichier.")
            return 1

        if not input_path.lower().endswith(".docx"):
            logging.error(f"Le fichier '{input_path}' n'est pas un fichier .docx.")
            print(f"Erreur: Le fichier '{input_path}' n'est pas un fichier .docx.")
            return 1

        # Convertir le fichier
        success: bool = convert_file(
            input_path,
            output_dir=output_dir,
            prefix=args.output_prefix,
            suffix=args.output_suffix,
            formats=formats,
            save_images=save_images,
            css_path=args.css,
            skip_existing=args.skip_existing,
            force=args.force,
            quiet=args.quiet,
            multipage=args.multipage,
        )

        return 0 if success else 1


if __name__ == "__main__":
    try:
        exit_code: int = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\nOpération annulée par l'utilisateur.")
        logging.info("Opération annulée par l'utilisateur.")
        sys.exit(130)
    except Exception as e:
        print(f"Erreur critique: {str(e)}")
        logging.exception("Erreur critique non gérée")
        sys.exit(1)
