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
from util import logger, uninterruptible_sleep, Settings
import net
from gui import notify, Popup


# constants
today = date.today()
s = sched.scheduler(time.time, uninterruptible_sleep)  # using uninterruptible_sleep() from util
root_dir = os.path.dirname(__file__)
src_dir = os.path.join(root_dir, "src")
WINDOWS = platform.system() == "Windows"
settings = Settings("settings.ini")


def pause_media(app: str) -> list or None:
    if not app or WINDOWS:
        return
    try:
        pids = list(map(int, subprocess.check_output(['pidof', app]).split()))
    except subprocess.CalledProcessError:
        return None
    for pid in pids:
        os.kill(pid, signal.SIGSTOP)
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
        kota = settings.city.capitalize()
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


def main(re=""):
    try:
        data = net.today_data()
        greet = f"Notifikasi Adzan {re}started"
        notify(greet)
        if re:
            logger.info(greet)
        net.print_data(data)
        schedule(data)
        try:
            s.run()
        except RuntimeError:
            for event in s.queue:
                s.cancel(event)
            return main("re")
    finally:
        os.remove(".pid")


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
            main()
    except KeyboardInterrupt:
        logger.error(f"User interupt or sys exit")
        raise
    except Exception as e:
        logger.exception(str(e)+'\n')
        notify("Adzan Notification error!", str(e))
