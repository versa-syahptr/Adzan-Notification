#!./env/bin/python3.7

import sys
import subprocess
import errno
import os


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
                p = subprocess.Popen(["./main.py"], start_new_session=True)
                f.write(str(p.pid))
                print(p.pid)

    def stop(self):
        with open(".pid", 'w+') as f:
            try:
                pid = int(f.read())
            except ValueError:
                pid = -1
            finally:
                if pid_exists(pid):
                    os.kill(pid, 9)
                else:
                    raise ProcessNotStartedException

    def restart(self):
        self.stop()
        self.start()


proc = Daemon()

if len(sys.argv) > 1:
    arg = sys.argv[1]
    # if sys.argv[1] == "start":
    #     start()
    # elif sys.argv[1] == "restart":
    #     stop()
    #     start()
    # elif sys.argv[1] == "stop":
    #     stop()
    if arg in ("start", "stop", "restart"):
        getattr(proc, arg)()
    else:
        print(f"Unknown param {arg}")
else:
    print("no param")

# if __name__ == '__main__':
#     with DaemonContext(working_directory="/media/versa/ProjectData/python/sholat"):
#         main()

