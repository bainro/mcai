'''
  Save screenshots and timestamps for syncing with action & rewards.
'''

import pandas as pd
import numpy as np
import queue
import time
import sys
import mss
import cv2
import os

sct = mss.mss()

'''
    Assumes 800x600 screen resolution & windowed game in top-left @ 400x300.
    Could use the controller/mouse to specify the exact window location.
    Wwould enable a more general solution. Removing the need for controller 
    would be great too.
'''
roi = {
  "top": 30,
  "left": 0, 
  "width": 400, 
  "height": 300
}

if __name__ == "__main__":
    num_args = len(sys.argv)
    assert num_args == 3, "specify recording location & duration (in seconds)"
    results_dir = os.path.join(str(sys.argv[1]))
    if not os.path.exists(results_dir):
        os.mkdir(results_dir)

    gray_dir = os.path.join(results_dir, "gray")
    if not os.path.exists(gray_dir):
        os.mkdir(gray_dir)

    run_duration = float(sys.argv[2])
    start_time = time.perf_counter()
    elapsed = 0
    i = -1

    timestamps = []

    while elapsed < run_duration:
        # save region of interest & ignore the transparency/alpha ch
        display_roi = np.asarray(sct.grab(roi), dtype=np.uint8)[:,:,:-1]
        gray = cv2.cvtColor(display_roi, cv2.COLOR_BGR2GRAY)
        save_path = os.path.join(gray_dir, str(i).zfill(6) + '.png')
        cv2.imwrite(save_path, gray)
        timestamps.append(time.time())
    
        if i == -1:
            print("skipping first loop because usually too slow")
            start_time = time.perf_counter()
            print("\n", "[grab.py] start_time: ", time.time())    
            timestamps.pop(-1)
            os.remove(save_path)

        i += 1
        elapsed = time.perf_counter() - start_time

    save_path = os.path.join(results_dir, 'states.csv')
    a = np.asarray(timestamps)
    np.savetxt(save_path, a, delimiter=",")