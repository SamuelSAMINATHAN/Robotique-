import cv2
import numpy as np
import pickle
import tflite_runtime.interpreter as tflite
import os
import time
import random

# === TFLite setup ===
interpreter = tflite.Interpreter(model_path="models/efficientnet-lite1/efficientnet-lite1-fp32.tflite")
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

def preprocess(img):
    img = cv2.resize(img, (240, 240))
    img = img.astype(np.float32) / 127.5 - 1
    return np.expand_dims(img, axis=0)

def get_embedding(img):
    input_data = preprocess(img)
    interpreter.set_tensor(input_details[0]['index'], input_data)
    interpreter.invoke()
    return interpreter.get_tensor(output_details[0]['index'])[0]

# === Augmentations ===
def augment_image(image):
    h, w = image.shape[:2]

    # Random flip
    if random.random() < 0.5:
        image = cv2.flip(image, 1)

    # Random rotation
    angle = random.uniform(-10, 10)
    M = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1)
    image = cv2.warpAffine(image, M, (w, h), borderMode=cv2.BORDER_REFLECT)

    # Random brightness/contrast
    alpha = random.uniform(0.7, 1.3)  # contrast
    beta = random.randint(-30, 30)    # brightness
    image = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)

    # Optional: slight blur or noise
    if random.random() < 0.3:
        image = cv2.GaussianBlur(image, (3, 3), 0)

    return image

# === Base de données ===
DB_FILE = "objects_efficientnet.pkl"
database = {}
if os.path.exists(DB_FILE):
    with open(DB_FILE, "rb") as f:
        database = pickle.load(f)

# === Initialisation du robot et de la caméra ===
from robomaster import robot

ep_robot = robot.Robot()
# 'sta' signifie mode Wi-Fi station; adaptez si besoin (ex: "rndis" pour USB)
ep_robot.initialize()
ep_camera = ep_robot.camera
ep_camera.start_video_stream(display=False, resolution='720p',)

mask_points = []
mode = "wait"
freeze_frame = None
obj_name = ""
collected_embeddings = []

def draw_polygon(event, x, y, flags, param):
    global mask_points, mode
    if mode == "draw":
        if event == cv2.EVENT_LBUTTONDOWN:
            mask_points.append((x, y))

cv2.namedWindow("Apprentissage")
cv2.setMouseCallback("Apprentissage", draw_polygon)

print("Appuie sur 'l' pour lancer l'apprentissage | 'q' pour quitter")

page_closed = False

while not page_closed:
    # Selon le mode, utiliser soit l'image figée, soit une image lue en direct depuis le robot
    if mode == "draw" and freeze_frame is not None:
        display = freeze_frame.copy()
    else:
        frame = ep_camera.read_cv2_image()
        if frame is None:
            continue
        display = frame.copy()

    # En mode "draw", on affiche le tracé du contour
    if mode == "draw":
        for i, pt in enumerate(mask_points):
            cv2.circle(display, pt, 3, (0, 255, 0), -1)
            if i > 0:
                cv2.line(display, mask_points[i - 1], pt, (0, 255, 0), 2)
        cv2.putText(display, "Trace un contour autour de l’objet (clics)", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        cv2.putText(display, "Entrée pour valider et lancer la capture auto", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)

    cv2.imshow("Apprentissage", display)
    key = cv2.waitKey(1)

    if key == ord('q'):
        break

    elif key == ord('l') and mode == "wait":
        # Geler l'image actuelle depuis la caméra du robot
        freeze_frame = ep_camera.read_cv2_image()
        if freeze_frame is None:
            continue
        cv2.imshow("Apprentissage", freeze_frame)
        cv2.waitKey(1)
        
        print("🧊 Caméra figée. Prépare-toi à entrer le nom de l’objet.")
        obj_name = input("Nom de l’objet : ").strip()
        
        mask_points = []
        collected_embeddings = []
        mode = "draw"

    # Touche "Entrée" (code 13) pour valider le contour dessiné
    elif key == 13 and mode == "draw" and len(mask_points) >= 3:
        print("🟡 Lancement des captures augmentées (1m30)...")
        start_time = time.time()
        duration = 90  # secondes
        pts = np.array(mask_points, np.int32)
        mask = np.zeros(freeze_frame.shape[:2], dtype=np.uint8)
        cv2.fillPoly(mask, [pts], 255)
        x, y, w, h = cv2.boundingRect(pts)

        count = 0
        while time.time() - start_time < duration:
            masked = cv2.bitwise_and(freeze_frame, freeze_frame, mask=mask)
            roi = masked[y:y+h, x:x+w]
            if roi.size > 0:
                aug = augment_image(roi)
                emb = get_embedding(aug)
                collected_embeddings.append(emb)
                count += 1
            time.sleep(0.05)  # cadence d’environ 20 vues/sec

        print(f"✅ {count} vues augmentées capturées pour '{obj_name}'.")

        if obj_name in database:
            database[obj_name].extend(collected_embeddings)
        else:
            database[obj_name] = collected_embeddings

        with open(DB_FILE, "wb") as f:
            pickle.dump(database, f)

        print("💾 Objet sauvegardé avec succès.")
        mode = "wait"

# Libérer les ressources
ep_camera.stop_video_stream()
ep_robot.close()
cv2.destroyAllWindows()
