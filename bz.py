import board  # type: ignore
import digitalio  # type: ignore
import spidev  # type: ignore
import adafruit_matrixkeypad  # type: ignore
import time
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import sh1106
from gpiozero import Button, Servo, RGBLED


class bzLock:
    def __init__(self):
        self.display = None
        self.numpad = None
        self.spi = None
        self.blue_button = Button(17)
        self.green_button = Button(27)
        self.red_button = Button(22)
        self.servo = Servo(4)
        self.led = RGBLED(red=25, green=24, blue=23)
        self.unlock()

    def setup_display(self):
        try:
            self.display = sh1106(i2c(port=1, address=0x3C))
            self.clear_display()
            return True
        except OSError:
            self.display = None
            print("Display is not connected")
            return False

    def clear_display(self):
        if self.display:
            self.display.clear()
        else:
            print("Display has not been set up")

    def text_to_display(self, text, xy=(0, 0), font=None):
        if self.display:
            with canvas(self.display) as draw:
                draw.text(xy, text, fill="white", font=font)
        else:
            print("Display has not been set up")

    def setup_numpad(self):
        cols = [digitalio.DigitalInOut(x)
                for x in (board.D26, board.D20, board.D21)]
        rows = [digitalio.DigitalInOut(x) for x in (
            board.D5, board.D6, board.D13, board.D19)]
        keys = (('1', '2', '3'), ('4', '5', '6'),
                ('7', '8', '9'), ('*', '0', '#'))
        self.numpad = adafruit_matrixkeypad.Matrix_Keypad(rows, cols, keys)

    def read_numpad(self):
        if self.numpad:
            keys = self.numpad.pressed_keys
            if keys:
                time.sleep(0.5)  # Debounce
                return keys[0]
            else:
                return None
        else:
            print("Numpad has not been set up")

    def lock(self):
        self.servo.min()

    def unlock(self):
        self.servo.max()

    def setup_spi(self):
        self.spi = spidev.SpiDev()
        self.spi.open(0, 0)
        self.spi.mode = 0b01
        self.spi.max_speed_hz = 1200000

    def detect_phone(self):
        readBytes = self.spi.xfer2(  # type: ignore
            [0b00000001, 0b10000000, 0x00])
        digitalValue = (((readBytes[1] & 0b11) << 8) | readBytes[2])
        if digitalValue > 200:
            return True
        return False

    def red_led(self):
        self.led.color = (1, 0, 0)

    def green_led(self):
        self.led.color = (0, 1, 0)

    def blue_led(self):
        self.led.color = (0, 0, 1)

    def yellow_led(self):
        self.led.color = (0.5, 1, 0)

    def off_led(self):
        self.led.color = (0, 0, 0)
