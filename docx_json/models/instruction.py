#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Modèle pour les instructions de formatage.
"""

from typing import Any, Dict, List, Optional

# Types de blocs supportés
BLOCK_TYPES = ["quote", "aside", "div", "section"]


class InstructionType:
    """Types d'instructions supportés."""

    CLASS = "class"
    ID = "id"
    IGNORE = "ignore"
    BLOCK = "block"
    TITLE = "title"  # Nouveau type d'instruction pour le titre du document
    HTML = "html"

    @classmethod
    def from_text(cls, text: str) -> Optional[str]:
        """Détermine le type d'instruction à partir du texte."""
        if text.startswith("class "):
            return cls.CLASS
        elif text.startswith("id "):
            return cls.ID
        elif text.startswith("ignore"):
            return cls.IGNORE
        elif any(text.startswith(f"{block} ") for block in BLOCK_TYPES):
            return cls.BLOCK
        elif text.startswith("title "):  # Analyse de l'instruction title
            return cls.TITLE
        elif text.startswith("html "):
            return cls.HTML
        return None


def extract_title_value(text: str) -> str:
    """
    Extrait la valeur du titre à partir du texte d'instruction.

    Args:
        text: Texte de l'instruction

    Returns:
        Valeur du titre
    """
    # Enlever le préfixe "title "
    return text[6:].strip() if text.startswith("title ") else ""
