"""
Tests unitaires pour HTMLGenerator
"""

import os
from typing import Any, Dict, List

import pytest

from docx_json.core.html_renderer import HTMLGenerator
from docx_json.core.html_renderer.base import ElementRenderer


class MockRenderer(ElementRenderer):
    """Renderer fictif pour les tests"""

    def __init__(self, html_generator):
        """
        Initialise le renderer fictif.

        Args:
            html_generator: Instance du générateur HTML principal
        """
        super().__init__(html_generator)

    def render(self, element: Dict[str, Any], indent_level: int = 0) -> List[str]:
        return [" " * indent_level + "mock-element"]


def test_generator_initialization(empty_json_data):
    """Test l'initialisation du générateur"""
    generator = HTMLGenerator(empty_json_data)

    assert generator._json_data == empty_json_data
    assert generator._renderers != {}
    assert all(
        isinstance(renderer, ElementRenderer)
        for renderer in generator._renderers.values()
    )


def test_generate_empty_document(empty_json_data):
    """Test la génération d'un document vide"""
    generator = HTMLGenerator(empty_json_data)

    html = generator.generate()

    assert "<!DOCTYPE html>" in html
    assert "<html" in html
    assert "<head>" in html
    assert "<body>" in html
    assert "</body>" in html
    assert "</html>" in html


def test_generate_with_custom_css(empty_json_data, custom_css):
    """Test la génération avec CSS personnalisé"""
    generator = HTMLGenerator(empty_json_data)

    html = generator.generate(custom_css)

    assert custom_css in html
    assert "<style>" in html
    assert "</style>" in html


def test_generate_paragraph(simple_paragraph_json):
    """Test la génération d'un paragraphe simple"""
    generator = HTMLGenerator(simple_paragraph_json)

    html = generator.generate()

    assert "<p>" in html
    assert "Test paragraph" in html
    assert "</p>" in html


def test_generate_heading(empty_json_data):
    """Test la génération d'un titre"""
    json_data = empty_json_data.copy()
    json_data["content"] = [
        {"type": "heading", "level": 1, "runs": [{"text": "Test heading"}]}
    ]
    generator = HTMLGenerator(json_data)

    html = generator.generate()

    assert "<h1>" in html
    assert "Test heading" in html
    assert "</h1>" in html


def test_generate_styled_text(styled_text_json):
    """Test la génération de texte avec styles"""
    generator = HTMLGenerator(styled_text_json)

    html = generator.generate()

    assert "<strong>Bold</strong>" in html
    assert "<em>Italic</em>" in html
    assert "<u>Underline</u>" in html


def test_generate_table(table_json):
    """Test la génération d'un tableau"""
    generator = HTMLGenerator(table_json)

    html = generator.generate()

    assert "<table" in html
    assert "<tr>" in html
    assert "<td>" in html
    assert "Cell 1" in html
    assert "Cell 2" in html
    assert "</table>" in html


def test_generate_with_custom_renderer(empty_json_data):
    """Test l'utilisation d'un renderer personnalisé"""
    json_data = empty_json_data.copy()
    json_data["content"] = [{"type": "custom", "data": "test"}]
    generator = HTMLGenerator(json_data)
    generator._renderers["custom"] = MockRenderer(generator)

    html = generator.generate()

    assert "mock-element" in html


def test_generate_multi_page(multi_page_json):
    """Test la génération multi-pages"""
    generator = HTMLGenerator(multi_page_json)

    # Créer un répertoire temporaire pour les tests
    test_output_dir = "test_output"
    os.makedirs(test_output_dir, exist_ok=True)

    files = []
    try:
        files = generator.generate_multi_page(test_output_dir, "test_doc")

        assert len(files) == 2
        assert all(os.path.exists(f) for f in files)

        # Vérifier le contenu des fichiers
        with open(files[0], "r", encoding="utf-8") as f:
            content = f.read()
            assert "Page 1" in content

        with open(files[1], "r", encoding="utf-8") as f:
            content = f.read()
            assert "Page 2" in content

    finally:
        # Nettoyer les fichiers de test
        for file in files:
            if os.path.exists(file):
                os.remove(file)
        if os.path.exists(test_output_dir):
            os.rmdir(test_output_dir)


def test_invalid_element_type(empty_json_data):
    """Test la gestion des types d'éléments invalides"""
    json_data = empty_json_data.copy()
    json_data["content"] = [{"type": "invalid_type", "data": "test"}]
    generator = HTMLGenerator(json_data)

    # Le générateur devrait lever une KeyError car le type d'élément n'existe pas
    # dans le dictionnaire des renderers
    with pytest.raises(KeyError) as excinfo:
        generator.generate()

    assert "invalid_type" in str(excinfo.value)


def test_html_attributes(empty_json_data):
    """Test la génération avec des attributs HTML personnalisés"""
    json_data = empty_json_data.copy()
    json_data["content"] = [
        {
            "type": "paragraph",
            "html_class": "custom-class",
            "html_id": "custom-id",
            "runs": [{"text": "Test"}],
        }
    ]
    generator = HTMLGenerator(json_data)

    html = generator.generate()

    assert 'class="custom-class"' in html
    assert 'id="custom-id"' in html


def test_nested_elements(nested_elements_json):
    """Test la génération d'éléments imbriqués"""
    generator = HTMLGenerator(nested_elements_json)

    html = generator.generate()

    assert "<blockquote>" in html
    assert "<p>" in html
    assert "Nested paragraph" in html
    assert "</p>" in html
    assert "</blockquote>" in html


def test_generate_with_images(json_with_images):
    """Test la génération avec des images"""
    generator = HTMLGenerator(json_with_images)

    html = generator.generate()

    assert "<img" in html
    assert 'src="data:image/png;base64,' in html
    assert "base64_encoded_image_data" in html
