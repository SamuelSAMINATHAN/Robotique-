import cv2
import robomaster
from robomaster import robot
from robomaster import vision


class RobotInfo:
    """
    Classe pour représenter les informations d'un robot détecté.
    - x, y : coordonnées du centre.
    - w, h : largeur et hauteur.
    """
    def __init__(self, x, y, w, h):
        self._x = x
        self._y = y
        self._w = w
        self._h = h

    @property
    def pt1(self):
        return int((self._x - self._w / 2) * 1280), int((self._y - self._h / 2) * 720)

    @property
    def pt2(self):
        return int((self._x + self._w / 2) * 1280), int((self._y + self._h / 2) * 720)

    @property
    def center(self):
        return int(self._x * 1280), int(self._y * 720)


robots = []


def on_detect_person(person_info):
    """
    Callback appelé lorsqu'un robot est détecté.
    - person_info : liste des coordonnées des robots détectés.
    """
    number = len(person_info)
    robots.clear()
    for i in range(0, number):
        x, y, w, h = person_info[i]
        robots.append(RobotInfo(x, y, w, h))
        print("robot: x:{0}, y:{1}, w:{2}, h:{3}".format(x, y, w, h))


if __name__ == '__main__':
    ep_robot = robot.Robot()
    ep_robot.initialize()

    ep_vision = ep_robot.vision
    ep_camera = ep_robot.camera

    ep_camera.start_video_stream(display=False)
    result = ep_vision.sub_detect_info(name="robot", callback=on_detect_person)

    for i in range(0, 500):
        img = ep_camera.read_cv2_image(strategy="newest", timeout=0.5)
        for j in range(0, len(robots)):
            cv2.rectangle(img, robots[j].pt1, robots[j].pt2, (255, 255, 255))  # Dessine un rectangle autour du robot
        cv2.imshow("robots", img)
        cv2.waitKey(1)

    # Libération des ressources
    result = ep_vision.unsub_detect_info(name="robot")
    ep_camera.stop_video_stream()
    ep_robot.close()
    cv2.destroyAllWindows()
