import cv2
import time
import json
from robomaster import robot, vision


class MarkerInfo:
    def __init__(self, x, y, w, h, info):
        self._x = x
        self._y = y
        self._w = w
        self._h = h
        self._info = info

    @property
    def pt1(self):
        return int((self._x - self._w / 2) * 1280), int((self._y - self._h / 2) * 720)

    @property
    def pt2(self):
        return int((self._x + self._w / 2) * 1280), int((self._y + self._h / 2) * 720)

    @property
    def center(self):
        return int(self._x * 1280), int(self._y * 720)

    @property
    def width(self):
        return self._w  # utile pour évaluer distance

    @property
    def text(self):
        return self._info


markers = []
tracking_started = False
last_dx = 0
tracking_errors = []


def on_detect_marker(marker_info):
    markers.clear()
    for x, y, w, h, info in marker_info:
        markers.append(MarkerInfo(x, y, w, h, info))


def track_marker(target: MarkerInfo, chassis):
    global tracking_started, last_dx

    frame_center_x = 1280 // 2
    target_cx, _ = target.center
    dx = target_cx - frame_center_x
    last_dx = dx

    bbox_w = target.width  # Normalisé [0, 1] par DJI SDK

    tracking_errors.append({
        "dx": dx,
        "bbox_width": bbox_w,
        "timestamp": time.time()
    })

    # 1. Rotation pour se centrer
    deadzone_px = 50
    if abs(dx) > deadzone_px:
        speed_z = dx * 0.1
        speed_z = max(min(speed_z, 30), -30)
        chassis.drive_speed(x=0, y=0, z=speed_z)
        return

    # 2. Quand centré : avance jusqu'à être proche
    # Plus le marker est large, plus il est proche
    desired_width = 0.18   # largeur idéale du marker pour l'atteindre
    min_width = 0.20       # ne pas dépasser cette largeur (trop proche)

    if bbox_w < desired_width:
        # Avancer doucement
        speed_x = (desired_width - bbox_w) * 2.0
        speed_x = max(min(speed_x, 0.4), 0)
        chassis.drive_speed(x=speed_x, y=0, z=0)
    else:
        # Stop si trop près
        chassis.drive_speed(x=0, y=0, z=0)


def search_for_marker(chassis, last_dx):
    direction = 15 if last_dx > 0 else -15
    chassis.drive_speed(x=0, y=0, z=direction)


if __name__ == '__main__':
    ep_robot = robot.Robot()
    ep_robot.initialize()

    ep_chassis = ep_robot.chassis
    ep_camera = ep_robot.camera
    ep_vision = ep_robot.vision

    ep_camera.start_video_stream(display=False)
    ep_vision.sub_detect_info(name="marker", callback=on_detect_marker)

    try:
        while True:
            img = ep_camera.read_cv2_image(strategy="newest", timeout=0.5)

            if markers:
                target = markers[0]
                track_marker(target, ep_chassis)

                # Visuel
                cv2.rectangle(img, target.pt1, target.pt2, (0, 255, 0), 2)
                cv2.putText(img, f"Marker {target.text}", target.center, cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)
            else:
                search_for_marker(ep_chassis, last_dx)

            cv2.imshow("Marker Tracking (Approach & Align)", img)
            if cv2.waitKey(1) == 27:
                break

    finally:
        with open("marker_tracking_errors.json", "w") as f:
            json.dump(tracking_errors, f, indent=2)

        ep_vision.unsub_detect_info(name="marker")
        ep_camera.stop_video_stream()
        ep_robot.close()
        cv2.destroyAllWindows()
