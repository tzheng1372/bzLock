import math
import datetime
import threading
import queue
import time
from PIL import ImageFont

from luma.core.render import canvas


class Clock:
    def __init__(self, bz):
        self.bz = bz
        self.bz.setup_display()
        self.bz.setup_numpad()

        self.states = ["sleeping", "focus_timer", "rest_timer", "setting"]
        self.state = self.states[0]

        self.last_time = "Unknown"
        self.remaining_time_queue = queue.Queue()
        self.timer_thread = None
        self.interrupt_flag = False

        self.DISPLAY_LOCK = threading.Lock()

        self.update_display()
        threading.Thread(target=self.switch_states).start()

    def posn(self, angle, arm_length):
        dx = int(math.cos(math.radians(angle)) * arm_length)
        dy = int(math.sin(math.radians(angle)) * arm_length)
        return (dx, dy)

    def draw_clock(self, draw):
        now = datetime.datetime.now()
        today_date = now.strftime("%b/%d/%y")
        today_time = now.strftime("%H:%M:%S")
        margin = 4
        cx = 30
        cy = 64 // 2
        left = cx - cy
        right = cx + cy

        hrs_angle = 270 + (30 * (now.hour + (now.minute / 60.0)))
        hrs = self.posn(hrs_angle, cy - margin - 7)

        min_angle = 270 + (6 * now.minute)
        mins = self.posn(min_angle, cy - margin - 2)

        sec_angle = 270 + (6 * now.second)
        secs = self.posn(sec_angle, cy - margin - 2)

        draw.ellipse((left + margin, margin, right -
                     margin, 64 - margin), outline="white")
        draw.line((cx, cy, cx + hrs[0], cy + hrs[1]), fill="white")
        draw.line((cx, cy, cx + mins[0], cy + mins[1]), fill="white")
        draw.line((cx, cy, cx + secs[0], cy + secs[1]), fill="red")
        draw.ellipse((cx - 2, cy - 2, cx + 2, cy + 2),
                     fill="white", outline="white")
        draw.text((2 * (cx + margin), cy - 8), today_date, fill="yellow")
        draw.text((2 * (cx + margin), cy), today_time, fill="yellow")

    def update_display(self):
        if self.state == "sleeping":
            now = datetime.datetime.now()
            today_time = now.strftime("%H:%M:%S")
            if today_time != self.last_time:
                self.last_time = today_time
                with self.DISPLAY_LOCK:
                    with canvas(self.bz.display) as draw:
                        self.draw_clock(draw)
        elif self.state in ["focus_timer", "rest_timer"]:
            mins, secs = divmod(self.get_remaining_time(), 60)
            timer = "{:02d}:{:02d}".format(mins, secs)
            with self.DISPLAY_LOCK:
                with canvas(self.bz.display) as draw:
                    draw.text((0, 0), timer, fill="white", font=ImageFont.truetype(
                        "IBMPlexMono-Regular.ttf", size=44))

        threading.Timer(0.1, self.update_display).start()

    def switch_states(self):
        while True:
            if self.bz.button1.is_pressed:
                self.state = "focus_timer"
                self.start_focus_timer(1500)
            elif self.bz.button2.is_pressed:
                self.state = "rest_timer"
                self.start_rest_timer(300)
            elif self.bz.button3.is_pressed:
                self.state = "sleeping"

    def start_focus_timer(self, num):
        self.remaining_time_queue.put(num)
        print("Starting focus timer for {} seconds...".format(num))
        if self.timer_thread and self.timer_thread.is_alive():
            self.interrupt_flag = True
            self.timer_thread.join()
        self.interrupt_flag = False
        self.timer_thread = threading.Thread(target=self.focus_timer)
        self.timer_thread.start()

    def start_rest_timer(self, num):
        self.remaining_time_queue.put(num)
        print("Starting rest timer for {} seconds...".format(num))
        if self.timer_thread and self.timer_thread.is_alive():
            self.interrupt_flag = True
            self.timer_thread.join()
        self.interrupt_flag = False
        self.timer_thread = threading.Thread(target=self.rest_timer)
        self.timer_thread.start()

    def focus_timer(self):
        self.interrupt_flag = False
        remaining_time = self.remaining_time_queue.get()
        while remaining_time > 0 and not self.interrupt_flag:
            print("Remaining time: {} seconds".format(remaining_time))
            time.sleep(1)
            remaining_time -= 1
        print("Focus timer ended.")

    def rest_timer(self):
        self.interrupt_flag = False
        remaining_time = self.remaining_time_queue.get()
        while remaining_time > 0 and not self.interrupt_flag:
            print("Remaining time: {} seconds".format(remaining_time))
            time.sleep(1)
            remaining_time -= 1
        print("Rest timer ended.")

    def get_remaining_time(self):
        if not self.remaining_time_queue.empty():
            return self.remaining_time_queue.queue[-1]
        return None
