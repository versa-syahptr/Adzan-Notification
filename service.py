#!./env/bin/python3.7

import errno
import os
import subprocess
import sys

from net import ask_city
from setting import Settings


class ProcessNotStartedException(Exception): pass


def pid_exists(pid):
    """Check whether pid exists in the current process table.
    UNIX only.
    """
    if pid < 0:
        return False
    if pid == 0:
        # According to "man 2 kill" PID 0 refers to every process
        # in the process group of the calling process.
        # On certain systems 0 is a valid PID but we have no way
        # to know that in a portable fashion.
        raise ValueError('invalid PID 0')
    try:
        os.kill(pid, 0)
    except OSError as err:
        if err.errno == errno.ESRCH:
            # ESRCH == No such process
            return False
        elif err.errno == errno.EPERM:
            # EPERM clearly means there's a process to deny access to
            return True
        else:
            # According to "man 2 kill" possible error values are
            # (EINVAL, EPERM, ESRCH)
            raise
    else:
        return True


class Daemon:
    def __init__(self):
        pass

    def start(self):
        with open(".pid", 'w+') as f:
            try:
                pid = int(f.read())
            except ValueError:
                pid = -1
            finally:
                if pid_exists(pid):
                    return
                if os.path.exists("./adzan-service.exe"):
                    app = "./adzan-service.exe"
                else:
                    app = "./main.py"
                p = subprocess.Popen(app, start_new_session=True)
                f.write(str(p.pid))
                print(p.pid)

    def stop(self):
        if os.path.exists(".pid"):
            with open(".pid") as f:
                pid = int(f.read())
                print(pid)
            if pid_exists(pid):
                os.kill(pid, 9)
                print("process stoped")
                return
        raise ProcessNotStartedException

    def restart(self, ignore_exception=False):
        if ignore_exception:
            try:
                self.stop()
            except ProcessNotStartedException:
                pass
            finally:
                self.start()
        else:
            self.stop()
            self.start() 


if __name__ == '__main__':
    proc = Daemon()
    settings = Settings("settings.cfg")
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg in ("start", "stop", "restart"):
            getattr(proc, arg)()
        elif arg == "-s":
            settings.city = ask_city()
            proc.restart(ignore_exception=True)
        else:
            print(f"Unknown param {arg}")
    else:
        print("no param")
