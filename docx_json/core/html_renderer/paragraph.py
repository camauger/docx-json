import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

# Configurer le logging
logger = logging.getLogger(__name__)


@dataclass
class Run:
    """Représente un segment de texte avec ses attributs de style."""

    text: str = ""
    bold: bool = False
    italic: bool = False
    underline: bool = False
    strike: bool = False
    superscript: bool = False
    subscript: bool = False
    color: Optional[str] = None
    size: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Run":
        """Crée un Run à partir d'un dictionnaire."""
        return cls(
            text=data.get("text", ""),
            bold=data.get("bold", False),
            italic=data.get("italic", False),
            underline=data.get("underline", False),
            strike=data.get("strike", False),
            superscript=data.get("superscript", False),
            subscript=data.get("subscript", False),
            color=data.get("color"),
            size=data.get("size"),
        )


@dataclass
class Paragraph:
    """Représente un paragraphe avec son contenu et ses attributs."""

    runs: List[Run] = field(default_factory=list)
    style: str = ""
    html_class: str = ""
    html_id: Optional[str] = None
    text: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Paragraph":
        """Crée un Paragraph à partir d'un dictionnaire."""
        runs = []
        if "runs" in data and isinstance(data["runs"], list):
            runs = [Run.from_dict(run) for run in data["runs"]]

        return cls(
            runs=runs,
            style=data.get("style", ""),
            html_class=data.get("html_class", "").strip(),
            html_id=data.get("html_id"),
            text=data.get("text"),
        )


class ParagraphRenderer:
    def render(
        self, element: Dict[str, Any] | Paragraph, indent_level: int = 0
    ) -> List[str]:
        """
        Rend un paragraphe en HTML.

        Args:
            element: Données du paragraphe (Dict ou Paragraph)
            indent_level: Niveau d'indentation

        Returns:
            Liste de lignes HTML
        """
        # Convertir en Paragraph si c'est un dictionnaire
        if isinstance(element, dict):
            paragraph = Paragraph.from_dict(element)
        else:
            paragraph = element

        indent = " " * indent_level

        # Vérifier si c'est un marqueur de vidéo
        video_id = self._extract_video_id(paragraph)
        if video_id:
            return self._create_video_iframe(video_id, indent)

        # Pour les paragraphes normaux
        classes = []

        # Classes CSS selon le style
        if paragraph.style:
            classes.append(f"style-{paragraph.style.lower().replace(' ', '-')}")

        # Ajouter les classes personnalisées
        if paragraph.html_class:
            classes.extend(paragraph.html_class.split())

        # Gestion du style 'Lead' (chapo)
        if paragraph.style.lower() == "lead" or "lead" in paragraph.html_class:
            if "lead" not in classes:
                classes.append("lead")

        # Toujours ajouter mb-3 pour l'espacement
        if "mb-3" not in classes:
            classes.append("mb-3")

        # Construire l'attribut class si nécessaire
        class_attr = f' class="{" ".join(classes)}"' if classes else ""
        id_attr = f' id="{paragraph.html_id}"' if paragraph.html_id else ""

        # Vérifier si le paragraphe contient des runs
        if paragraph.runs:
            # Construire le HTML avec les spans pour chaque run
            element_html = [f"{indent}<p{class_attr}{id_attr}>"]
            for run in paragraph.runs:
                span_html = self._format_run(run)
                if span_html:
                    element_html[0] += span_html
            element_html[0] += "</p>"
            return element_html

        # Paragraphe vide
        return [f"{indent}<p{class_attr}{id_attr}></p>"]

    def _extract_video_id(self, element: Any) -> Optional[str]:
        """
        Extrait l'ID vidéo d'un élément s'il contient un marqueur de vidéo.

        Args:
            element: L'élément à analyser (Dict, Paragraph ou str)

        Returns:
            L'ID de la vidéo ou None si ce n'est pas une vidéo
        """
        full_text = ""

        # Cas 1: Paragraph avec runs
        if isinstance(element, Paragraph) and element.runs:
            full_text = "".join([run.text for run in element.runs])
        # Cas 2: Paragraph avec texte direct
        elif isinstance(element, Paragraph) and element.text:
            full_text = element.text
        # Cas 3: élément avec runs (dict)
        elif isinstance(element, dict) and "runs" in element and element["runs"]:
            full_text = "".join([run.get("text", "") for run in element["runs"]])
        # Cas 4: élément de type chaîne
        elif isinstance(element, str):
            full_text = element
        # Cas 5: élément avec attribut text direct (dict)
        elif (
            isinstance(element, dict)
            and "text" in element
            and isinstance(element.get("text", ""), str)
        ):
            full_text = element.get("text", "")

        # Vérifier si c'est un marqueur de vidéo
        if full_text.strip().startswith("[Vidéo") and "]" in full_text:
            logger.debug(f"Marqueur vidéo trouvé: {full_text}")

            # Valeur par défaut
            video_id = "1069341210"

            # Rechercher l'ID de vidéo avec quote simple
            if "video_id='" in full_text:
                start_idx = full_text.find("video_id='") + 10
                end_idx = full_text.find("'", start_idx)
                if end_idx > start_idx:
                    video_id = full_text[start_idx:end_idx]
                    logger.debug(f"ID vidéo trouvé (quotes simples): {video_id}")
            # Rechercher l'ID de vidéo avec quote double
            elif 'video_id="' in full_text:
                start_idx = full_text.find('video_id="') + 10
                end_idx = full_text.find('"', start_idx)
                if end_idx > start_idx:
                    video_id = full_text[start_idx:end_idx]
                    logger.debug(f"ID vidéo trouvé (quotes doubles): {video_id}")

            return video_id

        return None

    def _create_video_iframe(self, video_id: str, indent: str) -> List[str]:
        """
        Crée le HTML pour un iframe de vidéo Vimeo.

        Args:
            video_id: L'ID de la vidéo
            indent: Indentation à appliquer

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

    def _format_run(self, run: Dict[str, Any] | Run) -> str:
        """
        Formate un run de texte en HTML.

        Args:
            run: Données du run (Dict ou Run)

        Returns:
            Chaîne HTML du run
        """
        # Convertir en Run si c'est un dictionnaire
        if isinstance(run, dict):
            run_obj = Run.from_dict(run)
        else:
            run_obj = run

        if not run_obj.text:
            return ""

        # Échapper les caractères spéciaux HTML
        text = (
            run_obj.text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        )

        # Appliquer les styles de façon ordonnée pour une meilleure prévisibilité
        formatted_text = text

        # Appliquer les balises HTML dans un ordre logique (de l'intérieur vers l'extérieur)
        if run_obj.subscript:
            formatted_text = f"<sub>{formatted_text}</sub>"
        if run_obj.superscript:
            formatted_text = f"<sup>{formatted_text}</sup>"
        if run_obj.strike:
            formatted_text = f"<s>{formatted_text}</s>"
        if run_obj.underline:
            formatted_text = f"<u>{formatted_text}</u>"
        if run_obj.italic:
            formatted_text = f"<em>{formatted_text}</em>"
        if run_obj.bold:
            formatted_text = f"<strong>{formatted_text}</strong>"

        # Appliquer les styles CSS
        style_attrs = []
        if run_obj.color:
            style_attrs.append(f"color:{run_obj.color}")
        if run_obj.size:
            style_attrs.append(f"font-size:{run_obj.size}")

        # Envelopper dans un span si des styles CSS sont nécessaires
        if style_attrs:
            formatted_text = (
                f'<span style="{"; ".join(style_attrs)}">{formatted_text}</span>'
            )

        return formatted_text
