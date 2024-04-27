import cv2 as cv
from numpy import ndarray


class Camera:
    """A simple class for capturing frames from a webcam.

    This class provides static methods for capturing frames from a webcam,
    displaying frames, and capturing video until the user quits.
    """

    def __init__(self) -> None:
        """Initialize the Camera object with VideoCapture."""
        self.cap = cv.VideoCapture(0)

    @staticmethod
    def get_frame(dsize: tuple = (480, 240)) -> ndarray:
        """Capture a frame from the webcam and resize it.

        Args:
            dsize (tuple): Desired size for the captured frame.

        Returns:
            ndarray: The captured and resized frame.
        """
        _, frame = Camera().cap.read()
        frame = cv.resize(frame, dsize)
        return frame

    @staticmethod
    def show_frame(frame: ndarray, window_name: str = "Frame") -> None:
        """Display a frame in a window.

        Args:
            frame (ndarray): The frame to display.
            window_name (str): Name of the window to display the frame in.
        """
        cv.imshow(window_name, frame)
        cv.waitKey(1)  # Adjust the delay for frame display

    @staticmethod
    def capture(dsize: tuple = (480, 240)):
        """Capture and display video from the webcam until the user quits.

        Args:
            dsize (tuple): Desired size for the captured frame.
        """
        cam = Camera()

        while cam.cap.isOpened():
            _, frame = cam.cap.read()
            cv.imshow("Live", frame)

            key = cv.waitKey(1)
            if key == ord("q") or key == 27:  # 'q' or 'Esc' key to quit
                break

        cam.cap.release()  # Release the VideoCapture object when done
        cv.destroyAllWindows()  # Close all OpenCV windows


if __name__ == "__main__":
    Camera.capture()
