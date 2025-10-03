# Makefile pour docx-json
# Commandes principales pour la conversion de documents DOCX

# Variables
PYTHON = python
PIP = pip
DOCX_JSON = docx-json

# Couleurs pour les messages
GREEN = \033[0;32m
NC = \033[0m # No Color

# Commandes principales
.PHONY: install install-dev clean test test-cov lint format type-check security quality ci convert convert-all convert-dir help

# Installation
install:
	@echo "$(GREEN)Installation des dépendances...$(NC)"
	$(PIP) install -e .
	$(PIP) install python-docx pandoc

# Nettoyage
clean:
	@echo "$(GREEN)Nettoyage des fichiers générés...$(NC)"
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type d -name "*.egg-info" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg" -exec rm -r {} +
	find . -type d -name "*.eggs" -exec rm -r {} +
	find . -type d -name "*.pytest_cache" -exec rm -r {} +
	find . -type d -name "*.tox" -exec rm -r {} +
	find . -type d -name "*.coverage" -exec rm -r {} +
	find . -type d -name "htmlcov" -exec rm -r {} +

# Tests
test:
	@echo "$(GREEN)Exécution des tests...$(NC)"
	pytest tests/

# Conversion simple d'un fichier
convert:
	@echo "$(GREEN)Conversion d'un fichier DOCX...$(NC)"
	@if [ -z "$(file)" ]; then \
		echo "Usage: make convert file=monfichier.docx"; \
		exit 1; \
	fi
	$(DOCX_JSON) $(file) --json --html --md

# Conversion de tous les formats
convert-all:
	@echo "$(GREEN)Conversion vers tous les formats...$(NC)"
	@if [ -z "$(file)" ]; then \
		echo "Usage: make convert-all file=monfichier.docx"; \
		exit 1; \
	fi
	$(DOCX_JSON) $(file) --json --html --md --standalone

# Conversion d'un dossier
convert-dir:
	@echo "$(GREEN)Conversion d'un dossier...$(NC)"
	@if [ -z "$(dir)" ]; then \
		echo "Usage: make convert-dir dir=mondossier"; \
		exit 1; \
	fi
	$(DOCX_JSON) $(dir) --recursive --json --html --md

# Conversion avec gestion des images
convert-images:
	@echo "$(GREEN)Conversion avec gestion des images...$(NC)"
	@if [ -z "$(file)" ]; then \
		echo "Usage: make convert-images file=monfichier.docx"; \
		exit 1; \
	fi
	$(DOCX_JSON) $(file) --no-save-images --html

# Conversion avec sortie personnalisée
convert-output:
	@echo "$(GREEN)Conversion avec sortie personnalisée...$(NC)"
	@if [ -z "$(file)" ] || [ -z "$(output)" ]; then \
		echo "Usage: make convert-output file=monfichier.docx output=output/"; \
		exit 1; \
	fi
	$(DOCX_JSON) $(file) --output-dir $(output) --json --html --md

# Mode debug
convert-debug:
	@echo "$(GREEN)Conversion en mode debug...$(NC)"
	@if [ -z "$(file)" ]; then \
		echo "Usage: make convert-debug file=monfichier.docx"; \
		exit 1; \
	fi
	$(DOCX_JSON) $(file) --verbose --json --html --md

# Aide
help:
	@echo "$(GREEN)Commandes disponibles:$(NC)"
	@echo "  make install           - Installation des dépendances"
	@echo "  make clean            - Nettoyage des fichiers générés"
	@echo "  make test             - Exécution des tests"
	@echo "  make convert          - Conversion simple d'un fichier"
	@echo "  make convert-all      - Conversion vers tous les formats"
	@echo "  make convert-dir      - Conversion d'un dossier"
	@echo "  make convert-images   - Conversion avec gestion des images"
	@echo "  make convert-output   - Conversion avec sortie personnalisée"
	@echo "  make convert-debug    - Conversion en mode debug"
	@echo ""
	@echo "Exemples d'utilisation:"
	@echo "  make convert file=document.docx"
	@echo "  make convert-dir dir=dossier/"
	@echo "  make convert-output file=document.docx output=output/"