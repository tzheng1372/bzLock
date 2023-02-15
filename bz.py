def info():  
    '''Prints a basic library description'''
    print("Software library for the bzLock project.")

import RPi.GPIO as GPIO
import spidev
from hx711 import HX711

ADC_Start = 0b00000001
ADC_CH0 = 0b10000000
FSR_pin = 23
spi = spidev.SpiDev()
spi.open(0,0)
spi.mode = 0b00
spi.max_speed_hz = 1200000

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

hx = HX711(dout_pin = 5, pd_sck_pin = 6)

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