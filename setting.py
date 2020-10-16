#!./env/bin/python3.7
import configparser
import platform
import subprocess

parser = configparser.ConfigParser(allow_no_value=True)


class Settings:
    class _Coms:
        def __init__(self):
            self._enabled = False
            self._address = ""
            self._port = 0

    class _Audio:
        def __init__(self):
            if "audio" not in parser:
                parser.add_section("audio")
            self.subuh = parser["audio"]["subuh"]
            self.other = parser["audio"]["other"]

    def __init__(self, filename):
        self.filename = filename
        self.comunication = self._Coms()
        self._file = parser.read(filename)
        self._data = None
        if 'api params' not in parser:
            parser.add_section('api params')
        self._data = parser['api params']
        self._city = ""


    @property
    def are_available(self):
        return bool(self._city)

    def write(self):
        with open(self.filename, 'w') as f:
            parser.write(f)

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
            subprocess.Popen(["xdg-open", self.filename], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        elif platform.system() == 'Windows':
            subprocess.Popen(self.filename)

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
    def city(self):
        self._city = self._data["city"]
        return self._city

    @city.setter
    def city(self, val):
        self._data["city"] = self._city = val.lower()
        self.write()


if __name__ == '__main__':
    # For testing
    seting = Settings("settings.ini")
    if not seting.are_available:
        seting.open_file()
    print(seting.data)
    print(parser['api params']['city'])
