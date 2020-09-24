import configparser


parser = configparser.ConfigParser()


class Settings:
    class _Coms:
        def __init__(self):
            self._enabled = False
            self._address = ""
            self._port = 0

    def __init__(self, filename):
        self.filename = filename
        self.comunication = self._Coms()
        self._file = parser.read(filename)
        self._data = None
        if 'PARAMS' not in parser:
            parser.add_section('PARAMS')
        self._data = parser['PARAMS']

        # DATA
        self._city = ""
        self._country = ''
        self._method = 0
        self._methodSettings = ""
        self._tune = ""

    @property
    def are_available(self):
        return bool(self._file)

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

    # PROPS
    @property
    def data(self):
        d = dict(parser['PARAMS'])
        # print(d)
        return d

    @data.setter
    def data(self, val: dict):
        for key, value in val.items():
            self._data[key] = value
        self.write()


    @property
    def city(self):
        self.data["city"] = self._city
        return self._city

    @city.setter
    def city(self, val):
        self.data["city"] = self._city = val.lower()
        self.write()


if __name__ == '__main__':
    seting = Settings("settings.cfg")
    # seting.set_default()
    print(seting.data)
    print(parser['PARAMS']['city'])
