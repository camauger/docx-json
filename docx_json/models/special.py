#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Modèles pour les éléments spéciaux du document.
"""

from dataclasses import dataclass, field
from typing import Any, Dict

from docx_json.models.base import DocumentElement


@dataclass
class ComponentMarker(DocumentElement):
    """Représente un marqueur de composant éducatif."""

    component_type: str
    attributes: Dict[str, str] = field(default_factory=dict)

    def __init__(self, component_type: str):
        super().__init__("component_marker")
        self.component_type = component_type
        # Initialiser les attributs directement via le dictionnaire pour éviter la récursion
        self.__dict__["attributes"] = {}

    def __setattr__(self, name, value):
        """
        Surcharge pour stocker les attributs personnalisés dans self.attributes.

        Args:
            name: Nom de l'attribut
            value: Valeur de l'attribut
        """
        if name in ["type", "component_type", "_type", "_html_class", "_html_id"]:
            # Attributs standards du modèle - utiliser le dict pour éviter la récursion
            super().__setattr__(name, value)
        elif name == "attributes":
            # Accès direct au dictionnaire pour éviter la récursion
            self.__dict__[name] = value
        else:
            # Autres attributs stockés dans le dictionnaire attributes
            self.__dict__["attributes"][name] = value

    def __getattr__(self, name):
        """
        Surcharge pour récupérer les attributs depuis self.attributes.

        Args:
            name: Nom de l'attribut à récupérer

        Returns:
            La valeur de l'attribut ou None s'il n'existe pas

        Raises:
            AttributeError: Si l'attribut n'existe pas dans attributes
        """
        # Accéder au dictionnaire directement pour éviter la récursion
        attributes = self.__dict__.get("attributes", {})
        if name in attributes:
            return attributes[name]
        raise AttributeError(f"{type(self).__name__} has no attribute '{name}'")

    def to_dict(self) -> Dict[str, Any]:
        """Convertit le marqueur en dictionnaire pour le JSON."""
        result = super().to_dict()
        result["component_type"] = self.component_type
        # Ajouter les attributs personnalisés
        if self.__dict__["attributes"]:
            result["attributes"] = self.__dict__["attributes"]
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
