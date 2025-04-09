import pyttsx3
import subprocess
import os

def texte_vers_audio():
    engine = pyttsx3.init()

    texte = "Bienvenu à l'Isep"
        # texte = input("Entrez le texte à prononcer : ")
            
            # Paramétrages optionnels : voix, vitesse, volume...
            # Liste des voix disponibles
            # voices = engine.getProperty('voices')
            # for idx, voice in enumerate(voices):
            #     print(idx, voice.name, voice.id)
            
            # Exemple : choisir la première voix
            # engine.setProperty('voice', voices[0].id)
            # Régler la vitesse de la parole (par défaut ~200 mots/min)
    engine.setProperty('rate', 150)
            
            # Lecture du texte à voix haute (sortie haut-parleurs)
    engine.say(texte)
    engine.runAndWait()
            
            # Enregistrement du texte dans un fichier audio WAV
    nom_fichier = f"_{texte}.wav"    
    engine.save_to_file(texte, nom_fichier)
    engine.runAndWait()
            
    subprocess.run([ "ffmpeg", "-i", nom_fichier, "-ar", "48000", "-ac",  "2", "-c:a", "pcm_s16le", f"{texte}.wav" ])
    os.remove(nom_fichier)

if __name__ == "__main__":
    texte_vers_audio()
   



