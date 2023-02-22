import board
import digitalio
import pigpio
import RPi.GPIO as GPIO
import spidev

from hx711 import HX711
import adafruit_matrixkeypad

from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import sh1106

# Initialize OLED
serial = i2c(port=1, address=0x3C)
device = sh1106(serial)

# Initialize FSR
ADC_Start = 0b00000001
ADC_CH0 = 0b10000000
FSR_pin = 23
spi = spidev.SpiDev()
spi.open(0,0)
spi.mode = 0b00
spi.max_speed_hz = 1200000

# Initialize LC
hx = HX711(dout_pin = 17, pd_sck_pin = 27)

# Initialize servo motor
pwm_pin = 12
pi = pigpio.pi()

def callback_fn(FSR_pin):
    return True

def fsr_detect_phone():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(FSR_pin, GPIO.IN)
    GPIO.add_event_detect(FSR_pin, GPIO.RISING, callback = callback_fn)

def fsr_adc_detect_phone():
    readBytes = spi.xfer2([ADC_Start, ADC_CH0, 0x00])
    digitalValue = (((readBytes[1] & 0b11) << 8) | readBytes[2])
    print(format(readBytes[2], '#010b'), format(readBytes[1], '#010b'), format(readBytes[0], '#010b'))
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

def numpad_get_input():
    cols = [digitalio.DigitalInOut(x) for x in (board.D26, board.D20, board.D21)]
    rows = [digitalio.DigitalInOut(x) for x in (board.D5, board.D6, board.D13, board.D19)]
    keys = ((1, 2, 3), (4, 5, 6), (7, 8, 9), ("*", 0, "#"))
    keypad = adafruit_matrixkeypad.Matrix_Keypad(rows, cols, keys)

    while True:
        keys = keypad.pressed_keys
        if keys:
            print("Pressed:", keys[0])
            return keys[0]

def oled_update(text):
    with canvas(device) as draw:
        draw.rectangle(device.bounding_box, outline="white", fill="black")
        draw.text((30, 40), text, fill="white")

def servo_position(angle):
    inc = int(angle * 100000 / 180)
    pi.hardware_PWM(pwm_pin, 50, 50000 + inc)
