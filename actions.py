'''
  Take controller inputs, save their timestamps, & send synthetic 
  input to minecraft. Synced up with grab.py & reward.py later.
'''

import direct_keyboard_inputs as k
from pynput import mouse
from xinput import *
import numpy as np
import time
import os

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

timestamps = []

if __name__ == "__main__":
    m = mouse.Controller()
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
        global timestamps

        print('button', button, pressed)
        if button == 6:
            if pressed:
                k.PressKey(k.ESC)
            else:
                k.ReleaseKey(k.ESC)

        # scroll up # bumper
        if button == 9:
            if pressed:
                timestamps.append([L_BUMP, time.time()])
                m.scroll(0, 1)

        # scroll down # bumper
        if button == 10:
            if pressed:
                timestamps.append([R_BUMP, time.time()])
                m.scroll(0, -1)

        # space / jump
        if button == 13:
            if pressed:
                k.PressKey(k.SPACE)
                timestamps.append([A_BTN, time.time()])
            else:
                k.ReleaseKey(k.SPACE)
                timestamps.append([A_BTN, time.time()])

    old_rx_thumb = 0.0
    old_ry_thumb = 0.0
    r_stick_x_a = 0
    r_stick_y_a = 0

    old_lx_thumb = 0.0
    old_ly_thumb = 0.0
    l_stick_x_a = 0
    l_stick_y_a = 0

    r_trig_a = 0
    old_r_trig = 0
    l_trig_a = 0
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

        global r_trig_a
        global old_r_trig
        global l_trig_a
        global old_l_trig

        global timestamps

        stick_thresh = 0.2

        print('axis', axis, value)

        if axis == 'right_trigger':
            if value == 1.0:
                print("right trigger on!")
                r_trig_a = 1
                timestamps.append([R_TRIG, time.time()])
            else:
                print("right trigger off!")
                r_trig_a = 0
                if old_r_trig < 1.0:
                    timestamps.append([R_TRIG, time.time()])
            old_r_trig = value

        if axis == 'left_trigger':
            if value == 1.0:
                print("left trigger on!")
                l_trig_a = 1
                timestamps.append([L_TRIG, time.time()])
            else:
                print("left trigger off!")
                l_trig_a = 0
                if old_l_trig < 1.0:
                    timestamps.append([L_TRIG, time.time()])
            old_l_trig = value

        if axis == "r_thumb_x":
            if abs(value) < 0.2 and r_stick_x_a != 0:
                print("r_thumb_x reset to the center!")
                if r_stick_x_a == -1:
                    timestamps.append([R_LEFT, time.time()])
                elif r_stick_x_a == 1:
                    timestamps.append([R_RIGHT, time.time()])
                else:
                    assert 0, "this case shouldn't be reached"
                r_stick_x_a = 0
            elif value > 0:
                if  old_rx_thumb < stick_thresh and value > stick_thresh:
                    print("right stick pressed to the right!")
                    r_stick_x_a = 1
                    timestamps.append([R_RIGHT, time.time()])
            else:
                if  abs(old_rx_thumb) < stick_thresh and abs(value) > stick_thresh:
                    print("right stick pressed to the left!") 
                    r_stick_x_a = -1
                    timestamps.append([R_LEFT, time.time()])
            old_rx_thumb = value
        
        if axis == "r_thumb_y":
            if abs(value) < 0.2 and r_stick_y_a != 0:
                print("r_thumb_y reset to the center!")
                if r_stick_y_a == -1:
                    timestamps.append([R_DOWN, time.time()])
                elif r_stick_y_a == 1:
                    timestamps.append([R_UP, time.time()])
                else:
                    assert 0, "this case shouldn't be reached"
                r_stick_y_a = 0
            elif value > 0:
                if  old_ry_thumb < stick_thresh and value > stick_thresh:
                    print("right stick pressed up!")
                    r_stick_y_a = 1
                    timestamps.append([R_UP, time.time()])
            else:
                if  abs(old_ry_thumb) < stick_thresh and abs(value) > stick_thresh:
                    print("right stick pressed down!") 
                    r_stick_y_a = -1
                    timestamps.append([R_DOWN, time.time()])
            old_ry_thumb = value

        if axis == "l_thumb_x":
            if abs(value) < 0.2 and l_stick_x_a != 0:
                print("l_thumb_x reset to the center!")
                if l_stick_x_a == -1:
                    timestamps.append([L_LEFT, time.time()])
                elif l_stick_x_a == 1:
                    timestamps.append([L_RIGHT, time.time()])
                else:
                    assert 0, "this case shouldn't be reached"
                l_stick_x_a = 0
            elif value > 0:
                if  old_lx_thumb < stick_thresh and value > stick_thresh:
                    print("left stick pressed to the right!")
                    l_stick_x_a = 1
                    timestamps.append([L_RIGHT, time.time()])
            else:
                if abs(old_lx_thumb) < stick_thresh and abs(value) > stick_thresh:
                    print("left stick pressed to the left!") 
                    l_stick_x_a = -1
                    timestamps.append([L_LEFT, time.time()])
            old_lx_thumb = value
        
        if axis == "l_thumb_y":
            if abs(value) < 0.2 and l_stick_y_a != 0:
                print("l_thumb_y reset to the center!")
                if l_stick_y_a == -1:
                    timestamps.append([L_DOWN, time.time()])
                elif l_stick_y_a == 1:
                    timestamps.append([L_UP, time.time()])
                else:
                    assert 0, "this case shouldn't be reached"
                l_stick_y_a = 0
            elif value > 0:
                if  old_ly_thumb < stick_thresh and value > stick_thresh:
                    print("left stick pressed up!")
                    l_stick_y_a = 1
                    timestamps.append([L_UP, time.time()])
            else:
                if  abs(old_ly_thumb) < stick_thresh and abs(value) > stick_thresh:
                    print("left stick pressed down!") 
                    l_stick_y_a = -1
                    timestamps.append([L_DOWN, time.time()])
            old_ly_thumb = value

    num_args = len(sys.argv)
    assert num_args == 3, "specify recording location & duration (in seconds)"

    results_dir = os.path.join(str(sys.argv[1]))
    if not os.path.exists(results_dir):
        os.mkdir(results_dir)

    run_duration = float(sys.argv[2])
    start_time = time.perf_counter()

    while time.perf_counter() - start_time < run_duration:
        j.dispatch_events()
        time.sleep(.01)
        
        ### right stick (mouse movement)
        if r_stick_x_a == 1:
            m.move(5, 0)
        elif r_stick_x_a == -1:
            m.move(-5, 0)

        if r_stick_y_a == 1:
            m.move(0, -5)
        elif r_stick_y_a == -1:
            m.move(0, 5)
        
        ### left stick (WASD)
        if l_stick_x_a == 1:
            k.PressKey(k.D)
            k.ReleaseKey(k.A)
        elif l_stick_x_a == 0:
            k.ReleaseKey(k.D)
            k.ReleaseKey(k.A)
        elif l_stick_x_a == -1:
            k.PressKey(k.A)
            k.ReleaseKey(k.D)
        
        if l_stick_y_a == 1:
            k.PressKey(k.W)
            k.ReleaseKey(k.S)
        elif l_stick_y_a == 0:
            k.ReleaseKey(k.S)
            k.ReleaseKey(k.W)
        elif l_stick_y_a == -1:
            k.PressKey(k.S)
            k.ReleaseKey(k.W)
        
        if r_trig_a :
            # dig, left mouse / right trigger
            m.press(mouse.Button.left)
        else:
            m.release(mouse.Button.left)

        if l_trig_a:
            # place, right mouse / left trigger
            m.press(mouse.Button.right)
        else:
            m.release(mouse.Button.right)

    save_path = os.path.join(results_dir, 'actions.csv')
    a = np.asarray(timestamps)
    np.savetxt(save_path, a, delimiter=",")