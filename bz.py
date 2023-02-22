import time
import RPi.GPIO as GPIO
import spidev
from hx711 import HX711
import digitalio
import board
import adafruit_matrixkeypad

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
    else:
        return False

def load_cell_shut_down():
    hx.power_down()

def get_numpad_input():
    cols = [digitalio.DigitalInOut(x) for x in (board.D26, board.D20, board.D21)]
    rows = [digitalio.DigitalInOut(x) for x in (board.D5, board.D6, board.D13, board.D19)]
    keys = ((1, 2, 3), (4, 5, 6), (7, 8, 9), ("*", 0, "#"))
    keypad = adafruit_matrixkeypad.Matrix_Keypad(rows, cols, keys)

    while True:
        keys = keypad.pressed_keys
        if keys:
            print("Pressed: ", keys)
            return keys

def update_display():
    pass

def clear_display():
    pass

def position_servo(angle):
    #on = (angle/180) + 1
    #duty = on/20
    pi.hardware_PWM(12, 59, (angle/180)*1000000)