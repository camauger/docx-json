#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Modèles pour les éléments textuels du document.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List

from docx_json.models.base import DocumentElement


@dataclass
class TextRun:
    """Représente un morceau de texte avec style."""

    text: str
    bold: bool = False
    italic: bool = False
    underline: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire."""
        return {
            "text": self.text,
            "bold": self.bold,
            "italic": self.italic,
            "underline": self.underline,
        }


@dataclass
class Paragraph(DocumentElement):
    """Représente un paragraphe dans le document."""

    runs: List[TextRun] = field(default_factory=list)

    def __init__(self):
        super().__init__("paragraph")
        self.runs = []

    def add_run(self, run: TextRun):
        """Ajoute un morceau de texte au paragraphe."""
        self.runs.append(run)

    def to_dict(self) -> Dict[str, Any]:
        """Convertit le paragraphe en dictionnaire pour le JSON."""
        result = super().to_dict()
        result["runs"] = [
            {
                "text": run.text,
                "bold": run.bold,
                "italic": run.italic,
                "underline": run.underline,
            }
            for run in self.runs
        ]
        return result


@dataclass
class Heading(DocumentElement):
    """Représente un titre dans le document."""

    level: int
    runs: List[TextRun] = field(default_factory=list)

    def __init__(self, level: int):
        super().__init__("heading")
        self.level = level
        self.runs = []

    def add_run(self, run: TextRun):
        """Ajoute un morceau de texte au titre."""
        self.runs.append(run)

    def to_dict(self) -> Dict[str, Any]:
        """Convertit le titre en dictionnaire pour le JSON."""
        result = super().to_dict()
        result["level"] = self.level
        result["runs"] = [
            {
                "text": run.text,
                "bold": run.bold,
                "italic": run.italic,
                "underline": run.underline,
            }
            for run in self.runs
        ]
        return result


@dataclass
class ListItem(DocumentElement):
    """Représente un élément de liste dans le document."""

    runs: List[TextRun] = field(default_factory=list)

    def __init__(self):
        super().__init__("list_item")
        self.runs = []

    def add_run(self, run: TextRun):
        """Ajoute un morceau de texte à l'élément de liste."""
        self.runs.append(run)

    def to_dict(self) -> Dict[str, Any]:
        """Convertit l'élément de liste en dictionnaire pour le JSON."""
        result = super().to_dict()
        result["runs"] = [
            {
                "text": run.text,
                "bold": run.bold,
                "italic": run.italic,
                "underline": run.underline,
            }
            for run in self.runs
        ]
        return result


@dataclass
class DocumentList(DocumentElement):
    """Représente une liste dans le document."""

    items: List[ListItem] = field(default_factory=list)
    ordered: bool = False

    def __init__(self, ordered: bool = False):
        super().__init__("list")
        self.items = []
        self.ordered = ordered

    def add_item(self, item: ListItem):
        """Ajoute un élément à la liste."""
        self.items.append(item)

    def to_dict(self) -> Dict[str, Any]:
        """Convertit la liste en dictionnaire pour le JSON."""
        result = super().to_dict()
        result["ordered"] = self.ordered
        result["items"] = [item.to_dict() for item in self.items]
        return result
