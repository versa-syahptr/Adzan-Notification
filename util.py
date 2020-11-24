import logging
import sys
from logging.handlers import RotatingFileHandler
BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

# The background is set with 40 plus the number of the color, and the foreground with 30

# These are the sequences need to get colored ouput
RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[1;%dm"
BOLD_SEQ = "\033[1m"


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
    ffmt = "%(asctime)s  | %(name)s{PID:%(process)d} - %(levelname)s => %(msg)s"  # file format
    sfmt = "%(name)s | %(levelname)s => %(msg)s"  # stream format

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


if __name__ == '__main__':
    """
    IGNORE THIS, testing purpose
    """
    def g():
        log.setLevel(logging.ERROR)
    def f():
        # log.setLevel(logging.DEBUG)
        log.debug("f")
    log = AdzanLogger(__name__)
    log.setLevel(logging.ERROR)
    print(log.level)
    g()
    log.info("a")
    f()