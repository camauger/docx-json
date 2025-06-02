#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Fonctions de conversion DOCX vers JSON/HTML/Markdown (couche de compatibilité)
----------------------------------------------------------------------------
"""

import logging
import os
import subprocess
from typing import Any, Dict, Optional

from docx_json.core.converter import DocxConverter


def convert_docx_to_json(
    docx_path: str, output_dir: str = ".", save_images_to_disk: bool = True
) -> Dict[str, Any]:
    """
    Convertit un document DOCX en structure JSON.

    Args:
        docx_path: Chemin du fichier DOCX
        output_dir: Répertoire de sortie pour les images
        save_images_to_disk: Si True, sauvegarde les images sur disque

    Returns:
        Dict: Dictionnaire JSON représentant le document
    """
    logging.info(f"Conversion du document '{docx_path}' vers JSON")

    # Utiliser DocxConverter pour convertir le document
    converter = DocxConverter(docx_path, output_dir, save_images_to_disk)
    return converter.convert()


def convert_docx_to_markdown(
    docx_path: str,
    output_path: Optional[str] = None,
    standalone: bool = True,
    extract_images: bool = True,
) -> str:
    """
    Convertit un document DOCX en Markdown en utilisant pandoc.

    Args:
        docx_path: Chemin du fichier DOCX à convertir
        output_path: Chemin du fichier Markdown de sortie (optionnel)
        standalone: Si True, génère un document Markdown autonome avec métadonnées
        extract_images: Si True, extrait les images dans un dossier 'images'

    Returns:
        str: Chemin du fichier Markdown généré

    Raises:
        FileNotFoundError: Si le fichier DOCX n'existe pas
        subprocess.CalledProcessError: Si pandoc n'est pas installé ou échoue
    """
    if not os.path.exists(docx_path):
        raise FileNotFoundError(f"Le fichier DOCX '{docx_path}' n'existe pas")

    # Déterminer le chemin de sortie si non spécifié
    if output_path is None:
        output_path = os.path.splitext(docx_path)[0] + ".md"

    # Préparer les arguments de pandoc
    args = ["pandoc", docx_path, "-o", output_path, "--wrap=none"]

    if standalone:
        args.append("--standalone")

    if extract_images:
        # Créer le dossier images s'il n'existe pas
        images_dir = os.path.join(os.path.dirname(output_path), "images")
        os.makedirs(images_dir, exist_ok=True)
        args.extend(["--extract-media", images_dir])

    logging.info(f"Conversion du document '{docx_path}' vers Markdown")

    try:
        # Exécuter pandoc
        subprocess.run(args, check=True, capture_output=True, text=True)
        logging.info(f"Document Markdown généré: {output_path}")
        return output_path
    except subprocess.CalledProcessError as e:
        logging.error(f"Erreur lors de la conversion: {e.stderr}")
        raise
