from utils import *

curve_list = []
avg_value = 10


def calc_lane_curve(image, display: int = 2) -> float:
    """
    Calculate the lane curvature of a road image.

    Args:
        image (numpy.ndarray): Input road image.
        display (int, optional): Display mode.
            - 0: Do not display anything.
            - 1: Display the result image only.
            - 2: Display intermediate processing steps. Default is 2.

    Returns:
        float: Lane curvature value.
    """
    image_copy = image.copy()
    image_result = image.copy()
    thresholded_image = threshold_image(image)

    height, width, channels = image.shape
    points = get_trackbars_value()
    warped_image = warp_image(thresholded_image, points, width, height)
    warped_image_points = draw_points(image_copy, points)

    mid_point, image_histogram = get_histogram(
        warped_image, display=True, min_percentage=0.5, region=4
    )
    avg_curve_point, image_histogram = get_histogram(
        warped_image, display=True, min_percentage=0.9
    )
    raw_curve = avg_curve_point - mid_point

    curve_list.append(raw_curve)
    if len(curve_list) > avg_value:
        curve_list.pop(0)
    curve = int(sum(curve_list) / len(curve_list))

    if display != 0:
        inv_warped_image = warp_image(warped_image, points, width, height, inv=True)
        inv_warped_image = cv.cvtColor(inv_warped_image, cv.COLOR_GRAY2BGR)
        inv_warped_image[0 : height // 3, 0:width] = 0, 0, 0
        image_lane_color = np.zeros_like(image)
        image_lane_color[:] = 0, 255, 0
        image_lane_color = cv.bitwise_and(inv_warped_image, image_lane_color)
        image_result = cv.addWeighted(image_result, 1, image_lane_color, 1, 0)
        mid_y = 450
        cv.putText(
            image_result,
            str(curve),
            (width // 2 - 80, 85),
            cv.FONT_HERSHEY_COMPLEX,
            2,
            (255, 0, 255),
            3,
        )
        cv.line(
            image_result,
            (width // 2, mid_y),
            (width // 2 + (curve * 3), mid_y),
            (255, 0, 255),
            5,
        )
        cv.line(
            image_result,
            ((width // 2 + (curve * 3)), mid_y - 25),
            (width // 2 + (curve * 3), mid_y + 25),
            (0, 255, 0),
            5,
        )
        for x in range(-30, 30):
            w = width // 20
            cv.line(
                image_result,
                (w * x + int(curve // 50), mid_y - 10),
                (w * x + int(curve // 50), mid_y + 10),
                (0, 0, 255),
                2,
            )
    if display == 2:
        stacked_image = stack_images(
            0.7,
            (
                [image, warped_image_points, warped_image],
                [image_histogram, image_lane_color, image_result],
            ),
        )
        cv.imshow("Image Stack", stacked_image)
    elif display == 1:
        cv.imshow("Result", image_result)

    curve = curve / 100
    if curve > 1:
        curve == 1
    if curve < -1:
        curve == -1

    return curve


if __name__ == "__main__":
    cap = cv.VideoCapture("src/lane.mp4")
    init_trackbars([102, 80, 20, 214])

    while True:
        ret, image = cap.read()

        if not ret:
            cap.set(cv.CAP_PROP_POS_FRAMES, 0)
            continue

        image = cv.resize(image, (480, 240))
        curve = calc_lane_curve(image)
        print(curve)

        key = cv.waitKey(1)

        if key == ord("q") or key == 27:
            break

    cap.release()
    cv.destroyAllWindows()
