import bz
import time

# load_cell_setup()
# fsr_detect_phone()
# fsr_adc_detect_phone()
# load_cell_get_weight()
# load_cell_shut_down()

bz = bz.bzLock()

while (1):
    print("enter 4 digits:")
    a = bz.read_numpad()
    b = bz.read_numpad()
    c = bz.read_numpad()
    d = bz.read_numpad()
    print(a, b, c, d)

    bz.text_to_display("text")
    time.sleep(3)
    bz.clear_display()
    time.sleep(3)

    bz.position_servo(0)
