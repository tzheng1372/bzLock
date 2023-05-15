from multiprocessing import Process, Manager, Lock
from time import sleep, time
from enum import Enum
from bz import bzLock


def show_menu():
    text = "Set timer length:\r\n    Press BLUE\r\nStart timer:\r\n    Press GREEN"
    bz.text_to_display(text)


def show_set_timer_submenu():
    text = "Set Focus Timer:\r\n    Press BLUE\r\nSet Rest Timer:\r\n    Press GREEN"
    bz.text_to_display(text)


def show_start_timer_submenu():
    text = "Start Focus Timer:\r\n    Press BLUE\r\nStart Rest Timer:\r\n    Press GREEN"
    bz.text_to_display(text)


def show_timer_remaining(time_remaining):
    text = f"Time remaining:\r\n{time_remaining // 60:02}:{time_remaining % 60:02}"
    bz.text_to_display(text)


def show_numpad_input(input_value):
    text = f"Input: {input_value} min\r\nConfirm:\r\n    Press GREEN"
    bz.text_to_display(text)


def show_close_box_message():
    text = "Please close the box\r\nwith phone inside"
    bz.text_to_display(text)
    sleep(1.5)


def show_stop_message():
    text = "Timer stopped"
    bz.text_to_display(text)
    sleep(1.5)


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


class MenuState(Enum):
    MAIN = 1
    SET_TIMER_SUBMENU = 2
    START_TIMER_SUBMENU = 3
    RUNNING_TIMER = 4


def hardware_interface_process(shared_state, bz):
    while True:
        shared_state['blue_button_pressed'] = bz.blue_button.is_pressed
        shared_state['green_button_pressed'] = bz.green_button.is_pressed
        shared_state['red_button_pressed'] = bz.red_button.is_pressed
        sleep(0.5)  # Short sleep to avoid busy waiting


def button_process(shared_state, bz, display_lock):
    while True:
        if shared_state['blue_button_pressed']:
            if shared_state["menu_state"] == MenuState.MAIN:
                bz.off_led()
                shared_state["menu_state"] = MenuState.SET_TIMER_SUBMENU
            elif shared_state["menu_state"] == MenuState.SET_TIMER_SUBMENU:
                bz.yellow_led()
                with display_lock:
                    show_numpad_input("")
                    shared_state["focus_timer_length"] = get_numpad_input(
                        25) * 60
                bz.off_led()
                shared_state["menu_state"] = MenuState.MAIN
            elif shared_state["menu_state"] == MenuState.START_TIMER_SUBMENU:
                if bz.detect_phone():
                    bz.blue_led()
                    shared_state["current_timer"] = shared_state["focus_timer_length"]
                    shared_state["timer_start_time"] = time()
                    shared_state["timer_type"] = "focus"
                    shared_state["timer_paused"] = False
                    bz.lock()
                    shared_state["menu_state"] = MenuState.RUNNING_TIMER
                else:
                    bz.yellow_led()
                    with display_lock:
                        show_close_box_message()
                    bz.off_led()
            elif shared_state["menu_state"] == MenuState.RUNNING_TIMER:
                print("Reset timer")
                if shared_state["timer_type"] == "focus":
                    bz.blue_led()
                    shared_state["current_timer"] = shared_state["focus_timer_length"]
                elif shared_state["timer_type"] == "rest":
                    bz.green_led()
                    shared_state["current_timer"] = shared_state["rest_timer_length"]
                shared_state["timer_start_time"] = time()
                shared_state["timer_paused"] = False

        elif shared_state['green_button_pressed']:
            if shared_state["menu_state"] == MenuState.MAIN:
                bz.off_led()
                shared_state["menu_state"] = MenuState.START_TIMER_SUBMENU
            elif shared_state["menu_state"] == MenuState.SET_TIMER_SUBMENU:
                bz.yellow_led()
                with display_lock:
                    show_numpad_input("")
                    shared_state["rest_timer_length"] = get_numpad_input(
                        5) * 60
                bz.off_led()
                shared_state["menu_state"] = MenuState.MAIN
            elif shared_state["menu_state"] == MenuState.START_TIMER_SUBMENU:
                bz.green_led()
                shared_state["current_timer"] = shared_state["rest_timer_length"]
                shared_state["timer_start_time"] = time()
                shared_state["timer_type"] = "rest"
                shared_state["timer_paused"] = False
                shared_state["menu_state"] = MenuState.RUNNING_TIMER
        elif shared_state["menu_state"] == MenuState.RUNNING_TIMER:
            if shared_state["timer_paused"]:
                print("Resume timer")
                shared_state["timer_start_time"] = time(
                ) - (shared_state["current_timer"] - shared_state["time_remaining"])
                shared_state["timer_paused"] = False
                bz.blue_led()
            else:
                print("Pause timer")
                shared_state["timer_paused"] = True
                bz.yellow_led()

        elif shared_state['red_button_pressed']:
            if shared_state["menu_state"] == MenuState.RUNNING_TIMER:
                bz.unlock()
                bz.red_led()
                with display_lock:
                    show_stop_message()
                bz.off_led()
                shared_state["menu_state"] = MenuState.MAIN

        sleep(0.1)


def timer_process(shared_state, bz, display_lock):
    while True:
        if shared_state["menu_state"] == MenuState.MAIN:
            with display_lock:
                show_menu()
            shared_state["current_timer"] = None

        elif shared_state["menu_state"] == MenuState.SET_TIMER_SUBMENU:
            with display_lock:
                show_set_timer_submenu()

        elif shared_state["menu_state"] == MenuState.START_TIMER_SUBMENU:
            with display_lock:
                show_start_timer_submenu()

        elif shared_state["menu_state"] == MenuState.RUNNING_TIMER:
            if shared_state["current_timer"] is not None and not shared_state["timer_paused"]:
                time_elapsed = time() - shared_state["timer_start_time"]
                time_remaining = int(
                    shared_state["current_timer"] - time_elapsed)

                if time_remaining <= 0:
                    print("Timer finished")
                    bz.unlock()
                    bz.off_led()
                    shared_state["menu_state"] = MenuState.MAIN
                else:
                    shared_state["time_remaining"] = time_remaining
                    with display_lock:
                        show_timer_remaining(time_remaining)

        sleep(0.1)


if __name__ == "__main__":
    bz = bzLock()
    bz.setup_display()
    bz.setup_numpad()
    bz.setup_spi()

    with Manager() as manager:
        shared_state = manager.dict()
        shared_state["menu_state"] = MenuState.MAIN
        shared_state["focus_timer_length"] = 25 * 60
        shared_state["rest_timer_length"] = 5 * 60
        shared_state["current_timer"] = None
        shared_state["timer_start_time"] = None
        shared_state["timer_type"] = None
        shared_state["timer_paused"] = False
        shared_state["time_remaining"] = 0
        shared_state["blue_button_pressed"] = False
        shared_state["green_button_pressed"] = False
        shared_state["red_button_pressed"] = False

        display_lock = Lock()

        p1 = Process(target=hardware_interface_process,
                     args=(shared_state, bz))
        p2 = Process(target=button_process, args=(
            shared_state, bz, display_lock))
        p3 = Process(target=timer_process, args=(
            shared_state, bz, display_lock))

        p1.start()
        p2.start()
        p3.start()

        p1.join()
        p2.join()
        p3.join()
