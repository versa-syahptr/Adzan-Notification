import json
import logging
import os
from datetime import date

import requests
from requests import HTTPError
from util import logger, settings


# logger = AdzanLogger(__name__)
API_ENDPOINT = "http://api.aladhan.com/v1/calendarByCity"
today = date.today()
root_dir = os.path.dirname(__file__)


class NoConnectionError(BaseException): pass


def get_location():
    req = requests.get("https://freegeoip.app/json")
    logger.info("kota ip")
    data = req.json()
    return [data['city'], data["country_code"]]


def check_city(**data) -> bool:
    r = requests.get(API_ENDPOINT, params=data)
    return r.status_code == 200


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


def download_data(*, with_filename: str) -> None:
    """

    :return: a filename string contains the data
    """
    if not check_connection():
        raise NoConnectionError

    params = settings.data
    logger.info(params)
    r = requests.get(API_ENDPOINT, params=params)
    try:
        r.raise_for_status()
    except HTTPError:
        logger.exception(f"HTTP Error occured!, please fix your api parameter(s) in 'settings.ini' file\n"
                         f"HTTP: {r.status_code}")
        raise

    data = {"params": params, **r.json()}
    data_dir = os.path.join(root_dir, "data")

    if not os.path.isdir(data_dir):
        logger.info("Data directory not exist, creating dir...")
        os.mkdir("data")

    with open(with_filename, 'w') as file:
        file.write(json.dumps(data))
        logger.info(f"Data {with_filename} saved")


def data_verified(filename: str) -> bool:
    with open(filename) as f:
        param = json.load(f).get("params")
    return param == settings.data


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
    if os.path.exists(filename) and data_verified(filename):
        logger.info(f"File exist, loading file: {filename}")
        return load_data(filename)
    else:
        try:
            download_data(with_filename=filename)
        except NoConnectionError:
            logger.error("no internet")
            return
        return load_data(filename)


def print_data(data=""):
    logger.setLevel(logging.ERROR)
    if not data:
        data = today_data()
    try:
        print(f"Waktu solat hari ini di {settings.city}")
        for key, value in data.items():
            print(f"{key}\t: {value}".expandtabs(10))
    except OSError as e:
        logger.error(f"couldn't print to stdout, error: {e}")


if __name__ == '__main__':
    today_data()
    print_data()
    # print(today_data())
