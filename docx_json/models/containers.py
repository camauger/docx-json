#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Modèles pour les éléments conteneurs du document.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List

from docx_json.models.base import DocumentElement


@dataclass
class Table(DocumentElement):
    """Représente un tableau dans le document."""

    rows: List[List[List[DocumentElement]]] = field(default_factory=list)

    def __init__(self):
        super().__init__("table")
        self.rows = []

    def add_row(self, row: List[List[DocumentElement]]):
        """Ajoute une ligne au tableau."""
        self.rows.append(row)

    def to_dict(self) -> Dict[str, Any]:
        """Convertit le tableau en dictionnaire pour le JSON."""
        result = super().to_dict()

        # Convertir récursivement tous les éléments en dictionnaires
        result["rows"] = [
            [[element.to_dict() for element in cell] for cell in row]
            for row in self.rows
        ]

        return result


@dataclass
class Component(DocumentElement):
    """Représente un composant éducatif complet."""

    component_type: str
    content: List[DocumentElement] = field(default_factory=list)

    def __init__(self, component_type: str):
        super().__init__("component")
        self.component_type = component_type
        self.content = []

    def add_element(self, element: DocumentElement):
        """Ajoute un élément au contenu du composant."""
        self.content.append(element)

    def to_dict(self) -> Dict[str, Any]:
        """Convertit le composant en dictionnaire pour le JSON."""
        result = super().to_dict()
        result["component_type"] = self.component_type
        result["content"] = [element.to_dict() for element in self.content]
        return result


@dataclass
class Block(DocumentElement):
    """Représente un bloc formaté (citation, encadré, etc.)."""

    block_type: str
    content: List[DocumentElement] = field(default_factory=list)

    def __init__(self, block_type: str):
        super().__init__("block")
        self.block_type = block_type
        self.content = []

    def add_element(self, element: DocumentElement):
        """Ajoute un élément au contenu du bloc."""
        self.content.append(element)

    def to_dict(self) -> Dict[str, Any]:
        """Convertit le bloc en dictionnaire pour le JSON."""
        result = super().to_dict()
        result["block_type"] = self.block_type
        result["content"] = [element.to_dict() for element in self.content]
        return result
