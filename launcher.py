#!/usr/bin/env python3.7
import errno
import os
import subprocess
import sys

from setting import Settings

cli = False
if "DISPLAY" not in os.environ:
    os.environ["DISPLAY"] = ':0'
    cli = True
cwd = os.path.abspath(os.path.dirname(__file__))
this = sys.argv[0]
usage = f"""
Usage:

{this} --start => start new Adzan-Notification process; throws error when the process has started
{this} --stop => stop current Adzan-Notification process; throws error if the process don't exist
{this} --restart => restart Adzan-Notification process
"""
setting = Settings("settings.ini")


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
        if os.path.exists(".pid"):
            with open(".pid", 'r') as f:
                try:
                    pid = int(f.read())
                except ValueError:
                    pid = -1

            if pid_exists(pid):
                sys.exit(f"Process already started with pid: {pid}")

        if cli and not setting.available:
            print("first run, please edit configuration file")
            subprocess.run(["nano", "settings.ini"])

        if os.path.exists("./adzan-service.exe"):
            app = "./adzan-service.exe"
        else:
            app = "./main.py"

        p = subprocess.Popen(app, start_new_session=True, env=os.environ, cwd=cwd)
        with open(".pid", 'w') as f:
            f.write(str(p.pid))
        print(p.pid)
        sys.exit(0)

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

    def restart(self):
        self.stop()
        self.start()


if __name__ == '__main__':
    proc = Daemon()
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg in ("--start", "--stop", "--restart"):
            getattr(proc, arg.lstrip('--'))()
        else:
            print(f"Unknown param {arg}{usage}")
    else:
        print(f"no param{usage}")
