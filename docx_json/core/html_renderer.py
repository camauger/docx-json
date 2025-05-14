#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module de rendu HTML pour la conversion DOCX vers HTML
------------------------------------------------------
"""

import logging
import os
import re
from typing import Any, Dict, List, Optional, Union

from docx_json.models import Component, Block

logger = logging.getLogger(__name__)


class HTMLGenerator:
    """
    Générateur de HTML à partir des données JSON du document.
    """

    def __init__(self, json_data: Dict[str, Any]):
        """
        Initialise le générateur HTML.

        Args:
            json_data: Données JSON du document
        """
        self.json_data = json_data
        self.custom_css = None
        self.css_path = None
        self.component_counters = {
            "accordion": 0,
            "carousel": 0,
            "tabs": 0,
            "audio": 0,
            "video": 0,
        }

    def generate(self, css_path: Optional[str] = None, custom_css: Optional[str] = None) -> str:
        """
        Génère le HTML complet du document.

        Args:
            css_path: Chemin vers un fichier CSS externe
            custom_css: CSS personnalisé à injecter dans le HTML

        Returns:
            Document HTML complet
        """
        self.css_path = css_path
        self.custom_css = custom_css

        html_parts = []
        html_parts.append(self.generate_html_header())

        # Générer le contenu
        for element in self.json_data.get("content", []):
            try:
                html_parts.append(self.render_element(element))
            except Exception as e:
                logger.error(f"Erreur de rendu HTML: {str(e)}")
                html_parts.append(f'<!-- Erreur lors du rendu : {str(e)} -->')
                html_parts.append('<div class="rendering-error">(Erreur de rendu)</div>')

        html_parts.append(self.generate_html_footer())
        return "\n".join(html_parts)

    def generate_html_header(self) -> str:
        """
        Génère l'en-tête HTML du document.

        Returns:
            En-tête HTML
        """
        # Récupérer le titre du document à partir des métadonnées
        title = self.json_data.get("meta", {}).get("title", "Document sans titre")

        return f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <title>{title}</title>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <link rel='stylesheet' href='https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css'>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" crossorigin="anonymous">
  <style>
    {self.custom_css or ""}
    @media print {
      .page-break {
        page-break-after: always;
        break-after: page;
      }
    }
  </style>
</head>
<body>
  <!-- En-tête -->
  <header class="bg-primary py-3 mb-4 shadow-sm">
    <div class="container">
      <div class="d-flex align-items-center">
        <h1 class="h4 mb-0">{title}</h1>
        <div class="ms-auto">
          <button class="btn btn-outline-light btn-sm" id="theme-toggle">
            <i class="bi bi-brightness-high" id="light-icon"></i>
            <i class="bi bi-moon-stars d-none" id="dark-icon"></i>
          </button>
        </div>
      </div>
    </div>
  </header>
  <!-- Contenu principal -->
  <main class='container'>
    <div class="col-8 m-auto py-4">"""

    def generate_html_footer(self) -> str:
        """
        Génère le pied de page HTML du document.

        Returns:
            Pied de page HTML
        """
        return """
    </div>
  </main>
  <!-- Pied de page -->
  <footer class="bg-light py-4 mt-5 border-top">
    <div class="container">
      <div class="row">
        <div class="col-md-6">
          <p class="mb-0 text-muted">© 2025 - TELUQ</p>
        </div>
        <div class="col-md-6 text-md-end">
          <a href="#" class="text-decoration-none me-3"><i class="bi bi-github"></i> GitHub</a>
          <a href="#" class="text-decoration-none"><i class="bi bi-book"></i> Documentation</a>
        </div>
      </div>
    </div>
  </footer>
  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-YvpcrYf0tY3lHB60NNkmXc5s9fDVZLESaAA55NDzOxhy9GkcIdslK1eN7N6jIeHz" crossorigin="anonymous"></script>
  <script>
    document.getElementById("theme-toggle").addEventListener("click", function() {
      document.body.classList.toggle("bg-dark");
      document.body.classList.toggle("text-white");
      document.getElementById("light-icon").classList.toggle("d-none");
      document.getElementById("dark-icon").classList.toggle("d-none");
      const containers = document.querySelectorAll(".container");
      containers.forEach(container => {
        if (document.body.classList.contains("bg-dark")) {
          container.style.backgroundColor = "#343a40";
          container.style.color = "#fff";
        } else {
          container.style.backgroundColor = "#fff";
          container.style.color = "#212529";
        }
      });
    });
  </script>
</body>
</html>"""

    def render_element(self, element: Dict[str, Any]) -> str:
        """
        Rend un élément du document en HTML.

        Args:
            element: Élément du document

        Returns:
            HTML correspondant à l'élément
        """
        element_type = element.get("type")

        if element_type == "paragraph":
            return self.render_paragraph(element)
        elif element_type == "heading":
            return self.render_heading(element)
        elif element_type == "component":
            return self.render_component(element)
        elif element_type == "block":
            return self.render_block(element)
        elif element_type == "table":
            return self.render_table(element)
        elif element_type == "list":
            return self.render_list(element)
        elif element_type == "image":
            return self.render_image(element)
        elif element_type == "raw_html":
            return element.get("content", "")

        # Type inconnu
        return f'<!-- Élément inconnu: {element_type} -->'

    # Les autres méthodes de rendu restent inchangées...