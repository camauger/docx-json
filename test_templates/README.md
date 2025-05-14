# Gabarits de test pour docx-json

Ce dossier contient des gabarits de documents conçus pour tester les fonctionnalités du convertisseur docx-json, notamment sa capacité à convertir des fichiers DOCX en formats JSON, HTML et Markdown.

## Fichiers de test

### Gabarits de base

- **basic_styles.docx** - Teste les titres (h1-h6) et les styles de texte (gras, italique, souligné)
- **lists_tables.docx** - Teste les listes (à puces, ordonnées, imbriquées) et les tableaux
- **components.docx** - Teste les composants pédagogiques (accordéon, onglets, vidéo, etc.)
- **images_links.docx** - Teste les images et les liens
- **complete_example.docx** - Combine toutes les fonctionnalités dans un document complet

### Fichiers supplémentaires

- **combined.docx** - Concaténation de plusieurs documents de test
- **local_images.docx** - Teste les images locales (SVG)

## Structure des tests

Chaque gabarit a été conçu pour tester un aspect spécifique du convertisseur :

1. **Styles de base**
   - Titres de différents niveaux (h1-h6)
   - Texte en gras, italique, souligné
   - Instructions spéciales (:::class, :::id)

2. **Listes et tableaux**
   - Listes à puces, numérotées
   - Listes imbriquées
   - Tableaux simples et complexes
   - Tableaux avec alignement

3. **Composants pédagogiques**
   - Accordéon
   - Onglets
   - Vidéo
   - Carrousel
   - Défilement
   - Audio

4. **Images et liens**
   - Images avec texte alternatif et titre
   - Liens simples et avec attributs
   - Images avec instructions spéciales

## Résultats des tests

Les tests ont permis de vérifier que le convertisseur docx-json :

- ✅ Gère correctement la conversion DOCX → JSON
- ✅ Produit du HTML sémantique
- ✅ Génère du Markdown bien formaté (nouvelle fonctionnalité)
- ✅ Traite les instructions spéciales (:::class, :::id, etc.)
- ✅ Reconnaît les composants pédagogiques
- ⚠️ Certaines fonctionnalités complexes (comme les imbrications profondes) peuvent nécessiter des ajustements
- ⚠️ Les images nécessitent une attention particulière pour leur traitement

## Comment utiliser ces gabarits

1. Pour convertir un gabarit individuel :

   ```bash
   python -m docx_json test_templates/basic_styles.docx --json --html --md
   ```

2. Les fichiers résultants (.json, .html, .md) peuvent être comparés avec les attentes pour valider les fonctionnalités.

3. Les résultats actuels des conversions sont inclus dans ce dossier pour référence.

## Notes supplémentaires

- Les instructions spéciales dans les documents DOCX sont traitées différemment par Pandoc (qui les considère comme du texte) et par docx-json (qui les interprète comme des instructions).
- Les composants pédagogiques comme [Accordéon] ne sont pas des éléments standard de DOCX/Markdown mais sont correctement interprétés par docx-json.
- L'intégration des images peut varier selon l'environnement (certaines images peuvent être manquantes dans les exemples).
