import board
import digitalio
import pigpio
import time
import RPi.GPIO as GPIO
import spidev

import adafruit_matrixkeypad
from hx711 import HX711
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import sh1106
from PIL import ImageFont

FONT = ImageFont.truetype("IBMPlexMono-Regular.ttf", size=44)

# Initialize FSR
ADC_Start = 0b00000001
ADC_CH0 = 0b10000000
FSR_pin = 23
spi = spidev.SpiDev()
spi.open(0, 0)
spi.mode = 0b00
spi.max_speed_hz = 1200000

# Initialize LC
hx = HX711(dout_pin=17, pd_sck_pin=27)


def callback_fn(FSR_pin):
    return True


def fsr_detect_phone():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(FSR_pin, GPIO.IN)
    GPIO.add_event_detect(FSR_pin, GPIO.RISING, callback=callback_fn)


def fsr_adc_detect_phone():
    readBytes = spi.xfer2([ADC_Start, ADC_CH0, 0x00])
    digitalValue = (((readBytes[1] & 0b11) << 8) | readBytes[2])
    print(format(readBytes[2], '#010b'), format(
        readBytes[1], '#010b'), format(readBytes[0], '#010b'))
    print(digitalValue)
    if digitalValue > 0:
        return True
    return False


def load_cell_setup():
    hx.power_up()
    hx.zero()


def load_cell_get_weight():
    weight = hx.get_weight_mean()
    return weight


def load_cell_detect_phone():
    weight = hx.get_weight_mean()
    if weight > 0:
        return True
    return False


def load_cell_shut_down():
    hx.power_down()


class bzLock:
    def __init__(self):
        self.display = None
        self.numpad = None

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
            with canvas(self.display) as draw:
                draw.rectangle(self.display.bounding_box, fill="black")
        else:
            print("Display has not been set up")

    def text_to_display(self, text):
        if self.display:
            with canvas(self.display) as draw:
                self.clear_display()
                draw.text((0, 0), text, fill="white", font=FONT)
        else:
            print("Display has not been set up")

    def setup_numpad(self):
        cols = [digitalio.DigitalInOut(x)
                for x in (board.D26, board.D20, board.D21)]
        rows = [digitalio.DigitalInOut(x) for x in (
            board.D5, board.D6, board.D13, board.D19)]
        keys = (('1', '2', '3'), ('4', '5', '6'),
                ('7', '8', '9'), ('*', '0', '#'))
        try:
            self.numpad = adafruit_matrixkeypad.Matrix_Keypad(rows, cols, keys)
            return True
        except OSError:
            self.display = None
            print("Numpad is not connected")
            return False

    def read_numpad(self):
        if self.numpad:
            while True:
                keys = self.numpad.pressed_keys
                if keys:
                    time.sleep(0.3)
                    return keys[0]
        else:
            print("Numpad has not been set up")

    def position_servo(self, angle):
        pwm_pin = 12
        inc = int(angle * 100000 / 180)
        pigpio.pi().hardware_PWM(pwm_pin, 50, 50000 + inc)
