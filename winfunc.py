import ctypes
# import sys
import subprocess
import os


# old notification
def _notify(title, msg=' ', icon="main.ico"):
    pass
    # return toaster.show_toast(title, msg, icon)

def notify(title, msg=' '):
    # using 'toast64' from https://github.com/go-toast/toast
    icon = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src', 'icon.png')
    cmd = [
            'toast64.exe',
            '--app-id', "Jadwal Sholat",
            '--title', title,
            '--message', msg,
            '--icon', str(icon)
        ]
    print(icon)
    return subprocess.call(cmd[0:9])


def _w(const: int) -> int:
    return ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), const)


def hideWindow():
    subprocess.call("cls")
    _w(0)
    notify("Jadwal Sholat is running", "click icon n sys tray to set")


def showConsole():
    return _w(1)


if __name__ == "__main__":
    print(notify("tes", 'hey'))
