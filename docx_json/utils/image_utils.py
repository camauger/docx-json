#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Utilitaires pour le traitement des images
----------------------------------------
"""

import base64
import logging
import os
from typing import Any, Dict


def extract_images(
    document: Any, output_dir: str, save_to_disk: bool = True
) -> Dict[str, str]:
    """
    Extrait les images du document .docx et les sauvegarde dans un dossier ou les encode en base64

    Args:
        document: L'objet Document de python-docx
        output_dir: Répertoire de sortie pour les fichiers générés
        save_to_disk: Si True, sauvegarde les images sur disque. Sinon, encode en base64.

    Returns:
        Un dictionnaire {nom_image: chemin_relatif} ou {nom_image: donnees_base64}
    """
    images = {}
    rels = document.part.rels

    # Si on sauvegarde sur disque, créer le dossier images
    if save_to_disk:
        images_dir = os.path.join(output_dir, "images")
        if not os.path.exists(images_dir):
            os.makedirs(images_dir)
            logging.info(f"Dossier images créé: {images_dir}")

    for rel in rels.values():
        if "image" in rel.target_ref:
            try:
                # Obtenir le nom de l'image depuis le chemin
                image_name = os.path.basename(rel.target_ref)

                # Vérifier si c'est une image externe
                if rel.is_external:
                    logging.warning(f"Image externe ignorée: {rel.target_ref}")
                    continue

                # Récupérer les données binaires
                image_data = rel.target_part.blob

                if save_to_disk:
                    # Chemin de sortie pour l'image
                    image_path = os.path.join(images_dir, image_name)

                    # Sauvegarder l'image
                    with open(image_path, "wb") as f:
                        f.write(image_data)

                    # Stocker le chemin relatif dans le dictionnaire
                    images[image_name] = f"images/{image_name}"
                    logging.debug(f"Image extraite et sauvegardée: {image_path}")
                else:
                    # Encoder en base64
                    encoded_image = base64.b64encode(image_data).decode("utf-8")
                    # Stocker dans le dictionnaire
                    images[image_name] = encoded_image
                    logging.debug(f"Image extraite et encodée en base64: {image_name}")

            except Exception as e:
                logging.warning(
                    f"Impossible d'extraire l'image {rel.target_ref}: {str(e)}"
                )

    return images
