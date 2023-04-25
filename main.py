import datetime
import math
import threading
import time

from queue import LifoQueue
from PIL import ImageFont
from luma.core.render import canvas

from bz import bzLock


stop_timer = threading.Event()


def posn(angle, arm_length):
    dx = int(math.cos(math.radians(angle)) * arm_length)
    dy = int(math.sin(math.radians(angle)) * arm_length)
    return (dx, dy)


def draw_clock(draw):
    now = datetime.datetime.now()
    today_date = now.strftime("%b/%d/%y")
    today_time = now.strftime("%H:%M:%S")
    margin = 4

    cx = 30
    cy = 32

    left = cx - cy
    right = cx + cy

    hrs_angle = 270 + (30 * (now.hour + (now.minute / 60.0)))
    hrs = posn(hrs_angle, cy - margin - 7)

    min_angle = 270 + (6 * now.minute)
    mins = posn(min_angle, cy - margin - 2)

    sec_angle = 270 + (6 * now.second)
    secs = posn(sec_angle, cy - margin - 2)

    draw.ellipse((left + margin, margin, right -
                 margin, 64 - margin), outline="white")
    draw.line((cx, cy, cx + hrs[0], cy + hrs[1]), fill="white")
    draw.line((cx, cy, cx + mins[0], cy + mins[1]), fill="white")
    draw.line((cx, cy, cx + secs[0], cy + secs[1]), fill="red")
    draw.ellipse((cx - 2, cy - 2, cx + 2, cy + 2),
                 fill="white", outline="white")
    draw.text((2 * (cx + margin), cy - 8), today_date, fill="yellow")
    draw.text((2 * (cx + margin), cy), today_time, fill="yellow")


def update_display():
    mins, secs = (0, 0)
    global clock

    while True:
        if clock:
            with DISPLAY_LOCK:
                with canvas(bz.display) as draw:
                    draw_clock(draw)
        # elif state in ["focus_timer", "rest_timer"]:
        else:
            with DISPLAY_LOCK:
                with canvas(bz.display) as draw:
                    if not remaining_time_queue.empty():
                        with REMAINING_TIME_LOCK:
                            mins, secs = remaining_time_queue.get()
                    timer = f"{mins:02d}:{secs:02d}"
                    draw.text((0, 0), timer, fill="white", font=ImageFont.truetype(
                        "IBMPlexMono-Regular.ttf", size=44))
        time.sleep(0.1)


def switch_states():
    while True:
        global state
        global stop_timer
        global clock

        if bz.button1.is_pressed:
            state = "focus_timer"
            print("state = focus_timer")
            stop_timer.set()
        elif bz.button2.is_pressed:
            state = "rest_timer"
            print("state = rest_timer")
            stop_timer.set()
        elif bz.button3.is_pressed:
            clock = not clock
            print("clock = not clock")
        time.sleep(0.3)


def timer(seconds):
    global stop_timer
    start_time = time.perf_counter()
    end_time = start_time + seconds

    while time.perf_counter() < end_time and not stop_timer.is_set():
        remaining_time = end_time - time.perf_counter()
        mins, secs = divmod(int(remaining_time), 60)
        timer = '{:02d}:{:02d}'.format(mins, secs)
        print(timer, end="\r")
        with REMAINING_TIME_LOCK:
            remaining_time_queue.put((mins, secs))
        time.sleep(0.1)

    if not stop_timer.is_set():
        print("\nTime's up!")
        return False
    return True


def run_timer(seconds):
    global stop_timer
    while True:
        stop_timer.clear()
        timer_thread = threading.Thread(target=timer, args=(seconds,))

        timer_thread.start()

        timer_thread.join()

        timer_reset = timer(seconds)
        if timer_reset:
            print("Resetting timer...")
        else:
            break


bz = bzLock()
bz.setup_display()
bz.setup_numpad()

states = ["focus_timer", "rest_timer", "setting"]
state = states[0]
clock = True

DISPLAY_LOCK = threading.Lock()
REMAINING_TIME_LOCK = threading.Lock()

remaining_time_queue = LifoQueue(maxsize=10)


run_display_thread = threading.Thread(target=update_display)
run_switch_thread = threading.Thread(target=switch_states)
run_timer_thread = threading.Thread(target=run_timer, args=(10,))


run_display_thread.start()
run_switch_thread.start()
run_timer_thread.start()

run_timer_thread.join()
