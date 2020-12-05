import configparser
import logging
import os
import platform
import shutil
import subprocess
import sys
from logging.handlers import RotatingFileHandler
from time import time, sleep

BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

# The background is set with 40 plus the number of the color, and the foreground with 30

# These are the sequences need to get colored ouput
RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[1;%dm"
BOLD_SEQ = "\033[1m"
parser = configparser.ConfigParser(allow_no_value=True)


COLORS = {
    'WARNING': YELLOW,
    'INFO': GREEN,
    'DEBUG': BLUE,
    'CRITICAL': YELLOW,
    'ERROR': RED
}


class ColoredFormatter(logging.Formatter):
    def __init__(self, fmt):
        self.use_color = sys.platform == "linux"  # disable color on other os
        fmt = self.formatter_message(fmt)
        logging.Formatter.__init__(self, fmt)

    def formatter_message(self, message):
        if self.use_color:
            message = message.replace("$RESET", RESET_SEQ).replace("$BOLD", BOLD_SEQ)
        else:
            message = message.replace("$RESET", "").replace("$BOLD", "")
        return message

    def format(self, record):
        levelname = record.levelname
        if self.use_color and levelname in COLORS:
            levelname_color = COLOR_SEQ % (30 + COLORS[levelname]) + levelname + RESET_SEQ
            record.levelname = levelname_color
        return logging.Formatter.format(self, record)


class AdzanLogger(logging.Logger):
    ffmt = "%(asctime)s  | %(name)s.%(module)s{PID:%(process)d} - %(levelname)s => %(msg)s"  # file format
    sfmt = "%(name)s.%(module)s | %(levelname)s => %(msg)s"  # stream format

    def __init__(self, name):
        logging.Logger.__init__(self, name, logging.INFO)

        file_formatter = ColoredFormatter(self.ffmt)
        stream_formatter = ColoredFormatter(self.sfmt)

        console = logging.StreamHandler(sys.stdout)
        console.setFormatter(stream_formatter)
        #                                               MB* KB * B
        file = RotatingFileHandler("adzan.log", maxBytes=2*1024*1024, backupCount=2)
        file.setFormatter(file_formatter)
        self.addHandler(console)
        self.addHandler(file)


class Settings:
    def __init__(self, filename):
        self.filename = filename
        self._file = parser.read(self.filename)
        self._data = None
        if 'api params' not in parser:
            parser.add_section('api params')
        self.audio = self.__Audio()
        self._data = parser['api params']
        self._city = ""

    def wait_for_edit(self):
        old_le = os.path.getmtime(self.filename)
        while True:
            le = os.path.getmtime(self.filename)
            sleep(1)
            if le > old_le:
                print("e", end=' ')
                if self.available:
                    print("OK")
                    break
        print("edited")
        self.load()

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
            subprocess.Popen(["xdg-open", self.filename])

        elif platform.system() == 'Windows':
            p = os.path.abspath(self.filename)
            print(p)
            subprocess.Popen(f'notepad "{p}"', shell=True)

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

    @property
    def media_player(self):
        return parser.get("misc", "media_player")

    # SUBCLASS
    class __Audio:
        def __init__(self):
            self.subuh = parser["audio"]["subuh"]
            self.other = parser["audio"]["other"]


def uninterruptible_sleep(seconds: float):
    """
    function uninterruptible_sleep(sec) by Versa Syahputra

    Delay execution for a given number of seconds. When the process suspended by system,
    this function will count how long the process has suspended and count it as "delayed time".
    If the suspend time exceeds the delay time it will raise RuntimeError

    :param seconds: the delay time, +- 1 second accuracy
    :type seconds: float
    :return: None
    """
    # convert to int to increase accuracy
    seconds = int(seconds)
    while seconds > 0:
        before = round(time())
        sleep(1)
        seconds -= 1
        # print(seconds)
        after = round(time())
        if after != before+1:
            seconds = seconds - ((after - before) - 1)
            if seconds < 0:
                raise RuntimeError("Process suspended too long")


# INSTANCES
logger = AdzanLogger("Adzan")


if __name__ == '__main__':
    """
    IGNORE THIS, testing purpose
    """
    def test_uis(sec):
        a = int(time())
        print(a)
        uninterruptible_sleep(sec)
        b = int(time())
        print(b)
        print(b-a)
        print(b-1 <= a+sec <= b+1)

    test_uis(120)
