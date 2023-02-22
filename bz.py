import board
import busio
import digitalio
import displayio
import terminalio
import time
import pigpio
import RPi.GPIO as GPIO
import spidev
import smbus

from hx711 import HX711
from adafruit_display_text import label
import adafruit_displayio_sh1106
import adafruit_matrixkeypad

# Initialize SPI for OLED
displayio.release_displays()

spi = busio.SPI(board.SCK, board.MOSI)
display_bus = displayio.FourWire(
    spi,
    command=board.OLED_DC,
    chip_select=board.OLED_CS,
    reset=board.OLED_RESET,
    baudrate=1000000,
)

WIDTH = 128
HEIGHT = 64
BORDER = 5
display = adafruit_displayio_sh1106.SH1106(display_bus, width=WIDTH, height=HEIGHT)

# Initialize servo motor
pwm_pin = 12
pi = pigpio.pi()

# Initialize FSR
ADC_Start = 0b00000001
ADC_CH0 = 0b10000000
FSR_pin = 23
spi = spidev.SpiDev()
spi.open(0,0)
spi.mode = 0b00
spi.max_speed_hz = 1200000

# Initialize LC
hx = HX711(dout_pin = 5, pd_sck_pin = 6)

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
    # Make the display context
    splash = displayio.Group()
    display.show(splash)

    color_bitmap = displayio.Bitmap(WIDTH, HEIGHT, 1)
    color_palette = displayio.Palette(1)
    color_palette[0] = 0xFFFFFF  # White

    bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
    splash.append(bg_sprite)

    # Draw a smaller inner rectangle
    inner_bitmap = displayio.Bitmap(WIDTH - BORDER * 2, HEIGHT - BORDER * 2, 1)
    inner_palette = displayio.Palette(1)
    inner_palette[0] = 0x000000  # Black
    inner_sprite = displayio.TileGrid(
        inner_bitmap, pixel_shader=inner_palette, x=BORDER, y=BORDER
    )
    splash.append(inner_sprite)

    # Draw a label
    text_area = label.Label(
        terminalio.FONT, text=text, color=0xFFFFFF, x=28, y=HEIGHT // 2 - 1
    )
    splash.append(text_area)

def servo_position(angle):
    inc = int(angle * 100000 / 180)
    pi.hardware_PWM(pwm_pin, 50, 50000 + inc)
