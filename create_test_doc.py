from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt, RGBColor
from docx.text.paragraph import Paragraph

from docx_json.core.docx_parser import DocxParser
from docx_json.core.html_renderer import HTMLGenerator
from docx_json.core.processor import DocumentProcessor
from docx_json.models import Component


def create_test_document() -> None:
    # Créer un nouveau document
    doc = Document()

    # Ajouter un titre
    title: Paragraph = doc.add_heading(
        "Document de Test - Styles et Composants Bootstrap", level=1
    )
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Section pour les styles de texte
    doc.add_heading("Styles de texte", level=2)

    # Titres
    for i in range(1, 7):
        doc.add_heading(f"Titre de niveau {i}", level=i)

    # Styles de paragraphe
    doc.add_heading("Styles de paragraphe", level=2)

    # Paragraphe normal
    p: Paragraph = doc.add_paragraph("Paragraphe normal")

    # Paragraphe en gras
    p = doc.add_paragraph()
    run = p.add_run("Paragraphe en gras")
    run.bold = True

    # Paragraphe en italique
    p = doc.add_paragraph()
    run = p.add_run("Paragraphe en italique")
    run.italic = True

    # Paragraphe souligné
    p = doc.add_paragraph()
    run = p.add_run("Paragraphe souligné")
    run.underline = True

    # Paragraphe avec styles combinés
    p = doc.add_paragraph()
    run = p.add_run("Paragraphe en gras et italique")
    run.bold = True
    run.italic = True

    # Listes
    doc.add_heading("Listes", level=2)

    # Liste à puces simple
    doc.add_heading("Liste à puces simple", level=3)
    for i in range(1, 4):
        p = doc.add_paragraph()
        p.style = "List Bullet"
        p.paragraph_format.left_indent = Pt(36)
        p.add_run(f"Élément {i}")

    # Liste numérotée simple
    doc.add_heading("Liste numérotée simple", level=3)
    for i in range(1, 4):
        p = doc.add_paragraph()
        p.style = "List Number"
        p.paragraph_format.left_indent = Pt(36)
        p.add_run(f"Élément {i}")

    # Liste à puces avec styles
    doc.add_heading("Liste à puces avec styles", level=3)
    for i in range(1, 4):
        p = doc.add_paragraph()
        p.style = "List Bullet"
        p.paragraph_format.left_indent = Pt(36)
        run = p.add_run(f"Élément {i}")
        if i == 1:
            run.bold = True
        elif i == 2:
            run.italic = True
        elif i == 3:
            run.underline = True

    # Liste imbriquée
    doc.add_heading("Liste imbriquée", level=3)
    # Premier niveau
    p = doc.add_paragraph()
    p.style = "List Bullet"
    p.paragraph_format.left_indent = Pt(36)
    p.add_run("Élément principal 1")

    # Sous-éléments
    p = doc.add_paragraph()
    p.style = "List Bullet"
    p.paragraph_format.left_indent = Pt(72)
    p.add_run("Sous-élément 1.1")

    p = doc.add_paragraph()
    p.style = "List Bullet"
    p.paragraph_format.left_indent = Pt(72)
    p.add_run("Sous-élément 1.2")

    # Deuxième élément principal
    p = doc.add_paragraph()
    p.style = "List Bullet"
    p.paragraph_format.left_indent = Pt(36)
    p.add_run("Élément principal 2")

    # Section pour les composants Bootstrap
    doc.add_heading("Composants Bootstrap", level=2)

    # Accordéon
    doc.add_heading("Accordéon", level=3)
    doc.add_paragraph("[Accordéon class='accordion' id='mainAccordion']")
    doc.add_heading("Axe 1 - Premier axe", level=4)
    doc.add_paragraph("Contenu du premier axe de l'accordéon.")
    doc.add_heading("Axe 2 - Deuxième axe", level=4)
    doc.add_paragraph("Contenu du deuxième axe de l'accordéon.")
    doc.add_heading("Axe 3 - Troisième axe", level=4)
    doc.add_paragraph("Contenu du troisième axe de l'accordéon.")
    doc.add_paragraph("[Fin Accordéon]")

    # Onglets
    doc.add_heading("Onglets", level=3)
    doc.add_paragraph("[Onglets class='nav nav-tabs' id='mainTabs']")
    doc.add_heading("Onglet 1", level=4)
    doc.add_paragraph("Contenu du premier onglet.")
    doc.add_heading("Onglet 2", level=4)
    doc.add_paragraph("Contenu du deuxième onglet.")
    doc.add_paragraph("[Fin Onglets]")

    # Carousel
    doc.add_heading("Carrousel", level=3)
    doc.add_paragraph(
        "[Carrousel class='carousel slide' id='mainCarousel' data-bs-ride='carousel']"
    )
    doc.add_heading("Diapositive 1", level=4)
    doc.add_paragraph("Contenu de la première diapositive.")
    doc.add_heading("Diapositive 2", level=4)
    doc.add_paragraph("Contenu de la deuxième diapositive.")
    doc.add_paragraph("[Fin Carrousel]")

    # Audio
    doc.add_heading("Audio", level=3)
    doc.add_paragraph("[Audio class='audio-player' id='mainAudio']")
    doc.add_paragraph("Titre de l'audio")
    doc.add_paragraph("Description de l'audio")
    doc.add_paragraph("[Fin Audio]")

    # Vidéo
    doc.add_heading("Vidéo", level=3)
    doc.add_paragraph("[Vidéo class='video-player' id='mainVideo']")
    doc.add_paragraph("Titre de la vidéo")
    doc.add_paragraph("Description de la vidéo")
    doc.add_paragraph("[Fin Vidéo]")

    # Sauvegarder le document
    doc.save("test_document.docx")

    # Générer le HTML
    parser = DocxParser("test_document.docx", ".")
    elements = parser.parse()

    # Traiter les instructions et les composants
    processed_elements = DocumentProcessor.process_instructions(elements)

    # Imprimer le nombre d'éléments pour déboguer
    print(f"Nombre d'éléments avant traitement: {len(elements)}")
    print(f"Nombre d'éléments après traitement: {len(processed_elements)}")

    # Vérifier les types d'éléments après traitement
    component_count = 0
    for element in processed_elements:
        if element.type == "component" and isinstance(element, Component):
            component_count += 1
            print(
                f"Composant trouvé: {element.component_type} avec {len(element.content)} éléments"
            )

    print(f"Nombre de composants trouvés: {component_count}")

    # Créer la structure JSON pour le générateur HTML
    json_data = {
        "meta": {"title": "Document de Test"},
        "content": [element.to_dict() for element in processed_elements],
        "images": parser.get_images(),
    }

    generator = HTMLGenerator(json_data)
    html_content = generator.generate()

    # Sauvegarder le HTML
    with open("test_document.html", "w", encoding="utf-8") as f:
        f.write(html_content)


if __name__ == "__main__":
    create_test_document()
