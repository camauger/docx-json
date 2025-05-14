#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script de lancement pour le convertisseur DOCX -> JSON/HTML
"""

from docx_json.__main__ import main

if __name__ == "__main__":
    main()

# Usage: python run_docx_converter.py <path_to_docx_file>
# Example: python run_docx_converter.py "C:\Users\user\Documents\test.docx"

# Génération CSS avec styles par défaut
# python run_docx_converter.py document.docx --json --generate-css

# # Génération CSS avec styles personnalisés
# python run_docx_converter.py document.docx --json --generate-css --css-styles styles_perso.json

# # Spécifier le chemin de sortie du CSS
# python run_docx_converter.py document.docx --json --generate-css --css-output mon_style.css
