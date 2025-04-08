#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Définitions des exceptions personnalisées pour le package docx_json
"""


class DocxJsonError(Exception):
    """Exception de base pour toutes les erreurs du package docx_json."""

    pass


class DocxValidationError(DocxJsonError):
    """Exception levée quand un document DOCX est invalide ou ne peut pas être ouvert."""

    pass


class ConversionError(DocxJsonError):
    """Exception levée quand la conversion échoue pour une raison quelconque."""

    pass


class ImageExtractionError(DocxJsonError):
    """Exception levée quand l'extraction des images échoue."""

    pass


class HTMLGenerationError(DocxJsonError):
    """Exception levée quand la génération du HTML échoue."""

    pass


class MarkdownGenerationError(DocxJsonError):
    """Exception levée quand la génération du Markdown échoue."""

    pass
