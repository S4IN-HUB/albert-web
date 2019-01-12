#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
sys.path.append(os.path.dirname(os.path.realpath(__file__)))

if "DJANGO_SETTINGS_MODULE" not in os.environ:
    os.environ["DJANGO_SETTINGS_MODULE"] = "base.settings"

import psutil
import socket
from thread import start_new_thread
from time import sleep


import django
django.setup()

from datetime import datetime
from django.utils import timezone
from django.core.cache import cache
from modules.customers.models import RelayCurrentValues, Relays, Devices, IrButton,TempValues

port = 8080


class DataHandler(object):
    """
    Socket data handler class
    """

    def __init__(self):
        self.client_conn = None
        self.client_addr = None
        self.client_data = None
        self.splitted_data = None
        self.parsed_data = None

        self.device = None
        self.is_new = True

    def update_status(self):
        """
        String Data parser
        :return:
        """
        _devices = Devices.objects.filter(status=True)
        for item in _devices:

            during = timezone.now() - item.last_connect
            print "during", during.seconds , item.name
            if during.seconds > 30:
                item.status = False
                item.save()

            # _cmd = cache.get(item.name, [])
            # _command = "ST"
            # _cmd.append({"CMD": _command, })
            # cache.set(item.name, _cmd)




if __name__ == "__main__":
    this_proc = os.getpid()

    greped_proc = False
    for proc in psutil.process_iter():
        if proc.name() == 'python' and len(proc.cmdline()) > 1:

            if sys.argv[0] == proc.cmdline()[1]:
                greped_proc = proc.pid

                if this_proc != greped_proc:
                    print "Bu islem zaten aktif"
                    sys.exit()

    a = DataHandler()
    islem = sys.argv[1]

    if hasattr(a, islem):
        getattr(a, islem)()
    else:
        print 'Bilinmeyen islev: %s' % islem
