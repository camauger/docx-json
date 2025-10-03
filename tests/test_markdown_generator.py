#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests pour le module markdown_generator.py
Tests complets pour la génération de Markdown
"""

import unittest

from docx_json.core.markdown_generator import MarkdownGenerator


class TestMarkdownGeneratorInit(unittest.TestCase):
    """Tests pour l'initialisation du MarkdownGenerator."""

    def setUp(self):
        """Crée des données de test."""
        self.minimal_json = {
            "meta": {"title": "test.docx"},
            "content": [],
            "images": {},
        }

    def test_generator_initialization(self):
        """Test initialisation basique."""
        generator = MarkdownGenerator(self.minimal_json)

        self.assertIsNotNone(generator)
        self.assertEqual(generator._json_data, self.minimal_json)
        self.assertEqual(generator._images, {})


class TestMarkdownGeneratorParagraphs(unittest.TestCase):
    """Tests pour la génération de paragraphes Markdown."""

    def test_simple_paragraph(self):
        """Test paragraphe simple."""
        json_data = {
            "meta": {"title": "test.docx"},
            "content": [
                {
                    "type": "paragraph",
                    "runs": [
                        {
                            "text": "Simple paragraphe",
                            "bold": False,
                            "italic": False,
                            "underline": False,
                        }
                    ],
                }
            ],
            "images": {},
        }

        generator = MarkdownGenerator(json_data)
        markdown = generator.generate()

        self.assertIn("Simple paragraphe", markdown)

    def test_paragraph_with_bold(self):
        """Test paragraphe avec texte en gras."""
        json_data = {
            "meta": {"title": "test.docx"},
            "content": [
                {
                    "type": "paragraph",
                    "runs": [
                        {
                            "text": "Texte gras",
                            "bold": True,
                            "italic": False,
                            "underline": False,
                        }
                    ],
                }
            ],
            "images": {},
        }

        generator = MarkdownGenerator(json_data)
        markdown = generator.generate()

        self.assertIn("**Texte gras**", markdown)

    def test_paragraph_with_italic(self):
        """Test paragraphe avec texte en italique."""
        json_data = {
            "meta": {"title": "test.docx"},
            "content": [
                {
                    "type": "paragraph",
                    "runs": [
                        {
                            "text": "Texte italique",
                            "bold": False,
                            "italic": True,
                            "underline": False,
                        }
                    ],
                }
            ],
            "images": {},
        }

        generator = MarkdownGenerator(json_data)
        markdown = generator.generate()

        self.assertIn("*Texte italique*", markdown)

    def test_paragraph_with_underline(self):
        """Test paragraphe avec texte souligné."""
        json_data = {
            "meta": {"title": "test.docx"},
            "content": [
                {
                    "type": "paragraph",
                    "runs": [
                        {
                            "text": "Texte souligné",
                            "bold": False,
                            "italic": False,
                            "underline": True,
                        }
                    ],
                }
            ],
            "images": {},
        }

        generator = MarkdownGenerator(json_data)
        markdown = generator.generate()

        # Souligné utilise HTML dans Markdown
        self.assertIn("<u>Texte souligné</u>", markdown)


class TestMarkdownGeneratorHeadings(unittest.TestCase):
    """Tests pour la génération de titres Markdown."""

    def test_heading_level_1(self):
        """Test titre niveau 1."""
        json_data = {
            "meta": {"title": "test.docx"},
            "content": [
                {
                    "type": "heading",
                    "level": 1,
                    "runs": [
                        {
                            "text": "Titre Principal",
                            "bold": True,
                            "italic": False,
                            "underline": False,
                        }
                    ],
                }
            ],
            "images": {},
        }

        generator = MarkdownGenerator(json_data)
        markdown = generator.generate()

        # Titre niveau 1 utilise ====
        self.assertIn("Titre Principal", markdown)
        self.assertIn("=", markdown)

    def test_heading_level_2(self):
        """Test titre niveau 2."""
        json_data = {
            "meta": {"title": "test.docx"},
            "content": [
                {
                    "type": "heading",
                    "level": 2,
                    "runs": [
                        {
                            "text": "Sous-titre",
                            "bold": False,
                            "italic": False,
                            "underline": False,
                        }
                    ],
                }
            ],
            "images": {},
        }

        generator = MarkdownGenerator(json_data)
        markdown = generator.generate()

        # Titre niveau 2 utilise ----
        self.assertIn("Sous-titre", markdown)
        self.assertIn("-", markdown)

    def test_heading_level_3(self):
        """Test titre niveau 3."""
        json_data = {
            "meta": {"title": "test.docx"},
            "content": [
                {
                    "type": "heading",
                    "level": 3,
                    "runs": [
                        {
                            "text": "Titre niveau 3",
                            "bold": False,
                            "italic": False,
                            "underline": False,
                        }
                    ],
                }
            ],
            "images": {},
        }

        generator = MarkdownGenerator(json_data)
        markdown = generator.generate()

        # Titre niveau 3+ utilise ###
        self.assertIn("### Titre niveau 3", markdown)


class TestMarkdownGeneratorTables(unittest.TestCase):
    """Tests pour la génération de tableaux Markdown."""

    def test_simple_table(self):
        """Test tableau simple 2x2."""
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
                                            "text": "A1",
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
                                            "text": "B1",
                                            "bold": False,
                                            "italic": False,
                                            "underline": False,
                                        }
                                    ],
                                }
                            ],
                        ],
                        [
                            [
                                {
                                    "type": "paragraph",
                                    "runs": [
                                        {
                                            "text": "A2",
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
                                            "text": "B2",
                                            "bold": False,
                                            "italic": False,
                                            "underline": False,
                                        }
                                    ],
                                }
                            ],
                        ],
                    ],
                }
            ],
            "images": {},
        }

        generator = MarkdownGenerator(json_data)
        markdown = generator.generate()

        # Vérifier format de tableau Markdown
        self.assertIn("| A1 | B1 |", markdown)
        self.assertIn("| A2 | B2 |", markdown)
        self.assertIn("| --- | --- |", markdown)  # Séparateur


class TestMarkdownGeneratorComponents(unittest.TestCase):
    """Tests pour la génération de composants pédagogiques."""

    def test_video_component(self):
        """Test composant vidéo."""
        json_data = {
            "meta": {"title": "test.docx"},
            "content": [
                {
                    "type": "component",
                    "component_type": "Vidéo",
                    "content": [
                        {
                            "type": "paragraph",
                            "runs": [
                                {
                                    "text": "Description vidéo",
                                    "bold": False,
                                    "italic": False,
                                    "underline": False,
                                }
                            ],
                        }
                    ],
                }
            ],
            "images": {},
        }

        generator = MarkdownGenerator(json_data)
        markdown = generator.generate()

        self.assertIn("[Vidéo]", markdown)
        self.assertIn("[Fin Vidéo]", markdown)
        self.assertIn("Description vidéo", markdown)

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
                                    "text": "Section",
                                    "bold": False,
                                    "italic": False,
                                    "underline": False,
                                }
                            ],
                        }
                    ],
                }
            ],
            "images": {},
        }

        generator = MarkdownGenerator(json_data)
        markdown = generator.generate()

        self.assertIn("[Accordéon]", markdown)
        self.assertIn("[Fin Accordéon]", markdown)


class TestMarkdownGeneratorBlocks(unittest.TestCase):
    """Tests pour la génération de blocs spéciaux."""

    def test_quote_block(self):
        """Test bloc de citation."""
        json_data = {
            "meta": {"title": "test.docx"},
            "content": [
                {
                    "type": "block",
                    "block_type": "quote",
                    "content": [
                        {
                            "type": "paragraph",
                            "runs": [
                                {
                                    "text": "Ceci est une citation",
                                    "bold": False,
                                    "italic": False,
                                    "underline": False,
                                }
                            ],
                        }
                    ],
                }
            ],
            "images": {},
        }

        generator = MarkdownGenerator(json_data)
        markdown = generator.generate()

        # Citation préfixée avec >
        self.assertIn("> Ceci est une citation", markdown)

    def test_aside_block(self):
        """Test bloc aside."""
        json_data = {
            "meta": {"title": "test.docx"},
            "content": [
                {
                    "type": "block",
                    "block_type": "aside",
                    "content": [
                        {
                            "type": "paragraph",
                            "runs": [
                                {
                                    "text": "Note importante",
                                    "bold": False,
                                    "italic": False,
                                    "underline": False,
                                }
                            ],
                        }
                    ],
                }
            ],
            "images": {},
        }

        generator = MarkdownGenerator(json_data)
        markdown = generator.generate()

        # Aside utilise :::info
        self.assertIn(":::info", markdown)
        self.assertIn(":::", markdown)


class TestMarkdownGeneratorMetadata(unittest.TestCase):
    """Tests pour la génération de métadonnées YAML."""

    def test_yaml_frontmatter(self):
        """Test génération frontmatter YAML."""
        json_data = {
            "meta": {"title": "document.docx"},
            "content": [],
            "images": {},
        }

        generator = MarkdownGenerator(json_data)
        markdown = generator.generate()

        # Vérifier présence du frontmatter YAML
        self.assertTrue(markdown.startswith("---"))
        self.assertIn("title: document.docx", markdown)
        self.assertIn("author: Généré automatiquement", markdown)
        self.assertIn("date:", markdown)

    def test_empty_content(self):
        """Test avec contenu vide."""
        json_data = {
            "meta": {"title": "empty.docx"},
            "content": [],
            "images": {},
        }

        generator = MarkdownGenerator(json_data)
        markdown = generator.generate()

        # Devrait au moins avoir le frontmatter
        self.assertIn("---", markdown)
        self.assertIn("title: empty.docx", markdown)


class TestMarkdownGeneratorRawHTML(unittest.TestCase):
    """Tests pour le HTML brut dans Markdown."""

    def test_raw_html_element(self):
        """Test élément HTML brut."""
        json_data = {
            "meta": {"title": "test.docx"},
            "content": [{"type": "raw_html", "content": "<hr />"}],
            "images": {},
        }

        generator = MarkdownGenerator(json_data)
        markdown = generator.generate()

        # HTML brut devrait être conservé
        self.assertIn("<hr />", markdown)


if __name__ == "__main__":
    unittest.main()
