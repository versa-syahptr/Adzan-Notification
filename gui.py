import os
import platform
import subprocess
import tkinter as tk
from queue import Queue

from PIL import Image, ImageTk


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
    import notify2
    notify2.init("Adzan")
    n = notify2.Notification(title, msg, icon=icon)
    n.set_hint("desktop-entry", "Adzan")
    n.set_hint("suppress-sound", True)
    n.show()
    return n

def _win_notify(title, msg=' '):
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
    return subprocess.call(cmd)

# class Gui:
#     def __init__(self):
#         self.root = tk.Tk()
#         self.WIDTH, self.HEIGTH = 450, 250
#         # self.root.overrideredirect(1)
#         self.popup_exist = False
#         self.root.withdraw()
#
#     def show_popup(self, msg, audio_path, test=False):
#         """
#         show popup & play adzan sound
#         :param msg: string -> message on popup
#         :param audio_path -> str path to audio file
#         :param test: bool -> for testing
#         :return: None
#         """
#         self.popup_exist = True
#         IMAGE_PATH = os.path.join("src", "bg")
#         X_PATH = os.path.join("src", "x")
#         WIDTH, HEIGTH = 450, 250
#         popup = tk.Toplevel()
#         popup.overrideredirect(1)
#         popup.geometry('{}x{}'.format(WIDTH, HEIGTH))
#         # Audio
#         #
#         # GUI Canvas
#         canvas = tk.Canvas(popup, width=WIDTH, height=HEIGTH)
#         canvas.pack()
#
#         bg_img = ImageTk.PhotoImage(Image.open(IMAGE_PATH).resize((WIDTH, HEIGTH), Image.ANTIALIAS))
#         canvas.background = bg_img  # Keep a reference in case this code is put in a function.
#         canvas.create_image(0, 0, anchor=tk.NW, image=bg_img)  # assign this to variable to get the id
#         x_img = ImageTk.PhotoImage(Image.open(X_PATH).resize((50, 50), Image.ANTIALIAS))
#
#         # assign all of these to variable to get the ids
#         button_window = canvas.create_image(WIDTH / 2, 3 * HEIGTH / 4, image=x_img)
#         canvas.create_text(WIDTH / 2, 1 * HEIGTH / 8, font=('lobster', 30), text="Adzan Notification")
#         canvas.create_text(WIDTH / 2, 2 * HEIGTH / 5, font=('Noto Sans Mono', 14), text=msg, width=400)
#         # binding mouse click
#         canvas.tag_bind(button_window, '<Button-1>', lambda x: popup.quit())
#
#         def quit_after():
#             """
#             quiter func thread
#             """
#             print(t.getName())
#             if test:
#                 sleep(20)
#             else:
#                 # adzan.wait_done()
#             # if self.popup_exist:
#             #     self.__quit()
#                 popup.quit()
#             return
#
#         _center(popup)
#         # Thread to stop gui
#         t = Thread(target=quit_after, daemon=True)
#         t.start()
#         # popup.after(500, quit_after)
#         # popup mainloop
#         popup.mainloop()
#         # adzan.stop()
#
#     def __quit(self, event="no"):
#         print(event)
#         self.root.destroy()
#         self.popup_exist = False


class Popup(tk.Toplevel):
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()
        super().__init__(self.root)
        self.IMAGE_PATH = os.path.join("src", "bg")
        self.X_PATH = os.path.join("src", "x")
        self.WIDTH, self.HEIGTH = 450, 250
        self.overrideredirect(1)
        self.geometry('{}x{}'.format(self.WIDTH, self.HEIGTH))
        self.q = Queue(maxsize=1)

    def show(self, msg):
        canvas = tk.Canvas(self, width=self.WIDTH, height=self.HEIGTH)
        canvas.pack()

        bg_img = ImageTk.PhotoImage(Image.open(self.IMAGE_PATH).resize((self.WIDTH, self.HEIGTH), Image.ANTIALIAS))
        canvas.background = bg_img  # Keep a reference in case this code is put in a function.
        canvas.create_image(0, 0, anchor=tk.NW, image=bg_img)  # assign this to variable to get the id
        x_img = ImageTk.PhotoImage(Image.open(self.X_PATH).resize((50, 50), Image.ANTIALIAS))

        # assign all of these to variable to get the ids
        button_window = canvas.create_image(self.WIDTH / 2, 3 * self.HEIGTH / 4, image=x_img)
        canvas.create_text(self.WIDTH / 2, 1 * self.HEIGTH / 8, font=('lobster', 30), text="Adzan Notification")
        canvas.create_text(self.WIDTH / 2, 2 * self.HEIGTH / 5, font=('Noto Sans Mono', 14), text=msg, width=400)
        # binding mouse click
        canvas.tag_bind(button_window, '<Button-1>', self.close)
        _center(self)
        self.mainloop()

    def close(self, event=""):
        if event:
            self.q.put(False)
        self.destroy()
        self.quit()


if platform.system() == "Windows":
    notify = _win_notify
elif platform.system() == "Linux":
    notify = _nux_notify
else:
    raise NotImplementedError

if __name__ == '__main__':
    window = Popup()
    window.show("Waktu sholat dhuhur pukul 11:41 untuk Kota bekasi dan sekitarnya")