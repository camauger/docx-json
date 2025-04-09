"""
Module contenant le renderer pour les éléments vidéo.
"""

from typing import Any, Dict, List

from .base import ElementRenderer


class VideoRenderer(ElementRenderer):
    """Classe pour le rendu des éléments vidéo."""

    def __init__(self, html_generator=None):
        """
        Initialise le renderer vidéo.

        Args:
            html_generator: Référence au générateur HTML principal
        """
        self.html_generator = html_generator

    def render(self, element: Dict[str, Any], indent_level: int = 0) -> List[str]:
        """
        Rend un élément vidéo en HTML.

        Args:
            element: Données de la vidéo
            indent_level: Niveau d'indentation

        Returns:
            Liste de lignes HTML
        """
        indent = " " * indent_level

        # Si c'est un élément de type paragraph contenant du texte comme "[Vidéo video_id='...']"
        if element["type"] == "paragraph" and "runs" in element:
            # Extraire le texte du premier run
            text = ""
            for run in element["runs"]:
                text += run.get("text", "")

            # Débogage
            print(f"VideoRenderer: Texte trouvé: '{text}'")

            # Vérifier si c'est un marqueur de vidéo
            if text.startswith("[Vidéo") and "]" in text:
                # Extraire l'ID de la vidéo
                video_id = "1069341210"  # Valeur par défaut

                # Essayer d'extraire l'ID à partir du texte
                if "video_id=" in text or "video_id='" in text or 'video_id="' in text:
                    # Extraction basique avec des quotes simples
                    start_idx = text.find("video_id='")
                    if start_idx > 0:
                        start_idx += 10  # Longueur de "video_id='"
                        end_idx = text.find("'", start_idx)
                        if end_idx > start_idx:
                            video_id = text[start_idx:end_idx]
                            print(
                                f"VideoRenderer: ID trouvé (quotes simples): '{video_id}'"
                            )

                    # Extraction basique avec des quotes doubles
                    start_idx = text.find('video_id="')
                    if start_idx > 0:
                        start_idx += 10  # Longueur de 'video_id="'
                        end_idx = text.find('"', start_idx)
                        if end_idx > start_idx:
                            video_id = text[start_idx:end_idx]
                            print(
                                f"VideoRenderer: ID trouvé (quotes doubles): '{video_id}'"
                            )

                print(f"VideoRenderer: Génération iframe vidéo avec ID: {video_id}")

                # Générer le HTML pour la vidéo Vimeo
                return [
                    f'{indent}<div class="video-container">',
                    f'{indent}  <iframe src="https://player.vimeo.com/video/{video_id}"',
                    f'{indent}          style="width:100%;height:400px;"',
                    f'{indent}          frameborder="0"',
                    f'{indent}          allow="autoplay; fullscreen; picture-in-picture"',
                    f"{indent}          allowfullscreen",
                    f'{indent}          title="Vimeo Video Player">',
                    f"{indent}  </iframe>",
                    f"{indent}</div>",
                    f'{indent}<script src="https://player.vimeo.com/api/player.js"></script>',
                ]
            else:
                print(
                    f"VideoRenderer: Le texte ne commence pas par '[Vidéo' ou ne contient pas ']'"
                )
        else:
            print(
                f"VideoRenderer: L'élément n'est pas un paragraphe ou n'a pas de runs"
            )
            print(
                f"VideoRenderer: Type: {element.get('type', 'inconnu')}, Runs: {'runs' in element}"
            )

        # Rendu par défaut (ne devrait pas être appelé)
        return [f"{indent}<!-- Élément vidéo non reconnu -->"]
