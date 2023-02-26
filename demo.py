import bz
import time

# load_cell_setup()
# fsr_detect_phone()
# fsr_adc_detect_phone()
# load_cell_get_weight()
# load_cell_shut_down()

while (1):
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

    bz.setup_display()
    bz.text_to_display("text")
    time.sleep(2)
    bz.clear_display()
    time.sleep(2)
