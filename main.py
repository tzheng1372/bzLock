import datetime
import math
from threading import Event, Lock, Thread
import time

from queue import LifoQueue
from PIL import ImageFont
from luma.core.render import canvas

from bz import bzLock


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

    while True:
        if state == "welcome":
            with display_lock:
                with canvas(bz.display) as draw:
                    text = "Blue for clock"
                    draw.text((0, 0), text, fill="white")
                    text = "Red for focus timer"
                    draw.text((0, 10), text, fill="white")
                    text = "Green for reset timer"
                    draw.text((0, 20), text, fill="white")

        elif state == "clock":
            with display_lock:
                with canvas(bz.display) as draw:
                    draw_clock(draw)

        else:
            with display_lock:
                with canvas(bz.display) as draw:
                    if not remaining_time_queue.empty():
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
            run_timer(1500)

        elif bz.button2.is_pressed:
            state = "rest_timer"
            run_timer(300)

        elif bz.button3.is_pressed:
            state = "clock"

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
        with remaining_time_lock:
            remaining_time_queue.put((mins, secs))
        time.sleep(0.1)

    if not stop_timer.is_set():
        print("\nTime's up!")


def run_timer(seconds):
    global stop_timer

    stop_timer.is_set()
    stop_timer.clear()
    timer_thread = Thread(target=timer, args=(seconds,))
    timer_thread.start()


bz = bzLock()
bz.setup_display()
bz.setup_numpad()

states = ["welcome", "clock", "focus_timer", "rest_timer", "setting"]
state = states[0]
clock = True

stop_timer = Event()

display_lock = Lock()
remaining_time_lock = Lock()

remaining_time_queue = LifoQueue(maxsize=10)

update_display_thread = Thread(target=update_display)
switch_states_thread = Thread(target=switch_states)

update_display_thread.start()
switch_states_thread.start()
