#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Classes de base pour les modèles de données.
"""

from typing import Any, Dict


class DocumentElement:
    """Classe de base pour tous les éléments du document."""

    def __init__(self, element_type: str):
        self._type = element_type
        self._html_class = ""
        self._html_id = ""

    @property
    def type(self) -> str:
        """Type de l'élément."""
        return self._type

    @property
    def html_class(self) -> str:
        """Classe CSS à appliquer en HTML."""
        return self._html_class

    @html_class.setter
    def html_class(self, value: str):
        self._html_class = value

    @property
    def html_id(self) -> str:
        """ID HTML à appliquer."""
        return self._html_id

    @html_id.setter
    def html_id(self, value: str):
        self._html_id = value

    def to_dict(self) -> Dict[str, Any]:
        """Convertit l'élément en dictionnaire pour le JSON."""
        result = {"type": self.type}

        if self.html_class:
            result["html_class"] = self.html_class

        if self.html_id:
            result["html_id"] = self.html_id

        return result
