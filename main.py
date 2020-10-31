#!./env/bin/python3.7

import logging
import os
import platform
import sched
import subprocess
import sys
import time
from datetime import datetime, date
from queue import Queue, Empty
from threading import Thread

import simpleaudio as sa

import net
from gui import notify, Popup
from net import settings

if platform.system() == "Windows":
    import psutil

# Log stuff
logger = logging.getLogger(__name__)
chndl = logging.StreamHandler()
fhndl = logging.FileHandler("adzan.log")
cf = logging.Formatter("%(name)s | %(levelname)s => %(msg)s")
ff = logging.Formatter("%(asctime)s  | %(name)s{PID:%(process)d} - LOG:%(levelname)s => %(msg)s")
chndl.setLevel(logging.INFO)
fhndl.setLevel(logging.WARNING)
chndl.setFormatter(cf)
fhndl.setFormatter(ff)
logger.addHandler(chndl)
logger.addHandler(fhndl)


# constants
APP_NAME = "Adzan Notification"
today = date.today()
s = sched.scheduler(time.time, time.sleep)
root_dir = os.path.dirname(__file__)
src_dir = os.path.join(root_dir, "src")
q = Queue(maxsize=1)
popup = Popup()


# FUNCTIONS
def ps_start():
    if platform.system() == "Windows":
        pname = psutil.Process(os.getpid()).name()
        p = subprocess.Popen(["psHandler.exe", pname], start_new_session=True)
        pid = str(p.pid)
        logger.info(f"ps started with pid: {pid}")
        with open("ps.pid", 'w') as f:
            f.write(pid)


def ps_stop():
    if platform.system() == "Windows":
        with open("ps.pid") as f:
            pid = int(f.read())
            os.kill(pid, 9)
        os.remove("ps.pid")


def do_adzan(solat: str, test=False):
    kota = net.settings.city
    audio = settings.audio.subuh if 'fajr' in solat.lower() else settings.audio.other
    audio_file = os.path.join(src_dir, audio)
    logger.info(f"Audio file: {audio_file}")
    now = datetime.now().strftime('%H:%M')
    msg = f"Waktu sholat {solat} pukul {now} untuk Kota {kota} dan sekitarnya"
    notify(title=f"Waktu sholat {solat} di {kota}", msg=msg)
    logger.info(msg)
    wvObj = sa.WaveObject.from_wave_file(audio_file)
    adzan = wvObj.play()
    q.put(msg)  # show the popup
    if test:
        time.sleep(20)
        adzan.stop()
    else:
        while adzan.is_playing():
            try:
                data = popup.q.get(timeout=0.5)
            except Empty:
                continue
            else:
                logger.info(data)
                adzan.stop()

    popup.close()


def show_popup(test=False):
    while True:
        if s.empty() and not test:
            break
        msg = q.get()
        popup.show(msg)
        if test:
            break


def schedule(jadwal: dict) -> list:
    event = []
    sholat_list = ["fajr", "dhuhr", "asr", "maghrib", "isha"]
    if not jadwal:
        notify("Notifikasi Adzan Error", "No internet or something else")
        sys.exit(-1)
    for nama, waktu in jadwal.items():
        print(nama, waktu)
        waktu = waktu.split()[0]
        if nama.lower() in sholat_list:
            timestamp = time.mktime(time.strptime(f"{today} {waktu}", "%Y-%m-%d %H:%M"))
            if timestamp > time.time():
                event.append(s.enterabs(timestamp, 1, do_adzan, argument=(nama,)))
    return event


def test():
    Thread(target=do_adzan, args=("", True), daemon=True).start()
    show_popup(True)


def sleep():
    if getattr(sys, "frozen", False):
        print("run.exe")
        subprocess.Popen("run.exe")
    else:
        subprocess.Popen("winHelper.py", shell=True)
        print("py")
    print("slept")
    sys.exit(0)


def main():
    t = Thread(target=s.run, daemon=True)
    try:
        global events
        notify("Notifikasi Adzan started")
        data = net.today_data()
        events = schedule(data)
        t.start()
        show_popup()  # func to wait the queue
    except KeyboardInterrupt:
        logger.exception("User interupt")
    finally:
        if os.path.exists(".pid"):
            os.remove(".pid")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1].lower() == "-t":
            test()
    else:
        try:
            ps_start()
            main()
            ps_stop()
        except Exception as e:
            logger.exception(e)
