#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Modèle de données pour les éléments du document.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class TextRun:
    """Représente un morceau de texte avec style."""
    text: str
    bold: bool = False
    italic: bool = False
    underline: bool = False


class DocumentElement:
    """Classe de base pour tous les éléments du document."""

    def __init__(self, element_type: str):
        self._type = element_type
        self._html_class = None
        self._html_id = None

    @property
    def type(self) -> str:
        """Type de l'élément."""
        return self._type

    @property
    def html_class(self) -> Optional[str]:
        """Classe CSS à appliquer en HTML."""
        return self._html_class

    @html_class.setter
    def html_class(self, value: str):
        self._html_class = value

    @property
    def html_id(self) -> Optional[str]:
        """ID HTML à appliquer."""
        return self._html_id

    @html_id.setter
    def html_id(self, value: str):
        self._html_id = value

    def to_dict(self) -> Dict[str, Any]:
        """Convertit l'élément en dictionnaire pour le JSON."""
        result = {"type": self._type}

        if self._html_class:
            result["html_class"] = self._html_class

        if self._html_id:
            result["html_id"] = self._html_id

        return result


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
                "underline": run.underline
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
                "underline": run.underline
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
                "underline": run.underline
            }
            for run in self.runs
        ]
        return result


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
            [
                [element.to_dict() for element in cell]
                for cell in row
            ]
            for row in self.rows
        ]

        return result


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
