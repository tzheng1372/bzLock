import datetime
import math
from threading import Event, Lock, Thread
import time

from queue import LifoQueue
from PIL import ImageFont
from luma.core.render import canvas
from enum import Enum


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


# def update_display():
#     mins, secs = (0, 0)

#     while True:
#         if state == "welcome":
#             with display_lock:
#                 with canvas(bz.display) as draw:
#                     text = "Blue for clock"
#                     draw.text((0, 0), text, fill="white")
#                     text = "Red for focus timer"
#                     draw.text((0, 10), text, fill="white")
#                     text = "Green for reset timer"
#                     draw.text((0, 20), text, fill="white")

#         elif state == "clock":
#             with display_lock:
#                 with canvas(bz.display) as draw:
#                     draw_clock(draw)

#         else:
#             with display_lock:
#                 with canvas(bz.display) as draw:
#                     if not remaining_time_queue.empty():
#                         mins, secs = remaining_time_queue.get()
#                     timer = f"{mins:02d}:{secs:02d}"
#                     draw.text((0, 0), timer, fill="white", font=ImageFont.truetype(
#                         "IBMPlexMono-Regular.ttf", size=44))
#         time.sleep(0.1)


# def switch_states():
#     global state
#     global stop_timer

#     while True:
#         if bz.button1.is_pressed:
#             if not state in ["focus_timer", "rest_timer"]:
#                 state = "focus_timer"
#                 run_timer(1500)

#         elif bz.button2.is_pressed:
#             if not state in ["focus_timer", "rest_timer"]:
#                 state = "rest_timer"
#                 run_timer(300)

#         elif bz.button3.is_pressed:
#             state = "clock"

#         time.sleep(0.3)


# def timer(seconds):
#     global stop_timer
#     start_time = time.perf_counter()
#     end_time = start_time + seconds

#     while time.perf_counter() < end_time and not stop_timer.is_set():
#         remaining_time = end_time - time.perf_counter()
#         mins, secs = divmod(int(remaining_time), 60)
#         timer = '{:02d}:{:02d}'.format(mins, secs)
#         print(timer, end="\r")
#         with remaining_time_lock:
#             remaining_time_queue.put((mins, secs))
#         time.sleep(0.1)

#     if not stop_timer.is_set():
#         print("\nTime's up!")


# def run_timer(seconds):
#     global stop_timer

#     stop_timer.clear()
#     timer_thread = Thread(target=timer, args=(seconds,))
#     timer_thread.start()


bz = bzLock()
bz.setup_display()
bz.setup_numpad()
bz.setup_spi()

display_lock = Lock()

# Enum for menu states


class MenuState(Enum):
    MAIN = 1
    SET_TIMER_SUBMENU = 2
    START_TIMER_SUBMENU = 3
    RUNNING_TIMER = 4


menu_state = MenuState.MAIN

# Timer lengths
focus_timer_length = 25 * 60
rest_timer_length = 5 * 60

# Timer tracking variables
current_timer = None
timer_start_time = None
timer_paused = False


def show_menu():
    with display_lock:
        text = "Set timer length:\r\n\tPress BLUE\r\nStart timer:\r\n\tPress GREEN"
        bz.text_to_display(text)


def show_set_timer_submenu():
    with display_lock:
        text = "Set Focus Timer:\r\n\tPress BLUE\r\nSet Rest Timer:\r\n\tPress GREEN"
        bz.text_to_display(text)


def show_start_timer_submenu():
    with display_lock:
        text = "Start Focus Timer:\r\n\tPress BLUE\r\nStart Rest Timer:\r\n\tPress GREEN"
        bz.text_to_display(text)


def show_timer_remaining(time_remaining):
    with display_lock:
        text = f"Time remaining:\r\n{time_remaining // 60:02}:{time_remaining % 60:02}"
        bz.text_to_display(text)


try:
    while True:
        if menu_state == MenuState.MAIN:
            show_menu()
            current_timer = None

        elif menu_state == MenuState.SET_TIMER_SUBMENU:
            show_set_timer_submenu()

        elif menu_state == MenuState.START_TIMER_SUBMENU:
            show_start_timer_submenu()

        elif menu_state == MenuState.RUNNING_TIMER:
            if current_timer is not None and not timer_paused:
                time_elapsed = time.time() - timer_start_time
                time_remaining = int(current_timer - time_elapsed)

                if time_remaining <= 0:
                    print("Timer finished")
                    # Add your code to unlock the box here
                    menu_state = MenuState.MAIN
                else:
                    show_timer_remaining(time_remaining)
            else:
                time.sleep(0.1)

        time.sleep(0.1)

        if bz.blue_button.is_pressed:  # type: ignore
            time.sleep(0.5)  # Debounce
            if menu_state == MenuState.MAIN:
                menu_state = MenuState.SET_TIMER_SUBMENU
            elif menu_state == MenuState.SET_TIMER_SUBMENU:
                print("Blue button pressed - Set focus timer length")
                # Add your code for setting the focus timer length here
                menu_state = MenuState.MAIN
            elif menu_state == MenuState.START_TIMER_SUBMENU:
                # todo: add detect phone in box and box closed
                current_timer = focus_timer_length
                timer_start_time = time.time()
                timer_paused = False
                menu_state = MenuState.RUNNING_TIMER
            elif menu_state == MenuState.RUNNING_TIMER:
                if timer_paused:
                    print("Resume timer")
                    timer_start_time = time.time() - (current_timer - time_remaining)
                    timer_paused = False
                else:
                    print("Pause timer")
                    timer_paused = True

        if bz.green_button.is_pressed:  # type: ignore
            time.sleep(0.5)  # Debounce
            if menu_state == MenuState.MAIN:
                menu_state = MenuState.START_TIMER_SUBMENU
            elif menu_state == MenuState.SET_TIMER_SUBMENU:
                print("Green button pressed - Set rest timer length")
                # Add your code for setting the rest timer length here
                menu_state = MenuState.MAIN
            elif menu_state == MenuState.START_TIMER_SUBMENU:
                # todo: add detect phone in box and box closed
                current_timer = rest_timer_length
                timer_start_time = time.time()
                timer_paused = False
                menu_state = MenuState.RUNNING_TIMER
            elif menu_state == MenuState.RUNNING_TIMER:
                if timer_paused:
                    print("Resume timer")
                    timer_start_time = time.time() - (current_timer - time_remaining)
                    timer_paused = False
                else:
                    print("Pause timer")
                    timer_paused = True

        if bz.red_button.is_pressed:  # type: ignore
            time.sleep(0.5)  # Debounce
            if menu_state == MenuState.RUNNING_TIMER:
                print("Stop timer and unlock box")
                # Add your code to unlock the box here
                menu_state = MenuState.MAIN

except KeyboardInterrupt:
    pass
