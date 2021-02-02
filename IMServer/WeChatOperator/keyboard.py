# Keyboard Event Simulator
# %%
import win32api
import win32con
import time

from . import VK_CODE

# %%


def key_press(c=''):
    win32api.keybd_event(VK_CODE[c], 0, 0, 0)
    win32api.keybd_event(VK_CODE[c], 0, win32con.KEYEVENTF_KEYUP, 0)
    time.sleep(0.01)


def key_press_combine(c='', down='ctrl'):
    win32api.keybd_event(VK_CODE[down], 0, 0, 0)
    time.sleep(0.01)
    key_press(c)
    win32api.keybd_event(VK_CODE[down], 0, win32con.KEYEVENTF_KEYUP, 0)
    time.sleep(0.01)


def key_input(str=''):
    for c in str:
        key_press(c)

# %%
