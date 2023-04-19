import datetime
import math
import threading
import time
import queue

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
    while True:
        with DISPLAY_LOCK:
            with canvas(bz.display) as draw:
                if state == "sleeping":
                    draw_clock(draw)
                elif state in ["focus_timer", "rest_timer"]:
                    with remaining_time_queue.mutex:  # Lock the queue to safely access the last element
                        if not remaining_time_queue.empty():
                            remaining_time = remaining_time_queue.queue[-1]
                            mins, secs = divmod(remaining_time, 60)
                            timer = f"{mins:02d}:{secs:02d}"
                            draw.text((0, 0), timer, fill="white", font=ImageFont.truetype(
                                "IBMPlexMono-Regular.ttf", size=44))
        time.sleep(0.1)


def switch_states():
    global state
    while True:
        if bz.button1.is_pressed:
            state = "focus_timer"
            start_timer(1500)
        elif bz.button2.is_pressed:
            state = "rest_timer"
            start_timer(300)
        elif bz.button3.is_pressed:
            state = "sleeping"
        time.sleep(0.1)


def start_timer(num):
    global timer_thread, interrupt_flag
    remaining_time_queue.put(num)
    print(f"Starting timer for {num} seconds...")
    if timer_thread and timer_thread.is_alive():
        interrupt_flag = True
        timer_thread.join()
    interrupt_flag = False
    timer_thread = threading.Thread(target=timer_function)
    timer_thread.start()


def timer_function():
    global interrupt_flag
    remaining_time = remaining_time_queue.get()
    while remaining_time > 0 and not interrupt_flag:
        print(f"Remaining time: {remaining_time} seconds")
        time.sleep(1)
        remaining_time -= 1
        if not interrupt_flag:
            remaining_time_queue.put(remaining_time)
    print("Timer ended.")


bz = bzLock()
bz.setup_display()
bz.setup_numpad()

states = ["sleeping", "focus_timer", "rest_timer", "setting"]
state = states[0]

remaining_time_queue = queue.Queue()
timer_thread = None
interrupt_flag = False

DISPLAY_LOCK = threading.Lock()

update_display_thread = threading.Thread(target=update_display)
update_display_thread.start()  # Start the update_display thread
threading.Thread(target=switch_states).start()
