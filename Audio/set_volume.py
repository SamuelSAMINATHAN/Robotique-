import subprocess
import os
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox

def modifier_volume_audio(fichier_entree, facteur_volume, fichier_sortie):
    """
    Modifie le volume d'un fichier audio.
    - fichier_entree : chemin du fichier audio d'entrée.
    - facteur_volume : facteur de modification du volume (ex : 1.5 pour +50%).
    - fichier_sortie : chemin du fichier audio de sortie.
    """
    if not os.path.exists(fichier_entree):
        messagebox.showerror("Erreur", f"Fichier introuvable : {fichier_entree}")
        return

    commande = [
        "ffmpeg",
        "-y",
        "-i", fichier_entree,
        "-filter:a", f"volume={facteur_volume}",
        fichier_sortie
    ]

    print("Commande exécutée :", " ".join(commande))
    result = subprocess.run(commande, capture_output=True, text=True)
    print(result.stdout)
    print(result.stderr)

    if result.returncode == 0:
        messagebox.showinfo("Succès", f"Fichier créé : {fichier_sortie}")
    else:
        messagebox.showerror("Erreur", f"Erreur pendant l'exécution de ffmpeg.\n\n{result.stderr}")

def lancer_interface():
    """
    Lance une interface graphique pour :
    - Sélectionner un fichier audio.
    - Entrer un facteur de volume.
    - Choisir un emplacement pour le fichier modifié.
    """
    root = tk.Tk()
    root.withdraw()  # Masquer la fenêtre principale

    fichier_entree = filedialog.askopenfilename(
        title="Choisir le fichier audio d'entrée",
        filetypes=[("Fichiers WAV", "*.wav"), ("Tous les fichiers", "*.*")]
    )
    if not fichier_entree:
        return

    facteur_volume = simpledialog.askfloat(
        "Facteur de volume",
        "Entrez le facteur de volume (ex: 1.5 pour +50%)",
        minvalue=0.1, maxvalue=10.0
    )
    if facteur_volume is None:
        return

    fichier_sortie = filedialog.asksaveasfilename(
        title="Enregistrer le fichier modifié",
        defaultextension=".wav",
        filetypes=[("Fichiers WAV", "*.wav")]
    )
    if not fichier_sortie:
        return

    modifier_volume_audio(fichier_entree, facteur_volume, fichier_sortie)

if __name__ == "__main__":
    lancer_interface()
