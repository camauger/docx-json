# 📝 Guide d'utilisation du convertisseur DOCX → JSON/HTML

Ce guide explique comment utiliser le package `docx_json` pour transformer vos documents Word (`.docx`) en fichiers JSON structurés et HTML sémantiques.

## 📋 Prérequis

1. Python 3.7 ou supérieur
2. La bibliothèque `python-docx` (installation : `pip install python-docx`)

## 🚀 Installation

### Installation du package depuis le dépôt

```bash
# Clonez le dépôt
git clone https://github.com/teluq/docx-json.git
cd docx-json

# Installez le package en mode développement
pip install -e .
```

### Utilisation sans installation

Vous pouvez aussi simplement utiliser le script de lancement inclus :

```bash
# Installez juste la dépendance
pip install python-docx

# Puis lancez le script directement
python run_docx_converter.py votre-document.docx --json --html
```

## 🚀 Utilisation de base

1. Placez votre fichier `.docx` dans un dossier de votre choix
2. Ouvrez un terminal
3. Exécutez la commande :

```bash
# Si vous avez installé le package
docx-json mon-document.docx --json --html

# OU en utilisant le script de lancement
python run_docx_converter.py mon-document.docx --json --html
```

### Options disponibles :
- `--json` : génère un fichier `.json` (activé par défaut si aucune option n'est spécifiée)
- `--html` : génère un fichier `.html`
- `--no-save-images` : encode les images en base64 au lieu de les sauvegarder comme fichiers séparés
- `--verbose` : affiche des messages de debug détaillés

## 🎮 Instructions spéciales dans Word

Vous pouvez ajouter des instructions spéciales dans votre document Word pour personnaliser le rendu. Ces instructions doivent être sur une ligne séparée et commencer par `:::`.

### Exemples d'instructions spéciales :

| Instruction | Effet |
|-------------|-------|
| `:::class hero dark` | Ajoute les classes CSS "hero" et "dark" au prochain élément |
| `:::id intro` | Attribue l'ID HTML "intro" au prochain élément |
| `:::ignore` | Exclut le prochain paragraphe ou tableau du rendu final |
| `:::quote start` | Débute un bloc citation (`<blockquote>`) |
| `:::quote end` | Ferme le bloc citation |
| `:::html <hr/>` | Insère directement du HTML brut |

## 🧩 Composants pédagogiques

Le convertisseur reconnaît des balises spéciales pour créer des composants interactifs Bootstrap. Ces composants sont délimités par des balises comme `[NomDuComposant]` et optionnellement `[Fin NomDuComposant]`.

### Composants pris en charge :

| Balise | Description |
|--------|-------------|
| `[Vidéo]` | Crée un conteneur vidéo avec ratio 16:9 |
| `[Audio]` | Crée un lecteur audio |
| `[Accordéon]` | Crée un composant accordéon Bootstrap |
| `[Carrousel]` | Crée un carrousel d'éléments |
| `[Onglets]` | Crée un système d'onglets |
| `[Défilement]` | Crée un composant avec menu de navigation par défilement |

### Comment structurer vos composants :

1. Commencez par la balise du composant sur une ligne seule (ex: `[Accordéon]`)
2. Pour l'accordéon, les onglets et le défilement :
   - Ajoutez des titres (Heading 1-6) pour créer les sections/onglets
   - Le texte du titre sera utilisé comme étiquette
   - Tout contenu situé entre deux titres sera placé dans la section correspondante
3. Pour le carrousel :
   - Chaque paragraphe/élément sera une diapositive distincte
4. Terminez optionnellement avec la balise de fin (ex: `[Fin Accordéon]`)

## 📚 Exemple complet

1. Créez un document Word contenant :

```
Titre principal
==============

:::class hero
:::id main-title

Ceci est un paragraphe d'introduction.

:::quote start
La citation commence ici.
Elle peut continuer sur plusieurs paragraphes.
:::quote end

:::html <hr/>

## Section secondaire

[Accordéon]
### Premier panneau
Contenu du premier panneau qui sera caché par défaut.

### Deuxième panneau
Plus de contenu caché ici.
[Fin Accordéon]

Un tableau suit :

| Col1 | Col2 |
|------|------|
| A    | B    |
| C    | D    |

:::ignore
Ce paragraphe sera ignoré dans le rendu final.
```

2. Sauvegardez ce document sous le nom `exemple.docx`

3. Lancez la conversion :
```bash
python run_docx_converter.py exemple.docx --json --html
```

4. Vous obtiendrez :
   - `exemple.json` : représentation structurée
   - `exemple.html` : version HTML propre et sémantique
   - Un dossier `images/` contenant les images extraites du document (si présentes)

## 🔍 Structure du fichier JSON généré

Le fichier JSON généré aura une structure similaire à celle-ci :

```json
{
  "meta": {
    "title": "exemple.docx"
  },
  "content": [
    {
      "type": "heading",
      "level": 1,
      "runs": [{"text": "Titre principal", "bold": true}],
      "html_class": "hero",
      "html_id": "main-title"
    },
    {
      "type": "paragraph",
      "runs": [{"text": "Ceci est un paragraphe d'introduction.", "bold": false}]
    },
    {
      "type": "block",
      "block_type": "quote",
      "content": [
        {
          "type": "paragraph",
          "runs": [{"text": "La citation commence ici.", "bold": false}]
        },
        {
          "type": "paragraph",
          "runs": [{"text": "Elle peut continuer sur plusieurs paragraphes.", "bold": false}]
        }
      ]
    },
    {
      "type": "raw_html",
      "content": "<hr/>"
    },
    {
      "type": "heading",
      "level": 2,
      "runs": [{"text": "Section secondaire", "bold": true}]
    },
    {
      "type": "component",
      "component_type": "Accordéon",
      "content": [
        {
          "type": "heading",
          "level": 3,
          "runs": [{"text": "Premier panneau", "bold": true}]
        },
        {
          "type": "paragraph",
          "runs": [{"text": "Contenu du premier panneau qui sera caché par défaut.", "bold": false}]
        },
        {
          "type": "heading",
          "level": 3,
          "runs": [{"text": "Deuxième panneau", "bold": true}]
        },
        {
          "type": "paragraph",
          "runs": [{"text": "Plus de contenu caché ici.", "bold": false}]
        }
      ]
    },
    {
      "type": "paragraph",
      "runs": [{"text": "Un tableau suit :", "bold": false}]
    },
    {
      "type": "table",
      "rows": [
        [
          [{"type": "paragraph", "runs": [{"text": "Col1", "bold": true}]}],
          [{"type": "paragraph", "runs": [{"text": "Col2", "bold": true}]}]
        ],
        [
          [{"type": "paragraph", "runs": [{"text": "A", "bold": false}]}],
          [{"type": "paragraph", "runs": [{"text": "B", "bold": false}]}]
        ],
        [
          [{"type": "paragraph", "runs": [{"text": "C", "bold": false}]}],
          [{"type": "paragraph", "runs": [{"text": "D", "bold": false}]}]
        ]
      ]
    }
  ],
  "images": {}
}
```

## 💡 Conseils

- Les instructions commençant par `:::` doivent être sur leur propre ligne (paragraphe).
- Utilisez la prévisualisation HTML pour vérifier le rendu avant de finaliser votre document.
- Pour les composants pédagogiques, utilisez des titres (Heading) pour structurer le contenu.
- Par défaut, les images sont extraites dans un dossier `images/`. Si vous préférez les avoir en base64 intégrées dans le HTML/JSON, utilisez l'option `--no-save-images`.

## 🐛 Résolution des problèmes

Si vous rencontrez des erreurs :

1. Vérifiez que le fichier `.docx` est valide et non corrompu
2. Assurez-vous que `python-docx` est bien installé
3. Vérifiez que vos instructions `:::` et vos balises de composants suivent la syntaxe correcte
4. Utilisez l'option `--verbose` pour voir plus de détails sur le processus de conversion

Pour plus d'informations, consultez le fichier README.md.