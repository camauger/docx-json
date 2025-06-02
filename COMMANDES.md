# 📝 Guide des Commandes CLI

Ce document détaille l'ensemble des commandes et options disponibles pour l'outil de conversion DOCX vers JSON/HTML/Markdown.

## 🚀 Commandes de Base

### Installation

```bash
# Installation depuis le dépôt
git clone [URL_DU_REPO]
cd docx-json
pip install -e .

# Installation des dépendances
pip install python-docx pandoc
```

### Utilisation Basique

```bash
# Conversion vers un seul format
docx-json monfichier.docx --json
docx-json monfichier.docx --html
docx-json monfichier.docx --md

# Conversion vers plusieurs formats
docx-json monfichier.docx --json --html --md

# Conversion de plusieurs fichiers
docx-json fichier1.docx fichier2.docx --json

# Conversion d'un dossier
docx-json dossier/ --json --recursive
```

## ⚙️ Options Disponibles

### Options de Format de Sortie

| Option | Description | Exemple |
|--------|-------------|---------|
| `--json` | Génère un fichier JSON structuré | `docx-json doc.docx --json` |
| `--html` | Génère un fichier HTML sémantique | `docx-json doc.docx --html` |
| `--md` | Génère un fichier Markdown | `docx-json doc.docx --md` |

### Options de Configuration

| Option | Description | Exemple |
|--------|-------------|---------|
| `--output-dir DIR` | Spécifie le répertoire de sortie | `docx-json doc.docx --output-dir output/` |
| `--no-save-images` | Encode les images en base64 | `docx-json doc.docx --no-save-images` |
| `--standalone` | Génère un document Markdown autonome | `docx-json doc.docx --md --standalone` |
| `--recursive` | Convertit récursivement tous les fichiers DOCX des dossiers | `docx-json dossier/ --recursive` |
| `--verbose` | Affiche des messages de debug | `docx-json doc.docx --verbose` |

### Options d'Information

| Option | Description | Exemple |
|--------|-------------|---------|
| `--version` | Affiche la version du programme | `docx-json --version` |
| `--help` | Affiche l'aide | `docx-json --help` |

## 📋 Exemples Complets

### 1. Conversion Simple

```bash
# Conversion vers JSON uniquement
docx-json document.docx --json

# Conversion vers HTML uniquement
docx-json document.docx --html

# Conversion vers Markdown uniquement
docx-json document.docx --md
```

### 2. Conversion Multiple

```bash
# Conversion vers tous les formats
docx-json document.docx --json --html --md

# Conversion vers JSON et HTML
docx-json document.docx --json --html
```

### 3. Gestion des Images

```bash
# Sauvegarder les images dans un dossier spécifique
docx-json document.docx --output-dir output/ --html

# Encoder les images en base64
docx-json document.docx --no-save-images --html
```

### 4. Conversion de Plusieurs Fichiers

```bash
# Conversion de plusieurs fichiers vers JSON
docx-json doc1.docx doc2.docx doc3.docx --json

# Conversion de plusieurs fichiers vers tous les formats
docx-json *.docx --json --html --md
```

### 5. Conversion de Dossiers

```bash
# Conversion non récursive d'un dossier
docx-json dossier/ --json

# Conversion récursive d'un dossier
docx-json dossier/ --recursive --json

# Conversion récursive avec préservation de la structure
docx-json dossier/ --recursive --output-dir output/ --json

# Conversion récursive de plusieurs dossiers
docx-json dossier1/ dossier2/ --recursive --json
```

### 6. Mode Débogage

```bash
# Afficher les messages de debug
docx-json document.docx --verbose --json

# Conversion avec debug et sortie dans un dossier spécifique
docx-json document.docx --verbose --output-dir debug_output/ --json --html
```

## 🎯 Bonnes Pratiques

1. **Vérification des Fichiers**
   - Assurez-vous que les fichiers DOCX sont valides avant la conversion
   - Vérifiez les permissions d'accès aux fichiers
   - Utilisez `--recursive` avec précaution sur les grands dossiers

2. **Gestion des Images**
   - Utilisez `--no-save-images` pour les petits documents
   - Utilisez `--output-dir` pour organiser les fichiers générés
   - En mode récursif, les images sont placées dans des sous-dossiers correspondants

3. **Performance**
   - Pour les gros documents, évitez de convertir vers tous les formats en même temps
   - Utilisez `--verbose` uniquement en cas de problème
   - En mode récursif, limitez la profondeur des dossiers si possible

4. **Organisation**
   - Créez des dossiers dédiés pour les fichiers générés
   - Utilisez des noms de fichiers descriptifs
   - En mode récursif, la structure des dossiers est préservée dans le répertoire de sortie

## ⚠️ Notes Importantes

1. **Dépendances**
   - Assurez-vous que pandoc est installé pour la conversion vers Markdown
   - Vérifiez que python-docx est à jour

2. **Limitations**
   - Certains styles complexes peuvent ne pas être parfaitement convertis
   - Les composants pédagogiques sont mieux supportés en HTML qu'en Markdown
   - En mode récursif, les chemins très longs peuvent causer des problèmes sur certains systèmes

3. **Résolution des Problèmes**
   - Utilisez `--verbose` pour identifier les erreurs
   - Vérifiez les logs pour plus de détails
   - Assurez-vous d'avoir les permissions nécessaires sur les dossiers
   - En cas d'erreur en mode récursif, vérifiez les chemins des fichiers