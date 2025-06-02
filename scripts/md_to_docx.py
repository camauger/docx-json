#!/usr/bin/env python
"""
Convertit un fichier Markdown en DOCX en utilisant pypandoc.
Usage: python md_to_docx.py <fichier_md> [<fichier_docx>]
"""

import os
import sys
import time

import pypandoc


def md_to_docx(input_file, output_file=None):
    """
    Convertit un fichier Markdown en DOCX.

    Args:
        input_file (str): Chemin vers le fichier Markdown d'entrée
        output_file (str, optional): Chemin vers le fichier DOCX de sortie. Si None,
                                    remplace l'extension .md par .docx

    Returns:
        str: Chemin vers le fichier de sortie
    """
    # Vérifier que le fichier d'entrée existe
    if not os.path.isfile(input_file):
        print(f"ERREUR: Le fichier {input_file} n'existe pas.")
        raise FileNotFoundError(f"Le fichier {input_file} n'existe pas.")
    else:
        print(f"INFO: Fichier d'entrée trouvé: {input_file}")

    # Déterminer le nom du fichier de sortie si non spécifié
    if output_file is None:
        base_name = os.path.splitext(input_file)[0]
        output_file = f"{base_name}.docx"
    print(f"INFO: Fichier de sortie: {output_file}")

    # Préparer les arguments pour pypandoc
    extra_args = ["--standalone", "--table-of-contents", "--toc-depth=3"]

    # Ajouter le fichier de référence s'il existe
    if os.path.exists("reference.docx"):
        extra_args.append("--reference-doc=reference.docx")
        print(f"INFO: Utilisation du fichier de référence: reference.docx")
    else:
        print(
            f"INFO: Aucun fichier de référence trouvé, utilisation du style par défaut"
        )

    # Convertir le fichier avec pypandoc
    try:
        print(f"INFO: Début de la conversion de {input_file} en {output_file}...")
        start_time = time.time()

        pypandoc.convert_file(
            input_file, "docx", outputfile=output_file, extra_args=extra_args
        )

        end_time = time.time()
        duration = end_time - start_time

        # Vérifier que le fichier a bien été créé
        if os.path.isfile(output_file):
            file_size = os.path.getsize(output_file)
            print(f"SUCCÈS: Conversion réussie en {duration:.2f} secondes!")
            print(f"SUCCÈS: Fichier créé: {output_file} ({file_size} octets)")
            return output_file
        else:
            print(f"ERREUR: Le fichier {output_file} n'a pas été créé.")
            raise FileNotFoundError(
                f"Le fichier de sortie {output_file} n'a pas été créé."
            )
    except Exception as e:
        print(f"ERREUR: Échec de la conversion - {str(e)}")
        raise


if __name__ == "__main__":
    # Afficher un en-tête
    print("\n" + "=" * 60)
    print(" CONVERTISSEUR MARKDOWN VERS DOCX ".center(60, "="))
    print("=" * 60 + "\n")

    # Vérifier les arguments
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <fichier_md> [<fichier_docx>]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    print(f"Fichier d'entrée: {input_file}")
    print(f"Fichier de sortie: {output_file if output_file else 'Automatique'}\n")

    try:
        result = md_to_docx(input_file, output_file)
        print(f"\nConversion terminée avec succès!")
        print(f"Fichier créé: {result}")
    except Exception as e:
        print(f"\nERREUR: {str(e)}")
        sys.exit(1)

    print("\n" + "=" * 60 + "\n")
