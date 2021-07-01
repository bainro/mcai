'''
  Script to capture keyboard & mouse inputs while an "expert" plays Minecraft.
  Saves tuples of experience {S, A, R, S'} into an .npy file.
'''

from pynput import mouse
from pynput.keyboard import Key, Controller
from xinput import *
import direct_keyboard_inputs as k
import numpy as np
import mss
import time
import cv2

# def on_move(x, y):
#     print('Pointer moved to {0}'.format(
#         (x, y)))

# def on_click(x, y, button, pressed):
#     print("button: ", button)
#     print('{0} at {1}'.format(
#         'Pressed' if pressed else 'Released',
#         (x, y)))
#     # if not pressed:
#     #     # Stop listener
#     #     return False

# def on_scroll(x, y, dx, dy):
#     print('Scrolled {0} at {1}'.format(
#         'down' if dy < 0 else 'up',
#         (x, y)))

# # Collect events until released
# with mouse.Listener(
#         on_move=on_move,
#         on_click=on_click,
#         on_scroll=on_scroll) as listener:
#     listener.join()

'''
# ...or, in a non-blocking fashion:
listener = mouse.Listener(
    on_move=on_move,
    on_click=on_click,
    on_scroll=on_scroll)
listener.start()
'''

m = mouse.Controller()
# didn't work except for typing in chat :-/
# k = Controller()
sct = mss.mss()

action_q = queue.Queue()
reward_q = queue.Queue()
action_q.task_done()

# start thread that does controller input monitoring,
# mapping from controller to synthetic mouse & keyboard.
# args = (None, None)
# xi_w = threading.Thread(target=xinput_worker, args=args)
# xi_w.start()

# nothing operator. default action.
NOOP = 0 

def record_worker(s0, s1):
  if len(action_q):
    a = action_q.get()
  else:
    a = NOOP

FPS = 10
max_duration = 1/FPS
step_start = timer.perf_counter()
step_end   = timer.perf_counter()
step_duration = step_end - step_start
assert step_duration < max_duration, "oopsies, too slow :("
fuse = 0.1 - step_duration
threading.Timer(interval=fuse, function=record_worker, args=[]).start()

# Assumes 800x600 screen resolution & windowed game in top-left @ 400x300
roi = {
  "top": 30, 
  "left": 0, 
  "width": 400, 
  "height": 300
}

time.sleep(1)
start = time.perf_counter()
for _ in range(10):
    # would grab a region of interest & ignore the transparency/alpha ch
    display_roi = np.asarray(sct.grab(roi), dtype=np.uint8)[:,:,:-1]
    gray = cv2.cvtColor(display_roi, cv2.COLOR_BGR2GRAY)
    cv2.imwrite("test_mono_mc" + str(_) + ".png", gray)
    #image_int = np.array(255*image[0], np.uint8)
    #cv2.imwrite("test_mono_mc.png", image_int)

end = time.perf_counter()
print("total seconds: ", (end - start))

if __name__ == "__main__":
    joysticks = XInputJoystick.enumerate_devices()
    device_numbers = list(map(attrgetter('device_number'), joysticks))

    print('found %d devices: %s' % (len(joysticks), device_numbers))

    if not joysticks:
        sys.exit(0)

    j = joysticks[0]
    print('using %d' % j.device_number)

    battery = j.get_battery_information()
    print(battery)

    @j.event
    def on_button(button, pressed):
        print('button', button, pressed)
        if button == 6:
            if pressed:
                k.PressKey(k.ESC)
            else:
                k.ReleaseKey(k.ESC)

        # scroll up # bumper
        if button == 9:
            if pressed:
                m.scroll(0, 1)

        # scroll down # bumper
        if button == 10:
            if pressed:
                m.scroll(0, -1)

        # space / jump
        if button == 13:
            if pressed:
                k.PressKey(k.SPACE)
                time.sleep(0.1)
                k.ReleaseKey(k.SPACE)

    old_rx_thumb = 0.0
    old_ry_thumb = 0.0
    r_stick_x_a = 0
    r_stick_y_a = 0

    old_lx_thumb = 0.0
    old_ly_thumb = 0.0
    l_stick_x_a = 0
    l_stick_y_a = 0

    @j.event
    def on_axis(axis, value):
        global old_rx_thumb
        global old_ry_thumb
        global r_stick_x_a
        global r_stick_y_a

        global old_lx_thumb
        global old_ly_thumb
        global l_stick_x_a
        global l_stick_y_a

        stick_thresh = 0.3

        print('axis', axis, value)

        if axis == "r_thumb_x":
            if abs(value) < 0.3 and r_stick_x_a != 0:
                print("r_thumb_x reset to the center!")
                r_stick_x_a = 0
            elif value > 0:
                if  old_rx_thumb < stick_thresh and value > stick_thresh:
                    print("right stick pressed to the right!")
                    r_stick_x_a = 1
            else:
                if  abs(old_rx_thumb) < stick_thresh and abs(value) > stick_thresh:
                    print("right stick pressed to the left!") 
                    r_stick_x_a = -1
            old_rx_thumb = value
        elif axis == "r_thumb_y":
            if abs(value) < 0.3 and r_stick_y_a != 0:
                print("r_thumb_y reset to the center!")
                r_stick_y_a = 0
            elif value > 0:
                if  old_ry_thumb < stick_thresh and value > stick_thresh:
                    print("right stick pressed up!")
                    r_stick_y_a = 1
            else:
                if  abs(old_ry_thumb) < stick_thresh and abs(value) > stick_thresh:
                    print("right stick pressed down!") 
                    r_stick_y_a = -1
            old_ry_thumb = value
        elif axis == "l_thumb_x":
            if abs(value) < 0.3 and l_stick_x_a != 0:
                print("l_thumb_x reset to the center!")
                l_stick_x_a = 0
            elif value > 0:
                if  old_lx_thumb < stick_thresh and value > stick_thresh:
                    print("left stick pressed to the right!")
                    l_stick_x_a = 1
            else:
                if abs(old_lx_thumb) < stick_thresh and abs(value) > stick_thresh:
                    print("left stick pressed to the left!") 
                    l_stick_x_a = -1
            old_lx_thumb = value
        elif axis == "l_thumb_y":
            if abs(value) < 0.3 and l_stick_y_a != 0:
                print("l_thumb_y reset to the center!")
                l_stick_y_a = 0
            elif value > 0:
                if  old_ly_thumb < stick_thresh and value > stick_thresh:
                    print("left stick pressed up!")
                    l_stick_y_a = 1
            else:
                if  abs(old_ly_thumb) < stick_thresh and abs(value) > stick_thresh:
                    print("left stick pressed down!") 
                    l_stick_y_a = -1
            old_ly_thumb = value

    while True:
        j.dispatch_events()
        time.sleep(.01)
        
        ### right stick (mouse movement)
        if r_stick_x_a == 1:
            m.move(5, 0)
        elif r_stick_x_a == -1:
            m.move(-5, 0)
        elif r_stick_y_a == 1:
            m.move(0, -5)
        elif r_stick_y_a == -1:
            m.move(0, 5)
        
        ### left stick (WASD)
        if l_stick_x_a == 1:
            k.PressKey(k.D)
        elif l_stick_x_a == -1:
            k.PressKey(k.A)
        elif l_stick_y_a == 1:
            k.PressKey(k.W)
        elif l_stick_y_a == -1:
            k.PressKey(k.S)
        else:
            k.ReleaseKey(k.W)
            k.ReleaseKey(k.A)
            k.ReleaseKey(k.S)
            k.ReleaseKey(k.D)