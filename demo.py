import bz
import time
from PIL import ImageFont

# load_cell_setup()
# fsr_detect_phone()
# fsr_adc_detect_phone()
# load_cell_get_weight()
# load_cell_shut_down()

TIME = ImageFont.truetype("IBMPlexMono-Regular.ttf", size=44)

bz = bz.bzLock()
bz.setup_display()
bz.setup_numpad()
bz.position_servo(0)  # Unlock the box

while (1):
    print("enter 4 digits:")
    a = bz.read_numpad()
    b = bz.read_numpad()
    c = bz.read_numpad()
    d = bz.read_numpad()
    print("you entered:", a, b, c, d)
    time.sleep(3)

    print("showing time")
    bz.text_to_display("88:88", font=TIME)
    time.sleep(3)
    print("showing text")
    bz.text_to_display("showing text")
    time.sleep(3)
    print("clearing text")
    bz.clear_display()
    time.sleep(3)

    print("positioning servo")
    bz.position_servo(0)
    time.sleep(3)
