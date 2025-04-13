import pyttsx3
import subprocess
import os

def texte_vers_audio():
    """
    Convertit un texte en audio avec des paramètres par défaut.
    - Texte : "Bienvenu à l'Isep".
    """
    engine = pyttsx3.init()

    texte = "Bienvenu à l'Isep" # Remplacez par le texte souhaité
    engine.setProperty('rate', 150)
    engine.say(texte)
    engine.runAndWait()

    nom_fichier = f"_{texte}.wav"    
    engine.save_to_file(texte, nom_fichier)
    engine.runAndWait()
            
    subprocess.run([ "ffmpeg", "-i", nom_fichier, "-ar", "48000", "-ac",  "2", "-c:a", "pcm_s16le", f"{texte}.wav" ])
    os.remove(nom_fichier)

if __name__ == "__main__":
    texte_vers_audio()
