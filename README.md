# 📄 DOCX to JSON/HTML/Markdown Converter

Un package Python pour convertir des fichiers `.docx` en fichiers `.json` structurés, `.html` sémantiques ou `.md` Markdown.
Il prend en charge les styles, les tableaux, les images et des **instructions intégrées** au document `.docx` pour personnaliser le rendu,
ainsi que des **composants pédagogiques** comme les vidéos, les accordéons, etc.

---

## ✨ Fonctionnalités principales

- ✅ Conversion du contenu `.docx` en JSON structuré
- ✅ Génération d'un fichier `.html` propre, avec structure sémantique
- ✅ Conversion vers `.md` Markdown (via pandoc)
- ✅ Gestion des **styles** (gras, italique, souligné)
- ✅ Support des **titres, paragraphes, listes, tableaux**
- ✅ Extraction des **images** (fichiers séparés ou base64)
- ✅ Conversion **récursive** de dossiers entiers
- ✅ Support des **composants pédagogiques**:
  - Vidéos
  - Audio
  - Accordéons
  - Carrousels
  - Onglets
  - Défilement
- ✅ Interprétation d'**instructions intégrées** (`:::`) dans le `.docx` pour :
  - Ajouter des classes CSS
  - Ignorer certains éléments
  - Envelopper des blocs (`quote`, `aside`, etc.)
  - Attribuer des ID HTML
  - Injecter du HTML brut

---

## 🚀 Installation

### Option 1: Installation depuis le dépôt

1. Clonez le dépôt
2. Installez le package en mode développement:

```bash
pip install -e .
```

### Option 2: Installation simple

1. Installez les dépendances principales:

```bash
pip install python-docx pandoc
```

2. Utilisez le script inclus `run_docx_converter.py`

---

## 🛠️ Utilisation

### Commande de base

```bash
# Si installé comme package
docx-json monfichier.docx --json --html --md

# OU en utilisant le script de lancement
python run_docx_converter.py monfichier.docx --json --html --md
```

### Options disponibles

| Option              | Description                                      |
|---------------------|--------------------------------------------------|
| `--json`            | Génère un fichier `.json` structuré              |
| `--html`            | Génère un fichier `.html` sémantique             |
| `--md`              | Génère un fichier `.md` Markdown                 |
| `--recursive`       | Convertit récursivement tous les fichiers DOCX des dossiers |
| `--standalone`      | Génère un document Markdown autonome avec métadonnées |
| `--no-save-images`  | Encode les images en base64 au lieu de les sauvegarder comme fichiers |
| `--output-dir`      | Spécifie le répertoire de sortie pour les fichiers générés |
| `--verbose`         | Affiche des messages de debug détaillés          |

### Exemples d'utilisation

```bash
# Conversion simple
docx-json document.docx --json

# Conversion vers plusieurs formats
docx-json document.docx --json --html --md

# Conversion d'un dossier entier
docx-json dossier/ --recursive --json

# Conversion avec préservation de la structure
docx-json dossier/ --recursive --output-dir output/ --json

# Conversion avec gestion des images
docx-json document.docx --no-save-images --html
```

Pour plus de détails sur les commandes et options disponibles, consultez le [Guide des Commandes](COMMANDES.md).

---

## 🧾 Exemple de structure JSON

```json
{
  "meta": {
    "title": "monfichier.docx"
  },
  "content": [
    {
      "type": "heading",
      "level": 1,
      "runs": [
        { "text": "Titre principal", "bold": true }
      ],
      "html_class": "hero dark",
      "html_id": "titre-accueil"
    },
    {
      "type": "paragraph",
      "runs": [
        { "text": "Voici un paragraphe de test." }
      ],
      "block": "quote"
    },
    {
      "type": "component",
      "component_type": "Accordéon",
      "content": [
        {
          "type": "heading",
          "level": 2,
          "runs": [{"text": "Section accordéon", "bold": true}]
        },
        {
          "type": "paragraph",
          "runs": [{"text": "Contenu de l'accordéon"}]
        }
      ]
    }
  ],
  "images": {
    "image1.png": "images/image1.png"
  }
}
```

---

## 🌐 Exemple de HTML généré

```html
<h1 class="hero dark" id="titre-accueil">Titre principal</h1>

<blockquote>
  <p>Voici un paragraphe de test.</p>
</blockquote>

<div class="accordion my-4" id="accordion-12345">
  <div class="accordion-item">
    <h2 class="accordion-header" id="heading-accordion-12345-item-1">
      <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapse-accordion-12345-item-1">
        Section accordéon
      </button>
    </h2>
    <div id="collapse-accordion-12345-item-1" class="accordion-collapse collapse">
      <div class="accordion-body">
        <p>Contenu de l'accordéon</p>
      </div>
    </div>
  </div>
</div>

<img src="images/image1.png" alt="image1.png" class="img-fluid my-3" />
```

---

## 📝 Instructions intégrées dans le document `.docx`

Les instructions sont des **paragraphes spéciaux** commençant par `:::` dans le document Word.
Elles **ne sont pas affichées** dans le rendu final, mais influencent les éléments suivants.

---

### ✅ Syntaxes supportées

| Instruction | Effet |
|-------------|-------|
| `:::class hero dark` | Ajoute des classes CSS au prochain élément |
| `:::id intro` | Attribue un ID HTML |
| `:::ignore` | Ignore le prochain paragraphe ou tableau |
| `:::quote start` | Débute un bloc `<blockquote>` |
| `:::quote end` | Termine le bloc `<blockquote>` |
| `:::html <hr />` | Injecte du HTML brut dans la sortie |

---

## 🎮 Composants pédagogiques

Le convertisseur reconnaît des **indicateurs de composants** dans le document, comme :

```
[Vidéo]
[Audio]
[Accordéon]
[Carrousel]
[Onglets]
[Défilement]
```

Ces balises sont interprétées comme des **délimiteurs de blocs** dans le contenu.
Vous pouvez les terminer avec la syntaxe `[Fin NomDuComposant]`.

### ➕ Exemple de bloc accordéon

```markdown
[Accordéon]
# Titre de l'accordéon
Contenu caché 1
Contenu caché 2
[Fin Accordéon]
```

Résultat HTML :

```html
<div class="accordion">
  <div class="accordion-item">
    <h2 class="accordion-header">
      <button class="accordion-button collapsed">Titre de l'accordéon</button>
    </h2>
    <div class="accordion-collapse collapse">
      <div class="accordion-body">
        <p>Contenu caché 1</p>
        <p>Contenu caché 2</p>
      </div>
    </div>
  </div>
</div>
```

---

## 🧪 Conseils de rédaction dans Word

- Placez les instructions (`:::`) dans leur **propre paragraphe**.
- Utilisez le style **"Normal"** pour les instructions.
- Pour les composants, ajoutez des titres (`Heading 1-6`) afin de structurer correctement les éléments.
- Utilisez des titres de même niveau pour créer plusieurs éléments (onglets, sections d'accordéon).

---

## 📂 Organisation du projet

```
docx-json/
├── docx_json/           # Module principal
│   ├── __init__.py      # Exportation des classes publiques
│   ├── __main__.py      # Point d'entrée CLI
│   ├── core/            # Fonctionnalités principales
│   │   ├── __init__.py
│   │   └── converter.py # Classes de conversion
│   └── models/          # Modèles de données
│       ├── __init__.py
│       └── elements.py  # Classes des éléments du document
├── run_docx_converter.py # Script de lancement
├── pyproject.toml       # Configuration du package
├── COMMANDES.md         # Guide des commandes CLI
└── README.md            # Documentation
```

---

## ✨ Pour aller plus loin (roadmap)

- [ ] Ajout d'un mode Markdown (`--md`)
- [ ] Support des styles personnalisés (couleurs, tailles, etc.)
- [ ] Interface web glisser-déposer (Flask ou FastAPI)
- [ ] Support des tableaux imbriqués et mises en page avancées

---
