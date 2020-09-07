import configparser
import requests
from datetime import date


today = date.today()
config = configparser.ConfigParser()
SETTINGS = "settings.cfg"
# FUNCTIONS

def get_kota():
    req = requests.get("https://freegeoip.app/json")
    return req.json()["city"]

def get_kota_id(kota) -> str:
    url = f"https://api.banghasan.com/sholat/format/json/kota/nama/{kota}"
    r = requests.get(url)
    data = r.json()
    kotaid = data["kota"][0]["id"]
    print(data)
    print('#'*10, f"\nkota = {kota},")
    return kotaid


def get_jadwal_sholat(kotaId, tanggal:str = today) -> dict:
    url = f"https://api.banghasan.com/sholat/format/json/jadwal/kota/{kotaId}/tanggal/{tanggal}"
    r = requests.get(url)
    data = r.json()
    return data['jadwal']['data']


def updateKota():
    nama = input("Masukan nama kota: ")
    kotaId = get_kota_id(nama)
    config["settings"] = dict(
            nama_kota=nama,
            kota_id=get_kota_id(nama)
        )
    with open("settings.cfg", 'x') as configfile:
        config.write(configfile)


def init() -> dict or bool:
    settings = config.read("settings.cfg")
    # check is file available
    try:
        if not settings:
            print("there's no settings file")
            nama = get_kota()
            config['settings'] = dict(
                nama_kota=nama,
                kota_id=get_kota_id(kota=nama)
            )
            today_data = config[f"data {today}"] = get_jadwal_sholat(config["settings"]["kota_id"])
            with open("settings.cfg", 'x') as configfile:
                config.write(configfile)

            return {**dict(today_data), "kota": nama}

        else:
            print("settings file exist")
            key = f"data {today}"
            if key in config:
                return {**config[key], "kota": config["settings"]["nama_kota"]}
            else:
                today_data = config[key] = get_jadwal_sholat(config["settings"]["kota_id"])
                with open("settings.cfg", 'w') as file:
                    config.write(file)
                return {**dict(today_data), "kota": config["settings"]["nama_kota"]}
    except Exception:
        return False


