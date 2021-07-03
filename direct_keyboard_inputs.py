# direct inputs
# source to this solution and code:
# http://stackoverflow.com/questions/14489013/simulate-python-keypresses-for-controlling-a-game
# http://www.gamespp.com/directx/directInputKeyboardScanCodes.html

import ctypes
import time

try:
    SendInput = ctypes.windll.user32.SendInput
except AttributeError:
    print("must be linux...")


ESC              = 0x01
W                = 0x11
A       = GREEN  = 0x1E # green note
S       = RED    = 0x1F # red note
D       = YELLOW = 0x20 # yellow note
F       = BLUE   = 0x21 # blue note
G       = STAR   = 0x22 # star power
Q                = 0x10 # just a Q key
SPACE   = ORANGE = 0x39 # orange note
R_SHIFT = STRUM  = 0x36 # right shift
ENTER            = 0x1C

# C struct redefinitions 
PUL = ctypes.POINTER(ctypes.c_ulong)
class KeyBdInput(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_ushort),
                ("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class HardwareInput(ctypes.Structure):
    _fields_ = [("uMsg", ctypes.c_ulong),
                ("wParamL", ctypes.c_short),
                ("wParamH", ctypes.c_ushort)]

class MouseInput(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time",ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class Input_I(ctypes.Union):
    _fields_ = [("ki", KeyBdInput),
                 ("mi", MouseInput),
                 ("hi", HardwareInput)]

class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong),
                ("ii", Input_I)]

def PressKey(hexKeyCode):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput(0, hexKeyCode, 0x0008, 0, ctypes.pointer(extra))
    x = Input(ctypes.c_ulong(1), ii_)
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

def ReleaseKey(hexKeyCode):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput(0, hexKeyCode, 0x0008 | 0x0002, 0, ctypes.pointer(extra))
    x = Input(ctypes.c_ulong(1), ii_)
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

if __name__ == '__main__':
    import threading
    from time import sleep
    import queue

    time.sleep(7)
    q = queue.Queue()

    def worker():
        while True:
            NOTES = q.get()
            print("Pressing: " + str(NOTES))
            for k in NOTES:
                PressKey(k)
            sleep(0.017)
            for k in NOTES:
                ReleaseKey(k)
            q.task_done()

    threading.Thread(target=worker, daemon=True).start()

    NOTES = [GREEN, RED, YELLOW, BLUE, ORANGE, STRUM]
    for _ in range(5):
        q.put(NOTES)

    time.sleep(3)

    # DOESN'T WORK FOR GH3!  
    # import win32com.client as comclt
    # wsh= comclt.Dispatch("WScript.Shell")
    # wsh.AppActivate("gh3.exe")
    # time.sleep(5)
    # for _ in range(20):
    #     start = time.perf_counter()
    #     wsh.SendKeys("aaaasdf")
    #     key_press_time = time.perf_counter() - start
    #     print('%.1fms' % (key_press_time * 1000)) # avg ~1.5ms per key

    # time.sleep(2)
    # for _ in range(1):
    #     PressKey(A)
    #     PressKey(ENTER)
    #     print(input(""))
        # time.sleep(0.01)
        # ReleaseKey(A)
        # time.sleep(0.01)
        # print("pressed A")