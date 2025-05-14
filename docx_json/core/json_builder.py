from typing import Any, Dict, List

from docx_json.models import DocumentElement


def build_json(
    elements: List[DocumentElement], metadata: Dict[str, Any], images: Dict[str, str]
) -> Dict[str, Any]:
    """
    Construit un objet JSON à partir des éléments du document.

    Args:
        elements: Liste des éléments du document
        metadata: Métadonnées du document, incluant le titre
        images: Dictionnaire des images extraites

    Returns:
        Objet JSON représentant le document
    """
    # Utiliser le titre des métadonnées s'il existe, sinon utiliser un titre par défaut
    title = metadata.get("title", "Sans titre")

    return {
        "meta": {"title": title},
        "content": [element.to_dict() for element in elements],
        "images": images,
    }
