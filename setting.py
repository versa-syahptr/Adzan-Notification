import configparser
import os
import platform
import shutil
import subprocess
import time

parser = configparser.ConfigParser(allow_no_value=True)


class Settings:
    def __init__(self, filename):
        self.filename = filename
        self._file = parser.read(self.filename)
        self._data = None
        if 'api params' not in parser:
            parser.add_section('api params')
        self.comunication = self._Coms()
        self.audio = self.__Audio()
        self._data = parser['api params']
        self._city = ""
        self._mode = "gui"

    def write_last_edit(self):
        ts = os.path.getmtime(self.filename)
        if "misc" not in parser:
            parser.add_section("misc")
        parser["misc"]["lastEdit"] = ts
        self.write()

    def wait_for_edit(self):
        old_le = os.path.getmtime(self.filename)
        while True:
            le = os.path.getmtime(self.filename)
            time.sleep(0.5)
            if le > old_le:
                print("edited")
                if self.available:
                    print("OK")
                    break
        print("edited")
        self.load()

    @property
    def modified_time(self):
        return parser.getfloat("misc", "lastEdit")

    @property
    def available(self):
        self.load()
        return bool(self.city and self.country)

    def write(self):
        ol = self.filename.split('.')
        ol.insert(1, 'old')
        old = ".".join(ol)
        if not os.path.exists(old):
            shutil.copy2(self.filename, old)
        with open(self.filename, 'w') as f:
            parser.write(f)

    def set_mode(self, mode):
        self._mode = mode

    def set_default(self):
        print("default")
        default = dict(
            country="id",
            method='99',
            methodSettings='20,null,18',
            tune='2,2,-2,3,2,2,2,1,0'
        )
        self.data = default

    def open_file(self):
        if platform.system() == 'Linux':
            cmd = "xdg-open"
            if self._mode == "cli":
                cmd = "editor"
            subprocess.call([cmd, self.filename])

        elif platform.system() == 'Windows':
            p = os.path.abspath(self.filename)
            print(p)
            subprocess.Popen(["start", p], shell=True)

    def load(self):
        parser.read(self.filename)

    # PROPS
    @property
    def data(self):
        d = dict(parser['api params'])
        return d

    @data.setter
    def data(self, val: dict):
        for key, value in val.items():
            self._data[key] = value
        self.write()

    @property
    def country(self):
        return parser['api params']["country"]

    @country.setter
    def country(self, val):
        parser['api params']["country"] = val
        self.write()
    
    @property
    def city(self):
        self._city = parser['api params']["city"]
        return self._city

    @city.setter
    def city(self, val):
        self._data["city"] = self._city = val.lower()
        self.write()

    # SUBCLASS
    class _Coms:
        def __init__(self):
            self._enabled = False
            self._address = ""
            self._port = 0

    class __Audio:
        def __init__(self):
            if "audio" not in parser:
                parser.add_section("audio")
            self.subuh = parser["audio"]["subuh"]
            self.other = parser["audio"]["other"]


if __name__ == '__main__':
    # For testing
    seting = Settings("settings.ini")
    if not seting.available:
        seting.open_file()
        seting.wait_for_edit()
    print(seting.data)
    print(seting.audio.subuh)
