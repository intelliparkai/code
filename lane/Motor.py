import RPi.GPIO as GPIO
from time import sleep

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)


class Motor:
    """
    A class for controlling a dual motor driver board using Raspberry Pi GPIO.

    Attributes:
        enable_a (int): GPIO pin number for motor A enable.
        input_1_a (int): GPIO pin number for motor A input 1.
        input_2_a (int): GPIO pin number for motor A input 2.
        enable_b (int): GPIO pin number for motor B enable.
        input_1_b (int): GPIO pin number for motor B input 1.
        input_2_b (int): GPIO pin number for motor B input 2.
        pwm_a: PWM object for controlling motor A speed.
        pwm_b: PWM object for controlling motor B speed.
        speed (float): Current speed of the motors.
    """

    def __init__(
        self,
        enable_a: int,
        input_1_a: int,
        input_2_a: int,
        enable_b: int,
        input_1_b: int,
        input_2_b: int,
    ) -> None:
        """
        Initializes the Motor object with GPIO pin numbers.

        Args:
            enable_a (int): GPIO pin number for motor A enable.
            input_1_a (int): GPIO pin number for motor A input 1.
            input_2_a (int): GPIO pin number for motor A input 2.
            enable_b (int): GPIO pin number for motor B enable.
            input_1_b (int): GPIO pin number for motor B input 1.
            input_2_b (int): GPIO pin number for motor B input 2.
        """
        self.enable_a = enable_a
        self.input_1_a = input_1_a
        self.input_2_a = input_2_a
        self.enable_b = enable_b
        self.input_1_b = input_1_b
        self.input_2_b = input_2_b
        self._setup()
        self.pwm_a = GPIO.PWM(self.enable_a, 100)
        self.pwm_b = GPIO.PWM(self.enable_b, 100)
        self.pwm_a.start(0)
        self.pwm_b.start(0)
        self.speed = 0

    def _setup(self) -> None:
        """
        Configures GPIO pins as outputs.
        """
        GPIO.setup(self.enable_a, GPIO.OUT)
        GPIO.setup(self.input_1_a, GPIO.OUT)
        GPIO.setup(self.input_2_a, GPIO.OUT)
        GPIO.setup(self.enable_b, GPIO.OUT)
        GPIO.setup(self.input_1_b, GPIO.OUT)
        GPIO.setup(self.input_2_b, GPIO.OUT)

    def _digital_write(self, high: int, low: int) -> None:
        """
        Writes digital values to GPIO pins.

        Args:
            high (int): GPIO pin number for setting high.
            low (int): GPIO pin number for setting low.
        """
        GPIO.output(high, GPIO.HIGH)
        GPIO.output(low, GPIO.LOW)

    def move(self, speed: float = 0.5, turn: float = 0, delay: int = 0) -> None:
        """
        Controls the movement of the motors.

        Args:
            speed (float): Speed of the motors (-1 to 1, where 1 is maximum forward speed).
            turn (float): Turning ratio (-1 to 1, where -1 is maximum left turn).
            delay (int): Delay in seconds after movement (default is 0).
        """
        speed *= 100
        turn *= 70
        left_speed = speed - turn
        right_speed = speed + turn

        if left_speed > 100:
            left_speed = 100
        elif left_speed < -100:
            left_speed = -100
        if right_speed > 100:
            right_speed = 100
        elif right_speed < -100:
            right_speed = -100

        self.pwm_a.ChangeDutyCycle(abs(left_speed))
        self.pwm_b.ChangeDutyCycle(abs(right_speed))

        if left_speed > 0:
            self._digital_write(self.input_1_a, self.input_2_a)
        else:
            self._digital_write(self.input_2_a, self.input_1_a)

        if right_speed > 0:
            self._digital_write(self.input_1_b, self.input_2_b)
        else:
            self._digital_write(self.input_2_b, self.input_1_b)

        sleep(delay)

    def stop(self, delay: int = 0) -> None:
        """
        Stops the motors.

        Args:
            delay (int): Delay in seconds after stopping (default is 0).
        """
        self.pwm_a.ChangeDutyCycle(0)
        self.pwm_b.ChangeDutyCycle(0)
        self.speed = 0
        sleep(delay)
