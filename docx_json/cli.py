#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Module contenant l'interface en ligne de commande pour docx-json."""

import argparse
import json
import logging
import os
import sys
from typing import Dict, List, Optional, cast

from docx_json import __version__
from docx_json.core.compatibility import generate_html, generate_markdown
from docx_json.core.converter import DocxConverter
from docx_json.core.html_renderer import HTMLGenerator
from docx_json.exceptions import DocxValidationError

# ... existing code ...
