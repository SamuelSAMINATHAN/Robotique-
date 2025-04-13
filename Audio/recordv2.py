import pyttsx3
import subprocess
import os

def texte_vers_audio(texte, voix_nom, fichier_sortie):
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')

    # Sélectionner la voix selon le nom partiel (ex : "Hortense", "Zira")
    voix_choisie = next((v for v in voices if voix_nom.lower() in v.name.lower()), None)

    if voix_choisie:
        engine.setProperty('voice', voix_choisie.id)
        print(f"Voix utilisée : {voix_choisie.name}")
    else:
        print(f"⚠️ Voix '{voix_nom}' non trouvée. Utilisation de la voix par défaut.")

    engine.setProperty('rate', 150)

    # Fichier temporaire
    fichier_temp = f"{fichier_sortie}"

    engine.save_to_file(texte, fichier_temp)
    engine.runAndWait()

    # Conversion WAV : 48kHz, stéréo, PCM 16 bits
    subprocess.run([
        "ffmpeg", "-y",
        "-i", fichier_temp,
        "-ar", "48000",
        "-ac", "2",
        "-c:a", "pcm_s16le",
        fichier_sortie
    ])

    # Nettoyage
    if os.path.exists(fichier_temp):
        os.remove(fichier_temp)

if __name__ == "__main__":
    texte = "Sucess"  # Remplacez par le texte souhaité

    # === CHOISISSEZ LA VOIX ICI EN COMMENTANT/DÉCOMMENTANT ===

    # Voix Windows : 

        # Voix française (par défaut)
    #texte_vers_audio(texte, voix_nom="Hortense", fichier_sortie=f"{texte}.wav")

        # Voix anglaise (décommenter pour l’utiliser)
    #texte_vers_audio(texte, voix_nom="Zira", fichier_sortie=f"{texte}.wav")

    # Voix Mac :

        # Voix francaise (par defaut)
    texte_vers_audio(texte, voix_nom="Thomas", fichier_sortie=f"{texte}.wav")

        # Voix anglaise (décommenter pour l’utiliser)
    #texte_vers_audio(texte, voix_nom="Samantha", fichier_sortie=f"{texte}.wav")
