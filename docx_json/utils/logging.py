#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Configuration du système de logging
----------------------------------
"""

import logging


def setup_logging(verbose: bool = False) -> None:
    """Configure le système de logging.

    Args:
        verbose: Si True, affiche les messages de debug
    """
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
