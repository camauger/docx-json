#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests pour les modules HTML renderer
Tests complets pour la génération HTML
"""

import unittest

from docx_json.core.html_renderer.generator import HTMLGenerator


class TestHTMLGeneratorInit(unittest.TestCase):
    """Tests pour l'initialisation du HTMLGenerator."""

    def setUp(self):
        """Crée des données de test."""
        self.minimal_json = {
            "meta": {"title": "test.docx"},
            "content": [],
            "images": {},
        }

    def test_generator_initialization(self):
        """Test initialisation basique."""
        generator = HTMLGenerator(self.minimal_json)

        self.assertIsNotNone(generator)

    def test_empty_content(self):
        """Test génération avec contenu vide."""
        generator = HTMLGenerator(self.minimal_json)
        html = generator.generate()

        # Devrait avoir la structure HTML de base
        self.assertIn("<!DOCTYPE html>", html)
        self.assertIn("<html", html)
        self.assertIn("</html>", html)
        self.assertIn("<head>", html)
        self.assertIn("<body>", html)


class TestHTMLGeneratorParagraphs(unittest.TestCase):
    """Tests pour la génération de paragraphes HTML."""

    def test_simple_paragraph(self):
        """Test paragraphe simple."""
        json_data = {
            "meta": {"title": "test.docx"},
            "content": [
                {
                    "type": "paragraph",
                    "runs": [
                        {
                            "text": "Simple text",
                            "bold": False,
                            "italic": False,
                            "underline": False,
                        }
                    ],
                }
            ],
            "images": {},
        }

        generator = HTMLGenerator(json_data)
        html = generator.generate()

        self.assertIn("<p>", html)
        self.assertIn("Simple text", html)
        self.assertIn("</p>", html)

    def test_paragraph_with_bold(self):
        """Test paragraphe avec gras."""
        json_data = {
            "meta": {"title": "test.docx"},
            "content": [
                {
                    "type": "paragraph",
                    "runs": [
                        {
                            "text": "Bold text",
                            "bold": True,
                            "italic": False,
                            "underline": False,
                        }
                    ],
                }
            ],
            "images": {},
        }

        generator = HTMLGenerator(json_data)
        html = generator.generate()

        self.assertIn("<strong>Bold text</strong>", html)

    def test_paragraph_with_italic(self):
        """Test paragraphe avec italique."""
        json_data = {
            "meta": {"title": "test.docx"},
            "content": [
                {
                    "type": "paragraph",
                    "runs": [
                        {
                            "text": "Italic text",
                            "bold": False,
                            "italic": True,
                            "underline": False,
                        }
                    ],
                }
            ],
            "images": {},
        }

        generator = HTMLGenerator(json_data)
        html = generator.generate()

        self.assertIn("<em>Italic text</em>", html)

    def test_paragraph_with_css_class(self):
        """Test paragraphe avec classe CSS."""
        json_data = {
            "meta": {"title": "test.docx"},
            "content": [
                {
                    "type": "paragraph",
                    "runs": [
                        {
                            "text": "Text",
                            "bold": False,
                            "italic": False,
                            "underline": False,
                        }
                    ],
                    "html_class": "highlight",
                }
            ],
            "images": {},
        }

        generator = HTMLGenerator(json_data)
        html = generator.generate()

        self.assertIn('class="highlight"', html)

    def test_paragraph_with_id(self):
        """Test paragraphe avec ID HTML."""
        json_data = {
            "meta": {"title": "test.docx"},
            "content": [
                {
                    "type": "paragraph",
                    "runs": [
                        {
                            "text": "Text",
                            "bold": False,
                            "italic": False,
                            "underline": False,
                        }
                    ],
                    "html_id": "intro",
                }
            ],
            "images": {},
        }

        generator = HTMLGenerator(json_data)
        html = generator.generate()

        self.assertIn('id="intro"', html)


class TestHTMLGeneratorHeadings(unittest.TestCase):
    """Tests pour la génération de titres HTML."""

    def test_heading_h1(self):
        """Test génération h1."""
        json_data = {
            "meta": {"title": "test.docx"},
            "content": [
                {
                    "type": "heading",
                    "level": 1,
                    "runs": [
                        {
                            "text": "Titre H1",
                            "bold": False,
                            "italic": False,
                            "underline": False,
                        }
                    ],
                }
            ],
            "images": {},
        }

        generator = HTMLGenerator(json_data)
        html = generator.generate()

        self.assertIn("<h1>", html)
        self.assertIn("Titre H1", html)
        self.assertIn("</h1>", html)

    def test_heading_h2(self):
        """Test génération h2."""
        json_data = {
            "meta": {"title": "test.docx"},
            "content": [
                {
                    "type": "heading",
                    "level": 2,
                    "runs": [
                        {
                            "text": "Titre H2",
                            "bold": False,
                            "italic": False,
                            "underline": False,
                        }
                    ],
                }
            ],
            "images": {},
        }

        generator = HTMLGenerator(json_data)
        html = generator.generate()

        self.assertIn("<h2>", html)
        self.assertIn("Titre H2", html)


class TestHTMLGeneratorTables(unittest.TestCase):
    """Tests pour la génération de tableaux HTML."""

    def test_simple_table(self):
        """Test tableau simple."""
        json_data = {
            "meta": {"title": "test.docx"},
            "content": [
                {
                    "type": "table",
                    "rows": [
                        [
                            [
                                {
                                    "type": "paragraph",
                                    "runs": [
                                        {
                                            "text": "Cell1",
                                            "bold": False,
                                            "italic": False,
                                            "underline": False,
                                        }
                                    ],
                                }
                            ],
                            [
                                {
                                    "type": "paragraph",
                                    "runs": [
                                        {
                                            "text": "Cell2",
                                            "bold": False,
                                            "italic": False,
                                            "underline": False,
                                        }
                                    ],
                                }
                            ],
                        ]
                    ],
                }
            ],
            "images": {},
        }

        generator = HTMLGenerator(json_data)
        html = generator.generate()

        self.assertIn("<table>", html)
        self.assertIn("<tr>", html)
        self.assertIn("<td>", html)
        self.assertIn("Cell1", html)
        self.assertIn("Cell2", html)


class TestHTMLGeneratorImages(unittest.TestCase):
    """Tests pour la génération d'images HTML."""

    def test_image_element(self):
        """Test élément image."""
        json_data = {
            "meta": {"title": "test.docx"},
            "content": [
                {
                    "type": "image",
                    "image_path": "images/test.png",
                    "alt_text": "Test Image",
                }
            ],
            "images": {"test.png": "images/test.png"},
        }

        generator = HTMLGenerator(json_data)
        html = generator.generate()

        self.assertIn("<img", html)
        self.assertIn('src="images/test.png"', html)
        self.assertIn('alt="Test Image"', html)


class TestHTMLGeneratorComponents(unittest.TestCase):
    """Tests pour la génération de composants pédagogiques."""

    def test_video_component(self):
        """Test composant vidéo."""
        json_data = {
            "meta": {"title": "test.docx"},
            "content": [
                {
                    "type": "component",
                    "component_type": "Vidéo",
                    "video_id": "123456",
                    "content": [],
                }
            ],
            "images": {},
        }

        generator = HTMLGenerator(json_data)
        html = generator.generate()

        self.assertIn("video-component", html)

    def test_accordion_component(self):
        """Test composant accordéon."""
        json_data = {
            "meta": {"title": "test.docx"},
            "content": [
                {
                    "type": "component",
                    "component_type": "Accordéon",
                    "content": [
                        {
                            "type": "heading",
                            "level": 2,
                            "runs": [
                                {
                                    "text": "Section 1",
                                    "bold": False,
                                    "italic": False,
                                    "underline": False,
                                }
                            ],
                        },
                        {
                            "type": "paragraph",
                            "runs": [
                                {
                                    "text": "Contenu",
                                    "bold": False,
                                    "italic": False,
                                    "underline": False,
                                }
                            ],
                        },
                    ],
                }
            ],
            "images": {},
        }

        generator = HTMLGenerator(json_data)
        html = generator.generate()

        self.assertIn("accordion", html)
        self.assertIn("Section 1", html)


class TestHTMLGeneratorCustomCSS(unittest.TestCase):
    """Tests pour le CSS personnalisé."""

    def test_custom_css(self):
        """Test avec CSS personnalisé."""
        json_data = {
            "meta": {"title": "test.docx"},
            "content": [],
            "images": {},
        }

        generator = HTMLGenerator(json_data)
        custom_css = "body { font-family: Arial; }"
        html = generator.generate(custom_css=custom_css)

        self.assertIn("<style>", html)
        self.assertIn("body { font-family: Arial; }", html)
        self.assertIn("</style>", html)
        # Ne devrait pas avoir Bootstrap CDN
        self.assertNotIn("bootstrap", html)

    def test_default_bootstrap(self):
        """Test avec Bootstrap par défaut."""
        json_data = {
            "meta": {"title": "test.docx"},
            "content": [],
            "images": {},
        }

        generator = HTMLGenerator(json_data)
        html = generator.generate()

        # Devrait avoir Bootstrap CDN
        self.assertIn("bootstrap", html.lower())


if __name__ == "__main__":
    unittest.main()
