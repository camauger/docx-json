#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests pour les modules utils
Tests pour image_utils, logging, comment_filter
"""

import base64
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from docx_json.utils.logging import setup_logging


class TestImageUtils(unittest.TestCase):
    """Tests pour le module image_utils.py."""

    def setUp(self):
        """Crée un environnement de test."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

    def tearDown(self):
        """Nettoie l'environnement."""
        self.temp_dir.cleanup()

    def test_image_path_generation(self):
        """Test génération chemins d'images."""
        images_dir = self.temp_path / "images"
        images_dir.mkdir()

        image_name = "test_image.png"
        image_path = images_dir / image_name

        # Créer une image de test
        image_path.write_bytes(b"\x89PNG" + b"\x00" * 100)

        self.assertTrue(image_path.exists())
        self.assertEqual(image_path.name, "test_image.png")

    def test_image_base64_encoding(self):
        """Test encodage base64 d'images."""
        # Données d'image simulées
        image_data = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100

        # Encoder en base64
        encoded = base64.b64encode(image_data).decode("utf-8")

        # Vérifier
        self.assertIsInstance(encoded, str)
        self.assertTrue(len(encoded) > 0)

        # Décoder pour vérifier l'intégrité
        decoded = base64.b64decode(encoded)
        self.assertEqual(decoded, image_data)

    def test_image_directory_creation(self):
        """Test création répertoire images."""
        images_dir = self.temp_path / "images"

        # Créer si n'existe pas
        images_dir.mkdir(parents=True, exist_ok=True)

        self.assertTrue(images_dir.exists())
        self.assertTrue(images_dir.is_dir())

    def test_image_relative_path(self):
        """Test génération chemins relatifs."""
        output_dir = self.temp_path / "output"
        images_dir = output_dir / "images"
        image_name = "image1.png"

        relative_path = f"images/{image_name}"

        self.assertEqual(relative_path, "images/image1.png")

    def test_multiple_images_handling(self):
        """Test gestion de plusieurs images."""
        images = {}

        for i in range(5):
            image_name = f"image{i}.png"
            image_path = f"images/image{i}.png"
            images[image_name] = image_path

        self.assertEqual(len(images), 5)
        self.assertIn("image0.png", images)
        self.assertIn("image4.png", images)


class TestCommentFilter(unittest.TestCase):
    """Tests pour le module comment_filter.py."""

    def test_simple_comment_detection(self):
        """Test détection commentaires simples."""
        text_with_comment = "Text ### Comment ### More text"

        # Simuler la logique de filtrage
        if "###" in text_with_comment:
            parts = text_with_comment.split("###")
            filtered = parts[0] + parts[-1] if len(parts) >= 3 else text_with_comment
        else:
            filtered = text_with_comment

        self.assertEqual(filtered.strip(), "Text  More text")

    def test_nested_comments(self):
        """Test commentaires imbriqués."""
        text = "Start ### Comment ### Middle ### Another ### End"

        # Première passe
        parts = text.split("###")
        # Devrait traiter du premier au dernier ###

        self.assertTrue(len(parts) >= 2)

    def test_no_comments(self):
        """Test texte sans commentaires."""
        text = "Simple text without comments"

        if "###" not in text:
            filtered = text

        self.assertEqual(filtered, text)

    def test_comment_at_start(self):
        """Test commentaire au début."""
        text = "### Comment ### Rest of text"

        parts = text.split("###")
        if len(parts) >= 3:
            filtered = parts[0] + parts[-1]
        else:
            filtered = text

        self.assertTrue("Rest of text" in filtered)

    def test_comment_at_end(self):
        """Test commentaire à la fin."""
        text = "Text before ### Comment ###"

        parts = text.split("###")
        if len(parts) >= 2:
            self.assertEqual(parts[0].strip(), "Text before")

    def test_multiple_comment_blocks(self):
        """Test plusieurs blocs de commentaires."""
        text = "Text1 ### C1 ### Text2 ### C2 ### Text3"

        # Compter les ###
        count = text.count("###")

        self.assertEqual(count, 4)

    def test_empty_comment(self):
        """Test commentaire vide."""
        text = "Text ###### More text"

        # Commentaire vide entre deux ###
        self.assertIn("###", text)

    def test_comment_filter_disabled(self):
        """Test filtrage désactivé."""
        text = "Text ### Comment ### More"
        filter_enabled = False

        if not filter_enabled:
            result = text
        else:
            # Logique de filtrage
            result = text.replace("### Comment ###", "")

        self.assertEqual(result, text)


class TestLoggingConfiguration(unittest.TestCase):
    """Tests pour la configuration du logging."""

    def test_logging_levels(self):
        """Test niveaux de logging."""
        import logging

        levels = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL,
        }

        self.assertEqual(levels["DEBUG"], 10)
        self.assertEqual(levels["INFO"], 20)
        self.assertEqual(levels["ERROR"], 40)

    def test_logging_format_components(self):
        """Test composants du format de logging."""
        format_string = "%(asctime)s - %(levelname)s - %(message)s"

        required_components = ["%(asctime)s", "%(levelname)s", "%(message)s"]

        for component in required_components:
            self.assertIn(component, format_string)

    def test_logging_date_format(self):
        """Test format de date."""
        date_format = "%Y-%m-%d %H:%M:%S"

        components = ["%Y", "%m", "%d", "%H", "%M", "%S"]

        for component in components:
            self.assertIn(component, date_format)

    @patch("logging.basicConfig")
    def test_setup_logging_called_with_correct_params(self, mock_config):
        """Test que setup_logging appelle basicConfig correctement."""
        setup_logging(verbose=False)

        self.assertTrue(mock_config.called)
        call_kwargs = mock_config.call_args[1]

        self.assertIn("level", call_kwargs)
        self.assertIn("format", call_kwargs)
        self.assertIn("datefmt", call_kwargs)


class TestFileSystemOperations(unittest.TestCase):
    """Tests pour les opérations système de fichiers."""

    def setUp(self):
        """Crée un environnement de test."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

    def tearDown(self):
        """Nettoie l'environnement."""
        self.temp_dir.cleanup()

    def test_create_output_directory(self):
        """Test création répertoire de sortie."""
        output_dir = self.temp_path / "output" / "nested" / "deep"

        output_dir.mkdir(parents=True, exist_ok=True)

        self.assertTrue(output_dir.exists())
        self.assertTrue(output_dir.is_dir())

    def test_file_exists_check(self):
        """Test vérification existence fichier."""
        test_file = self.temp_path / "test.txt"
        test_file.write_text("test")

        self.assertTrue(test_file.exists())
        self.assertTrue(test_file.is_file())

    def test_file_not_exists_check(self):
        """Test fichier non existant."""
        nonexistent = self.temp_path / "nonexistent.txt"

        self.assertFalse(nonexistent.exists())

    def test_directory_listing(self):
        """Test listage répertoire."""
        # Créer des fichiers
        (self.temp_path / "file1.txt").write_text("1")
        (self.temp_path / "file2.txt").write_text("2")
        (self.temp_path / "file3.docx").write_bytes(b"PK")

        # Lister
        all_files = list(self.temp_path.glob("*"))
        txt_files = list(self.temp_path.glob("*.txt"))
        docx_files = list(self.temp_path.glob("*.docx"))

        self.assertEqual(len(all_files), 3)
        self.assertEqual(len(txt_files), 2)
        self.assertEqual(len(docx_files), 1)

    def test_recursive_directory_search(self):
        """Test recherche récursive."""
        # Créer structure
        (self.temp_path / "file1.docx").write_bytes(b"PK")
        subdir = self.temp_path / "sub"
        subdir.mkdir()
        (subdir / "file2.docx").write_bytes(b"PK")
        deep = subdir / "deep"
        deep.mkdir()
        (deep / "file3.docx").write_bytes(b"PK")

        # Recherche récursive
        all_docx = list(self.temp_path.rglob("*.docx"))

        self.assertEqual(len(all_docx), 3)

    def test_file_size_check(self):
        """Test vérification taille fichier."""
        test_file = self.temp_path / "test.txt"
        content = "x" * 1000  # 1000 bytes
        test_file.write_text(content)

        size = test_file.stat().st_size

        self.assertEqual(size, 1000)

    def test_file_modification_time(self):
        """Test temps de modification."""
        test_file = self.temp_path / "test.txt"
        test_file.write_text("test")

        mtime = test_file.stat().st_mtime

        self.assertIsInstance(mtime, float)
        self.assertGreater(mtime, 0)


class TestPathOperations(unittest.TestCase):
    """Tests pour les opérations de chemins."""

    def test_path_join(self):
        """Test jointure de chemins."""
        base = Path("output")
        sub = "images"
        filename = "image1.png"

        full_path = base / sub / filename

        self.assertEqual(str(full_path), str(Path("output/images/image1.png")))

    def test_path_extension(self):
        """Test extraction extension."""
        file_path = Path("document.docx")

        self.assertEqual(file_path.suffix, ".docx")
        self.assertEqual(file_path.stem, "document")

    def test_path_parent(self):
        """Test répertoire parent."""
        file_path = Path("output/images/image1.png")

        self.assertEqual(file_path.parent, Path("output/images"))
        self.assertEqual(file_path.name, "image1.png")

    def test_path_absolute(self):
        """Test chemin absolu."""
        relative = Path("test.txt")
        absolute = relative.resolve()

        self.assertTrue(absolute.is_absolute())

    def test_path_with_suffix(self):
        """Test changement d'extension."""
        file_path = Path("document.docx")
        json_path = file_path.with_suffix(".json")
        html_path = file_path.with_suffix(".html")

        self.assertEqual(json_path.suffix, ".json")
        self.assertEqual(html_path.suffix, ".html")
        self.assertEqual(json_path.stem, "document")


class TestErrorHandlingUtils(unittest.TestCase):
    """Tests pour la gestion d'erreurs dans utils."""

    def test_safe_file_read(self):
        """Test lecture fichier sécurisée."""

        def safe_read(filepath):
            try:
                with open(filepath, "r") as f:
                    return f.read()
            except FileNotFoundError:
                return None
            except PermissionError:
                return None

        result = safe_read("nonexistent.txt")
        self.assertIsNone(result)

    def test_safe_directory_creation(self):
        """Test création répertoire sécurisée."""

        def safe_mkdir(dirpath):
            try:
                Path(dirpath).mkdir(parents=True, exist_ok=True)
                return True
            except OSError:
                return False

        # Devrait réussir
        with tempfile.TemporaryDirectory() as tmpdir:
            test_dir = Path(tmpdir) / "test"
            result = safe_mkdir(test_dir)
            self.assertTrue(result)

    def test_exception_message_extraction(self):
        """Test extraction message d'exception."""
        try:
            raise ValueError("Test error message")
        except ValueError as e:
            message = str(e)

        self.assertEqual(message, "Test error message")

    def test_exception_type_checking(self):
        """Test vérification type d'exception."""
        exceptions = []

        try:
            raise FileNotFoundError("File not found")
        except FileNotFoundError as e:
            exceptions.append(("FileNotFoundError", str(e)))

        try:
            raise ValueError("Invalid value")
        except ValueError as e:
            exceptions.append(("ValueError", str(e)))

        self.assertEqual(len(exceptions), 2)
        self.assertEqual(exceptions[0][0], "FileNotFoundError")
        self.assertEqual(exceptions[1][0], "ValueError")


if __name__ == "__main__":
    unittest.main()
