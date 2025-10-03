#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
DOCX to JSON/HTML Converter
---------------------------

Un package Python pour convertir des fichiers .docx en
fichiers .json structurés ou .html sémantiques.
"""

# Pour la compatibilité, exposer également les fonctions de l'ancienne API
from docx_json.core.compatibility import (
    extract_images,
    generate_html,
    generate_markdown,
    get_document_json,
    get_paragraph_json,
    get_table_json,
    process_instructions,
)
from docx_json.core.converter import DocxConverter, HTMLGenerator
from docx_json.models.elements import (
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

__version__ = "1.0.1"
__author__ = "Développeur TÉLUQ"
