import cv2
import time
import pickle
import numpy as np

# Charger la base de données des embeddings
DB_FILE = "/Users/samsam/Documents/vscode/Python/extension_python/Reconnaissance/Item_Reco/objects_efficientnet.pkl"
with open(DB_FILE, "rb") as f:
    database = pickle.load(f)

def get_embedding(img, interpreter, input_details, output_details):
    """Extrait l'embedding d'une image à l'aide du modèle TFLite."""
    img = cv2.resize(img, (240, 240))
    img = img.astype(np.float32) / 127.5 - 1
    img = np.expand_dims(img, axis=0)
    interpreter.set_tensor(input_details[0]['index'], img)
    interpreter.invoke()
    return interpreter.get_tensor(output_details[0]['index'])[0]

def find_closest_match(embedding, database, threshold=0.6):
    """Trouve l'objet le plus proche dans la base de données."""
    min_distance = float("inf")
    best_match = None
    for obj_name, embeddings in database.items():
        for db_embedding in embeddings:
            distance = np.linalg.norm(embedding - db_embedding)
            if distance < min_distance:
                min_distance = distance
                best_match = obj_name
    return best_match if min_distance < threshold else None

def track_universal(target_detector, control_logic, chassis, camera_index=0, display=True):
    """
    Fonction de suivi universelle pour RoboMaster.
    - target_detector() doit retourner un dictionnaire contenant : {'x': ..., 'y': ..., 'w': ..., 'h': ...}
    - control_logic(target, chassis) applique la vitesse au robot à partir de la détection
    - chassis : instance du chassis du robot
    """
    import tflite_runtime.interpreter as tflite

    # Initialisation du modèle TFLite
    interpreter = tflite.Interpreter(model_path="models/efficientnet-lite1/efficientnet-lite1-fp32.tflite")
    interpreter.allocate_tensors()
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    cap = cv2.VideoCapture(camera_index)

    if not cap.isOpened():
        print("Erreur : Impossible d'ouvrir la caméra.")
        return

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Erreur : Impossible de lire l'image.")
                break

            # Détection de l'objet
            target = target_detector(frame)

            if target:
                x, y, w, h = target["x"], target["y"], target["w"], target["h"]
                roi = frame[int(y - h / 2):int(y + h / 2), int(x - w / 2):int(x + w / 2)]

                if roi.size > 0:
                    embedding = get_embedding(roi, interpreter, input_details, output_details)
                    match = find_closest_match(embedding, database)

                    if match:
                        print(f"Objet détecté : {match}")
                        control_logic(target, chassis)

                        # Affichage
                        if display:
                            x1, y1 = int(x - w / 2), int(y - h / 2)
                            x2, y2 = int(x + w / 2), int(y + h / 2)
                            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                            cv2.putText(frame, match, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                            cv2.circle(frame, (int(x), int(y)), 4, (0, 0, 255), -1)
                    else:
                        print("Aucun objet correspondant trouvé.")
                        chassis.drive_speed(x=0, y=0, z=0)
            else:
                # Stop movement if nothing is detected
                chassis.drive_speed(x=0, y=0, z=0)

            if display:
                cv2.imshow("Universal Tracker", frame)
                if cv2.waitKey(1) & 0xFF == 27:
                    break
    finally:
        cap.release()
        if display:
            cv2.destroyAllWindows()