#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Point d'entrée principal pour l'exécution en tant que module
----------------------------------------------------------

Permet d'exécuter le module directement avec:
    python -m docx_json fichier.docx --options
"""

import sys

from docx_json.cli.main import main

if __name__ == "__main__":
    sys.exit(main())
