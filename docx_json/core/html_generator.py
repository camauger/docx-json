#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module pour la génération de HTML à partir de la structure JSON
--------------------------------------------------------------
Ce module est maintenant organisé dans le package html_renderer.
Ce fichier est maintenu pour la compatibilité avec le code existant.
"""

from typing import Any, Dict, Optional

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
