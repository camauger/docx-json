"""
Module contenant le renderer pour les éléments vidéo.
"""

from typing import Any, Dict, List

# Utiliser l'import relatif correct
from .base import ElementRenderer


class VideoRenderer(ElementRenderer):
    """Classe pour le rendu des éléments vidéo."""

    def __init__(self, html_generator: Any) -> None:
        """
        Initialise le renderer vidéo.

        Args:
            html_generator: Générateur HTML parent
        """
        super().__init__(html_generator)

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
        html_lines = []

        try:
            # Extraire le texte de l'élément selon son type
            text = ""

            # Si c'est un élément de type paragraph contenant du texte comme "[Vidéo video_id='...']"
            if isinstance(element, dict) and element.get("type") == "paragraph":
                if "runs" in element and element["runs"]:
                    # Concaténer tous les textes des runs
                    for run in element["runs"]:
                        text += run.get("text", "")
                elif "text" in element and isinstance(element["text"], str):
                    text = element["text"]
            # Sinon, si c'est juste une chaîne de texte
            elif isinstance(element, str):
                text = element
            # Sinon, si c'est un composant vidéo avec attributes
            elif (
                isinstance(element, dict)
                and element.get("type") == "component"
                and element.get("component_type") == "Vidéo"
            ):
                # Obtenir l'ID de la vidéo à partir des attributs
                if "attributes" in element and isinstance(element["attributes"], dict):
                    video_id = element["attributes"].get("video_id", "1069341210")
                    print(f"VideoRenderer: ID vidéo composant: {video_id}")
                    return self._generate_video_iframe(video_id, indent)

            # Vérifier si c'est un marqueur de vidéo
            if text and ("[Vidéo" in text or "[vidéo" in text) and "]" in text:
                # Extraire l'ID de la vidéo
                video_id = "1069341210"  # Valeur par défaut

                # Rechercher l'ID dans plusieurs formats possibles
                if "video_id=" in text or "video_id='" in text or 'video_id="' in text:
                    # Quotes simples
                    if "video_id='" in text:
                        start_idx = text.find("video_id='")
                        if start_idx >= 0:
                            start_idx_value = start_idx + 10  # Longueur de "video_id='"
                            end_idx = text.find("'", start_idx_value)
                            if end_idx > start_idx_value:
                                # Extraire le sous-texte
                                video_id = text[start_idx_value:end_idx]
                                print(
                                    f"VideoRenderer: ID trouvé (quotes simples): '{video_id}'"
                                )

                    # Quotes doubles
                    elif 'video_id="' in text:
                        start_idx = text.find('video_id="')
                        if start_idx >= 0:
                            start_idx_value = start_idx + 10  # Longueur de 'video_id="'
                            end_idx = text.find('"', start_idx_value)
                            if end_idx > start_idx_value:
                                # Extraire le sous-texte
                                video_id = text[start_idx_value:end_idx]
                                print(
                                    f"VideoRenderer: ID trouvé (quotes doubles): '{video_id}'"
                                )

                print(f"VideoRenderer: Génération iframe vidéo avec ID: {video_id}")
                return self._generate_video_iframe(video_id, indent)

            print(
                f"VideoRenderer: Le texte ne commence pas par '[Vidéo' ou ne contient pas ']'"
            )

        except Exception as e:
            print(f"Erreur dans VideoRenderer: {str(e)}")
            return [f"{indent}<!-- Erreur de rendu vidéo: {str(e)} -->"]

        # Si on arrive ici, l'élément n'est pas reconnu comme une vidéo
        return [f"{indent}<!-- Élément vidéo non reconnu -->"]

    def _generate_video_iframe(self, video_id: str, indent: str) -> List[str]:
        """
        Génère le HTML pour une vidéo.

        Args:
            video_id: Identifiant de la vidéo
            indent: Indentation

        Returns:
            Liste de lignes HTML
        """
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
