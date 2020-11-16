#!./env/bin/python3.7

import logging
import os
import platform
import sched
import signal
import subprocess
import sys
import time
from datetime import datetime, date

import net
from gui import notify, Popup
from net import settings

if platform.system() == "Windows":
    import psutil

# Log stuff
logger = logging.getLogger(__name__)
chndl = logging.StreamHandler(sys.stdout)
fhndl = logging.FileHandler("adzan.log")
cf = logging.Formatter("%(name)s | %(levelname)s => %(msg)s")
ff = logging.Formatter("%(asctime)s  | %(name)s{PID:%(process)d} - %(levelname)s => %(msg)s")
chndl.setFormatter(cf)
fhndl.setFormatter(ff)
logger.addHandler(chndl)
logger.addHandler(fhndl)
logger.setLevel(logging.INFO)


# constants
APP_NAME = "Adzan Notification"
today = date.today()
s = sched.scheduler(time.time, time.sleep)
root_dir = os.path.dirname(__file__)
src_dir = os.path.join(root_dir, "src")
media_pids = []
WINDOWS = platform.system() == "Windows"


# FUNCTIONS
def ps_start():
    if WINDOWS:
        pname = psutil.Process(os.getpid()).name()
        p = subprocess.Popen(["psHandler.exe", pname], start_new_session=True, stdout=subprocess.DEVNULL)
        pid = str(p.pid)
        logger.info(f"ps started with pid: {pid}")
        with open("ps.pid", 'w') as f:
            f.write(pid)


def ps_stop():
    if WINDOWS:
        with open("ps.pid") as f:
            pid = int(f.read())
            os.kill(pid, 9)
        os.remove("ps.pid")


def pause_media(app: str) -> list or None:
    if not app or WINDOWS:
        return
    try:
        pids = list(map(int, subprocess.check_output(['pidof', app]).split()))
    except subprocess.CalledProcessError:
        return None
    for pid in pids:
        os.kill(pid, signal.SIGSTOP)
        print(pid)
    logger.info(f"{settings.media_player} with pid: {pids} stopped")
    return pids


def resume_media(pids: list):
    if not pids:
        return
    logger.info(f"pids: {pids} resumed")
    time.sleep(1)  # add a bit delay
    for pid in pids:
        os.kill(pid, signal.SIGCONT)


def do_adzan(solat: str, test=False):
    pids = pause_media(settings.media_player)
    try:
        kota = settings.city
        audio = settings.audio.subuh if 'fajr' in solat.lower() else settings.audio.other
        audio_file = os.path.join(src_dir, audio)
        logger.info(f"Audio file: {audio_file}")
        now = datetime.now().strftime('%H:%M')
        msg = f"Waktu sholat {solat} pukul {now} untuk Kota {kota} dan sekitarnya"
        notify(title=f"Waktu sholat {solat} di {kota}", msg=msg)
        logger.info(msg)
        popup = Popup()
        popup.show(msg, audio_file, test=test)
    except Exception as ex:
        logger.exception(f"Exception occured in adzan calls!, {ex}")
        raise
    finally:
        resume_media(pids)


def schedule(jadwal: dict):
    event = []
    sholat_list = ["fajr", "dhuhr", "asr", "maghrib", "isha"]
    if not jadwal:
        notify("Notifikasi Adzan Error", "No internet or something else")
        sys.exit(-1)
    for nama, waktu in jadwal.items():
        waktu = waktu.split()[0]
        if nama.lower() in sholat_list:
            timestamp = time.mktime(time.strptime(f"{today} {waktu}", "%Y-%m-%d %H:%M"))
            if timestamp > time.time():
                s.enterabs(timestamp, 1, do_adzan, argument=(nama,))
                event.append(nama)
    logger.info(f"scheduled for adzan: {event}")


def test_func():
    logger.setLevel(logging.ERROR)  # disable INFO logging from here
    net.print_data()
    time.sleep(2)
    print("TEST MODE, adzan plays for 20 seconds")
    do_adzan("Subuh", test=True)  # test mode
    print("wait")
    time.sleep(10)
    print("NON-TEST MODE, you can quit by clicking X button or ^C")
    do_adzan("Maghrib")  # NON-Test mode
    time.sleep(2)
    print("yeeah")


def main():
    data = net.today_data()
    notify("Notifikasi Adzan started")
    net.print_data()
    schedule(data)
    s.run()


if __name__ == "__main__":
    try:
        if len(sys.argv) > 1:
            arg = sys.argv[1]
            if arg == "-t":
                test_func()
            elif arg == "-d":
                net.print_data()
            else:
                print(f"Unknown param {arg}")
        else:
            ps_start()
            main()
            ps_stop()
    except KeyboardInterrupt as e:
        logger.error(f"User interupt or sys exit: {e}")
        raise
    except Exception as e:
        logger.exception(str(e)+'\n')
