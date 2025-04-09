import cv2
import time
import json
from robomaster import robot, vision


class PersonInfo:
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


persons = []
tracking_errors = []
last_dx = 0
tracking_started = False


def on_detect_person(person_info):
    persons.clear()
    for x, y, w, h in person_info:
        persons.append(PersonInfo(x, y, w, h))


def track_person(target: PersonInfo, chassis):
    global last_dx, tracking_started

    frame_center = (1280 // 2, 720 // 2)
    target_center = target.center

    dx = target_center[0] - frame_center[0]
    dy = frame_center[1] - target_center[1]
    last_dx = dx

    tracking_errors.append({
        "dx": dx,
        "dy": dy,
        "timestamp": time.time()
    })

    # --- CENTRAGE INTELLIGENT ---
    deadzone_px = 80
    if not tracking_started:
        if abs(dx) < deadzone_px:
            tracking_started = True
        else:
            speed_z = dx * 0.1
            speed_z = max(min(speed_z, 30), -30)
            chassis.drive_speed(x=0, y=0, z=speed_z)
            return dx, dy

    # --- TRACKING FLUIDE ---
    Kp_x = 1 / 200.0
    Kp_y = 1 / 300.0
    Kp_z = -1 / 400.0

    speed_x = dy * Kp_x
    speed_y = dx * Kp_y
    speed_z = dx * Kp_z

    if abs(dx) < 20:
        speed_z = 0

    speed_x = max(min(speed_x, 0.4), -0.4)
    speed_y = max(min(speed_y, 0.4), -0.4)
    speed_z = max(min(speed_z, 30), -30)

    chassis.drive_speed(x=speed_x, y=speed_y, z=speed_z)
    return dx, dy


def search_for_person(chassis, last_dx):
    # Tourne dans la dernière direction connue
    direction = 15 if last_dx > 0 else -15
    chassis.drive_speed(x=0, y=0, z=direction)


if __name__ == '__main__':
    ep_robot = robot.Robot()
    ep_robot.initialize()

    ep_chassis = ep_robot.chassis
    ep_camera = ep_robot.camera
    ep_vision = ep_robot.vision

    ep_camera.start_video_stream(display=False)
    ep_vision.sub_detect_info(name="person", callback=on_detect_person)

    try:
        while True:
            img = ep_camera.read_cv2_image(strategy="newest", timeout=0.5)

            if persons:
                target = persons[0]
                dx, dy = track_person(target, ep_chassis)

                # Affichage visuel
                cv2.rectangle(img, target.pt1, target.pt2, (0, 255, 0), 2)
                center_img = (1280 // 2, 720 // 2)
                target_c = target.center
                cv2.line(img, center_img, target_c, (0, 0, 255), 2)
                cv2.circle(img, center_img, 5, (255, 0, 0), -1)

                # Affichage de la zone morte
                cv2.line(img, (center_img[0] - 80, 0), (center_img[0] - 80, 720), (100, 100, 100), 1)
                cv2.line(img, (center_img[0] + 80, 0), (center_img[0] + 80, 720), (100, 100, 100), 1)

                cv2.putText(img, f"dx: {dx} px | dy: {dy} px", (20, 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            else:
                tracking_started = False
                search_for_person(ep_chassis, last_dx)

            cv2.imshow("Person Tracking Final Test", img)
            if cv2.waitKey(1) == 27:
                break

    finally:
        with open("person_tracking_errors.json", "w") as f:
            json.dump(tracking_errors, f, indent=2)

        ep_vision.unsub_detect_info(name="person")
        ep_camera.stop_video_stream()
        ep_robot.close()
        cv2.destroyAllWindows()
