import pyttsx3
import subprocess
import os
import platform

def generer_fichier_audio(texte, voix_id, nom_sortie):
    engine = pyttsx3.init()
    engine.setProperty('voice', voix_id)
    engine.setProperty('rate', 150)

    fichier_temp = f"_temp_{nom_sortie}"
    engine.save_to_file(texte, fichier_temp)
    engine.runAndWait()

    # Convertir en WAV propre
    subprocess.run([
        "ffmpeg", "-y",
        "-i", fichier_temp,
        "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le",
        nom_sortie
    ])

    os.remove(fichier_temp)

def texte_vers_audio():
    texte = "ALERTE"
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    systeme = platform.system().lower()

    # Sélection des voix
    voix_fr = next((v for v in voices if "fr" in v.id.lower() or "thomas" in v.name.lower() or "amélie" in v.name.lower()), voices[0])
    voix_en = next((v for v in voices if "english" in v.name.lower() or "zira" in v.name.lower() or "david" in v.name.lower()), None)

    if not voix_en:
        print("⚠️ Aucune voix anglaise trouvée. Utilisation de la voix par défaut.")
        voix_en = voices[0]

    print("Voix française utilisée :", voix_fr.name)
    print("Voix anglaise utilisée :", voix_en.name)

    generer_fichier_audio(texte, voix_fr.id, "alerte_fr.wav")
    generer_fichier_audio(texte, voix_en.id, "alerte_en.wav")

if __name__ == "__main__":
    texte_vers_audio()
