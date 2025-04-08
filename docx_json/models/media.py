#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Modèles pour les éléments médias du document.
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional

from docx_json.models.base import DocumentElement


@dataclass
class Image(DocumentElement):
    """Représente une image dans le document."""

    rId: Optional[str] = None
    image_path: Optional[str] = None
    alt_text: str = "Image"

    def __init__(self, alt_text: str = "Image"):
        super().__init__("image")
        self.alt_text = alt_text

    def to_dict(self) -> Dict[str, Any]:
        """Convertit l'image en dictionnaire pour le JSON."""
        result = super().to_dict()
        result["alt_text"] = self.alt_text

        if self.rId:
            result["rId"] = self.rId

        if self.image_path:
            result["image_path"] = self.image_path

        return result
