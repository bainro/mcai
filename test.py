'''
  Script to capture keyboard & mouse inputs while an "expert" plays Minecraft.
  Saves tuples of experience {S, A, R, S'} into an .npy file.
'''

from pynput.keyboard import Key, Controller
import direct_keyboard_inputs as k
from pynput import mouse
from xinput import *
import numpy as np
import threading
import queue
import time
import mss
import cv2

m = mouse.Controller()
sct = mss.mss()

action_q = queue.Queue()
reward_q = queue.Queue()
# action_q.task_done()

# start thread that does controller input monitoring,
# mapping from controller to synthetic mouse & keyboard.
# args = (None, None)
# xi_w = threading.Thread(target=xinput_worker, args=args)
# xi_w.start()

# nothing operator. default action.
NOOP    = 0
R_TRIG  = 1
L_TRIG  = 2
R_BUMP  = 3
L_BUMP  = 4
L_LEFT  = 5
L_DOWN  = 6
L_RIGHT = 7
L_UP    = 8
R_LEFT  = 9
R_DOWN  = 10
R_RIGHT = 11
R_UP    = 12
A_BTN   = 13

def record_worker():
    FPS = 10
    max_duration = 1 / FPS
    step_start = time.perf_counter()
    step_end   = time.perf_counter()
    step_duration = step_end - step_start
    assert step_duration < max_duration, "oopsies, too slow :("
    fuse = 0.1 - step_duration

    r_left = r_right = r_up = r_down = l_left = l_right = l_up = l_down = r_trig = l_trig = False    

    if action_q.qsize() > 0:
        action = action_q.get()
    else:
        action = NOOP

    ### right stick (mouse movement)
    if action == R_LEFT:
        r_left != r_left
        if r_left:
            m.move(-5, 0)

    elif action == R_RIGHT:
        r_right != r_right
        if r_right:
            m.move(5, 0)
    
    elif action == R_UP:
        r_up != r_up
        if r_up:
            m.move(0, -5)

    elif action == R_DOWN:
        r_down != r_down
        if r_down:
            m.move(0, 5)

    ### left stick (WASD)
    elif action == L_LEFT:
        l_left != l_left
        if l_left:
            k.PressKey(k.A)
        else:
            k.ReleaseKey(k.A)
            
    elif action == L_RIGHT:
        l_right != l_right
        if l_right:
            k.PressKey(k.D)
        else:
            k.ReleaseKey(k.D)

    elif action == L_UP:
        l_up != l_up
        if l_up:
            k.PressKey(k.W)
        else:
            k.ReleaseKey(k.W)

    elif action == L_DOWN:
        l_down != l_down
        if l_down:
            k.PressKey(k.S)
        else:
            k.ReleaseKey(k.S)
    
    # dig, left mouse / right trigger
    elif action == R_TRIG:
        r_trig != r_trig
        if r_trig:
            m.press(mouse.Button.left)
        else:
            m.release(mouse.Button.left)

    # place, right mouse / left trigger
    elif action == L_TRIG:
        l_trig != l_trig
        if l_trig:
            m.press(mouse.Button.right)
        else:
            m.release(mouse.Button.right)

    else:
        assert action == NOOP, "was expecting no-op :-/"  

threading.Timer(interval=0, function=record_worker, args=[]).start()

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
        # SELECT is unpause. Leave in for testing / debugging.
        # Shouldn't be observed or done by the AI agent.
        if button == 6:
            if pressed:
                k.PressKey(k.ESC)
            else:
                k.ReleaseKey(k.ESC)

        # scroll up # bumper
        if button == 9:
            if pressed:
                action_q.put(L_BUMP)
                # m.scroll(0, 1)

        # scroll down # bumper
        if button == 10:
            if pressed:
                action_q.put(R_BUMP)
                # m.scroll(0, -1)

        # space / jump
        if button == 13:
            if pressed:
                # k.PressKey(k.SPACE)
                action_q.put(A_BTN)
            else:
                # k.ReleaseKey(k.SPACE)
                action_q.put(A_BTN)

    old_rx_thumb = 0.0
    old_ry_thumb = 0.0
    r_stick_x_a = 0
    r_stick_y_a = 0

    old_lx_thumb = 0.0
    old_ly_thumb = 0.0
    l_stick_x_a = 0
    l_stick_y_a = 0

    old_r_trig = 0
    old_l_trig = 0

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

        global old_r_trig
        global old_l_trig

        stick_thresh = 0.2

        print('axis', axis, value)

        if axis == 'right_trigger':
            if value == 1.0:
                print("right trigger on!")
                action_q.put(R_TRIG)
            else:
                print("right trigger off!")
                if old_r_trig < 1.0:
                    action_q.put(R_TRIG)
            old_r_trig = value

        if axis == 'left_trigger':
            if value == 1.0:
                print("left trigger on!")
                action_q.put(L_TRIG)
            else:
                print("left trigger off!")
                if old_l_trig < 1.0:
                    action_q.put(L_TRIG)
            old_l_trig = value

        if axis == "r_thumb_x":
            if abs(value) < 0.2 and r_stick_x_a != 0:
                print("r_thumb_x reset to the center!")
                if r_stick_x_a == -1:
                    action_q.put(R_LEFT)
                elif r_stick_x_a == 1:
                    action_q.put(R_RIGHT)
                else:
                    assert 0, "this case shouldn't be reached"
                r_stick_x_a = 0
            elif value > 0:
                if  old_rx_thumb < stick_thresh and value > stick_thresh:
                    print("right stick pressed to the right!")
                    r_stick_x_a = 1
                    action_q.put(R_RIGHT)
            else:
                if  abs(old_rx_thumb) < stick_thresh and abs(value) > stick_thresh:
                    print("right stick pressed to the left!") 
                    r_stick_x_a = -1
                    action_q.put(R_LEFT)
            old_rx_thumb = value
        
        if axis == "r_thumb_y":
            if abs(value) < 0.2 and r_stick_y_a != 0:
                print("r_thumb_y reset to the center!")
                if r_stick_y_a == -1:
                    action_q.put(R_DOWN)
                elif r_stick_y_a == 1:
                    action_q.put(R_UP)
                else:
                    assert 0, "this case shouldn't be reached"
                r_stick_y_a = 0
            elif value > 0:
                if  old_ry_thumb < stick_thresh and value > stick_thresh:
                    print("right stick pressed up!")
                    r_stick_y_a = 1
                    action_q.put(R_UP)
            else:
                if  abs(old_ry_thumb) < stick_thresh and abs(value) > stick_thresh:
                    print("right stick pressed down!") 
                    r_stick_y_a = -1
                    action_q.put(R_DOWN)
            old_ry_thumb = value

        if axis == "l_thumb_x":
            if abs(value) < 0.2 and l_stick_x_a != 0:
                print("l_thumb_x reset to the center!")
                if l_stick_x_a == -1:
                    action_q.put(L_LEFT)
                elif l_stick_x_a == 1:
                    action_q.put(L_RIGHT)
                else:
                    assert 0, "this case shouldn't be reached"
                l_stick_x_a = 0
            elif value > 0:
                if  old_lx_thumb < stick_thresh and value > stick_thresh:
                    print("left stick pressed to the right!")
                    l_stick_x_a = 1
                    action_q.put(L_RIGHT)
            else:
                if abs(old_lx_thumb) < stick_thresh and abs(value) > stick_thresh:
                    print("left stick pressed to the left!") 
                    l_stick_x_a = -1
                    action_q.put(L_LEFT)
            old_lx_thumb = value
        
        if axis == "l_thumb_y":
            if abs(value) < 0.2 and l_stick_y_a != 0:
                print("l_thumb_y reset to the center!")
                if l_stick_y_a == -1:
                    action_q.put(L_DOWN)
                elif l_stick_y_a == 1:
                    action_q.put(L_UP)
                else:
                    assert 0, "this case shouldn't be reached"
                l_stick_y_a = 0
            elif value > 0:
                if  old_ly_thumb < stick_thresh and value > stick_thresh:
                    print("left stick pressed up!")
                    l_stick_y_a = 1
                    action_q.put(L_UP)
            else:
                if  abs(old_ly_thumb) < stick_thresh and abs(value) > stick_thresh:
                    print("left stick pressed down!") 
                    l_stick_y_a = -1
                    action_q.put(L_DOWN)
            old_ly_thumb = value

    while True:
        j.dispatch_events()
        time.sleep(.01)