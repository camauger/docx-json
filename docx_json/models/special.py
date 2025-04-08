#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Modèles pour les éléments spéciaux du document.
"""

from dataclasses import dataclass
from typing import Any, Dict

from docx_json.models.base import DocumentElement


@dataclass
class ComponentMarker(DocumentElement):
    """Représente un marqueur de composant éducatif."""

    component_type: str

    def __init__(self, component_type: str):
        super().__init__("component_marker")
        self.component_type = component_type

    def to_dict(self) -> Dict[str, Any]:
        """Convertit le marqueur en dictionnaire pour le JSON."""
        result = super().to_dict()
        result["component_type"] = self.component_type
        return result


@dataclass
class ComponentEnd(DocumentElement):
    """Représente un marqueur de fin de composant éducatif."""

    component_type: str

    def __init__(self, component_type: str):
        super().__init__("component_end")
        self.component_type = component_type

    def to_dict(self) -> Dict[str, Any]:
        """Convertit le marqueur de fin en dictionnaire pour le JSON."""
        result = super().to_dict()
        result["component_type"] = self.component_type
        return result


@dataclass
class Instruction(DocumentElement):
    """Représente une instruction de formatage."""

    content: str

    def __init__(self, content: str):
        super().__init__("instruction")
        self.content = content

    def to_dict(self) -> Dict[str, Any]:
        """Convertit l'instruction en dictionnaire pour le JSON."""
        result = super().to_dict()
        result["content"] = self.content
        return result


@dataclass
class RawHTML(DocumentElement):
    """Représente du code HTML brut à insérer."""

    content: str

    def __init__(self, content: str):
        super().__init__("raw_html")
        self.content = content

    def to_dict(self) -> Dict[str, Any]:
        """Convertit le HTML brut en dictionnaire pour le JSON."""
        result = super().to_dict()
        result["content"] = self.content
        return result
