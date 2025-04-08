#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Exceptions personnalisées pour le module docx_json.
"""


class DocxJsonError(Exception):
    """Exception de base pour toutes les erreurs du module docx_json."""

    pass


class DocxValidationError(DocxJsonError):
    """Exception levée lorsque le document DOCX n'est pas valide."""

    def __init__(
        self, message="The DOCX file is invalid or corrupted", *args, **kwargs
    ):
        super().__init__(message, *args, **kwargs)


class ConversionError(DocxJsonError):
    """Exception levée lorsqu'une erreur survient pendant la conversion du document."""

    pass


class OutputGenerationError(ConversionError):
    """Exception levée lorsqu'une erreur survient pendant la génération du fichier de sortie."""

    pass


class ImageHandlingError(ConversionError):
    """Exception levée lors d'erreurs liées au traitement des images."""

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
