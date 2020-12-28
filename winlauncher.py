import os
from os import path
import sys
from time import sleep
import tempfile
import subprocess
from psutil import pid_exists
import multiprocessing as mp
from pymsgbox._native_win import alert, WARNING, INFO


"""
FILE        : winlauncher.py
AUTHOR      : Versa Syahputra
Description : Adzan Notification entry point for Windows
"""


normal_dir = path.abspath(path.dirname(path.realpath(__file__)))  # normal python bundle_dir
bundle_dir = getattr(sys, "_MEIPASS", normal_dir)  # bundled dir
os.chdir(bundle_dir)
print(os.getcwd())


from main import main       # must import after changing dir
from util import logger
process = mp.Process(target=main, daemon=True)


def get_pid():
    if os.path.exists(".pid"):
        with open(".pid", 'r') as f:
            try:
                pid = int(f.read())
            except ValueError:
                pid = -1
    else:
        pid = -1

    return pid


def start():
    pid = get_pid()
    if pid_exists(pid):
        alert(f"Process already started with pid: {pid}", "Adzan Service already started!", icon=WARNING)
        sys.exit()

    process.start()
    with open(".pid", 'w+') as f:
        f.write(str(process.pid))
    print(f"Proess started with pid: {process.pid}")
    sleep(1)
    os._exit(0)


def stop():
    pid = get_pid()
    if pid_exists(pid):
        os.kill(pid, 9)
        print("process stoped")
        alert("Adzan Notification Stopped.", "Adzan Notification", icon=INFO)
        return
    else:
        alert("No Adzan-Notification process exists", "Adzan Notification", icon=INFO)
        sys.exit(-1)


def restart():
    stop()
    sleep(1)
    start()


def data():
    from net import print_data
    fmt = print_data(format_only=True)
    tmp = tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, prefix="Waktu Sholat [", suffix="]")
    print(tmp.name)
    tmp.write(fmt)
    tmp.seek(0)
    tmp.close()
    subprocess.run(["notepad.exe", tmp.name])
    os.remove(tmp.name)


if __name__ == '__main__':
    mp.set_start_method("spawn")
    mp.freeze_support()
    if len(sys.argv) > 1:
        arg = str(sys.argv[1])
        if ":" in arg:
            arg = arg.split(':')[1]  # app link, eg: "adzan:start"
        if arg == "start":
            start()
        elif arg == "stop":
            stop()
        elif arg == "restart":
            restart()
        elif arg == "data":
            data()
        else:
            alert(f'Unknown param "{arg}"', "Adzan Notification", icon=WARNING)
            logger.error(f"Unknown param {arg}")
    else:
        start()
