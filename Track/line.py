import cv2
import time
import math
from robomaster import robot, vision


class PointInfo:
    def __init__(self, x, y, theta, c):
        self._x = x
        self._y = y
        self._theta = theta
        self._c = c

    @property
    def pt(self):
        return int(self._x * 1280), int(self._y * 720)

    @property
    def raw(self):
        return self._x, self._y

    @property
    def angle_deg(self):
        return math.degrees(self._theta)

    @property
    def color(self):
        return 255, 255, 255


line_points = []
last_dx = 0


def on_detect_line(line_info):
    number = len(line_info)
    line_points.clear()
    line_type = line_info[0]
    for i in range(1, number):
        x, y, theta, c = line_info[i]
        line_points.append(PointInfo(x, y, theta, c))


def track_line(chassis, point: PointInfo):
    global last_dx

    center_x = 1280 // 2
    px, py = point.pt
    dx = px - center_x
    last_dx = dx

    theta = point._theta  # radians

    # Vitesse de rotation avec orientation
    speed_z = -dx * 0.1 + theta * 50

    # Vitesse avant
    deadzone_px = 40
    speed_x = 0.35 if abs(dx) < deadzone_px else 0.25

    speed_z = max(min(speed_z, 30), -30)
    speed_x = max(min(speed_x, 0.5), -0.5)

    chassis.drive_speed(x=speed_x, y=0, z=speed_z)
    return dx, theta


def search_for_line(chassis, last_dx):
    direction = 15 if last_dx > 0 else -15
    chassis.drive_speed(x=0, y=0, z=direction)


if __name__ == '__main__':
    # 🟦 Choix de la couleur
    supported_colors = ["red", "green", "blue", "white", "black"]
    line_color = input(f"Quelle couleur de ligne veux-tu suivre ? {supported_colors} : ").strip().lower()

    if line_color not in supported_colors:
        print(f"Couleur '{line_color}' non prise en charge. Utilise : {supported_colors}")
        exit()

    ep_robot = robot.Robot()
    ep_robot.initialize()

    ep_chassis = ep_robot.chassis
    ep_camera = ep_robot.camera
    ep_vision = ep_robot.vision

    ep_camera.start_video_stream(display=False)
    ep_vision.sub_detect_info(name="line", color=line_color, callback=on_detect_line)

    try:
        while True:
            img = ep_camera.read_cv2_image(strategy="newest", timeout=0.5)

            if line_points:
                lowest_point = max(line_points, key=lambda p: p.pt[1])
                dx, theta = track_line(ep_chassis, lowest_point)

                # Affichage visuel
                cv2.circle(img, lowest_point.pt, 6, (0, 255, 0), -1)
                center_x = 1280 // 2
                cv2.line(img, (center_x, 0), (center_x, 720), (100, 100, 100), 1)

                cv2.putText(img, f"dx: {dx:.1f} px", (20, 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                cv2.putText(img, f"theta: {lowest_point.angle_deg:.1f}°", (20, 70),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 255), 2)
            else:
                search_for_line(ep_chassis, last_dx)

            cv2.imshow(f"Line Following ({line_color})", img)
            if cv2.waitKey(1) == 27:
                break

    finally:
        ep_vision.unsub_detect_info(name="line")
        ep_camera.stop_video_stream()
        ep_robot.close()
        cv2.destroyAllWindows()
