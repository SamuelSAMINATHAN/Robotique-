import cv2
import numpy as np
from robomaster import robot

print("Appuie sur 'q' pour quitter.")

# === Initialisation du robot et de la caméra ===
ep_robot = robot.Robot()
ep_robot.initialize(conn_type="sta")  # 'sta' pour mode Wi-Fi station ; adapter si nécessaire
ep_camera = ep_robot.camera
ep_camera.start_video_stream(display=False, resolution='720p', fps=30)

while True:
    # Lire l'image depuis la caméra du robot
    frame = ep_camera.read_cv2_image()
    if frame is None:
        continue

    display = frame.copy()
    h, w = frame.shape[:2]

    # Zone centrale (ici, 50% de la taille minimale de l'image)
    size = int(min(h, w) * 0.5)
    x = (w - size) // 2
    y = (h - size) // 2
    roi = frame[y:y + size, x:x + size]

    # Conversion de la zone d'intérêt en HSV et extraction de la teinte
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    hue = hsv[:, :, 0]

    # Calcul de la moyenne des teintes
    avg_hue = int(np.mean(hue))

    # Détermination simple de la couleur dominante en fonction de l'hue moyen
    if avg_hue < 10 or avg_hue > 160:
        color_name = "Rouge"
        color = (0, 0, 255)
    elif 10 < avg_hue <= 25:
        color_name = "Orange"
        color = (0, 128, 255)
    elif 25 < avg_hue <= 35:
        color_name = "Jaune"
        color = (0, 255, 255)
    elif 35 < avg_hue <= 85:
        color_name = "Vert"
        color = (0, 255, 0)
    elif 85 < avg_hue <= 130:
        color_name = "Bleu"
        color = (255, 0, 0)
    elif 130 < avg_hue <= 160:
        color_name = "Violet"
        color = (255, 0, 255)
    else:
        color_name = "Inconnu"
        color = (255, 255, 255)

    # Affichage de la zone centrale avec le rectangle et l'information de couleur
    cv2.rectangle(display, (x, y), (x + size, y + size), color, 2)
    cv2.putText(display, f"Couleur dominante : {color_name} (hue={avg_hue})",
                (x + 5, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    cv2.imshow("Couleur dominante (centre)", display)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Libération des ressources
ep_camera.stop_video_stream()
ep_robot.close()
cv2.destroyAllWindows()
