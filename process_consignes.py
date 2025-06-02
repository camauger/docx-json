#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script pour post-traiter les fichiers HTML et formater les composants Consignes.
"""

import logging
import os
import re
import sys

# Configurer le logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


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
    print(f"Trouvé {consignes_count} occurrences de '[Consignes]' dans le HTML")

    # Chercher le pattern plus précis
    matches = re.findall(r'<p class="mb-3 lead">\[Consignes\]</p>', html_content)
    print(
        f"Trouvé {len(matches)} marqueurs de début de composant dans le format attendu"
    )

    # Chercher tous les paragraphes pour débogage
    all_p = re.findall(r"<p[^>]*>(.*?)</p>", html_content)
    for i, p in enumerate(all_p):
        if "[Consignes]" in p:
            print(f"Trouvé '[Consignes]' dans le paragraphe {i+1}: {p[:50]}...")

    if consignes_count > 0:
        logging.info(f"Trouvé {consignes_count} composants Consignes à formater")
        # Créer un pattern plus simple qui ne dépend pas de la classe CSS
        simple_pattern = (
            r"<p[^>]*>\s*\[Consignes\]\s*</p>(.*?)<p[^>]*>\s*\[Fin Consignes\]\s*</p>"
        )

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

        # Appliquer le remplacement avec un regex simplifié
        html_with_consignes = re.sub(
            simple_pattern, format_consignes, html_content, flags=re.DOTALL
        )

        if html_with_consignes != html_content:
            logging.info("Post-traitement des composants Consignes terminé avec succès")
            return html_with_consignes
        else:
            logging.warning("Aucun composant Consignes n'a pu être formaté")

    return html_content


def main(html_path: str) -> None:
    """
    Fonction principale qui traite un fichier HTML.

    Args:
        html_path: Chemin vers le fichier HTML à traiter
    """
    if not os.path.exists(html_path):
        logging.error(f"Fichier '{html_path}' introuvable")
        sys.exit(1)

    if not html_path.lower().endswith(".html"):
        logging.error(f"Le fichier '{html_path}' n'est pas un fichier HTML")
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
            logging.info(f"Fichier original sauvegardé: '{backup_path}'")

            # Écrire le nouveau contenu
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(new_html_content)
            logging.info(f"Composants Consignes formatés dans: '{html_path}'")
        else:
            logging.info("Aucune modification apportée au fichier HTML")

    except Exception as e:
        logging.error(f"Erreur lors du traitement: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python process_consignes.py <fichier_html>")
        sys.exit(1)

    main(sys.argv[1])
