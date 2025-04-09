from docx import Document
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt, RGBColor


def create_test_document():
    # Créer un nouveau document
    doc = Document()

    # Ajouter un titre principal
    title = doc.add_heading("Document de Test pour le Convertisseur Docx-Json", 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Section 1: Composants Bootstrap
    doc.add_heading("1. Composants Bootstrap", level=1)

    # Accordéon
    doc.add_heading("Accordéon", level=2)

    # Début de l'accordéon
    p = doc.add_paragraph("[Accordéon]")

    # Premier élément de l'accordéon
    p = doc.add_heading(
        "Axe 1 - L'atteinte du plein potentiel de toutes et de tous", level=3
    )

    p = doc.add_paragraph(
        "La Politique favorise entre autres la mise en place d'interventions rapides et continues qui sont adaptées à la diversité des personnes et des besoins."
    )

    # Deuxième élément de l'accordéon
    p = doc.add_heading(
        "Axe 2 - Un milieu inclusif propice au développement, à l'apprentissage et à la réussite",
        level=3,
    )

    p = doc.add_paragraph(
        "La Politique soutient notamment que la réussite éducative est favorisée par le développement de pratiques éducatives et pédagogiques de qualité, et par un environnement inclusif, sain, sécuritaire, stimulant et créatif."
    )

    # Troisième élément de l'accordéon
    p = doc.add_heading(
        "Axe 3 - Des acteurs et des partenaires mobilisés pour la réussite", level=3
    )

    p = doc.add_paragraph(
        "La Politique vise à soutenir l'engagement des parents et l'appui concerté des membres de la communauté."
    )

    # Fin de l'accordéon
    p = doc.add_paragraph("[Fin Accordéon]")

    # Onglets
    doc.add_heading("Onglets", level=2)

    # Début des onglets
    p = doc.add_paragraph("[Onglets]")

    p = doc.add_heading("Home", level=3)
    p = doc.add_paragraph(
        "This is some placeholder content for the Home tab's associated content."
    )

    p = doc.add_heading("Profile", level=3)
    p = doc.add_paragraph(
        "This is some placeholder content for the Profile tab's associated content."
    )

    # Fin des onglets
    p = doc.add_paragraph("[Fin Onglets]")

    # Carrousel
    doc.add_heading("Carrousel", level=2)

    # Début du carrousel
    p = doc.add_paragraph("[Carrousel]")

    p = doc.add_heading("First slide", level=3)
    p = doc.add_paragraph("[Image: First slide]")

    p = doc.add_heading("Second slide", level=3)
    p = doc.add_paragraph("[Image: Second slide]")

    p = doc.add_heading("Third slide", level=3)
    p = doc.add_paragraph("[Image: Third slide]")

    # Fin du carrousel
    p = doc.add_paragraph("[Fin Carrousel]")

    # Sauvegarder le document
    doc.save("test_document.docx")


if __name__ == "__main__":
    create_test_document()
