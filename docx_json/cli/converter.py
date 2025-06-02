#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module pour la conversion de fichiers DOCX.
"""

import argparse
import json
import logging
import os
import sys
import time
from typing import Any, Dict, Optional, Set, Tuple

from docx_json.cli.css_command import handle_css_generation
from docx_json.core.compatibility import (
    generate_html,
    generate_markdown,
    generate_multi_page_html,
    get_document_json,
    validate_docx,
)
from docx_json.core.converter_functions import convert_docx_to_json
from docx_json.core.html_generator import HTMLGenerator
from docx_json.core.processor import DocumentProcessor
from docx_json.exceptions import ConversionError, DocxValidationError
from docx_json.utils.comment_filter import filter_comments_from_json
from docx_json.utils.consignes_handler import process_consignes_in_html


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
    filter_comments: bool = True,
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
        filter_comments: Si True, filtre les commentaires délimités par ###

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
            docx_path, output_dir or ".", save_images
        )

        # Appliquer les transformations au document JSON (filtrage des commentaires)
        json_data = DocumentProcessor.process_document(json_data, filter_comments)

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
                    json_data,
                    output_dir=html_output_dir,
                    base_filename=html_base_name,
                    css_path=css_path,
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

                # Traiter les composants Consignes dans chaque fichier HTML
                for html_file in html_files:
                    try:
                        with open(html_file, "r", encoding="utf-8") as f:
                            html_content = f.read()

                        # Traiter les composants Consignes
                        html_with_consignes = process_consignes_in_html(html_content)

                        # Si des modifications ont été apportées, sauvegarder le fichier
                        if html_with_consignes != html_content:
                            with open(html_file, "w", encoding="utf-8") as f:
                                f.write(html_with_consignes)
                            logging.info(
                                f"Composants Consignes traités dans '{html_file}'"
                            )
                    except Exception as e:
                        logging.warning(
                            f"Erreur lors du traitement des composants Consignes dans '{html_file}': {str(e)}"
                        )
            else:
                # Générer un seul fichier HTML
                html_content = generate_html(json_data, css_path=css_path)

                # Traiter les composants Consignes
                html_with_consignes = process_consignes_in_html(html_content)

                with open(output_paths["html"], "w", encoding="utf-8") as f:
                    f.write(html_with_consignes)
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


def validate_docx(docx_path: str) -> bool:
    """
    Valide si le fichier est un DOCX valide.

    Args:
        docx_path: Chemin du fichier à valider

    Returns:
        bool: True si le fichier est valide
    """
    if not os.path.exists(docx_path):
        return False

    if not os.path.isfile(docx_path):
        return False

    if not docx_path.lower().endswith(".docx"):
        return False

    # Vérifier l'en-tête ZIP du fichier DOCX
    try:
        with open(docx_path, "rb") as f:
            # Les fichiers DOCX sont des archives ZIP - vérifier la signature ZIP
            # Les premiers octets d'un fichier ZIP sont 'PK' + des octets de version
            signature = f.read(4)
            return signature == b"PK\x03\x04"
    except:
        return False


def needs_conversion(source_path: str, target_path: str) -> bool:
    """
    Vérifie si un fichier source doit être converti en fichier cible.

    Args:
        source_path: Chemin du fichier source
        target_path: Chemin du fichier cible

    Returns:
        bool: True si la conversion est nécessaire
    """
    # Si le fichier cible n'existe pas, conversion nécessaire
    if not os.path.exists(target_path):
        return True

    # Si le fichier source est plus récent que le fichier cible, conversion nécessaire
    source_mtime = os.path.getmtime(source_path)
    target_mtime = os.path.getmtime(target_path)
    return source_mtime > target_mtime


def get_output_paths(
    docx_path: str,
    output_dir: Optional[str] = None,
    prefix: Optional[str] = None,
    suffix: Optional[str] = None,
    formats: Tuple[bool, bool, bool] = (True, False, False),
) -> Dict[str, str]:
    """
    Génère les chemins de sortie pour les différents formats.

    Args:
        docx_path: Chemin du fichier DOCX
        output_dir: Dossier de destination
        prefix: Préfixe pour les noms de fichiers
        suffix: Suffixe pour les noms de fichiers
        formats: Formats à générer (json, html, markdown)

    Returns:
        dict: Chemins de sortie pour chaque format
    """
    # Déterminer le répertoire de sortie
    if output_dir is None:
        output_dir = os.path.dirname(docx_path) or "."

    # Créer le répertoire de sortie s'il n'existe pas
    os.makedirs(output_dir, exist_ok=True)

    # Nom du fichier sans extension
    base_name = os.path.splitext(os.path.basename(docx_path))[0]

    # Ajouter préfixe et suffixe si nécessaire
    if prefix:
        base_name = f"{prefix}{base_name}"
    if suffix:
        base_name = f"{base_name}{suffix}"

    # Chemins de sortie pour les différents formats
    output_paths = {}

    # Ajouter les chemins de sortie selon les formats demandés
    if formats[0]:  # JSON
        output_paths["json"] = os.path.join(output_dir, f"{base_name}.json")
    if formats[1]:  # HTML
        output_paths["html"] = os.path.join(output_dir, f"{base_name}.html")
    if formats[2]:  # Markdown
        output_paths["markdown"] = os.path.join(output_dir, f"{base_name}.md")

    return output_paths


def get_document_json(
    docx_path: str, output_dir: str = ".", save_images_to_disk: bool = True
) -> Dict[str, Any]:
    """
    Obtient un dictionnaire JSON à partir d'un fichier DOCX.

    Args:
        docx_path: Chemin du fichier DOCX
        output_dir: Répertoire où sauvegarder les images
        save_images_to_disk: Si True, sauvegarde les images sur disque

    Returns:
        dict: Données JSON du document
    """
    try:
        from docx_json.core.docx_parser import DocxParser

        # Charger le document et extraire les éléments
        parser = DocxParser(docx_path, output_dir, save_images_to_disk)
        elements = parser.parse()
        images = parser.get_images()
        metadata = parser.metadata

        # Créer le JSON final
        json_output = {
            "meta": metadata,
            "content": elements,
            "images": images,
        }

        return json_output

    except Exception as e:
        raise ConversionError(f"Erreur lors de la conversion en JSON: {str(e)}")


def generate_html(json_data: Dict[str, Any], css_path: Optional[str] = None) -> str:
    """
    Génère un document HTML à partir des données JSON.

    Args:
        json_data: Données JSON du document
        css_path: Chemin vers un fichier CSS personnalisé

    Returns:
        str: Document HTML
    """
    try:
        from docx_json.core.html_generator import HTMLGenerator

        generator = HTMLGenerator(json_data)
        html = generator.generate(custom_css=css_path)
        return html

    except Exception as e:
        raise ConversionError(f"Erreur lors de la génération du HTML: {str(e)}")


def generate_multi_page_html(
    json_data: Dict[str, Any],
    output_dir: str,
    base_filename: str,
    css_path: Optional[str] = None,
) -> list:
    """
    Génère plusieurs fichiers HTML à partir des données JSON.

    Args:
        json_data: Données JSON du document
        output_dir: Répertoire de sortie
        base_filename: Nom de base pour les fichiers HTML
        css_path: Chemin vers un fichier CSS personnalisé

    Returns:
        list: Liste des chemins des fichiers générés
    """
    try:
        from docx_json.core.html_generator import HTMLGenerator

        generator = HTMLGenerator(json_data)
        files = generator.generate_multi_page(
            output_dir=output_dir, base_filename=base_filename, custom_css=css_path
        )
        return files

    except Exception as e:
        raise ConversionError(
            f"Erreur lors de la génération du HTML multi-pages: {str(e)}"
        )


def generate_markdown(json_data: Dict[str, Any]) -> str:
    """
    Génère du Markdown à partir des données JSON.

    Args:
        json_data: Données JSON du document

    Returns:
        str: Document Markdown
    """
    try:
        from docx_json.core.markdown_generator import MarkdownGenerator

        generator = MarkdownGenerator(json_data)
        markdown = generator.generate()
        return markdown

    except Exception as e:
        raise ConversionError(f"Erreur lors de la génération du Markdown: {str(e)}")


def handle_css_generation(
    args: argparse.Namespace, json_path: str
) -> Optional[Set[str]]:
    """
    Gère la génération du CSS à partir du fichier JSON.

    Args:
        args: Arguments de ligne de commande
        json_path: Chemin du fichier JSON

    Returns:
        Optional[Set[str]]: Ensemble des classes CSS générées ou None en cas d'erreur
    """
    try:
        # Importer ici pour éviter les dépendances circulaires
        from docx_json.utils.css_generator import load_custom_styles, process_json_file

        # Extraire le nom de base
        base_name = os.path.splitext(os.path.basename(json_path))[0]

        # Déterminer le chemin de sortie du CSS
        css_output_path = args.css_output
        if not css_output_path:
            # Réutiliser le même nom que le fichier JSON mais avec extension .css
            css_output_path = os.path.join(
                os.path.dirname(json_path), f"{base_name}.css"
            )

        # Charger les styles personnalisés si spécifiés
        custom_styles = None
        if args.css_styles:
            custom_styles = load_custom_styles(args.css_styles)

        # Générer le CSS
        return process_json_file(
            json_path, css_output_path, custom_styles=custom_styles
        )

    except Exception as e:
        logging.error(f"Erreur lors de la génération du CSS: {str(e)}")
        print(f"Erreur lors de la génération du CSS: {str(e)}")
        return None


# Exemples d'usage

if __name__ == "__main__":
    # Exemple de conversion d'un fichier DOCX
    docx_path = "chemin/vers/votre/document.docx"
    output_dir = "chemin/vers/dossier/sortie"
    formats = (True, True, True)  # JSON, HTML, Markdown

    convert_file(docx_path, output_dir, formats=formats)
