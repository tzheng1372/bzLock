def info():  
    '''Prints a basic library description'''
    print("Software library for the bzLock project.")

import RPi.GPIO as GPIO
import spidev
from hx711 import HX711

ADC_Start = 0b00000001
ADC_CH0 = 0b10000000


def callback_fn(FSR_pin):
    print("phone detected")

def detect_phone():
    GPIO.setmode(GPIO.BCM)
    FSR_pin = 23

    GPIO.setup(FSR_pin, GPIO.IN)
    GPIO.add_event_detect(FSR_pin, GPIO.RISING, callback = callback_fn)

def get_weight():
    spi = spidev.SpiDev()
    spi.open(0,0)
    spi.mode = 0b00
    spi.max_speed_hz = 1200000
    readBytes = spi.xfer2([ADC_Start, ADC_CH0, 0x00])
    digitalValue = (((readBytes[1] & 0b11) << 8) | readBytes[2])
    print(format(readBytes[2], '#010b'), format(readBytes[1], '#010b'), format(readBytes[0], '#010b'))
    print(digitalValue)

hx = HX711(dout_pin = 5, pd_sck_pin = 6)

def get_weight():
    pass

def detect_phone():
    pass