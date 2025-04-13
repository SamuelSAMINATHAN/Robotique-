import time
import queue
import sounddevice as sd
import json
from vosk import Model, KaldiRecognizer
from robomaster import robot

# 🔹 INITIALISATION DU ROBOT
# Initialise le robot RoboMaster pour exécuter des commandes.
ep_robot = robot.Robot()
ep_robot.initialize()

# 🔹 INITIALISATION DU MODÈLE VOSK
# Charge le modèle de reconnaissance vocale VOSK pour la langue française.
model_path = "model_fr"
model = Model(model_path)
recognizer = KaldiRecognizer(model, 16000)

# 🔹 PARAMÈTRES AUDIO
# Configure les paramètres audio pour capturer la voix en temps réel.
SAMPLERATE = 16000
BLOCKSIZE = 8000
audio_queue = queue.Queue()

def audio_callback(indata, frames, time, status):
    """ Capture l'audio et l'ajoute à la file d'attente """
    if status:
        print(f"⚠️ Erreur audio : {status}")
    audio_queue.put(bytes(indata))

def detect_and_act():
    """
    Fonction principale :
    - Écoute les commandes vocales en temps réel.
    - Exécute des actions spécifiques en fonction des commandes (mots) reconnues.
    """
    with sd.InputStream(samplerate=SAMPLERATE, blocksize=BLOCKSIZE, dtype='int16',
                        channels=1, callback=audio_callback):
        print("Le RoboMaster écoute... Dites une commande ou 'stop'.")

        while True:
            data = audio_queue.get()
            
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                text = result.get("text", "").lower()
                print(f"👂 Détecté : {text}")

                # 🔸 Commandes personnalisées
                if "commande 1" in text:  # Remplacez par votre commande
                    print(" Action pour commande 1")
                    # TODO: insérer l'action ici

                elif "commande 2" in text:
                    print(" Action pour commande 2")
                    # TODO: insérer l'action ici

                elif "stop" in text:
                    print("🛑 Arrêt du programme")
                    break

try:
    detect_and_act()
finally:
    ep_robot.close()
    print("Fermeture du RoboMaster.")
