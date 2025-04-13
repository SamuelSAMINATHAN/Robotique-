import os
import cv2
import time
import pickle
import numpy as np
import face_recognition
from robomaster import robot

DATA_FILE = "known_faces.dat"

def load_known_faces():
    """
    Charge les encodages de visages et les noms associés depuis un fichier.
    """
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "rb") as f:
            data = pickle.load(f)
            return data.get("encodings", []), data.get("names", [])
    return [], []

def save_known_faces(encodings, names):
    """
    Sauvegarde les encodages de visages et les noms associés dans un fichier.
    """
    data = {"encodings": encodings, "names": names}
    with open(DATA_FILE, "wb") as f:
        pickle.dump(data, f)

def main():
    # Initialisation du robot et de la caméra
    ep_robot = robot.Robot()
    ep_robot.initialize(conn_type="sta")
    ep_camera = ep_robot.camera
    ep_camera.start_video_stream(display=False, resolution='720p', fps=30)

    # Chargement des visages connus
    known_face_encodings, known_face_names = load_known_faces()
    print("Visages déjà connus :", known_face_names)

    try:
        while True:
            frame = ep_camera.read_cv2_image()
            if frame is None:
                continue

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_frame)
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

            for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                name = "Inconnu"
                if known_face_encodings:
                    matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.5)
                    face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                    best_match_index = np.argmin(face_distances)
                    if matches[best_match_index]:
                        name = known_face_names[best_match_index]

                # Dessiner un rectangle autour du visage
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

            cv2.imshow("RoboMaster Face Recognition", frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('r') and face_encodings:
                print("Visage détecté. Saisissez le nom pour ce visage :")
                nom = input("Nom : ")
                known_face_encodings.append(face_encodings[0])
                known_face_names.append(nom)
                save_known_faces(known_face_encodings, known_face_names)
                print(f"Visage de {nom} enregistré.")

    finally:
        ep_camera.stop_video_stream()
        ep_robot.close()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
