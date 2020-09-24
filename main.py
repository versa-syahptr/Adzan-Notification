#!./env/bin/python3.7

import platform
import sched
import os
import time
import sys
import net

from datetime import datetime, date
import simpleaudio as sa

system = platform.system()
# platform constants
ISDOS = system == "Windows"
ISNUX = system == "Linux"
# platform spesific import
if ISDOS:
    from winfunc import notify
elif ISNUX:
    from linux import notify


# comnstants
APP_NAME = "Adzan Notification"
today = date.today()
s = sched.scheduler(time.time, time.sleep)
root_dir = os.path.dirname(__file__)
src_dir = os.path.join(root_dir, "src")
notifications = []


# FUNCTIONS
def do_adzan(solat:str, kota:str):
    audio = f"{solat}.wav" if "fajr" in solat.lower() else "adzan.wav"
    audio_file = os.path.join(src_dir, audio)
    now = datetime.now().strftime('%H:%M')
    n = notify(title=f"Waktu sholat {solat} di {kota}", msg=f"Waktu sholat {solat} pukul {now} di {net.settings.city}.")
    notifications.append(n)
    wvObj = sa.WaveObject.from_wave_file(audio_file) 
    adzan = wvObj.play()
    adzan.wait_done()


def schedule(jadwal: dict) -> list:
    event = []
    sholat_list = ["fajr", "dhuhr", "asr", "maghrib", "isha"]
    if not jadwal:
        notify("Notifikasi Adzan Error", "No internet or something else")
        sys.exit(1)
    for nama, waktu in jadwal.items():
        print(nama, waktu)
        waktu = waktu.split()[0]
        if nama.lower() in sholat_list:
            timestamp = time.mktime(time.strptime(f"{today} {waktu}", "%Y-%m-%d %H:%M"))
            if timestamp > time.time():
                event.append(s.enterabs(timestamp, 1, do_adzan, argument=(nama,)))
    return event


events = []


def main():
    try:
        global events
        notifications.append(notify("Notifikasi Adzan started"))
        # data = fetcher.init()
        data = net.today_data()
        events = schedule(data)
        s.run()
    except KeyboardInterrupt:
        for event in events:
            s.cancel(event)
        for notif in notifications:
            notif.close()
    finally:
        if ISNUX:
            os.remove(".pid")


if __name__ == "__main__":
    main()

