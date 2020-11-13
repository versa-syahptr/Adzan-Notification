#!/usr/bin/env python3.7
import errno
import os
import subprocess
import sys
from time import sleep

from setting import Settings

# launcher.py is UNIX ONLY #

cli = False
if "DISPLAY" not in os.environ:
    os.environ["DISPLAY"] = ':0'
    cli = True

this = os.path.realpath(__file__)
cwd = os.path.abspath(os.path.dirname(this))

usage = """
Usage: adzan <command>
   or: adzan [option]

Commands:
    start       Start new Adzan-Notification process; throws error when the process has started
    stop        Stop current Adzan-Notification process; throws error if the process don't exist
    restart     Restart Adzan-Notification process
    stats       View process statisticss (aka "ps -F")

Options:
    -t, --test  Test the adzan
    -d, --data  Print today's sholat time schedule
"""
setting = Settings("settings.ini")


def pid_exists(pid: int):
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

    def _get_pid(self):
        if os.path.exists(".pid"):
            with open(".pid", 'r') as f:
                try:
                    pid = int(f.read())
                except ValueError:
                    pid = -1
        else:
            pid = 0

        return pid

    def start(self):

        pid = self._get_pid()
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
        print(f"Proess started with pid: {p.pid}")
        sys.exit(0)

    def stop(self):
        pid = self._get_pid()
        if pid_exists(pid):
            os.kill(pid, 9)
            print("process stoped")
            return
        else:
            print("No Adzan-Notification process exists")
            sys.exit(-1)

    def restart(self):
        self.stop()
        sleep(1)
        self.start()

    def stats(self):
        pid = self._get_pid()
        if pid_exists(pid):
            try:
                out = subprocess.check_output(["ps", "-F", str(pid)]).decode().rstrip()
            except subprocess.CalledProcessError:
                out = "Somethings wrong, i can feel it!"

            print(out)
        else:
            print(f"No Adzan-Notification process exists")
            sys.exit(-1)

    def symlink(self):
        target = "/usr/local/bin/adzan"
        if os.path.exists(target):
            sys.exit("symlink already there")
        try:
            os.link(this, target)
            print("ok")
        except IOError as e:
            if e.errno == errno.EPERM:
                sys.exit("You need sudo priviledge to run this")
            raise


if __name__ == '__main__':
    proc = Daemon()
    os.chdir(cwd)
    if len(sys.argv) > 1:
        arg = str(sys.argv[1])
        if arg in ("start", "stop", "restart", "stats"):
            getattr(proc, arg)()
        elif arg.startswith("-"):
            if arg.startswith("--"):
                arg = arg[1:3]
            subprocess.run(["./main.py", arg])
        else:
            print(f"Unknown param {arg}{usage}")
    else:
        print(f"no param{usage}")
