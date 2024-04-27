import cv2 as cv
import numpy as np
from typing import Any, Union


def threshold_image(image: np.ndarray) -> np.ndarray:
    """
    Apply thresholding operation to isolate white regions in an image.

    Args:
        image (numpy.ndarray): Input image in BGR format.

    Returns:
        numpy.ndarray: Binary mask representing the thresholded image.
    """
    hsv_image = cv.cvtColor(image, cv.COLOR_BGR2HSV)
    lower_white = np.array([80, 0, 0])
    upper_white = np.array([255, 160, 255])
    mask = cv.inRange(hsv_image, lower_white, upper_white)
    return mask


def warp_image(
    image: np.ndarray, points: np.float32, width: int, height: int, inv: bool = False
) -> np.ndarray:
    """
    Perform perspective transformation (warping) on an input image.

    Args:
        image (numpy.ndarray): Input image.
        points (numpy.ndarray): Coordinates of the four corners of the region of interest in the input image.
        width (int): Width of the output warped image.
        height (int): Height of the output warped image.
        inv (bool, optional): Boolean flag indicating whether to perform an inverse perspective transformation. Default is False.

    Returns:
        numpy.ndarray: Warped image.
    """
    points_1 = np.float32(points)
    points_2 = np.float32([[0, 0], [width, 0], [0, height], [width, height]])
    if inv:
        matrix = cv.getPerspectiveTransform(points_2, points_1)
    else:
        matrix = cv.getPerspectiveTransform(points_1, points_2)
    warped_image = cv.warpPerspective(image, matrix, (width, height))
    return warped_image


def void(arg: Any) -> None:
    """
    A placeholder function that does nothing.

    Args:
        arg (Any): Any input argument.

    Returns:
        None
    """
    pass


def init_trackbars(
    initial_values: np.float32, target_width: int = 480, target_height: int = 240
) -> None:
    """
    Initialize trackbars for adjusting perspective transformation parameters.

    Args:
        initial_values (numpy.ndarray): Initial values for trackbar positions.
        target_width (int, optional): Target width for the trackbars window. Default is 480.
        target_height (int, optional): Target height for the trackbars window. Default is 240.

    Returns:
        None
    """
    cv.namedWindow("Trackbars")
    cv.resizeWindow("Trackbars", 360, 240)
    cv.createTrackbar(
        "Width Top", "Trackbars", initial_values[0], target_width // 2, void
    )
    cv.createTrackbar("Height Top", "Trackbars", initial_values[1], target_height, void)
    cv.createTrackbar(
        "Width Bottom", "Trackbars", initial_values[2], target_width // 2, void
    )
    cv.createTrackbar(
        "Height Bottom", "Trackbars", initial_values[3], target_height, void
    )


def get_trackbars_value(
    target_width: int = 480, target_height: int = 240
) -> np.float32:
    """
    Get the current positions of the trackbars.

    Args:
        target_width (int, optional): Target width for the trackbars window. Default is 480.
        target_height (int, optional): Target height for the trackbars window. Default is 240.

    Returns:
        numpy.ndarray: Updated positions of the trackbars.
    """
    width_top = cv.getTrackbarPos("Width Top", "Trackbars")
    height_top = cv.getTrackbarPos("Height Top", "Trackbars")
    width_bottom = cv.getTrackbarPos("Width Bottom", "Trackbars")
    height_bottom = cv.getTrackbarPos("Height Bottom", "Trackbars")
    points = np.float32(
        [
            (width_top, height_top),
            (target_width - width_top, height_top),
            (width_bottom, height_bottom),
            (target_width - width_bottom, height_bottom),
        ]
    )
    return points


def draw_points(image: np.ndarray, points: np.float32) -> np.ndarray:
    """
    Draw points on an image.

    Args:
        image (numpy.ndarray): Input image.
        points (numpy.ndarray): Coordinates of points to be drawn.

    Returns:
        numpy.ndarray: Image with points drawn.
    """
    for x in range(4):
        cv.circle(
            image, (int(points[x][0]), int(points[x][1])), 15, (0, 0, 255), cv.FILLED
        )
    return image


def get_histogram(
    image, min_percentage: float = 0.1, display: bool = False, region: int = 1
) -> Union[float, np.ndarray, tuple]:
    """
    Calculate histogram of an image.

    Args:
        image: The input image.
        min_percentage (float, optional): Minimum percentage of the maximum histogram value for thresholding. Default is 0.1.
        display (bool, optional): Whether to display the histogram. Default is False.
        region (int, optional): Region of interest for histogram calculation. Default is 1.

    Returns:
        Union[float, np.ndarray, tuple]: Base point of the histogram or tuple containing the base point and the histogram image if display is True.
    """
    if region == 1:
        histogram_values = np.sum(image, axis=0)
    else:
        histogram_values = np.sum(image[image.shape[0] // region :, :], axis=0)

    max_value = np.max(histogram_values)
    min_value = min_percentage * max_value

    idx_array = np.where(histogram_values >= min_value)
    base_point = int(np.average(idx_array))

    if display:
        image_histogram = np.zeros((image.shape[0], image.shape[1], 3), np.uint8)
        for x, intensity in enumerate(histogram_values):
            cv.line(
                image_histogram,
                (x, image.shape[0]),
                (x, image.shape[0] - intensity // 255 // region),
                (255, 0, 255),
                1,
            )
            cv.circle(
                image_histogram,
                (base_point, image.shape[0]),
                20,
                (0, 255, 255),
                cv.FILLED,
            )
        return base_point, image_histogram

    return base_point


def stack_images(scale: int, image_array: np.ndarray) -> np.ndarray:
    """
    Stack images horizontally or vertically.

    Args:
        scale (int): Scaling factor for images.
        image_array (numpy.ndarray): Array of images to stack.

    Returns:
        numpy.ndarray: Stacked image.
    """
    rows = len(image_array)
    cols = len(image_array[0])
    rows_available = isinstance(image_array[0], list)
    width = image_array[0][0].shape[1]
    height = image_array[0][0].shape[0]
    if rows_available:
        for x in range(0, rows):
            for y in range(0, cols):
                if image_array[x][y].shape[:2] == image_array[0][0].shape[:2]:
                    image_array[x][y] = cv.resize(
                        image_array[x][y], (0, 0), None, scale, scale
                    )
                else:
                    image_array[x][y] = cv.resize(
                        image_array[x][y],
                        (image_array[0][0].shape[1], image_array[0][0].shape[0]),
                        None,
                        scale,
                        scale,
                    )
                if len(image_array[x][y].shape) == 2:
                    image_array[x][y] = cv.cvtColor(
                        image_array[x][y], cv.COLOR_GRAY2BGR
                    )
        blank_image = np.zeros((height, width, 3), np.uint8)
        hor = [blank_image] * rows
        hor_con = [blank_image] * rows
        for x in range(0, rows):
            hor[x] = np.hstack(image_array[x])
        ver = np.vstack(hor)
    else:
        for x in range(0, rows):
            if image_array[x].shape[:2] == image_array[0].shape[:2]:
                image_array[x] = cv.resize(image_array[x], (0, 0), None, scale, scale)
            else:
                image_array[x] = cv.resize(
                    image_array[x],
                    (image_array[0].shape[1], image_array[0].shape[0]),
                    None,
                    scale,
                    scale,
                )
            if len(image_array[x].shape) == 2:
                image_array[x] = cv.cvtColor(image_array[x], cv.COLOR_GRAY2BGR)
        hor = np.hstack(image_array)
        ver = hor
    return ver
