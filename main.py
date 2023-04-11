from threading import Lock, Thread
from luma.core.render import canvas
from bz import bzLock

import datetime
import time
import math

display_lock = Lock()

bz = bzLock()

bz.setup_display()


def posn(angle, arm_length):
    dx = int(math.cos(math.radians(angle)) * arm_length)
    dy = int(math.sin(math.radians(angle)) * arm_length)
    return (dx, dy)


def clock_to_display():
    today_last_time = "Unknown"
    while True:
        display_lock.acquire()
        now = datetime.datetime.now()
        today_date = now.strftime("%d %b %y")
        today_time = now.strftime("%H:%M:%S")
        if today_time != today_last_time:
            today_last_time = today_time
            with canvas(bz.display) as draw:
                now = datetime.datetime.now()
                today_date = now.strftime("%d %b %y")
                margin = 4
                cx = 30
                cy = min(64, 64) / 2
                left = cx - cy
                right = cx + cy
                hrs_angle = 270 + (30 * (now.hour + (now.minute / 60.0)))
                hrs = posn(hrs_angle, cy - margin - 7)
                min_angle = 270 + (6 * now.minute)
                mins = posn(min_angle, cy - margin - 2)
                sec_angle = 270 + (6 * now.second)
                secs = posn(sec_angle, cy - margin - 2)
                draw.ellipse((left + margin, margin, right - margin,
                             min(128, 64) - margin), outline="white")
                draw.line((cx, cy, cx + hrs[0], cy + hrs[1]), fill="white")
                draw.line((cx, cy, cx + mins[0], cy + mins[1]), fill="white")
                draw.line((cx, cy, cx + secs[0], cy + secs[1]), fill="red")
                draw.ellipse((cx - 2, cy - 2, cx + 2, cy + 2),
                             fill="white", outline="white")
                draw.text((2 * (cx + margin), cy - 8),
                          today_date, fill="yellow")
                draw.text((2 * (cx + margin), cy), today_time, fill="yellow")
        display_lock.release()
        time.sleep(0.1)


clock_to_display_thread = Thread(target=clock_to_display)

clock_to_display_thread.start()
