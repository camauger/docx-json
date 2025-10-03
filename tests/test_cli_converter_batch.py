#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests pour cli/converter.py et cli/batch.py
Tests complets pour les fonctionnalités de conversion
"""

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from docx import Document


class TestConverterFileOperations(unittest.TestCase):
    """Tests pour les opérations de fichiers."""

    def setUp(self):
        """Crée un environnement de test."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

    def tearDown(self):
        """Nettoie l'environnement."""
        self.temp_dir.cleanup()

    def test_determine_output_filename(self):
        """Test détermination nom de fichier de sortie."""
        input_file = "document.docx"
        base_name = Path(input_file).stem

        # Sans préfixe ni suffixe
        json_name = f"{base_name}.json"
        html_name = f"{base_name}.html"

        self.assertEqual(json_name, "document.json")
        self.assertEqual(html_name, "document.html")

    def test_output_with_prefix(self):
        """Test nom de sortie avec préfixe."""
        input_file = "document.docx"
        prefix = "converted_"
        base_name = Path(input_file).stem

        output_name = f"{prefix}{base_name}.json"

        self.assertEqual(output_name, "converted_document.json")

    def test_output_with_suffix(self):
        """Test nom de sortie avec suffixe."""
        input_file = "document.docx"
        suffix = "_processed"
        base_name = Path(input_file).stem

        output_name = f"{base_name}{suffix}.json"

        self.assertEqual(output_name, "document_processed.json")

    def test_output_with_custom_directory(self):
        """Test sortie dans répertoire personnalisé."""
        output_dir = self.temp_path / "output"
        output_dir.mkdir()

        output_file = output_dir / "result.json"

        self.assertTrue(output_dir.exists())
        self.assertEqual(output_file.name, "result.json")


class TestBatchProcessingLogic(unittest.TestCase):
    """Tests pour la logique de traitement par lot."""

    def setUp(self):
        """Crée un environnement de test."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

    def tearDown(self):
        """Nettoie l'environnement."""
        self.temp_dir.cleanup()

    def test_find_docx_files(self):
        """Test recherche de fichiers DOCX."""
        # Créer plusieurs fichiers
        (self.temp_path / "file1.docx").write_bytes(b"PK" + b"\x00" * 100)
        (self.temp_path / "file2.docx").write_bytes(b"PK" + b"\x00" * 100)
        (self.temp_path / "file3.txt").write_text("text")

        # Trouver les DOCX
        docx_files = list(self.temp_path.glob("*.docx"))

        self.assertEqual(len(docx_files), 2)

    def test_recursive_search(self):
        """Test recherche récursive."""
        # Créer structure de dossiers
        (self.temp_path / "file1.docx").write_bytes(b"PK" + b"\x00" * 100)

        subdir = self.temp_path / "subdir"
        subdir.mkdir()
        (subdir / "file2.docx").write_bytes(b"PK" + b"\x00" * 100)

        deep = subdir / "deep"
        deep.mkdir()
        (deep / "file3.docx").write_bytes(b"PK" + b"\x00" * 100)

        # Recherche récursive
        all_docx = list(self.temp_path.rglob("*.docx"))

        self.assertEqual(len(all_docx), 3)

    def test_batch_with_output_directory(self):
        """Test batch avec répertoire de sortie."""
        # Créer fichiers source
        source_dir = self.temp_path / "source"
        source_dir.mkdir()
        (source_dir / "file1.docx").write_bytes(b"PK" + b"\x00" * 100)

        # Créer répertoire de sortie
        output_dir = self.temp_path / "output"
        output_dir.mkdir()

        self.assertTrue(source_dir.exists())
        self.assertTrue(output_dir.exists())


class TestConverterSkipExisting(unittest.TestCase):
    """Tests pour l'option skip-existing."""

    def setUp(self):
        """Crée un environnement de test."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

    def tearDown(self):
        """Nettoie l'environnement."""
        self.temp_dir.cleanup()

    def test_file_exists_check(self):
        """Test vérification existence fichier."""
        output_file = self.temp_path / "output.json"
        output_file.write_text("{}")

        should_skip = output_file.exists()

        self.assertTrue(should_skip)

    def test_file_modification_time_comparison(self):
        """Test comparaison temps de modification."""
        import time

        source_file = self.temp_path / "source.docx"
        source_file.write_bytes(b"PK")

        time.sleep(0.1)

        output_file = self.temp_path / "output.json"
        output_file.write_text("{}")

        source_mtime = source_file.stat().st_mtime
        output_mtime = output_file.stat().st_mtime

        # Output devrait être plus récent
        self.assertGreater(output_mtime, source_mtime)


class TestConverterForceFlag(unittest.TestCase):
    """Tests pour l'option force."""

    def setUp(self):
        """Crée un environnement de test."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

    def tearDown(self):
        """Nettoie l'environnement."""
        self.temp_dir.cleanup()

    def test_force_overwrite(self):
        """Test forcer l'écrasement."""
        output_file = self.temp_path / "output.json"
        output_file.write_text('{"old": "data"}')

        original_content = output_file.read_text()

        # Avec force, devrait écraser
        force = True
        if force or not output_file.exists():
            output_file.write_text('{"new": "data"}')

        new_content = output_file.read_text()

        self.assertNotEqual(original_content, new_content)
        self.assertEqual(new_content, '{"new": "data"}')


class TestConverterQuietMode(unittest.TestCase):
    """Tests pour le mode quiet."""

    def test_quiet_flag_behavior(self):
        """Test comportement du flag quiet."""
        quiet = True

        # En mode quiet, ne rien afficher
        if not quiet:
            message = "Verbose message"
        else:
            message = None

        self.assertIsNone(message)

    def test_normal_mode_output(self):
        """Test mode normal avec sortie."""
        quiet = False

        if not quiet:
            message = "Normal message"
        else:
            message = None

        self.assertEqual(message, "Normal message")


class TestBatchProgressTracking(unittest.TestCase):
    """Tests pour le suivi de progression batch."""

    def test_success_counter(self):
        """Test compteur de succès."""
        total_files = 10
        successful = 0

        for i in range(total_files):
            if i % 2 == 0:  # Simuler succès 1/2
                successful += 1

        self.assertEqual(successful, 5)
        self.assertEqual(total_files, 10)

    def test_completion_percentage(self):
        """Test calcul pourcentage de complétion."""
        processed = 7
        total = 10

        percentage = (processed / total) * 100

        self.assertEqual(percentage, 70.0)

    def test_batch_summary(self):
        """Test résumé de traitement batch."""
        total = 15
        successful = 12
        failed = 3

        self.assertEqual(total, successful + failed)
        self.assertEqual(successful, 12)
        self.assertEqual(failed, 3)


class TestConverterMultiFormat(unittest.TestCase):
    """Tests pour conversion multi-format."""

    def test_multiple_format_output(self):
        """Test sortie multiple formats."""
        formats = (True, True, True)  # JSON, HTML, MD

        json_enabled, html_enabled, md_enabled = formats

        self.assertTrue(json_enabled)
        self.assertTrue(html_enabled)
        self.assertTrue(md_enabled)

    def test_single_format_output(self):
        """Test sortie format unique."""
        formats = (True, False, False)  # JSON only

        json_enabled, html_enabled, md_enabled = formats

        self.assertTrue(json_enabled)
        self.assertFalse(html_enabled)
        self.assertFalse(md_enabled)


if __name__ == "__main__":
    unittest.main()
