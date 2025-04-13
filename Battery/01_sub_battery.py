import time
from robomaster import robot


def sub_info_handler(batter_info):
    percent = batter_info
    print("Battery: {0}%.".format(percent))


if __name__ == '__main__':
    ep_robot = robot.Robot()
    ep_robot.initialize()

    ep_battery = ep_robot.battery

    ep_battery.sub_battery_info(5, sub_info_handler)
    time.sleep(10)
    ep_battery.unsub_battery_info()

    ep_robot.close()