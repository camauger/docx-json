#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module principal pour la conversion de fichiers DOCX en JSON/HTML/Markdown
Ce module fournit une compatibilité avec l'ancienne API tout en utilisant
la nouvelle implémentation modulaire.

Ce fichier est conservé pour des raisons de rétrocompatibilité.
Pour les nouvelles applications, utilisez directement:
- docx_json.cli.converter
- docx_json.cli.batch
- docx_json.cli.main
"""

import sys
import warnings

# Émettre un avertissement de dépréciation mais ne pas perturber l'exécution
warnings.warn(
    "Le module 'docx_json.convert' est déprécié. "
    "Utilisez plutôt 'docx_json.cli.converter', 'docx_json.cli.batch' ou 'docx_json.cli.main'.",
    DeprecationWarning,
    stacklevel=2,
)

# Importer les fonctions depuis les nouveaux emplacements pour maintenir la compatibilité API
from docx_json.cli.main import main

# Exécuter la fonction principale si appelé directement
if __name__ == "__main__":
    try:
        exit_code: int = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\nOpération annulée par l'utilisateur.")
        sys.exit(130)
    except Exception as e:
        print(f"Erreur critique: {str(e)}")
        sys.exit(1)
