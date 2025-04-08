#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Modèles de données pour la conversion DOCX
"""

# Import de la classe de base
from docx_json.models.base import DocumentElement

# Import des éléments conteneurs
from docx_json.models.containers import Block, Component, Table

# Import des éléments médias
from docx_json.models.media import Image

# Import des éléments spéciaux
from docx_json.models.special import ComponentEnd, ComponentMarker, Instruction, RawHTML

# Import des éléments textuels
from docx_json.models.text import Heading, ListItem, Paragraph, TextRun

# Pour conserver la compatibilité avec le code existant
__all__ = [
    "DocumentElement",
    "TextRun",
    "Paragraph",
    "Heading",
    "ListItem",
    "Image",
    "Table",
    "Component",
    "ComponentMarker",
    "ComponentEnd",
    "Block",
    "Instruction",
    "RawHTML",
]
