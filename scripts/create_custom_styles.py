#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script pour créer un exemple de fichier de styles CSS personnalisés
"""

import argparse
import json
import os


def create_example_styles(output_path="custom_styles.json"):
    """
    Crée un fichier JSON contenant des exemples de styles CSS personnalisés.

    Args:
        output_path: Chemin où enregistrer le fichier de styles
    """
    styles = {
        # Styles de texte
        "hero": """
        font-size: 3rem;
        font-weight: 700;
        color: #007bff;
        margin-bottom: 2rem;
        text-align: center;
        text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.2);
        """,
        "subtitle": """
        font-size: 1.5rem;
        font-weight: 500;
        color: #6c757d;
        margin-bottom: 1.5rem;
        """,
        # Conteneurs et mise en page
        "card": """
        background-color: #fff;
        border-radius: 0.5rem;
        border: 1px solid #dee2e6;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        padding: 2rem;
        margin-bottom: 2rem;
        transition: transform 0.3s ease;
        """,
        "panel": """
        background-color: #f8f9fa;
        border-radius: 0.375rem;
        border: 1px solid #dee2e6;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        """,
        # Notifications et alertes
        "info-box": """
        background-color: #cfe2ff;
        border-left: 5px solid #0d6efd;
        color: #084298;
        padding: 1.25rem;
        margin-bottom: 1.5rem;
        border-radius: 0.375rem;
        """,
        "warning-box": """
        background-color: #fff3cd;
        border-left: 5px solid #ffc107;
        color: #664d03;
        padding: 1.25rem;
        margin-bottom: 1.5rem;
        border-radius: 0.375rem;
        """,
        "success-box": """
        background-color: #d1e7dd;
        border-left: 5px solid #198754;
        color: #0f5132;
        padding: 1.25rem;
        margin-bottom: 1.5rem;
        border-radius: 0.375rem;
        """,
        # Mise en forme de texte
        "highlight": """
        background-color: #fff3cd;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        """,
        "strong-text": """
        font-weight: 700;
        color: #495057;
        """,
        # Utilitaires
        "center": "text-align: center;",
        "right": "text-align: right;",
        "justify": "text-align: justify;",
        "small": "font-size: 0.875rem;",
        "large": "font-size: 1.25rem;",
        "primary": "color: #0d6efd;",
        "secondary": "color: #6c757d;",
        "success": "color: #198754;",
        "danger": "color: #dc3545;",
        "bordered": "border: 1px solid #dee2e6; border-radius: 0.375rem; padding: 1rem;",
        "shadow": "box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);",
    }

    # Créer le répertoire de sortie si nécessaire
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    # Enregistrer au format JSON (indentation pour lisibilité)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(styles, f, indent=2)

    print(f"Fichier de styles personnalisés créé: {os.path.abspath(output_path)}")
    print("\nUtilisez ce fichier avec l'option --css-styles lors de la conversion:")
    print(
        f"  python -m docx_json votre_document.docx --json --generate-css --css-styles {output_path}"
    )


def main():
    """Fonction principale pour l'exécution en ligne de commande."""
    parser = argparse.ArgumentParser(
        description="Crée un fichier d'exemple de styles CSS personnalisés"
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default="custom_styles.json",
        help="Chemin où enregistrer le fichier de styles (par défaut: custom_styles.json)",
    )

    args = parser.parse_args()
    create_example_styles(args.output)


if __name__ == "__main__":
    main()
