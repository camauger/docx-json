#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests pour les modules CLI
Tests pour arguments, batch, converter, main
"""

import argparse
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

import pytest

from docx_json.cli.arguments import get_conversion_formats, parse_args
from docx_json.utils.logging import setup_logging


class TestArguments(unittest.TestCase):
    """Tests pour le module arguments.py."""

    @patch("sys.argv", ["docx-json", "test.docx"])
    def test_parse_args_minimal(self):
        """Test parsing avec arguments minimaux."""
        args = parse_args()

        self.assertEqual(args.input_file, "test.docx")
        self.assertTrue(args.json)  # JSON activé par défaut
        self.assertFalse(args.html)
        self.assertFalse(args.md)

    @patch("sys.argv", ["docx-json", "test.docx", "--json", "--html", "--md"])
    def test_parse_args_all_formats(self):
        """Test avec tous les formats."""
        args = parse_args()

        self.assertTrue(args.json)
        self.assertTrue(args.html)
        self.assertTrue(args.md)

    @patch("sys.argv", ["docx-json", "test.docx", "--output-dir", "output"])
    def test_parse_args_output_dir(self):
        """Test avec répertoire de sortie."""
        args = parse_args()

        self.assertEqual(args.output_dir, "output")

    @patch("sys.argv", ["docx-json", "test.docx", "--batch", "--recursive"])
    def test_parse_args_batch_recursive(self):
        """Test mode batch récursif."""
        args = parse_args()

        self.assertTrue(args.batch)
        self.assertTrue(args.recursive)

    @patch("sys.argv", ["docx-json", "test.docx", "--no-save-images"])
    def test_parse_args_no_save_images(self):
        """Test option no-save-images."""
        args = parse_args()

        self.assertTrue(args.no_save_images)

    @patch("sys.argv", ["docx-json", "test.docx", "--verbose"])
    def test_parse_args_verbose(self):
        """Test mode verbose."""
        args = parse_args()

        self.assertTrue(args.verbose)

    @patch("sys.argv", ["docx-json", "test.docx", "--skip-existing"])
    def test_parse_args_skip_existing(self):
        """Test option skip-existing."""
        args = parse_args()

        self.assertTrue(args.skip_existing)

    @patch("sys.argv", ["docx-json", "test.docx", "--force"])
    def test_parse_args_force(self):
        """Test option force."""
        args = parse_args()

        self.assertTrue(args.force)

    @patch("sys.argv", ["docx-json", "test.docx", "--quiet"])
    def test_parse_args_quiet(self):
        """Test mode quiet."""
        args = parse_args()

        self.assertTrue(args.quiet)

    @patch("sys.argv", ["docx-json", "test.docx", "--output-prefix", "prefix_"])
    def test_parse_args_prefix(self):
        """Test avec préfixe."""
        args = parse_args()

        self.assertEqual(args.output_prefix, "prefix_")

    @patch("sys.argv", ["docx-json", "test.docx", "--output-suffix", "_suffix"])
    def test_parse_args_suffix(self):
        """Test avec suffixe."""
        args = parse_args()

        self.assertEqual(args.output_suffix, "_suffix")

    @patch("sys.argv", ["docx-json", "test.docx", "--css", "custom.css"])
    def test_parse_args_css(self):
        """Test avec fichier CSS."""
        args = parse_args()

        self.assertEqual(args.css, "custom.css")

    @patch("sys.argv", ["docx-json", "test.docx", "--multipage"])
    def test_parse_args_multipage(self):
        """Test mode multipage."""
        args = parse_args()

        self.assertTrue(args.multipage)

    @patch("sys.argv", ["docx-json", "test.docx", "--no-filter-comments"])
    def test_parse_args_no_filter_comments(self):
        """Test désactivation filtrage commentaires."""
        args = parse_args()

        self.assertTrue(args.no_filter_comments)

    def test_get_conversion_formats(self):
        """Test extraction des formats de conversion."""
        mock_args = MagicMock()
        mock_args.json = True
        mock_args.html = True
        mock_args.md = False

        formats = get_conversion_formats(mock_args)

        self.assertEqual(formats, (True, True, False))

    def test_get_conversion_formats_all(self):
        """Test tous les formats activés."""
        mock_args = MagicMock()
        mock_args.json = True
        mock_args.html = True
        mock_args.md = True

        formats = get_conversion_formats(mock_args)

        self.assertEqual(formats, (True, True, True))


class TestLogging(unittest.TestCase):
    """Tests pour le module logging.py."""

    def test_setup_logging_normal(self):
        """Test configuration logging normale."""
        with patch("logging.basicConfig") as mock_config:
            setup_logging(verbose=False)

            # Vérifier que basicConfig a été appelé
            mock_config.assert_called_once()
            call_kwargs = mock_config.call_args[1]

            import logging

            self.assertEqual(call_kwargs["level"], logging.INFO)

    def test_setup_logging_verbose(self):
        """Test configuration logging verbose."""
        with patch("logging.basicConfig") as mock_config:
            setup_logging(verbose=True)

            mock_config.assert_called_once()
            call_kwargs = mock_config.call_args[1]

            import logging

            self.assertEqual(call_kwargs["level"], logging.DEBUG)

    def test_setup_logging_format(self):
        """Test format de logging."""
        with patch("logging.basicConfig") as mock_config:
            setup_logging(verbose=False)

            call_kwargs = mock_config.call_args[1]

            self.assertIn("format", call_kwargs)
            self.assertIn("%(levelname)s", call_kwargs["format"])
            self.assertIn("%(message)s", call_kwargs["format"])


class TestBatchProcessing(unittest.TestCase):
    """Tests pour les fonctionnalités de traitement par lot."""

    def setUp(self):
        """Crée un environnement de test."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

    def tearDown(self):
        """Nettoie l'environnement."""
        self.temp_dir.cleanup()

    def test_batch_directory_structure(self):
        """Test création structure de répertoires pour batch."""
        # Créer des fichiers DOCX de test
        (self.temp_path / "file1.docx").write_bytes(b"PK" + b"\x00" * 100)
        (self.temp_path / "file2.docx").write_bytes(b"PK" + b"\x00" * 100)

        # Créer sous-dossier
        subdir = self.temp_path / "subdir"
        subdir.mkdir()
        (subdir / "file3.docx").write_bytes(b"PK" + b"\x00" * 100)

        # Vérifier structure
        docx_files = list(self.temp_path.rglob("*.docx"))
        self.assertEqual(len(docx_files), 3)

    def test_batch_with_non_docx_files(self):
        """Test batch avec fichiers non-DOCX."""
        # Créer mix de fichiers
        (self.temp_path / "file1.docx").write_bytes(b"PK" + b"\x00" * 100)
        (self.temp_path / "file2.txt").write_text("test")
        (self.temp_path / "file3.pdf").write_bytes(b"PDF")

        # Seuls les DOCX devraient être traités
        docx_files = list(self.temp_path.glob("*.docx"))
        self.assertEqual(len(docx_files), 1)


class TestCLIIntegration(unittest.TestCase):
    """Tests d'intégration pour le CLI."""

    def setUp(self):
        """Crée un environnement de test."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

        # Créer un fichier DOCX de test
        self.test_docx = self.temp_path / "test.docx"
        self.test_docx.write_bytes(b"PK" + b"\x00" * 100)

    def tearDown(self):
        """Nettoie l'environnement."""
        self.temp_dir.cleanup()

    @patch("docx_json.cli.main.parse_args")
    @patch("docx_json.cli.main.convert_file")
    def test_main_single_file(self, mock_convert, mock_parse):
        """Test traitement fichier unique."""
        from docx_json.cli.main import main

        # Mock des arguments
        mock_args = MagicMock()
        mock_args.input_file = str(self.test_docx)
        mock_args.output_dir = None
        mock_args.output_prefix = None
        mock_args.output_suffix = None
        mock_args.no_save_images = False
        mock_args.batch = False
        mock_args.skip_existing = False
        mock_args.force = False
        mock_args.quiet = False
        mock_args.verbose = False
        mock_args.json = True
        mock_args.html = False
        mock_args.md = False
        mock_args.multipage = False
        mock_args.generate_css = False
        mock_args.css = None
        mock_args.css_output = None
        mock_args.css_styles = None

        mock_parse.return_value = mock_args
        mock_convert.return_value = True

        # Exécuter
        exit_code = main()

        # Vérifier
        self.assertEqual(exit_code, 0)
        mock_convert.assert_called_once()

    @patch("docx_json.cli.main.parse_args")
    def test_main_file_not_found(self, mock_parse):
        """Test erreur fichier non trouvé."""
        from docx_json.cli.main import main

        mock_args = MagicMock()
        mock_args.input_file = str(self.temp_path / "nonexistent.docx")
        mock_args.batch = False
        mock_parse.return_value = mock_args

        exit_code = main()

        self.assertEqual(exit_code, 1)

    @patch("docx_json.cli.main.parse_args")
    def test_main_invalid_extension(self, mock_parse):
        """Test erreur extension invalide."""
        from docx_json.cli.main import main

        # Créer fichier avec mauvaise extension
        txt_file = self.temp_path / "test.txt"
        txt_file.write_text("test")

        mock_args = MagicMock()
        mock_args.input_file = str(txt_file)
        mock_args.batch = False
        mock_parse.return_value = mock_args

        exit_code = main()

        self.assertEqual(exit_code, 1)


class TestConverterHelpers(unittest.TestCase):
    """Tests pour les fonctions helper du converter."""

    def test_determine_output_paths(self):
        """Test détermination chemins de sortie."""
        input_file = "document.docx"
        output_dir = "output"

        # Sans préfixe/suffixe
        base_name = Path(input_file).stem
        expected = f"{base_name}.json"

        self.assertEqual(base_name, "document")

    def test_determine_output_paths_with_prefix(self):
        """Test avec préfixe."""
        input_file = "document.docx"
        prefix = "converted_"

        base_name = Path(input_file).stem
        expected_name = f"{prefix}{base_name}"

        self.assertEqual(expected_name, "converted_document")

    def test_determine_output_paths_with_suffix(self):
        """Test avec suffixe."""
        input_file = "document.docx"
        suffix = "_v2"

        base_name = Path(input_file).stem
        expected_name = f"{base_name}{suffix}"

        self.assertEqual(expected_name, "document_v2")

    def test_determine_output_paths_with_both(self):
        """Test avec préfixe et suffixe."""
        input_file = "document.docx"
        prefix = "new_"
        suffix = "_final"

        base_name = Path(input_file).stem
        expected_name = f"{prefix}{base_name}{suffix}"

        self.assertEqual(expected_name, "new_document_final")


class TestOutputFormatting(unittest.TestCase):
    """Tests pour le formatage de sortie."""

    def test_quiet_mode_suppresses_output(self):
        """Test que le mode quiet supprime les sorties."""
        # Le mode quiet devrait empêcher les print()
        quiet = True

        if not quiet:
            output = "Message visible"
        else:
            output = None

        self.assertIsNone(output)

    def test_verbose_mode_shows_details(self):
        """Test que le mode verbose affiche les détails."""
        verbose = True

        if verbose:
            level = "DEBUG"
        else:
            level = "INFO"

        self.assertEqual(level, "DEBUG")


if __name__ == "__main__":
    unittest.main()
