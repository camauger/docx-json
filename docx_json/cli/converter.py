#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module de conversion d'un fichier DOCX individuel
------------------------------------------------
"""

import argparse
import json
import logging
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from docx_json.cli.css_command import handle_css_generation
from docx_json.core.compatibility import (
    generate_html,
    generate_markdown,
    generate_multi_page_html,
    get_document_json,
    validate_docx,
)
from docx_json.exceptions import ConversionError, DocxValidationError


def get_output_paths(
    docx_path: str,
    output_dir: Optional[str] = None,
    prefix: Optional[str] = None,
    suffix: Optional[str] = None,
    formats: Tuple[bool, bool, bool] = (True, False, False),
) -> Dict[str, str]:
    """
    Génère les chemins des fichiers de sortie.

    Args:
        docx_path: Chemin vers le fichier DOCX
        output_dir: Dossier de destination (optionnel)
        prefix: Préfixe pour les noms de fichiers (optionnel)
        suffix: Suffixe pour les noms de fichiers (optionnel)
        formats: Tuple de booléens (json, html, markdown)

    Returns:
        Dict[str, str]: Dictionnaire avec les chemins de sortie
    """
    # Utiliser Path pour une meilleure manipulation des chemins
    input_path = Path(docx_path)
    base_name: str = input_path.stem

    # Appliquer préfixe et suffixe si spécifiés
    if prefix:
        base_name = f"{prefix}{base_name}"
    if suffix:
        base_name = f"{base_name}{suffix}"

    # Déterminer le dossier de sortie
    out_dir: Path = Path(output_dir) if output_dir else input_path.parent

    # Créer le dossier de sortie s'il n'existe pas
    out_dir.mkdir(parents=True, exist_ok=True)

    # Générer les chemins
    paths: Dict[str, str] = {}
    if formats[0]:  # JSON
        paths["json"] = str(out_dir / f"{base_name}.json")
    if formats[1]:  # HTML
        paths["html"] = str(out_dir / f"{base_name}.html")
    if formats[2]:  # Markdown
        paths["markdown"] = str(out_dir / f"{base_name}.md")

    return paths


def needs_conversion(input_path: str, output_path: str) -> bool:
    """
    Vérifie si le fichier de sortie doit être régénéré.

    Args:
        input_path: Chemin du fichier d'entrée
        output_path: Chemin du fichier de sortie

    Returns:
        bool: True si le fichier de sortie n'existe pas ou est plus ancien que l'entrée
    """
    # Si le fichier de sortie n'existe pas, conversion nécessaire
    if not os.path.exists(output_path):
        return True

    # Comparer les dates de modification
    input_mtime: float = os.path.getmtime(input_path)
    output_mtime: float = os.path.getmtime(output_path)

    # Si le fichier d'entrée est plus récent, conversion nécessaire
    return input_mtime > output_mtime


def convert_file(
    docx_path: str,
    output_dir: Optional[str] = None,
    prefix: Optional[str] = None,
    suffix: Optional[str] = None,
    formats: Tuple[bool, bool, bool] = (True, False, False),
    save_images: bool = True,
    css_path: Optional[str] = None,
    css_styles: Optional[str] = None,
    generate_css: bool = False,
    skip_existing: bool = False,
    force: bool = False,
    quiet: bool = False,
    multipage: bool = False,
    verbose: bool = False,
) -> bool:
    """
    Convertit un fichier DOCX dans les formats demandés.

    Args:
        docx_path: Chemin du fichier DOCX
        output_dir: Dossier de destination
        prefix: Préfixe pour les noms de fichiers
        suffix: Suffixe pour les noms de fichiers
        formats: Formats à générer (json, html, markdown)
        save_images: Si True, sauvegarde les images extraites
        css_path: Chemin vers un fichier CSS personnalisé
        css_styles: Chemin vers un fichier JSON avec styles CSS personnalisés
        generate_css: Si True, génère un fichier CSS
        skip_existing: Ignore les fichiers déjà convertis
        force: Force la reconversion même si les fichiers existent
        quiet: Mode silencieux
        multipage: Si True, génère plusieurs fichiers HTML aux sauts de page
        verbose: Si True, affiche des messages de détail

    Returns:
        bool: True si la conversion a réussi
    """
    try:
        # Générer les chemins de sortie
        output_paths: Dict[str, str] = get_output_paths(
            docx_path, output_dir, prefix, suffix, formats
        )

        # Vérifier si les fichiers existent déjà et si on doit les ignorer
        if skip_existing and not force:
            all_exist = True
            for fmt, path in output_paths.items():
                if needs_conversion(docx_path, path):
                    all_exist = False
                    break

            if all_exist:
                if not quiet:
                    print(f"Fichier '{docx_path}' déjà converti, ignoré.")
                logging.info(f"Fichier '{docx_path}' déjà converti, ignoré.")
                return True

        # Valider le fichier DOCX
        if not validate_docx(docx_path):
            raise DocxValidationError(
                f"Le fichier '{docx_path}' n'est pas un fichier DOCX valide."
            )

        # Mesurer le temps de traitement
        start_time = time.time()

        if not quiet:
            print(f"Traitement du fichier '{docx_path}'...")
        logging.info(f"Traitement du fichier '{docx_path}'...")

        # Convertir le document
        json_data: Dict[str, Any] = get_document_json(
            docx_path, output_dir, save_images
        )

        # Générer et sauvegarder le JSON si demandé
        if formats[0]:  # JSON
            with open(output_paths["json"], "w", encoding="utf-8") as f:
                json.dump(json_data, f, ensure_ascii=False, indent=2)
            if not quiet:
                print(f"Fichier JSON créé: '{output_paths['json']}'")
            logging.info(f"Fichier JSON créé: '{output_paths['json']}'")

        # Générer et sauvegarder le HTML si demandé
        if formats[1]:  # HTML
            if multipage:
                # Déterminer le nom de base pour les fichiers HTML
                html_base_name = os.path.splitext(
                    os.path.basename(output_paths["html"])
                )[0]
                # Utiliser le répertoire de sortie
                html_output_dir = os.path.dirname(output_paths["html"])

                # S'assurer que le répertoire de sortie est valide
                if not html_output_dir:
                    html_output_dir = os.path.dirname(docx_path)
                if not html_output_dir:
                    html_output_dir = "."

                # Générer plusieurs fichiers HTML
                html_files = generate_multi_page_html(
                    json_data, html_output_dir, html_base_name, css_path
                )

                if not quiet:
                    print(
                        f"{len(html_files)} fichiers HTML créés dans: '{html_output_dir}'"
                    )
                    for html_file in html_files:
                        print(f"  - '{os.path.basename(html_file)}'")
                logging.info(
                    f"{len(html_files)} fichiers HTML créés dans: '{html_output_dir}'"
                )
            else:
                # Générer un seul fichier HTML
                html_content = generate_html(json_data, css_path=css_path)
                with open(output_paths["html"], "w", encoding="utf-8") as f:
                    f.write(html_content)
                if not quiet:
                    print(f"Fichier HTML créé: '{output_paths['html']}'")
                logging.info(f"Fichier HTML créé: '{output_paths['html']}'")

        # Générer et sauvegarder le Markdown si demandé
        if formats[2]:  # Markdown
            markdown_content = generate_markdown(json_data)
            with open(output_paths["markdown"], "w", encoding="utf-8") as f:
                f.write(markdown_content)
            if not quiet:
                print(f"Fichier Markdown créé: '{output_paths['markdown']}'")
            logging.info(f"Fichier Markdown créé: '{output_paths['markdown']}'")

        # Après avoir généré le JSON, vérifier si on doit générer le CSS
        if generate_css and output_paths.get("json"):
            # Créer un namespace pour les arguments de génération CSS
            css_args = argparse.Namespace()
            css_args.generate_css = generate_css
            css_args.css_output = css_path
            css_args.css_styles = css_styles
            css_args.verbose = verbose

            handle_css_generation(css_args, output_paths["json"])

        # Afficher le temps de traitement
        elapsed_time = time.time() - start_time
        if not quiet:
            print(f"Conversion terminée en {elapsed_time:.2f} secondes.")
        logging.info(f"Conversion terminée en {elapsed_time:.2f} secondes.")

        return True

    except DocxValidationError as e:
        logging.error(f"Erreur de validation: {str(e)}")
        if not quiet:
            print(f"Erreur de validation: {str(e)}")
        return False

    except ConversionError as e:
        logging.error(f"Erreur de conversion: {str(e)}")
        if not quiet:
            print(f"Erreur de conversion: {str(e)}")
        return False

    except Exception as e:
        logging.exception("Erreur inattendue lors de la conversion")
        if not quiet:
            print(f"Erreur inattendue: {str(e)}")
        return False


# Exemples d'usage

if __name__ == "__main__":
    # Exemple de conversion d'un fichier DOCX
    docx_path = "chemin/vers/votre/document.docx"
    output_dir = "chemin/vers/dossier/sortie"
    formats = (True, True, True)  # JSON, HTML, Markdown

    convert_file(docx_path, output_dir, formats=formats)
