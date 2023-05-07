# from queue import LifoQueue
# from luma.core.render import canvas

from threading import Lock
from time import sleep, time
from enum import Enum
from bz import bzLock


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


# Initialize to main menu
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
        text = "Set timer length:\r\n    Press BLUE\r\nStart timer:\r\n    Press GREEN"
        bz.text_to_display(text)


def show_set_timer_submenu():
    with display_lock:
        text = "Set Focus Timer:\r\n    Press BLUE\r\nSet Rest Timer:\r\n    Press GREEN"
        bz.text_to_display(text)


def show_start_timer_submenu():
    with display_lock:
        text = "Start Focus Timer:\r\n    Press BLUE\r\nStart Rest Timer:\r\n    Press GREEN"
        bz.text_to_display(text)


def show_timer_remaining(time_remaining):
    with display_lock:
        text = f"Time remaining:\r\n{time_remaining // 60:02}:{time_remaining % 60:02}"
        bz.text_to_display(text)


def show_numpad_input(input_value):
    with display_lock:
        text = f"Input: {input_value} min\r\nConfirm:\r\n    Press GREEN"
        bz.text_to_display(text)


def show_close_box_message():
    with display_lock:
        text = "Please close the box\r\nwith phone inside"
        bz.text_to_display(text)
        sleep(1)


# Function for getting numpad input
def get_numpad_input(default: int):
    input_value = ""
    while True:
        key = bz.read_numpad()
        if key:
            if key == "*" or key == "#":
                continue
            elif key == "0" and len(input_value) == 0:
                continue
            input_value += key
            print(input_value)
            show_numpad_input(input_value)

            if len(input_value) >= 4:
                break

        # Break the loop if the green button is pressed
        if bz.green_button.is_pressed:  # type: ignore
            break

        sleep(0.1)
    try:
        return int(input_value)
    except:
        return default


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
                time_elapsed = time() - timer_start_time  # type: ignore
                time_remaining = int(current_timer - time_elapsed)

                if time_remaining <= 0:
                    print("Timer finished")
                    bz.unlock()
                    menu_state = MenuState.MAIN
                else:
                    show_timer_remaining(time_remaining)
            else:
                sleep(0.1)

        sleep(0.1)

        if bz.blue_button.is_pressed:  # type: ignore
            sleep(0.5)  # Debounce
            if menu_state == MenuState.MAIN:
                menu_state = MenuState.SET_TIMER_SUBMENU
            elif menu_state == MenuState.SET_TIMER_SUBMENU:
                show_numpad_input("")
                focus_timer_length = get_numpad_input(25) * 60
                menu_state = MenuState.MAIN
            elif menu_state == MenuState.START_TIMER_SUBMENU:
                # todo: add detect phone in box and box closed
                if bz.detect_phone():
                    current_timer = focus_timer_length
                    timer_start_time = time()
                    timer_paused = False
                    bz.lock()
                    menu_state = MenuState.RUNNING_TIMER
                else:
                    show_close_box_message()
            elif menu_state == MenuState.RUNNING_TIMER:
                if timer_paused:
                    print("Resume timer")
                    timer_start_time = time() - (current_timer - time_remaining)  # type: ignore
                    timer_paused = False
                else:
                    print("Pause timer")
                    timer_paused = True

        elif bz.green_button.is_pressed:  # type: ignore
            sleep(0.5)  # Debounce
            if menu_state == MenuState.MAIN:
                menu_state = MenuState.START_TIMER_SUBMENU
            elif menu_state == MenuState.SET_TIMER_SUBMENU:
                show_numpad_input("")
                rest_timer_length = get_numpad_input(5) * 60
                menu_state = MenuState.MAIN
            elif menu_state == MenuState.START_TIMER_SUBMENU:
                current_timer = rest_timer_length
                timer_start_time = time()
                timer_paused = False
                menu_state = MenuState.RUNNING_TIMER
            elif menu_state == MenuState.RUNNING_TIMER:
                if timer_paused:
                    print("Resume timer")
                    timer_start_time = time() - (current_timer - time_remaining)  # type: ignore
                    timer_paused = False
                else:
                    print("Pause timer")
                    timer_paused = True

        elif bz.red_button.is_pressed:  # type: ignore
            sleep(0.5)  # Debounce
            if menu_state == MenuState.RUNNING_TIMER:
                print("Stop timer and unlock box")
                bz.unlock()
                menu_state = MenuState.MAIN

except KeyboardInterrupt:
    bz.clear_display()


# import datetime
# import math

# def posn(angle, arm_length):
#     dx = int(math.cos(math.radians(angle)) * arm_length)
#     dy = int(math.sin(math.radians(angle)) * arm_length)
#     return (dx, dy)


# def draw_clock(draw):
#     now = datetime.datetime.now()
#     today_date = now.strftime("%b/%d/%y")
#     today_time = now.strftime("%H:%M:%S")
#     margin = 4

#     cx = 30
#     cy = 32

#     left = cx - cy
#     right = cx + cy

#     hrs_angle = 270 + (30 * (now.hour + (now.minute / 60.0)))
#     hrs = posn(hrs_angle, cy - margin - 7)

#     min_angle = 270 + (6 * now.minute)
#     mins = posn(min_angle, cy - margin - 2)

#     sec_angle = 270 + (6 * now.second)
#     secs = posn(sec_angle, cy - margin - 2)

#     draw.ellipse((left + margin, margin, right -
#                  margin, 64 - margin), outline="white")
#     draw.line((cx, cy, cx + hrs[0], cy + hrs[1]), fill="white")
#     draw.line((cx, cy, cx + mins[0], cy + mins[1]), fill="white")
#     draw.line((cx, cy, cx + secs[0], cy + secs[1]), fill="red")
#     draw.ellipse((cx - 2, cy - 2, cx + 2, cy + 2),
#                  fill="white", outline="white")
#     draw.text((2 * (cx + margin), cy - 8), today_date, fill="yellow")
#     draw.text((2 * (cx + margin), cy), today_time, fill="yellow")
