# CLAUDE.md - AI Assistant Guide

This document provides guidance for AI assistants (like Claude) working with the `docx-json` codebase.

---

## 🎯 Project Overview

**docx-json** is a Python package that converts DOCX files to structured JSON, semantic HTML, and Markdown formats. It supports pedagogical components (videos, accordions, carousels, tabs) and embedded instructions for customizing output.

**Key Features:**
- DOCX → JSON/HTML/Markdown conversion
- Embedded instructions (`:::class`, `:::id`, `:::quote`, etc.)
- Pedagogical components (accordions, videos, tabs, carousels)
- Recursive directory conversion
- Image extraction (separate files or base64)
- Style support (bold, italic, underline, headings, lists, tables)

**Version:** 1.0.1
**Python:** >=3.7
**License:** MIT

---

## 📁 Project Structure

```
docx-json/
├── docx_json/                    # Main package
│   ├── __main__.py              # Entry point
│   ├── cli.py                   # CLI argument parsing
│   ├── convert.py               # Main conversion logic
│   ├── exceptions.py            # Custom exceptions
│   ├── core/                    # Core functionality
│   │   ├── docx_parser.py      # DOCX parsing logic
│   │   ├── html_renderer.py    # HTML rendering (delegates to html_renderer/)
│   │   ├── markdown_generator.py # Markdown generation
│   │   ├── compatibility.py     # Backward compatibility
│   │   └── html_renderer/       # HTML rendering modules
│   │       ├── base.py          # Base renderer class
│   │       ├── generator.py     # Main HTML generator
│   │       ├── paragraph.py     # Paragraph rendering
│   │       ├── table.py         # Table rendering
│   │       ├── image.py         # Image rendering
│   │       ├── video.py         # Video component
│   │       ├── component.py     # Pedagogical components
│   │       ├── raw_html.py      # Raw HTML injection
│   │       ├── page_break.py    # Page break handling
│   │       └── text.py          # Text/run rendering
│   ├── models/                  # Data models
│   ├── utils/                   # Utility functions
│   │   ├── logging.py          # Logging utilities
│   │   ├── file_utils.py       # File operations
│   │   └── path_utils.py       # Path validation
│   └── tests/                   # Unit tests
├── tests/                       # Integration tests
├── examples/                    # Example DOCX files
├── scripts/                     # Utility scripts
├── docs/                        # Documentation
│   └── code-review/            # Code review documentation
├── Makefile                     # Common commands
├── pyproject.toml              # Project configuration
├── requirements.txt            # Dependencies
└── run_docx_converter.py       # Standalone script

```

---

## 🔑 Key Components

### 1. **CLI (`cli.py`)**
- Handles command-line arguments
- Options: `--json`, `--html`, `--md`, `--recursive`, `--output-dir`, etc.
- Entry point: `docx-json` command or `python -m docx_json`

### 2. **Parser (`core/docx_parser.py`)**
- Reads DOCX files using `python-docx`
- Extracts content, styles, images, tables
- Processes embedded instructions (`:::class`, `:::id`, etc.)
- Identifies pedagogical components

### 3. **HTML Renderer (`core/html_renderer/`)**
- **Modular architecture** (v1.0.1+): Each element type has its own module
- `generator.py`: Main HTML generation orchestrator
- `paragraph.py`: Handles paragraphs and text runs
- `table.py`: Renders tables
- `image.py`: Handles image embedding
- `component.py`: Renders pedagogical components (accordions, tabs, etc.)
- `video.py`: Renders video embeds
- `raw_html.py`: Injects raw HTML
- `base.py`: Base renderer with shared utilities

### 4. **Markdown Generator (`core/markdown_generator.py`)**
- Converts JSON to Markdown
- Uses pandoc for final conversion
- Supports standalone mode with metadata

### 5. **Models (`models/`)**
- Type-checked data structures
- Represents document elements (paragraphs, runs, tables, etc.)

---

## 🧪 Development Workflow

### Setup
```bash
# Install dependencies
make install

# Or manually
pip install -e .
pip install -e ".[dev]"
```

### Testing
```bash
# Run all tests
make test

# Run with coverage
pytest --cov=docx_json --cov-report=html

# Run specific test
pytest tests/test_convert.py::test_specific_function

# Run only fast tests
pytest -m "not slow"
```

### Code Quality
```bash
# Format code
black docx_json/
isort docx_json/

# Type checking
mypy docx_json/

# Linting
flake8 docx_json/

# Security scan
bandit -r docx_json/
```

### Common Tasks
```bash
# Convert a file
make convert file=document.docx

# Convert to all formats
make convert-all file=document.docx

# Convert directory
make convert-dir dir=examples/

# Debug mode
make convert-debug file=document.docx
```

---

## 🔍 Important Implementation Details

### Embedded Instructions
Instructions are paragraphs starting with `:::` in the DOCX file. They modify the next element:

- `:::class hero dark` → Adds CSS classes to next element
- `:::id intro` → Sets HTML id
- `:::ignore` → Skips next element
- `:::quote start` / `:::quote end` → Wraps content in `<blockquote>`
- `:::html <hr />` → Injects raw HTML
- `:::title` → Extracts document title from next paragraph

Instructions are **filtered out** from the final output.

### Pedagogical Components
Components are delimited by paragraphs like `[Accordéon]` or `[Vidéo]`:

**Supported components:**
- `[Vidéo]` / `[Video]` → Video embed
- `[Audio]` → Audio player
- `[Accordéon]` / `[Accordion]` → Collapsible sections
- `[Carrousel]` / `[Carousel]` → Image carousel
- `[Onglets]` / `[Tabs]` → Tabbed content
- `[Défilement]` / `[Scrolling]` → Scrollable sections

Components end with `[Fin NomDuComposant]` or auto-close at document end.

### Image Handling
- By default: Saved as separate files in `images/` directory
- With `--no-save-images`: Encoded as base64 in HTML
- JSON always stores image paths/references

### HTML Rendering Strategy (v1.0.1+)
The HTML renderer was refactored into a **modular architecture**:

1. **Separation of concerns**: Each element type has its own module
2. **Base renderer**: Shared utilities in `base.py`
3. **Generator orchestration**: `generator.py` coordinates rendering
4. **Type safety**: Models define clear data structures

This improves maintainability and testability.

---

## 🐛 Common Issues & Solutions

### Issue: Path traversal vulnerability (CRIT-001)
**Status:** FIXED in v1.0.1
**Solution:** `path_utils.py` validates all file paths to prevent directory traversal attacks.

### Issue: Images not found
**Check:**
- Are images embedded in the DOCX? (not just linked)
- Is output directory writable?
- Use `--verbose` to see detailed logs

### Issue: Markdown generation fails
**Check:**
- Is pandoc installed? (`pip install pandoc`)
- Is the JSON structure valid?

### Issue: Components not rendering
**Check:**
- Component names must match exactly: `[Accordéon]`, `[Vidéo]`, etc.
- Components must have content (headings define sections)
- Use `--verbose` to debug component detection

---

## 📊 Testing Coverage

**Current Coverage:** ~37% (v1.0.1)
**Tests Added:** 171+ new tests in v1.0.1

**Key test areas:**
- ✅ Path validation (security)
- ✅ HTML rendering for each element type
- ✅ Component rendering
- ✅ Instruction parsing
- ✅ Image handling
- ✅ Table rendering
- 🚧 Edge cases (ongoing)

**Test files:**
- `tests/test_convert.py` - Main conversion tests
- `tests/test_security.py` - Security tests (path traversal, etc.)
- `docx_json/core/html_renderer/tests/` - HTML renderer unit tests
- `docx_json/utils/tests/` - Utility function tests

---

## 🎯 Working with This Codebase

### Adding a New Feature

1. **Read existing code** in related modules
2. **Add tests first** (TDD approach)
3. **Implement feature** following existing patterns
4. **Update type hints** (mypy compatible)
5. **Run tests & linting** before committing
6. **Update documentation** (README, INSTRUCTIONS, etc.)

### Modifying HTML Rendering

1. **Locate the right module** in `core/html_renderer/`
   - Paragraphs → `paragraph.py`
   - Tables → `table.py`
   - Components → `component.py`
   - Images → `image.py`
2. **Modify the rendering logic**
3. **Add/update tests** in `core/html_renderer/tests/`
4. **Test with real DOCX files** from `examples/`

### Adding a New Instruction

1. **Update `docx_parser.py`** to recognize the instruction
2. **Modify `html_renderer/generator.py`** to apply it
3. **Add tests** for the new instruction
4. **Document** in INSTRUCTIONS.md

### Adding a New Component

1. **Update component detection** in `docx_parser.py`
2. **Add rendering logic** in `core/html_renderer/component.py`
3. **Add tests** for the component
4. **Document** in README.md and INSTRUCTIONS.md

---

## 🔒 Security Considerations

**CRITICAL:** Always validate file paths before file operations.

Use `docx_json/utils/path_utils.py`:
```python
from docx_json.utils.path_utils import validate_safe_path

# Validate before using
safe_path = validate_safe_path(user_provided_path)
```

**Never** directly use user-provided paths without validation.

---

## 📚 Key Files to Review

When starting work on this project, review these files first:

1. **README.md** - User-facing documentation
2. **INSTRUCTIONS.md** - Detailed usage instructions
3. **docx_json/cli.py** - Command-line interface
4. **docx_json/convert.py** - Main conversion orchestrator
5. **docx_json/core/docx_parser.py** - DOCX parsing logic
6. **docx_json/core/html_renderer/generator.py** - HTML generation
7. **pyproject.toml** - Project configuration
8. **Makefile** - Common commands

---

## 🚀 Quick Reference

### Run Conversion
```bash
docx-json file.docx --json --html --md
```

### Run Tests
```bash
pytest
```

### Format Code
```bash
black docx_json/ && isort docx_json/
```

### Type Check
```bash
mypy docx_json/
```

### View Coverage
```bash
pytest --cov=docx_json --cov-report=html
open htmlcov/index.html
```

---

## 📖 Additional Documentation

- **README.md** - User documentation
- **INSTRUCTIONS.md** - Detailed usage instructions
- **COMMANDES.md** - Command reference
- **docs/code-review/** - Code review documentation (v1.0.1)
- **CHANGELOG.md** - Version history

---

## 💡 Tips for AI Assistants

1. **Always read before writing**: Use Read tool before Edit/Write
2. **Validate assumptions**: Check file existence with Glob/Read
3. **Run tests after changes**: Use `make test` or `pytest`
4. **Follow existing patterns**: Consistency is key
5. **Check type hints**: Use mypy to catch type errors
6. **Validate paths**: Always use `path_utils.py` for file operations
7. **Use verbose mode**: `--verbose` flag helps debug issues
8. **Review recent commits**: Check git log for recent changes
9. **Test with real files**: Use examples/ directory for testing
10. **Update docs**: Keep README, INSTRUCTIONS in sync with code

---

## 🤝 Contributing

When making changes:

1. Create a feature branch: `git checkout -b feature/my-feature`
2. Make changes following code style (black, isort)
3. Add tests for new functionality
4. Run test suite: `pytest`
5. Run type checker: `mypy docx_json/`
6. Commit with clear messages
7. Push and create pull request

---

## 📞 Support

- **Issues:** Report at GitHub Issues (see pyproject.toml)
- **Documentation:** See README.md, INSTRUCTIONS.md, COMMANDES.md
- **Code Review:** See docs/code-review/ for v1.0.1 improvements

---

**Last Updated:** 2025-11-20 (v1.0.1)
