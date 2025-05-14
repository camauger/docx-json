from typing import Any, Dict, List


class ParagraphRenderer:
    def render(self, element: Dict[str, Any], indent_level: int = 0) -> List[str]:
        """
        Rend un paragraphe en HTML.

        Args:
            element: Données du paragraphe
            indent_level: Niveau d'indentation

        Returns:
            Liste de lignes HTML
        """
        indent = " " * indent_level

        # Vérifier si c'est un marqueur de vidéo en examinant le texte directement
        full_text = ""

        # Extraire le texte complet du paragraphe à partir des runs
        if "runs" in element and element["runs"]:
            # Extraire le texte du premier run pour un check rapide
            first_run_text = element["runs"][0].get("text", "")
            print(f"DEBUG PARAGRAPHE FIRST RUN: {first_run_text}")  # Pour déboguer

            # Récupérer le texte complet
            full_text = "".join([run.get("text", "") for run in element["runs"]])
            print(f"DEBUG TEXTE COMPLET DU PARAGRAPHE: {full_text}")  # Pour déboguer

            # Vérifier si le texte commence par [Vidéo
            if full_text.strip().startswith("[Vidéo") and "]" in full_text:
                print(f"DEBUG MARQUEUR VIDÉO TROUVÉ: {full_text}")  # Pour déboguer

                # Valeur par défaut
                video_id = "1069341210"

                # Rechercher l'ID de vidéo
                if "video_id='" in full_text:
                    start_idx = full_text.find("video_id='") + 10
                    end_idx = full_text.find("'", start_idx)
                    if end_idx > start_idx:
                        video_id = full_text[start_idx:end_idx]
                        print(
                            f"DEBUG ID VIDÉO (quotes simples): {video_id}"
                        )  # Pour déboguer
                elif 'video_id="' in full_text:
                    start_idx = full_text.find('video_id="') + 10
                    end_idx = full_text.find('"', start_idx)
                    if end_idx > start_idx:
                        video_id = full_text[start_idx:end_idx]
                        print(
                            f"DEBUG ID VIDÉO (quotes doubles): {video_id}"
                        )  # Pour déboguer

                # Générer l'iframe pour la vidéo
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
        # Vérifier autrement si c'est un texte direct ou une chaîne
        elif (
            isinstance(element, str)
            and element.strip().startswith("[Vidéo")
            and "]" in element
        ):
            full_text = element
            print(f"DEBUG MARQUEUR VIDÉO (TEXT): {full_text}")  # Pour déboguer

            # Valeur par défaut
            video_id = "1069341210"

            # Rechercher l'ID de vidéo
            if "video_id='" in full_text:
                start_idx = full_text.find("video_id='") + 10
                end_idx = full_text.find("'", start_idx)
                if end_idx > start_idx:
                    video_id = full_text[start_idx:end_idx]
                    print(f"DEBUG ID VIDÉO (TEXT, quotes simples): {video_id}")
            elif 'video_id="' in full_text:
                start_idx = full_text.find('video_id="') + 10
                end_idx = full_text.find('"', start_idx)
                if end_idx > start_idx:
                    video_id = full_text[start_idx:end_idx]
                    print(f"DEBUG ID VIDÉO (TEXT, quotes doubles): {video_id}")

            # Générer l'iframe pour la vidéo
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
        # Si l'élément a un texte direct (sans runs)
        elif (
            "text" in element
            and isinstance(element.get("text", ""), str)
            and element.get("text", "").strip().startswith("[Vidéo")
            and "]" in element.get("text", "")
        ):
            full_text = element.get("text", "")
            print(f"DEBUG MARQUEUR VIDÉO (DIRECT TEXT): {full_text}")  # Pour déboguer

            # Valeur par défaut
            video_id = "1069341210"

            # Rechercher l'ID de vidéo
            if "video_id='" in full_text:
                start_idx = full_text.find("video_id='") + 10
                end_idx = full_text.find("'", start_idx)
                if end_idx > start_idx:
                    video_id = full_text[start_idx:end_idx]
                    print(f"DEBUG ID VIDÉO (DIRECT, quotes simples): {video_id}")
            elif 'video_id="' in full_text:
                start_idx = full_text.find('video_id="') + 10
                end_idx = full_text.find('"', start_idx)
                if end_idx > start_idx:
                    video_id = full_text[start_idx:end_idx]
                    print(f"DEBUG ID VIDÉO (DIRECT, quotes doubles): {video_id}")

            # Générer l'iframe pour la vidéo
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

        # Pour les paragraphes normaux
        style = element.get("style", "")
        html_class = element.get("html_class", "").strip()
        classes = []

        # Classes CSS selon le style
        if style:
            classes.append(f"style-{style.lower().replace(' ', '-')}")

        # Ajouter les classes personnalisées
        if html_class:
            classes.extend(html_class.split())

        # Gestion du style 'Lead' (chapo)
        if style.lower() == "lead" or "lead" in html_class:
            if "lead" not in classes:
                classes.append("lead")

        # Toujours ajouter mb-3 pour l'espacement
        if "mb-3" not in classes:
            classes.append("mb-3")

        # Construire l'attribut class si nécessaire
        class_attr = f' class="{" ".join(classes)}"' if classes else ""
        id_attr = f' id="{element["html_id"]}"' if element.get("html_id") else ""

        # Vérifier si le paragraphe contient des textes
        if "runs" in element and element["runs"]:
            # Construire le HTML avec les spans pour chaque run
            element_html = [f"{indent}<p{class_attr}{id_attr}>"]
            for run in element["runs"]:
                span_html = self._format_run(run)
                if span_html:
                    element_html[0] += span_html
            element_html[0] += "</p>"
            return element_html

        # Paragraphe vide
        return [f"{indent}<p{class_attr}{id_attr}></p>"]

    def _format_run(self, run: Dict[str, Any]) -> str:
        """
        Formate un run de texte en HTML.

        Args:
            run: Données du run

        Returns:
            Chaîne HTML du run
        """
        if not run or "text" not in run:
            return ""

        text = run["text"]
        if not text:
            return ""

        # Échapper les caractères spéciaux HTML
        text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

        # Appliquer les styles de texte
        if run.get("bold", False):
            text = f"<strong>{text}</strong>"
        if run.get("italic", False):
            text = f"<em>{text}</em>"
        if run.get("underline", False):
            text = f"<u>{text}</u>"
        if run.get("strike", False):
            text = f"<s>{text}</s>"
        if run.get("superscript", False):
            text = f"<sup>{text}</sup>"
        if run.get("subscript", False):
            text = f"<sub>{text}</sub>"

        # Appliquer la couleur si présente
        if "color" in run:
            text = f'<span style="color:{run["color"]}">{text}</span>'

        # Appliquer la taille si présente
        if "size" in run:
            text = f'<span style="font-size:{run["size"]}">{text}</span>'

        return text
