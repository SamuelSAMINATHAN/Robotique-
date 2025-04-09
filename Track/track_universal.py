import cv2
import time

def track_universal(target_detector, control_logic, chassis, camera_index=0, display=True):
    """
    Fonction de suivi universelle pour RoboMaster.
    - target_detector() doit retourner un dictionnaire contenant : {'x': ..., 'y': ..., 'w': ..., 'h': ...}
    - control_logic(target, chassis) applique la vitesse au robot à partir de la détection
    - chassis : instance du chassis du robot
    """
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

            target = target_detector(frame)

            if target:
                control_logic(target, chassis)

                # Affichage
                if display:
                    x, y, w, h = target["x"], target["y"], target["w"], target["h"]
                    x1, y1 = int(x - w / 2), int(y - h / 2)
                    x2, y2 = int(x + w / 2), int(y + h / 2)
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.circle(frame, (int(x), int(y)), 4, (0, 0, 255), -1)
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