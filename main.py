import datetime
import math
import threading
import time
import queue

from PIL import ImageFont
from luma.core.render import canvas

from bz import bzLock


DISPLAY_LOCK = threading.Lock()

bz = bzLock()

bz.setup_display()
bz.setup_numpad()


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
    cy = 64 // 2
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
    global last_time
    if state == "sleeping":
        now = datetime.datetime.now()
        today_time = now.strftime("%H:%M:%S")
        if today_time != last_time:
            last_time = today_time
            with DISPLAY_LOCK:
                with canvas(bz.display) as draw:
                    draw_clock(draw)
    elif state in ["focus_timer", "rest_timer"]:
        mins, secs = divmod(remaining_time, 60)
        timer = "{:02d}:{:02d}".format(mins, secs)
        with DISPLAY_LOCK:
            with canvas(bz.display) as draw:
                draw.text((0, 0), timer, fill="white", font=ImageFont.truetype(
                    "IBMPlexMono-Regular.ttf", size=44))

    threading.Timer(0.1, update_display).start()


def countdown_timer(count):
    global remaining_time
    remaining_time = count
    while count > 0:
        print(count)
        count -= 1
        remaining_time = count
        time.sleep(1)
    print("Time's up!")


def switch_states():
    global state
    while True:
        if bz.button1.is_pressed:
            state = "focus_timer"
            start_focus_timer(1500)
        elif bz.button2.is_pressed:
            state = "rest_timer"
            start_rest_timer(300)
        elif bz.button3.is_pressed:
            state = "sleeping"


def start_focus_timer(num):
    global remaining_time_queue
    remaining_time_queue.put(num)
    print("Starting focus timer for {} seconds...".format(num))
    t = threading.Thread(target=focus_timer)
    t.start()


def start_rest_timer(num):
    global remaining_time_queue
    remaining_time_queue.put(num)
    print("Starting rest timer for {} seconds...".format(num))
    t = threading.Thread(target=rest_timer)
    t.start()


def focus_timer():
    global remaining_time_queue
    remaining_time = remaining_time_queue.get()
    while remaining_time > 0:
        print("Remaining time: {} seconds".format(remaining_time))
        time.sleep(1)
        remaining_time -= 1
    print("Focus timer ended.")


def rest_timer():
    global remaining_time_queue
    remaining_time = remaining_time_queue.get()
    while remaining_time > 0:
        print("Remaining time: {} seconds".format(remaining_time))
        time.sleep(1)
        remaining_time -= 1
    print("Rest timer ended.")


states = ["sleeping", "focus_timer", "rest_timer", "setting"]
state = states[0]

last_time = "Unknown"
remaining_time_queue = queue.Queue()

update_display()
threading.Thread(target=switch_states).start()
