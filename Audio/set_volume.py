import subprocess
import os
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox

def modifier_volume_audio(fichier_entree, facteur_volume, fichier_sortie):
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
    root = tk.Tk()
    root.withdraw()  # Masquer la fenêtre principale

    # Choisir fichier d'entrée
    fichier_entree = filedialog.askopenfilename(
        title="Choisir le fichier audio d'entrée",
        filetypes=[("Fichiers WAV", "*.wav"), ("Tous les fichiers", "*.*")]
    )
    if not fichier_entree:
        return

    # Demander le facteur de volume
    facteur_volume = simpledialog.askfloat(
        "Facteur de volume",
        "Entrez le facteur de volume (ex: 1.5 pour +50%)",
        minvalue=0.1, maxvalue=10.0
    )
    if facteur_volume is None:
        return

    # Choisir emplacement de sortie
    fichier_sortie = filedialog.asksaveasfilename(
        title="Enregistrer le fichier modifié",
        defaultextension=".wav",
        filetypes=[("Fichiers WAV", "*.wav")]
    )
    if not fichier_sortie:
        return

    # Lancer la modification
    modifier_volume_audio(fichier_entree, facteur_volume, fichier_sortie)

if __name__ == "__main__":
    lancer_interface()
