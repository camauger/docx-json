#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module de traitement par lot des fichiers DOCX
---------------------------------------------
"""

import logging
import os
from pathlib import Path
from typing import List, Optional, Tuple

from tqdm import tqdm

from docx_json.cli.converter import convert_file


def find_docx_files(directory: str, recursive: bool = False) -> List[str]:
    """
    Trouve tous les fichiers DOCX dans un dossier.

    Args:
        directory: Chemin du dossier à scanner
        recursive: Si True, parcourt aussi les sous-dossiers

    Returns:
        List[str]: Liste des chemins des fichiers DOCX trouvés
    """
    docx_files = []
    directory_path = Path(directory)

    # Déterminer le modèle de recherche en fonction du mode récursif
    if recursive:
        # Utiliser glob récursif pour trouver tous les fichiers .docx
        docx_files = [str(p) for p in directory_path.glob("**/*.docx")]
    else:
        # Seulement le dossier principal
        docx_files = [str(p) for p in directory_path.glob("*.docx")]

    return docx_files


def process_batch(
    input_dir: str,
    output_dir: Optional[str] = None,
    prefix: Optional[str] = None,
    suffix: Optional[str] = None,
    formats: Tuple[bool, bool, bool] = (True, False, False),
    save_images: bool = True,
    css_path: Optional[str] = None,
    skip_existing: bool = False,
    force: bool = False,
    recursive: bool = False,
    quiet: bool = False,
) -> Tuple[int, int]:
    """
    Traite tous les fichiers DOCX trouvés dans un dossier.

    Args:
        input_dir: Dossier contenant les fichiers DOCX
        output_dir: Dossier de destination
        prefix: Préfixe pour les noms de fichiers
        suffix: Suffixe pour les noms de fichiers
        formats: Formats à générer (json, html, markdown)
        save_images: Si True, sauvegarde les images extraites
        css_path: Chemin vers un fichier CSS personnalisé
        skip_existing: Ignore les fichiers déjà convertis
        force: Force la reconversion même si les fichiers existent
        recursive: Si True, parcourt aussi les sous-dossiers
        quiet: Mode silencieux

    Returns:
        Tuple[int, int]: Nombre de fichiers traités avec succès et nombre total
    """
    # Vérifier que le dossier d'entrée existe et est un dossier
    if not os.path.isdir(input_dir):
        logging.error(f"Pour le mode batch, '{input_dir}' doit être un dossier.")
        if not quiet:
            print(f"Erreur: Pour le mode batch, '{input_dir}' doit être un dossier.")
        return (0, 0)

    # Trouver tous les fichiers DOCX
    docx_files = find_docx_files(input_dir, recursive)

    if not docx_files:
        logging.warning(f"Aucun fichier DOCX trouvé dans '{input_dir}'.")
        if not quiet:
            print(f"Attention: Aucun fichier DOCX trouvé dans '{input_dir}'.")
        return (0, 0)

    # Afficher le nombre de fichiers trouvés
    if not quiet:
        print(f"Traitement de {len(docx_files)} fichiers DOCX...")
    logging.info(f"Traitement de {len(docx_files)} fichiers DOCX...")

    # Traiter chaque fichier avec une barre de progression
    success_count = 0
    with tqdm(total=len(docx_files), disable=quiet) as progress_bar:
        for docx_file in docx_files:
            if convert_file(
                docx_file,
                output_dir=output_dir,
                prefix=prefix,
                suffix=suffix,
                formats=formats,
                save_images=save_images,
                css_path=css_path,
                skip_existing=skip_existing,
                force=force,
                quiet=True,  # Mode silencieux pour les fichiers individuels
            ):
                success_count += 1
            progress_bar.update(1)
            progress_bar.set_description(f"Traité {progress_bar.n}/{len(docx_files)}")

    # Résumé
    if not quiet:
        print(
            f"Conversion terminée: {success_count}/{len(docx_files)} fichiers convertis avec succès."
        )
    logging.info(
        f"Conversion terminée: {success_count}/{len(docx_files)} fichiers convertis avec succès."
    )

    return (success_count, len(docx_files))
