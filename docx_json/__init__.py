#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
DOCX to JSON/HTML Converter
---------------------------

Un package Python pour convertir des fichiers .docx en
fichiers .json structurés ou .html sémantiques.
"""

from docx_json.core.converter import DocxConverter, HTMLGenerator
from docx_json.models.elements import (
    DocumentElement, TextRun, Paragraph, Heading, ListItem,
    Image, Table, ComponentMarker, ComponentEnd,
    Component, Block, Instruction, RawHTML
)

__version__ = "1.0.0"
__author__ = "Développeur TÉLUQ"
