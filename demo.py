import bz
import time
import RPi.GPIO as GPIO
import spidev
from hx711 import HX711
import digitalio
import board
import adafruit_matrixkeypad

ADC_Start = 0b00000001
ADC_CH0 = 0b10000000
FSR_pin = 23
spi = spidev.SpiDev()
spi.open(0,0)
spi.mode = 0b00
spi.max_speed_hz = 1200000

hx = HX711(dout_pin = 5, pd_sck_pin = 6)
load_cell_setup()
fsr_detect_phone()
fsr_adc_detect_phone()
load_cell_get_weight()
load_cell_shut_down()