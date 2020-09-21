# import pymsgbox
import notify2


def _nux_notify(title, msg='', *, icon='masjid'):
    notify2.init("Adzan")
    n = notify2.Notification(title, msg, icon=icon)
    n.set_hint("desktop-entry", "Adzan")
    n.set_hint("suppress-sound", True)
    n.show()
    return n



notify = _nux_notify


if __name__ == '__main__':
    _nux_notify("title", "msg", icon="masjid")
    # from time import sleep
    # notif = notify("tes", "msg", icon="masjid")
    # sleep(5)
    # notif.close()pi
