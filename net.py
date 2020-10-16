import json
import os
from datetime import date

import requests
from pymsgbox import confirm, prompt
from requests import HTTPError

from setting import Settings

OLD_API_ENDPOINT = "https://api.pray.zone/v2/times/this_month.json"
API_ENDPOINT = "http://api.aladhan.com/v1/calendarByCity"
today = date.today()
root_dir = os.path.dirname(__file__)

# Settings file
CFG = "settings.cfg"
settings = Settings(CFG)


class NoConnectionError(BaseException): pass


def get_location():
    req = requests.get("https://freegeoip.app/json")
    print("kota ip")
    data = req.json()
    return {"city": data['city'], "country": data["country_code"]}


def ask_city():
    """
    show gui popup to ask user city
    :return: str citi name
    """
    pr = lambda x: prompt(title="Jadwal Sholat", text="Masukan lokasi anda", default=x)
    if check_connection():
        city = get_location()
        ask = confirm(title="Jadwal Sholat", text=f"Lokasi anda yang terdeteksi adalah\n Kota {city}",
                      buttons=("Benar", "Salah"))
        if ask == 'Salah':
            city = pr(city)
    else:
        city = pr("")
        while not city:
            city = pr("")
            continue
    return city


def check_city(**data) -> bool:
    r = requests.head(API_ENDPOINT, params=data)
    return r.headers


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


def get_data() -> dict or bool:
    """

    :param kota: Nama kota
    :return: Dictionary data if data for specified city is available, otherwise return False
    """
    if not check_connection():
        return False
    print(settings.data)
    r = requests.get(API_ENDPOINT, params=settings.data)
    try:
        r.raise_for_status()
    except HTTPError as e:
        print(e)
        return

    return r.json()


def save_data(data: dict):
    data_dir = os.path.join(root_dir, "data")
    if not os.path.isdir(data_dir):
        os.mkdir("data")
    filename = os.path.join(data_dir, f"{settings.city}-{today.month}-{today.year}.json")
    if data:
        with open(filename, 'w') as file:
            file.write(json.dumps(data))
            print("saved")
    else:
        raise NoConnectionError


def load_data(file):
    print("file loaded")
    with open(file) as f:
        data = json.load(f)
    return {**data["data"][today.day - 1]["timings"]}


def today_data() -> dict or None:
    # if not settings.are_available:
    #     settings.city = ask_city()
    #     settings.set_default()
    #     print(settings.data)
    filename = os.path.join(root_dir, "data", f"{settings.city}-{today.month}-{today.year}.json")
    if os.path.exists(filename):
        return load_data(filename)
    else:
        try:
            data = get_data()
            save_data(data)
        except NoConnectionError:
            print("no internet")
            return
        return load_data(filename)


def print_data():
    """ future development """
    data = today_data()
    for key, value in data.items():
        print(f"{key}:({value})")


if __name__ == '__main__':
    print(check_city(city="beaksi", country="id"))
    # print(today_data())