import subprocess
import sys
import os

def modifier_volume_audio(fichier_entree, facteur_volume, fichier_sortie=None):
    if not os.path.exists(fichier_entree):
        print("Fichier introuvable :", fichier_entree)
        return

    if fichier_sortie is None:
        base, ext = os.path.splitext(fichier_entree)
        fichier_sortie = f"{base}_volume_{facteur_volume}{ext}"

    commande = [
        "ffmpeg",
        "-y",  # overwrite
        "-i", fichier_entree,
        "-filter:a", f"volume={facteur_volume}",
        "-ar", "48000",
        "-ac", "2",
        "-c:a", "pcm_s16le",
        fichier_sortie
    ]

    print("Commande exécutée :", " ".join(commande))
    subprocess.run(commande)

    print(f"Fichier créé : {fichier_sortie}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Utilisation : python set_volume.py fichier_entree.wav facteur_volume [fichier_sortie.wav]")
        print("Exemple : python set_volume.py a.wav 1.5")
    else:
        fichier_entree = sys.argv[1]
        facteur_volume = float(sys.argv[2])
        fichier_sortie = sys.argv[3] if len(sys.argv) > 3 else None
        modifier_volume_audio(fichier_entree, facteur_volume, fichier_sortie)