import datetime
import math
import threading
import time
from queue import LifoQueue

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
    elif state == "focus_timer":
        if not remaining_focus_time.empty():
            timer = remaining_focus_time.get()
            remaining_focus_time.put(timer)
            mins, secs = divmod(timer, 60)
            timer = "{:02d}:{:02d}".format(mins, secs)
            with DISPLAY_LOCK:
                with canvas(bz.display) as draw:
                    draw.text((0, 0), timer, fill="white", font=ImageFont.truetype(
                        "IBMPlexMono-Regular.ttf", size=44))
        else:
            print("timer queue empty")
    elif state == "rest_timer":
        if not remaining_rest_time.empty():
            timer = remaining_rest_time.get()
            remaining_rest_time.put(timer)
            mins, secs = divmod(timer, 60)
            timer = "{:02d}:{:02d}".format(mins, secs)
            with DISPLAY_LOCK:
                with canvas(bz.display) as draw:
                    draw.text((0, 0), timer, fill="white", font=ImageFont.truetype(
                        "IBMPlexMono-Regular.ttf", size=44))
        else:
            print("timer queue empty")

    threading.Timer(0.01, update_display).start()


def countdown_timer(num, queue):
    if num == 0:
        queue.put(num)
        return
    queue.put(num)
    threading.Timer(1, countdown_timer, args=[num-1, queue]).start()


def switch_states():
    global state
    while True:
        if bz.button1.is_pressed:
            state = "focus_timer"
            countdown_timer(1500, remaining_focus_time)
        elif bz.button2.is_pressed:
            state = "rest_timer"
            countdown_timer(300, remaining_rest_time)
        elif bz.button3.is_pressed:
            state = "sleeping"


states = ["sleeping", "focus_timer", "rest_timer", "setting"]
state = states[0]

last_time = "Unknown"
remaining_focus_time = LifoQueue(maxsize=1)
remaining_rest_time = LifoQueue(maxsize=1)

update_display()
threading.Thread(target=switch_states).start()
