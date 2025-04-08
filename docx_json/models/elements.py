#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Modèle de données pour les éléments du document.

Ce module est conservé pour des raisons de rétrocompatibilité.
Pour les nouvelles applications, utilisez les modules spécialisés:
- docx_json.models.base
- docx_json.models.text
- docx_json.models.media
- docx_json.models.containers
- docx_json.models.special
"""

import warnings

# Émettre un avertissement de dépréciation mais ne pas perturber l'exécution
warnings.warn(
    "Le module 'docx_json.models.elements' est déprécié. "
    "Utilisez plutôt les modules spécialisés dans docx_json.models.*",
    DeprecationWarning,
    stacklevel=2,
)

# Import de tous les éléments depuis leurs nouveaux emplacements
from docx_json.models import (
    Block,
    Component,
    ComponentEnd,
    ComponentMarker,
    DocumentElement,
    Heading,
    Image,
    Instruction,
    ListItem,
    Paragraph,
    RawHTML,
    Table,
    TextRun,
)

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
