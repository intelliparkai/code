from motor import Motor
from lane import calc_lane_curve
import camera

motor = Motor(2, 3, 4, 17, 22, 27)


def main():
    image = camera.get_frame()
    curve = calc_lane_curve(image, 1)

    sensitivity = 1.3
    max_value = 0.3
    if curve > max_value:
        curve = max_value
    if curve < -max_value:
        curve = -max_value
    if curve > 0:
        sensitivity = 1.7
        if curve < 0.05:
            curve = 0
    else:
        if curve > -0.08:
            curve = 0
    motor.move(0.20, -curve * sensitivity, 0.05)


if __name__ == "__main__":
    while True:
        main()
