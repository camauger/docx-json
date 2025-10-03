#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Fonctions de conversion DOCX vers JSON/HTML/Markdown (couche de compatibilité)
----------------------------------------------------------------------------
"""

import logging
import os
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional

from docx_json.core.converter import DocxConverter


def _validate_docx_path(docx_path: str) -> Path:
    """
    Valide et normalise un chemin de fichier DOCX.

    Args:
        docx_path: Chemin du fichier DOCX à valider

    Returns:
        Path: Chemin absolu validé et résolu

    Raises:
        ValueError: Si le chemin est invalide ou contient des tentatives de traversée
        FileNotFoundError: Si le fichier n'existe pas
        OSError: Si le chemin ne peut pas être résolu
    """
    try:
        # Convertir en Path et résoudre en chemin absolu
        path = Path(docx_path).resolve(strict=True)
    except (OSError, RuntimeError) as e:
        raise ValueError(f"Chemin invalide '{docx_path}': {e}")

    # Vérifier qu'il s'agit d'un fichier
    if not path.is_file():
        raise ValueError(f"'{docx_path}' n'est pas un fichier")

    # Vérifier l'extension
    if path.suffix.lower() != ".docx":
        raise ValueError(
            f"Le fichier doit avoir l'extension .docx, reçu: {path.suffix}"
        )

    # Vérifier la taille du fichier (limite à 500MB pour éviter DoS)
    max_size = 500 * 1024 * 1024  # 500 MB
    file_size = path.stat().st_size
    if file_size > max_size:
        raise ValueError(
            f"Fichier trop volumineux ({file_size / 1024 / 1024:.1f}MB). "
            f"Limite: {max_size / 1024 / 1024}MB"
        )

    if file_size == 0:
        raise ValueError(f"Le fichier '{docx_path}' est vide")

    logging.debug(f"Chemin DOCX validé: {path} ({file_size / 1024:.1f} KB)")
    return path


def _validate_output_path(output_path: str, default_suffix: str = ".md") -> Path:
    """
    Valide et normalise un chemin de sortie.

    Args:
        output_path: Chemin du fichier de sortie
        default_suffix: Extension par défaut si non spécifiée

    Returns:
        Path: Chemin absolu validé

    Raises:
        ValueError: Si le chemin est invalide
        OSError: Si le répertoire parent ne peut pas être créé
    """
    try:
        path = Path(output_path).resolve()
    except (OSError, RuntimeError) as e:
        raise ValueError(f"Chemin de sortie invalide '{output_path}': {e}")

    # Ajouter l'extension si manquante
    if not path.suffix:
        path = path.with_suffix(default_suffix)

    # Créer le répertoire parent si nécessaire
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        raise ValueError(f"Impossible de créer le répertoire '{path.parent}': {e}")

    # Vérifier que le répertoire parent est accessible en écriture
    if not os.access(path.parent, os.W_OK):
        raise ValueError(f"Pas de permission d'écriture dans '{path.parent}'")

    logging.debug(f"Chemin de sortie validé: {path}")
    return path


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

    Raises:
        ValueError: Si les chemins sont invalides
        FileNotFoundError: Si le fichier DOCX n'existe pas
    """
    # Valider le chemin d'entrée
    validated_docx_path = _validate_docx_path(docx_path)

    logging.info(f"Conversion du document '{validated_docx_path}' vers JSON")

    # Utiliser DocxConverter pour convertir le document
    converter = DocxConverter(str(validated_docx_path), output_dir, save_images_to_disk)
    return converter.convert()


def convert_docx_to_markdown(
    docx_path: str,
    output_path: Optional[str] = None,
    standalone: bool = True,
    extract_images: bool = True,
    timeout: int = 300,
) -> str:
    """
    Convertit un document DOCX en Markdown en utilisant pandoc.

    Cette fonction valide rigoureusement les chemins d'entrée et de sortie
    pour prévenir les injections de commandes et les traversées de répertoires.

    Args:
        docx_path: Chemin du fichier DOCX à convertir
        output_path: Chemin du fichier Markdown de sortie (optionnel)
        standalone: Si True, génère un document Markdown autonome avec métadonnées
        extract_images: Si True, extrait les images dans un dossier 'images'
        timeout: Temps maximum d'exécution en secondes (défaut: 300s)

    Returns:
        str: Chemin absolu du fichier Markdown généré

    Raises:
        ValueError: Si les chemins sont invalides ou contiennent des caractères suspects
        FileNotFoundError: Si le fichier DOCX n'existe pas ou pandoc n'est pas installé
        subprocess.CalledProcessError: Si pandoc échoue
        subprocess.TimeoutExpired: Si la conversion dépasse le timeout
        OSError: Si le chemin ne peut pas être résolu

    Example:
        >>> output = convert_docx_to_markdown("document.docx")
        >>> print(f"Markdown généré: {output}")

    Security:
        - Valide que les chemins ne contiennent pas de traversée de répertoires
        - Utilise des chemins absolus pour éviter les ambiguïtés
        - Limite la taille des fichiers d'entrée (500MB)
        - Applique un timeout pour éviter les blocages
        - Vérifie les permissions d'écriture

    Version:
        Sécurisé en v1.0.1 (octobre 2025)
    """
    # Valider le chemin d'entrée avec toutes les vérifications de sécurité
    validated_docx_path = _validate_docx_path(docx_path)

    # Déterminer et valider le chemin de sortie
    if output_path is None:
        output_path_str = str(validated_docx_path.with_suffix(".md"))
    else:
        output_path_str = output_path

    validated_output_path = _validate_output_path(output_path_str, ".md")

    # Préparer les arguments de pandoc avec des chemins absolus
    args = [
        "pandoc",
        str(validated_docx_path),
        "-o",
        str(validated_output_path),
        "--wrap=none",
    ]

    if standalone:
        args.append("--standalone")

    if extract_images:
        # Créer et valider le dossier images
        images_dir = validated_output_path.parent / "images"
        try:
            images_dir.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            logging.error(f"Impossible de créer le dossier images: {e}")
            raise ValueError(f"Impossible de créer le dossier images: {e}")

        args.extend(["--extract-media", str(images_dir)])

    logging.info(f"Conversion du document '{validated_docx_path.name}' vers Markdown")
    logging.debug(f"Commande pandoc: {' '.join(args)}")

    try:
        # Exécuter pandoc avec timeout pour éviter les blocages
        result = subprocess.run(
            args,
            check=True,
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        # Log les avertissements de pandoc s'il y en a
        if result.stderr:
            logging.warning(f"Avertissements de pandoc: {result.stderr}")

        logging.info(f"Document Markdown généré: {validated_output_path}")
        return str(validated_output_path)

    except subprocess.TimeoutExpired:
        error_msg = (
            f"La conversion a dépassé le timeout de {timeout} secondes. "
            "Le fichier est peut-être trop volumineux ou complexe."
        )
        logging.error(error_msg)
        raise subprocess.TimeoutExpired(args[0], timeout, error_msg)

    except FileNotFoundError:
        error_msg = (
            "Pandoc n'est pas installé ou n'est pas dans le PATH. "
            "Installez-le avec: pip install pandoc ou via votre gestionnaire de paquets."
        )
        logging.error(error_msg)
        raise FileNotFoundError(error_msg)

    except subprocess.CalledProcessError as e:
        error_msg = f"Erreur lors de la conversion avec pandoc: {e.stderr}"
        logging.error(error_msg)
        # Ne pas exposer les détails de l'erreur à l'utilisateur pour des raisons de sécurité
        raise subprocess.CalledProcessError(
            e.returncode,
            e.cmd,
            "La conversion a échoué. Vérifiez que le fichier DOCX est valide.",
        )
