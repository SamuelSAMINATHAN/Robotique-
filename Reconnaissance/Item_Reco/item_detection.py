import cv2
import numpy as np
import pickle
import tflite_runtime.interpreter as tflite
from sklearn.metrics.pairwise import cosine_similarity

# Import pour l'utilisation de la caméra du robot
from robomaster import robot

# === Configuration TFLite ===
interpreter = tflite.Interpreter(model_path="models/efficientnet-lite1/efficientnet-lite1-fp32.tflite")
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

def preprocess(img):
    """Redimensionne et normalise l'image pour EfficientNet."""
    img = cv2.resize(img, (240, 240))
    img = img.astype(np.float32) / 127.5 - 1
    return np.expand_dims(img, axis=0)

def get_embedding(img):
    """Extrait l'embedding de l'image en passant par le modèle TFLite."""
    input_data = preprocess(img)
    interpreter.set_tensor(input_details[0]['index'], input_data)
    interpreter.invoke()
    return interpreter.get_tensor(output_details[0]['index'])[0]

# === Chargement de la base d’objets ===
DB_FILE = "objects_efficientnet.pkl"
with open(DB_FILE, "rb") as f:
    database = pickle.load(f)

object_names = list(database.keys())
print("\n📦 Objets appris :", object_names)

THRESHOLD = 0.45

# === Initialisation du robot et démarrage du flux caméra ===
ep_robot = robot.Robot()
# 'sta' signifie mode Wi-Fi station; adaptez si besoin (ex: "rndis" pour USB)
ep_robot.initialize()
ep_camera = ep_robot.camera
ep_camera.start_video_stream(display=False, resolution='720p',)


print("Appuyez sur 'q' dans la fenêtre d'affichage pour quitter.")

num_frame=0
skip_frame=5

color=(0, 0, 0)
text=""


while True:
    # Lecture de l'image depuis la caméra du robot
    frame = ep_camera.read_cv2_image()
    if frame is None:
        continue

    frame = cv2.resize(frame, (1280, 720))


    display = frame.copy()
    h, w = frame.shape[:2]

    # Créer un grand carré centré dans l'image (75% de la taille minimale)
    size = int(min(h, w) * 0.75)
    x = (w - size) // 2
    y = (h - size) // 2
    
    if (skip_frame==num_frame):

        roi = frame[y:y + size, x:x + size]
        emb = get_embedding(roi)
        
        best_score = 0
        best_match = None
        for name, embs in database.items():
            sims = cosine_similarity([emb], embs)
            avg_sim = np.mean(sims)
            if avg_sim > best_score:
                best_score = avg_sim
                best_match = name

        if best_score > THRESHOLD:
            color = (0, 255, 0)
            text = f"{best_match} ({best_score:.2f})"
        else:
            color = (0, 0, 255)
            text = f"Aucun objet reconnu ({best_score:.2f})"

        num_frame=0

    cv2.rectangle(display, (x, y), (x + size, y + size), color, 2)
    cv2.putText(display, text, (x + 5, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

    cv2.imshow("Zone centrale large", display)
    num_frame += 1
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Libérer les ressources
ep_camera.stop_video_stream()
ep_robot.close()
cv2.destroyAllWindows()
