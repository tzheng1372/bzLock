import bz
import time
import spidev
from hx711 import HX711

"""
ADC_Start = 0b00000001
ADC_CH0 = 0b10000000
FSR_pin = 23
spi = spidev.SpiDev()
spi.open(0,0)
spi.mode = 0b00
spi.max_speed_hz = 1200000

hx = HX711(dout_pin = 5, pd_sck_pin = 6)
"""

while(1):
    print("enter 4 digits:")
    a = bz.numpad_get_input()
    time.sleep(0.3)
    b = bz.numpad_get_input()
    time.sleep(0.3)
    c = bz.numpad_get_input()
    time.sleep(0.3)
    d = bz.numpad_get_input()
    time.sleep(0.3)
    print(a, b, c, d)

    print("screen is off")
    bz.oled_off()
    time.sleep(1)
    print("screen is on")
    bz.oled_on()
    time.sleep(1)
    print("type something to show on display:")
    bz.oled_update(input())
    time.sleep(0.3)
