#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module pour le traitement spécial des composants Consignes.
"""

import logging
import os
import re
import sys
from typing import Any, Dict, List


def _extract_consignes_from_html(html: str) -> str:
    """
    Remplace les paragraphes [Consignes]...[Fin Consignes] par un composant formaté.

    Args:
        html: Le HTML à traiter

    Returns:
        Le HTML avec les composants Consignes formatés
    """
    # Pattern pour trouver les blocs de consignes
    pattern = r'<p class="mb-3 lead">\[Consignes\]</p>(.*?)<p class="mb-3 lead">\[Fin Consignes\]</p>'

    def format_consignes(match) -> str:
        """Remplacer les consignes trouvées par un composant formaté."""
        content = match.group(1)
        return (
            '<section class="consignes-component">\n'
            '  <div class="card my-4 border-0 shadow-sm">\n'
            '    <div class="card-body consignes" style="background-color: #fffde7; border-left: 4px solid #fb8c00; font-style: italic; padding: 1rem;">\n'
            f"{content}\n"
            "    </div>\n"
            "  </div>\n"
            "</section>"
        )

    # Appliquer le remplacement avec un regex qui capture le contenu entre les marqueurs
    html_with_consignes = re.sub(pattern, format_consignes, html, flags=re.DOTALL)
    logging.info("Post-traitement des composants Consignes terminé")
    return html_with_consignes


def process_consignes_in_html(html_content: str) -> str:
    """
    Fonction principale pour traiter les composants Consignes dans un fichier HTML.

    Args:
        html_content: Contenu HTML à traiter

    Returns:
        Contenu HTML avec les composants Consignes formatés
    """
    # Compter le nombre d'occurrences de [Consignes] dans le HTML
    consignes_count = html_content.count("[Consignes]")

    if consignes_count > 0:
        logging.info(f"Trouvé {consignes_count} composants Consignes à formater")
        # Appliquer le traitement spécial pour les consignes
        return _extract_consignes_from_html(html_content)

    return html_content


def main(html_path: str) -> None:
    """
    Fonction principale qui traite un fichier HTML.

    Args:
        html_path: Chemin vers le fichier HTML à traiter
    """
    # Configurer le logging manuellement sans basicConfig
    logger = logging.getLogger("consignes_handler")
    logger.setLevel(logging.INFO)

    # Ajouter un handler qui écrit sur la console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    if not os.path.exists(html_path):
        logger.error(f"Fichier '{html_path}' introuvable")
        sys.exit(1)

    if not html_path.lower().endswith(".html"):
        logger.error(f"Le fichier '{html_path}' n'est pas un fichier HTML")
        sys.exit(1)

    try:
        # Lire le fichier HTML
        with open(html_path, "r", encoding="utf-8") as f:
            html_content = f.read()

        # Traiter les composants Consignes
        new_html_content = process_consignes_in_html(html_content)

        # Si le contenu a été modifié, sauvegarder le fichier
        if new_html_content != html_content:
            # Sauvegarder une copie du fichier original
            backup_path = f"{html_path}.bak"
            with open(backup_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            logger.info(f"Fichier original sauvegardé: '{backup_path}'")

            # Écrire le nouveau contenu
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(new_html_content)
            logger.info(f"Composants Consignes formatés dans: '{html_path}'")
        else:
            logger.info("Aucune modification apportée au fichier HTML")

    except Exception as e:
        logger.error(f"Erreur lors du traitement: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m docx_json.utils.consignes_handler <fichier_html>")
        sys.exit(1)

    main(sys.argv[1])
