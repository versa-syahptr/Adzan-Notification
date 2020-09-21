import configparser
import json
import os

import requests
from datetime import date
from requests import HTTPError
from pymsgbox import confirm, prompt
# from main import APP_NAME


API_ENDPOINT = "https://api.pray.zone/v2/times/this_month.json"
today = date.today()
config = configparser.ConfigParser()
CFG = "settings.cfg"
settings = config.read(CFG)
root_dir = os.path.dirname(__file__)


class NoConnectionError(BaseException): pass


def get_kota():
    req = requests.get("https://freegeoip.app/json")
    print("kota ip")
    return req.json()["city"]


def ask_city():
    pr = lambda x: prompt(title="Jadwal Sholat", text="Masukan lokasi anda", default=x)
    if check_connection():
        city = get_kota()
        ask = confirm(title="Jadwal Sholat", text=f"Lokasi anda yang terdeteksi adalah\n Kota {city}", buttons=("Benar", "Salah"))
        if ask == 'Salah':
            city = pr(city)
    else:
        city = pr("")
        while not city:
            city = pr("")
            continue

    print(city)
    config["settings"] = dict(kota=city)
    with open(CFG, 'w') as f:
        config.write(f)


def check_connection() -> bool:
    """
    check internet connection
    :return True when connection successful, either False:
    """
    try:
        requests.get("https://google.com", timeout=5)
        return True
    except Exception:
        return False


def get_data(kota: str) -> dict or bool:
    """

    :param kota: Nama kota
    :return: Dictionary data if data for specified city is available, otherwise return False
    """
    if not check_connection():
        return False

    r = requests.get(API_ENDPOINT, params={"city": kota, "school": 10})
    try:
        r.raise_for_status()
    except HTTPError as e:
        print(e)
        return

    return r.json()


def save_data(data: dict):
    kota = config["settings"]['kota']
    if not os.path.exists("data"):
        os.mkdir("data")
    filename = os.path.join(root_dir, "data", f"{kota}-{today.month}-{today.year}.json")
    if data:
        with open(filename, 'w') as file:
            file.write(json.dumps(data))
            print("saved")
    else:
        raise NoConnectionError


def load_data(file):
    with open(file) as f:
        data = json.load(f)
    return {**data["results"]["datetime"][today.day - 1]["times"], **data["results"]["location"]}


def today_data() -> dict or None:
    if not settings:
        ask_city()
    kota = config["settings"]['kota']
    filename = os.path.join(root_dir, "data", f"{kota}-{today.month}-{today.year}.json")
    if os.path.exists(filename):
        return load_data(filename)
    else:
        try:
            data = get_data(kota)
            save_data(data)
        except NoConnectionError:
            print("no internet")
            return
        return load_data(filename)