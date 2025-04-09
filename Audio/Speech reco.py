import time
import queue
import sounddevice as sd
import json
from vosk import Model, KaldiRecognizer
from robomaster import robot

# -------------------------
# 🔹 INITIALISATION DU ROBOT
# -------------------------
ep_robot = robot.Robot()
ep_robot.initialize()

# -------------------------
# 🔹 INITIALISATION DU MODÈLE VOSK
# -------------------------
model_path = "model_fr"
model = Model(model_path)
recognizer = KaldiRecognizer(model, 16000)

# -------------------------
# 🔹 PARAMÈTRES AUDIO
# -------------------------
SAMPLERATE = 16000
BLOCKSIZE = 8000
audio_queue = queue.Queue()

def audio_callback(indata, frames, time, status):
    """ Capture l'audio et l'ajoute à la file d'attente """
    if status:
        print(f"⚠️ Erreur audio : {status}")
    audio_queue.put(bytes(indata))

# -------------------------
# 🔹 FONCTION PRINCIPALE
# -------------------------
def detect_and_act():
    with sd.InputStream(samplerate=SAMPLERATE, blocksize=BLOCKSIZE, dtype='int16',
                        channels=1, callback=audio_callback):
        print("🎤 Le RoboMaster écoute... Dites une commande ou 'stop'.")

        while True:
            data = audio_queue.get()
            
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                text = result.get("text", "").lower()
                print(f"👂 Détecté : {text}")

                # 🔸 PLACEHOLDER POUR LES COMMANDES PERSONNALISÉES
                if "commande 1" in text:
                    print("👉 Action pour commande 1")
                    # TODO: insérer l'action ici

                elif "commande 2" in text:
                    print("👉 Action pour commande 2")
                    # TODO: insérer l'action ici

                elif "stop" in text:
                    print("🛑 Arrêt du programme")
                    break

try:
    detect_and_act()
finally:
    ep_robot.close()
    print("🔄 Fermeture du RoboMaster.")
