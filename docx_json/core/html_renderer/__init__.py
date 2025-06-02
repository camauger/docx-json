"""
Package pour les renderers HTML du convertisseur DOCX-JSON.
Ce package contient les classes responsables du rendu des différents éléments HTML.
"""

import logging
from typing import Any, Dict, List, Optional

from .base import ElementRenderer
from .block import BlockRenderer
from .component import ComponentRenderer
from .generator import HTMLGenerator
from .image import ImageRenderer
from .page_break import PageBreakRenderer
from .raw_html import RawHTMLRenderer
from .table import TableRenderer
from .text import TextElementRenderer

__all__ = [
    "ElementRenderer",
    "TextElementRenderer",
    "TableRenderer",
    "BlockRenderer",
    "ComponentRenderer",
    "ImageRenderer",
    "RawHTMLRenderer",
    "PageBreakRenderer",
    "HTMLGenerator",
]
