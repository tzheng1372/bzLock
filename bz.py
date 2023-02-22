import board
import busio
import digitalio
import spidev
import smbus
import time

from hx711 import HX711
from PIL import Image, ImageDraw, ImageFont

import RPi.GPIO as GPIO
import adafruit_matrixkeypad
import adafruit_ssd1306

# OLED specs
OLED_WIDTH = 128
OLED_HEIGHT = 64
OLED_ADDRESS = 0x3C
OLED_REGADDR = 0x00
OLED_DISPOFF = 0xAE
OLED_DISPON  = 0xAF

# Initialize smbus and I2C library busio
bus = smbus.SMBus(1)
i2c = busio.I2C(board.SCL, board.SDA)
oled = adafruit_ssd1306.SSD1306_I2C(OLED_WIDTH, OLED_HEIGHT, i2c, addr=OLED_ADDRESS)

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
    else:
        return False

def load_cell_get_weight():
    hx.power_up()
    hx.zero()
    if hx._ready():
        weight = hx.get_weight_mean()
    return weight
    
def load_cell_detect_phone():
    if hx._ready():
        weight = hx.get_weight_mean()
    if weight > 0:
        return True
    else:
        return False

def numpad_get_input():
    cols = [digitalio.DigitalInOut(x) for x in (board.D26, board.D20, board.D21)]
    rows = [digitalio.DigitalInOut(x) for x in (board.D5, board.D6, board.D13, board.D19)]
    keys = ((1, 2, 3), (4, 5, 6), (7, 8, 9), ("*", 0, "#"))
    keypad = adafruit_matrixkeypad.Matrix_Keypad(rows, cols, keys)

    while True:
        keys = keypad.pressed_keys
        if keys:
            print("Pressed: ", keys)
            return keys[0]

def oled_update(text):
    # Graphics stuff - create a canvas to draw/write on
    image = Image.new("1", (oled.width, oled.height))
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()

    # Draw a rectangle with no fill, ten pixels thick
    draw.rectangle((0, 0, oled.width-1, oled.height-1), outline=10, fill=0)

    # Draw some text
    (font_width, font_height) = font.getsize(text)
    draw.text( # position text in center
        (oled.width // 2 - font_width // 2, oled.height // 2 - font_height // 2),  
        text,
        font=font,
        fill=255,
    )

    # Display image
    oled.image(image)
    oled.show()

def oled_off():
    bus.write_byte_data(OLED_ADDRESS, OLED_REGADDR, OLED_DISPOFF)

def oled_on():
    bus.write_byte_data(OLED_ADDRESS, OLED_REGADDR, OLED_DISPON)

def position_servo(angle):
    pass
