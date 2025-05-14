# Module Core - Documentation

Ce module contient les composants principaux du convertisseur DOCX-JSON. Il est responsable de l'analyse des documents DOCX, de leur transformation en structure JSON intermédiaire, et de la génération de formats de sortie (HTML, Markdown, etc.).

## Architecture générale

Le module utilise une architecture modulaire où chaque composant a une responsabilité bien définie :

```
docx_json/core/
├── __init__.py             # Définition du package
├── docx_parser.py          # Analyse des fichiers DOCX
├── processor.py            # Traitement intermédiaire des données
├── converter.py            # Conversion principale DOCX -> JSON
├── compatibility.py        # Gestion de la compatibilité entre versions
├── html_generator.py       # Compatibilité pour la génération HTML
├── markdown_generator.py   # Génération de Markdown à partir du JSON
└── html_renderer/          # Package de génération HTML modulaire
    ├── __init__.py         # Définition du package renderer
    ├── base.py             # Classe de base des renderers
    ├── generator.py        # Classe principale HTMLGenerator
    ├── text.py             # Renderer pour les éléments textuels
    ├── table.py            # Renderer pour les tableaux
    ├── block.py            # Renderer pour les blocs (citations, etc.)
    ├── component.py        # Renderer pour les composants interactifs
    ├── image.py            # Renderer pour les images
    └── raw_html.py         # Renderer pour le HTML brut
```

## Composants principaux

### `docx_parser.py`

Ce module est responsable de l'extraction des données brutes à partir des fichiers DOCX, utilisant la bibliothèque `python-docx` pour accéder au contenu du document.

### `processor.py`

Module intermédiaire effectuant des transformations et des traitements sur les données extraites avant la représentation finale.

### `converter.py`

Contient la logique principale pour convertir un document DOCX en représentation JSON, en orchestrant le processus d'extraction et de transformation.

### `compatibility.py`

Assure la compatibilité entre différentes versions de documents et des structures de données intermédiaires.

### `markdown_generator.py`

Génère une représentation Markdown à partir de la structure JSON du document.

### `html_generator.py`

Fichier de compatibilité qui redirige vers le nouveau package `html_renderer`. Ce fichier est maintenu pour assurer la compatibilité avec le code existant.

### Package `html_renderer`

Implémente la génération HTML de manière modulaire et extensible. Ce package utilise une architecture orientée composants détaillée ci-dessous.

## Architecture du package `html_renderer`

Le générateur HTML utilise un modèle de conception Stratégie pour représenter les différents types d'éléments du document. Cette architecture facilite la maintenance et l'extension du code.

### Classe de base : `ElementRenderer`

Classe abstraite qui définit l'interface commune à tous les renderers d'éléments HTML :

```python
class ElementRenderer(ABC):
    @abstractmethod
    def render(self, element: Dict[str, Any], indent_level: int = 0) -> List[str]:
        """Génère le HTML pour un élément spécifique."""
        pass
```

### Renderers spécialisés

Chaque type d'élément est géré par un renderer spécialisé, organisé dans son propre fichier :

1. **`TextElementRenderer` (text.py)**
   - Responsable des éléments textuels (paragraphes, titres, listes)
   - Gère le formatage du texte (gras, italique, souligné)

2. **`TableRenderer` (table.py)**
   - Génère le HTML pour les tableaux
   - Traite récursivement les cellules contenant des paragraphes

3. **`BlockRenderer` (block.py)**
   - Gère les blocs comme les citations et les encadrés
   - Applique les styles appropriés à chaque type de bloc

4. **`ComponentRenderer` (component.py)**
   - Responsable des composants interactifs complexes
   - Implémente des renderers spécifiques pour :
     - Accordéons
     - Carrousels
     - Onglets
     - Vidéos
     - Audio
     - Défilement (scrollspy)

5. **`ImageRenderer` (image.py)**
   - Gère l'inclusion des images dans le document HTML

6. **`RawHTMLRenderer` (raw_html.py)**
   - Permet l'insertion de HTML brut dans le document généré

### Classe principale : `HTMLGenerator` (generator.py)

Coordonne le processus de génération HTML :

- Initialise tous les renderers spécialisés
- Maintient un dictionnaire de mappage entre types d'éléments et renderers
- Génère la structure HTML de base (head, body, scripts)
- Délègue le rendu de chaque élément au renderer approprié

```python
self._renderers = {
    "paragraph": self._text_renderer,
    "heading": self._text_renderer,
    "list_item": self._text_renderer,
    "table": self._table_renderer,
    "block": self._block_renderer,
    "component": self._component_renderer,
    "image": self._image_renderer,
    "raw_html": self._raw_html_renderer,
}
```

## Avantages de cette architecture

1. **Maintenabilité** : Chaque classe a une responsabilité unique et bien définie
2. **Extensibilité** : Ajouter un nouveau type d'élément se fait en créant un nouveau renderer
3. **Testabilité** : Les renderers peuvent être testés indépendamment
4. **Lisibilité** : Le code est organisé de manière logique et modulaire
5. **Séparation des préoccupations** : La logique de rendu est séparée de la structure des données
6. **Facilité de débogage** : Problèmes isolés dans des fichiers spécifiques
7. **Meilleure organisation du code** : Fichiers plus courts et ciblés

## Workflow typique

1. Le document DOCX est analysé par `docx_parser.py`
2. `converter.py` transforme les données en structure JSON intermédiaire
3. `html_generator.py` ou le package `html_renderer` génère le format de sortie HTML
4. Chaque élément est traité par un renderer spécialisé selon son type

## Exemple d'utilisation

```python
from docx_json.core.converter import DocxToJsonConverter
from docx_json.core.html_renderer import HTMLGenerator

# Convertir DOCX en JSON
converter = DocxToJsonConverter("document.docx")
json_data = converter.convert()

# Générer HTML
html_generator = HTMLGenerator(json_data)
html_output = html_generator.generate()

# Sauvegarder le résultat
with open("output.html", "w", encoding="utf-8") as f:
    f.write(html_output)
```

## Extension du système de rendu HTML

Pour ajouter un nouveau type d'élément :

1. Créer une nouvelle classe de renderer héritant de `ElementRenderer`
2. Implémenter la méthode `render()`
3. Ajouter une instance à la classe `HTMLGenerator`
4. Mettre à jour le dictionnaire `_renderers` pour mapper le type d'élément au renderer

Par exemple, pour ajouter un nouveau type d'élément "code" :

```python
# Nouveau fichier code.py
from typing import Any, Dict, List
from .base import ElementRenderer

class CodeRenderer(ElementRenderer):
    def render(self, element: Dict[str, Any], indent_level: int = 0) -> List[str]:
        indent = " " * indent_level
        language = element.get("language", "")
        code = element.get("code", "")

        return [
            f'{indent}<pre>',
            f'{indent}  <code class="language-{language}">',
            f'{indent}    {code}',
            f'{indent}  </code>',
            f'{indent}</pre>'
        ]

# Dans generator.py, ajouter:
from .code import CodeRenderer

# Dans __init__ de HTMLGenerator:
self._code_renderer = CodeRenderer()
self._renderers["code"] = self._code_renderer
```
