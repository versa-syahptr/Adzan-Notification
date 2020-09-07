#!./env/bin/python3.7

# imports
import platform
import sched

# import pymsgbox
from datetime import datetime, date
import os
import time
import sys
# System spesific imports
import fetcher

system = platform.system()
ISDOS = system == "Windows"
ISNUX = system == "Linux"
if ISDOS:
    from winfunc import notify
    # ssslolfrom playsound import playsound
elif ISNUX:
    from linux import notify
import simpleaudio as sa


today = date.today()
s = sched.scheduler(time.time, time.sleep)
root_dir = os.path.dirname(__file__)
src_dir = os.path.join(root_dir, "src")


# FUNCTIONS
def do_adzan(solat:str, kota:str):
    audio = f"{solat}.wav" if "subuh" in solat.lower() else "adzan.wav"
    audio_file = os.path.join(src_dir, audio)
    now = datetime.now().strftime('%H:%M')
    notify(title=f"Waktu sholat {solat} di {kota}", msg=f"Waktu sholat {solat} pukul {now} di {kota}.")
    wvObj = sa.WaveObject.from_wave_file(audio_file) 
    adzan = wvObj.play()
    adzan.wait_done()
        


def schedule(jadwal:dict) -> list:
    event = []
    sholat_list = ["subuh", "dzuhur", "ashar", "maghrib", "isya"]
    if not jadwal:
        notify("Notifikasi Adzan Error", "No internet or something else")
        sys.exit(1)
    for nama, waktu in jadwal.items():
        print(nama, waktu)
        if nama in sholat_list:
            timestamp = time.mktime(time.strptime(f"{today} {waktu}", "%Y-%m-%d %H:%M"))
            if timestamp > time.time():
                event.append(s.enterabs(timestamp, 1, do_adzan, argument=(nama, jadwal['kota'])))
    return event


events = []


def main():
    try:
        global events
        notify("Notifikasi Adzan started")
        data = fetcher.init()
        events = schedule(data)
        s.run()
    except KeyboardInterrupt:
        for event in events:
            s.cancel(event)
    finally:
        if ISNUX:
            os.remove(".pid")


if __name__ == "__main__":
    main()

