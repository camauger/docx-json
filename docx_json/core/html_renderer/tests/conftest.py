"""
Configuration et fixtures pour les tests pytest
"""

from typing import Any, Dict

import pytest


@pytest.fixture
def empty_json_data() -> Dict[str, Any]:
    """Fixture pour un document JSON vide"""
    return {"content": [], "images": {}, "meta": {"title": "Document vide"}}


@pytest.fixture
def simple_paragraph_json() -> Dict[str, Any]:
    """Fixture pour un document avec un paragraphe simple"""
    return {
        "content": [{"type": "paragraph", "runs": [{"text": "Test paragraph"}]}],
        "images": {},
        "meta": {"title": "Document avec paragraphe"},
    }


@pytest.fixture
def styled_text_json() -> Dict[str, Any]:
    """Fixture pour un document avec du texte stylisé"""
    return {
        "content": [
            {
                "type": "paragraph",
                "runs": [
                    {"text": "Bold", "bold": True},
                    {"text": "Italic", "italic": True},
                    {"text": "Underline", "underline": True},
                ],
            }
        ],
        "images": {},
        "meta": {"title": "Document avec texte stylisé"},
    }


@pytest.fixture
def table_json() -> Dict[str, Any]:
    """Fixture pour un document avec un tableau"""
    return {
        "content": [
            {
                "type": "table",
                "rows": [
                    [{"type": "paragraph", "runs": [{"text": "Cell 1"}]}],
                    [{"type": "paragraph", "runs": [{"text": "Cell 2"}]}],
                ],
            }
        ],
        "images": {},
        "meta": {"title": "Document avec tableau"},
    }


@pytest.fixture
def multi_page_json() -> Dict[str, Any]:
    """Fixture pour un document multi-pages"""
    return {
        "content": [
            {"type": "paragraph", "runs": [{"text": "Page 1"}]},
            {"type": "page_break"},
            {"type": "paragraph", "runs": [{"text": "Page 2"}]},
        ],
        "images": {},
        "meta": {"title": "Document multi-pages"},
    }


@pytest.fixture
def nested_elements_json() -> Dict[str, Any]:
    """Fixture pour un document avec des éléments imbriqués"""
    return {
        "content": [
            {
                "type": "block",
                "block_type": "quote",
                "content": [
                    {"type": "paragraph", "runs": [{"text": "Nested paragraph"}]}
                ],
            }
        ],
        "images": {},
        "meta": {"title": "Document avec éléments imbriqués"},
    }


@pytest.fixture
def custom_css() -> str:
    """Fixture pour le CSS personnalisé"""
    return "body { background: #fff; }"


@pytest.fixture
def json_with_images() -> Dict[str, Any]:
    """Fixture pour un document avec des images"""
    return {
        "content": [
            {"type": "paragraph", "runs": [{"text": "Text with image"}]},
            {"type": "image", "src": "test.png"},
        ],
        "images": {"test.png": "base64_encoded_image_data"},
        "meta": {"title": "Document avec images"},
    }
