#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module pour la génération de HTML à partir de la structure JSON
--------------------------------------------------------------
Ce module est maintenant organisé dans le package html_renderer.
Ce fichier est maintenu pour la compatibilité avec le code existant.
"""

from typing import Any, Dict, List, Optional

from docx_json.core.html_renderer import HTMLGenerator

# Exportation de la classe HTMLGenerator pour la compatibilité
__all__ = ["HTMLGenerator"]


def generate_html(json_data: Dict[str, Any], custom_css: Optional[str] = None) -> str:
    """
    Fonction utilitaire pour générer du HTML à partir de données JSON.

    Args:
        json_data: Dictionnaire représentant le document
        custom_css: CSS personnalisé à utiliser (optionnel)

    Returns:
        Une chaîne de caractères contenant le HTML
    """
    generator = HTMLGenerator(json_data)
    return generator.generate(custom_css)


def generate_multi_page_html(
    json_data: Dict[str, Any],
    output_dir: str,
    base_filename: str,
    custom_css: Optional[str] = None,
) -> List[str]:
    """
    Fonction utilitaire pour générer plusieurs fichiers HTML à partir de données JSON,
    en divisant le document aux sauts de page.

    Args:
        json_data: Dictionnaire représentant le document
        output_dir: Répertoire de sortie pour les fichiers HTML
        base_filename: Nom de base pour les fichiers (sans extension)
        custom_css: CSS personnalisé à utiliser (optionnel)

    Returns:
        Liste des chemins des fichiers HTML générés
    """
    generator = HTMLGenerator(json_data)
    return generator.generate_multi_page(output_dir, base_filename, custom_css)
