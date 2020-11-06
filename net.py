import json
import logging
import os
import sys
from datetime import date

import requests
from requests import HTTPError

from setting import Settings

# Log stuff
logger = logging.getLogger(__name__)
chndl = logging.StreamHandler(sys.stdout)
fhndl = logging.FileHandler("adzan.log")
cf = logging.Formatter("%(name)s - %(level)s => %(msg)s")
ff = logging.Formatter("%(asctime)s  | %(name)s{PID:%(process)d} - %(level)s => %(msg)s")
chndl.setFormatter(cf)
fhndl.setFormatter(ff)
logger.setLevel(logging.INFO)


API_ENDPOINT = "http://api.aladhan.com/v1/calendarByCity"
today = date.today()
root_dir = os.path.dirname(__file__)

# Settings file
settings = Settings("settings.ini")


class NoConnectionError(BaseException): pass


def get_location():
    req = requests.get("https://freegeoip.app/json")
    logger.info("kota ip")
    data = req.json()
    return [data['city'], data["country_code"]]


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
        logger.error("NO INTERNET!!")
        return False


def get_data() -> dict or bool:
    """

    :param kota: Nama kota
    :return: Dictionary data if data for specified city is available, otherwise return False
    """
    if not check_connection():
        return False
    logger.info(settings.data)
    r = requests.get(API_ENDPOINT, params=settings.data)
    try:
        r.raise_for_status()
    except HTTPError:
        logger.exception(f"HTTP Error occured!, please fix your api parameter(s) in 'settings.ini' file\n"
                         f"HTTP: {r.status_code}")
        return

    return r.json()


def save_data(data: dict):
    data_dir = os.path.join(root_dir, "data")
    if not os.path.isdir(data_dir):
        logger.info("Data directory not exist, creating dir...")
        os.mkdir("data")
    filename = os.path.join(data_dir, f"{settings.city}-{today.month}-{today.year}.json")
    if data:
        with open(filename, 'w') as file:
            file.write(json.dumps(data))
            logger.info(f"Data {filename} saved")
    else:
        raise NoConnectionError


def load_data(file):
    logger.info("file loaded")
    with open(file) as f:
        data = json.load(f)
    d = {**data["data"][today.day - 1]["timings"]}
    return d


def today_data() -> dict or None:
    if not settings.available:
        logger.info("No city provided in setting")
        settings.open_file()
        settings.wait_for_edit()
    filename = os.path.join(root_dir, "data", f"{settings.city}-{today.month}-{today.year}.json")
    if os.path.exists(filename):
        logger.info(f"File exist, loading file: {filename}")
        return load_data(filename)
    else:
        try:
            data = get_data()
            save_data(data)
        except NoConnectionError:
            logger.warning("no internet")
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
