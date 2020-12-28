import os
import platform
import subprocess
import time
import tkinter as tk

import simpleaudio as sa
from PIL import Image, ImageTk
from util import logger


def _center(win):
    """
    centers a tkinter window
    modified from: https://stackoverflow.com/a/10018670
    """
    win.update_idletasks()
    width = win.winfo_width()
    frm_width = win.winfo_rootx() - win.winfo_x()
    win_width = width + 2 * frm_width
    height = win.winfo_height()
    titlebar_height = win.winfo_rooty() - win.winfo_y()
    win_height = height + titlebar_height + frm_width
    x = win.winfo_screenwidth() // 2 - win_width // 2
    y = win.winfo_screenheight() // 2 - win_height // 2
    win.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    win.deiconify()


def _nux_notify(title, msg='', *, icon='masjid'):
    if platform.machine().startswith("arm"):
        logger.warning("Notification not supported in Raspberry Pi or other arm-based machines")
        return
    import notify2
    notify2.init("Adzan")
    n = notify2.Notification(title, msg, icon=icon)
    n.set_hint("desktop-entry", "Adzan")
    n.set_hint("suppress-sound", True)
    n.show()
    return n


# TODO: implement this without toast64.exe
def _win_notify(title, msg=' '):
    # using 'toast64' from https://github.com/go-toast/toast
    icon = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src', 'icon.png')
    cmd = [
            'toast64.exe',
            '--app-id', "Jadwal Sholat",
            '--title', title,
            '--message', msg,
            '--icon', str(icon),
            '--action', 'Lihat waktu sholat',
            '--action-arg', 'adzan:data'
        ]
    logger.info("Command: "+" ".join(cmd))
    return subprocess.call(cmd, stdout=subprocess.DEVNULL)


if platform.system() == "Windows":
    notify = _win_notify
elif platform.system() == "Linux":
    notify = _nux_notify
else:
    raise NotImplementedError


class Popup(tk.Toplevel):
    def __init__(self):
        tk.Toplevel.__init__(self)
        self.master.withdraw()
        self.IMAGE_PATH = os.path.join("src", "bg")
        self.X_PATH = os.path.join("src", "x")
        self.WIDTH, self.HEIGTH = 450, 250
        self.overrideredirect(1)
        self.geometry('{}x{}'.format(self.WIDTH, self.HEIGTH))
        self.audio = ""
        self.running = False

    def show(self, msg: str, audio: str, *, test=False):
        self.audio = audio
        self.lift()
        # self.attributes('-topmost', True)
        canvas = tk.Canvas(self, width=self.WIDTH, height=self.HEIGTH)
        canvas.pack()

        bg_img = ImageTk.PhotoImage(Image.open(self.IMAGE_PATH).resize((self.WIDTH, self.HEIGTH), Image.ANTIALIAS))
        canvas.background = self.bg = bg_img  # Keep a reference in case this code is put in a function.
        canvas.create_image(0, 0, anchor=tk.NW, image=bg_img)  # assign this to variable to get the id
        x_img = ImageTk.PhotoImage(Image.open(self.X_PATH).resize((50, 50), Image.ANTIALIAS))

        # assign all of these to variable to get the ids
        button_window = canvas.create_image(self.WIDTH / 2, 3 * self.HEIGTH / 4, image=x_img)
        canvas.create_text(self.WIDTH / 2, 1 * self.HEIGTH / 8, font=('lobster', 30), text="Adzan Notification")
        canvas.create_text(self.WIDTH / 2, 2 * self.HEIGTH / 5, font=('Noto Sans Mono', 14), text=msg, width=400)
        # binding mouse click
        canvas.tag_bind(button_window, '<Button-1>', self.close)
        _center(self)
        self.running = True
        wvObj = sa.WaveObject.from_wave_file(self.audio)
        adzan = wvObj.play()
        while self.running:
            self.update()
            self.update_idletasks()
            if test:
                time.sleep(20)
                self.close()
                break
            if not adzan.is_playing():
                self.close()
                break
        adzan.stop()

    def close(self, event=""):
        self.attributes('-topmost', False)
        self.withdraw()
        self.running = False

