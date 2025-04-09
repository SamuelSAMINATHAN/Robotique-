import os
import cv2
import time
import pickle
import numpy as np
import face_recognition


from robomaster import robot
from robomaster import camera

DATA_FILE = "known_faces.dat"

def load_known_faces():
    """
    Charge les encodages de visages et les noms associés depuis le fichier DATA_FILE.
    Retourne deux listes : known_face_encodings et known_face_names.
    """
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "rb") as f:
            data = pickle.load(f)
            return data.get("encodings", []), data.get("names", [])
    return [], []

def save_known_faces(encodings, names):
    """
    Sauvegarde les encodages de visages et les noms associés dans DATA_FILE.
    """
    data = {"encodings": encodings, "names": names}
    with open(DATA_FILE, "wb") as f:
        pickle.dump(data, f)

def main():
    # 1. Initialisation du robot
    ep_robot = robot.Robot()
    # Selon votre configuration :
    # - "sta" si le robot est connecté en Wi-Fi (station mode)
    # - "ap" si le robot est en mode point d'accès
    # - "rndis" si vous êtes en USB
    ep_robot.initialize()

    # 2. Initialisation de la caméra
    ep_camera = ep_robot.camera
    ep_camera.start_video_stream(display=False)
   
    # - display=False => on n’affiche pas la fenêtre interne du SDK
    # - vous pouvez adapter la résolution (360p, 480p, 720p, 1080p) et le fps

    # 3. Chargement de la base de visages
    known_face_encodings, known_face_names = load_known_faces()
    print("Visages déjà connus :", known_face_names)
    print("Appuyez sur 'r' pour enregistrer un visage, 'q' pour quitter.")

    try:
        while True:
            # 4. Lecture de l'image depuis la caméra du robot
            frame = ep_camera.read_cv2_image(strategy="newest")
            if frame is None:
                # Parfois, read_cv2_image() peut renvoyer None si le flux est indisponible
                continue
            time.sleep(0.03)

            # 5. Conversion BGR -> RGB pour face_recognition
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # 6. Détection des visages + extraction des encodages
            face_locations = face_recognition.face_locations(rgb_frame)
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

            # 7. Comparaison avec les visages connus
            for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                name = "Inconnu"

                if known_face_encodings:
                    matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.5)
                    face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                    best_match_index = np.argmin(face_distances)
                    if matches[best_match_index]:
                        name = known_face_names[best_match_index]

                # Dessiner le rectangle + nom
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

            # 8. Affichage dans une fenêtre OpenCV
            cv2.imshow("RoboMaster Face Recognition", frame)

            # 9. Gestion des touches
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                # Quitter la boucle
                break
            elif key == ord('r'):
                # Enregistrer le premier visage détecté
                if face_encodings:
                    print("Visage détecté. Saisissez le nom pour ce visage :")
                    nom = input("Nom : ")
                    known_face_encodings.append(face_encodings[0])
                    known_face_names.append(nom)
                    save_known_faces(known_face_encodings, known_face_names)
                    print(f"Visage de {nom} enregistré.")
                else:
                    print("Aucun visage détecté pour l'enregistrement.")

        # 10. Nettoyage
        cv2.destroyAllWindows()

    finally:
        # Arrêter le flux vidéo et fermer la connexion
        ep_camera.stop_video_stream()
        ep_robot.close()

if __name__ == "__main__":
    main()
