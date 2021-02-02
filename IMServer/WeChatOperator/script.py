# Draft script

# %%
import win32api
import win32con
import win32gui
import win32clipboard as wc
import pywintypes
import pandas as pd

import time
from .keyboard import key_press
from .keyboard import key_press_combine

# %%


def getCopy():
    ''' Get contents in the clipboard '''
    wc.OpenClipboard()
    t = wc.GetClipboardData(win32con.CF_UNICODETEXT)
    wc.CloseClipboard()
    return t


def setCopy(str):
    '''
    Set [str] to the clipboard
    - @str: Strint to be set in the clipboard
    '''
    wc.OpenClipboard()
    wc.EmptyClipboard()
    wc.SetClipboardData(win32con.CF_UNICODETEXT, str)
    wc.CloseClipboard()


# %%


class Windows(object):
    def __init__(self):
        self.hwnd_df = pd.DataFrame()

    def update(self, obj):
        self.hwnd_df = self.hwnd_df.append(obj, ignore_index=True)

    def find_by_title(self, title):
        return self.hwnd_df.query(f'title=="{title}"')


# wns = Windows()


# def get_all_hwnd(hwnd, mouse):
#     if all([win32gui.IsWindow(hwnd),
#             win32gui.IsWindowEnabled(hwnd),
#             win32gui.IsWindowVisible(hwnd)]):
#         wns.update(dict(
#             hwnd=hwnd,
#             title=win32gui.GetWindowText(hwnd)
#         ))


# win32gui.EnumWindows(get_all_hwnd, 0)

# wns.hwnd_df

# %%
# f_hwnd = win32gui.GetForegroundWindow()

# %%
# hwnd = wns.find_by_title('微信')['hwnd'].values[0]
# win32gui.SetForegroundWindow(int(hwnd))

# %%
# setCopy(time.ctime())
# print(getCopy())
# key_press_combine('v')
# key_press('enter')

# %%
# win32gui.SetForegroundWindow(f_hwnd)
# key_press_combine('tab', 'alt')

# %%


class WeChatOperator(object):
    def __init__(self):
        self.enum_windows()

    def enum_windows(self):
        ''' Enumerate existing windows '''
        self.wns = Windows()

        def get_all_hwnd(hwnd, mouse):
            ''' Handlers on enumerating windows by win32gui.EnumWindows'''
            if all([win32gui.IsWindow(hwnd),
                    win32gui.IsWindowEnabled(hwnd),
                    win32gui.IsWindowVisible(hwnd)]):
                self.wns.update(dict(
                    hwnd=hwnd,
                    title=win32gui.GetWindowText(hwnd)
                ))

        win32gui.EnumWindows(get_all_hwnd, 0)

        return self.wns.hwnd_df

    def write_message(self, message):
        stack = []
        stack.append(win32gui.GetForegroundWindow())

        hwnd = self.wns.find_by_title('微信')['hwnd'].values[0]
        win32gui.SetForegroundWindow(int(hwnd))

        setCopy(message)
        print(getCopy())
        key_press_combine('v')
        key_press('enter')

        for e in stack:
            win32gui.SetForegroundWindow(e)

        return 0

    def display_wechat(self):
        self.enum_windows()

        stack = []
        stack.append(win32gui.GetForegroundWindow())

        hwnd = self.wns.find_by_title('微信')['hwnd'].values[0]
        win32gui.SetForegroundWindow(int(hwnd))
        time.sleep(0.01)

        for e in stack:
            try:
                win32gui.SetForegroundWindow(e)
            except pywintypes.error:
                continue

        return 0
