from bz import bzLock
from time import sleep

bz = bzLock()
bz.setup_display()
bz.setup_numpad()
bz.setup_spi()
sleep(1)

bz.lock()
sleep(1)

bz.text_to_display("text")
sleep(1)

bz.clear_display()
sleep(1)

while True:
    key = bz.read_numpad()
    if key:
        print(key)

    sleep(0.1)
