#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import psutil
import socket
import sys
from thread import start_new_thread

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
sys.path.append(os.path.dirname(os.path.realpath(__file__)))

if "DJANGO_SETTINGS_MODULE" not in os.environ:
    os.environ["DJANGO_SETTINGS_MODULE"] = "base.settings"

import django

django.setup()
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist

from modules.customers.models import RelayCurrentValues, Relays, Devices

port = 12121


class DataHandler(object):
    def __init__(self):
        self.client_conn = None
        self.client_addr = None
        self.client_data = None
        self.splitted_data = None
        self.parsed_data = None

        self.device = None

    def parse_data(self):
        self.splitted_data = self.client_data.split('\r\n')
        self.parsed_data = []
        for item in self.splitted_data:
            if len(item) > 1:
                self.parsed_data.append(item.strip('#').split('#'))
        print self.parsed_data

    def process_data(self):
        for _data in self.parsed_data:
            if _data is None or not _data:
                continue
            elif self.device and _data[1] != self.device.name:
                raise Exception(
                    "Data arrived from %s but working with %s device. Disconnecting." % (_data[1], self.device.name)
                )

            if _data[0] == "DN":
                # Örnek veri: #CV#TANKAR001
                try:
                    self.device = Devices.objects.get(name=_data[1])
                except ObjectDoesNotExist:
                    raise Exception("%s device is not found in DB" % (_data[1]))
                finally:
                    self.device.ip = str(_data[2])
                    self.device.wan_ip = self.client_addr[0]
                    self.device.save()

            elif _data[0] == "CV":
                # Örnek veri: #CV#TANKAR001#A0#8.54#1878.68#
                try:
                    relay = Relays.objects.get(device__name=_data[1], relay_no=int(_data[2]))
                except ObjectDoesNotExist:
                    raise Exception("%s numbered relay record does not exist!" % _data[2])

                RelayCurrentValues(relay=relay, current_value=_data[3], power_cons=_data[4]).save()

            elif _data[0] == "ST" and _data[1] == self.device.name:
                # Örnek veri: #ST#TANKAR001#1#0
                try:
                    relay = Relays.objects.get(device__name=_data[1], relay_no=int(_data[2]))
                    relay.pressed = True if not int(_data[3]) else False
                    relay.save()
                except ObjectDoesNotExist:
                    raise Exception("%s numbered relay record does not exist!" % _data[2])

            else:
                print "Unexpected data: %s" % _data

    def send_command(self):
        if self.device:
            command = cache.get(self.device.name, None)

            if command is not None:
                print command
                cache.delete(self.device)
                parsed_command = "#RC#{relay}#{cmd}#".format(relay=command[0], cmd=command[1])
                print parsed_command
                try:
                    self.client_conn.send(parsed_command)
                except Exception as uee:
                    print uee
                    print('Unable to send command %s to Client' % parsed_command)

    def read(self, client_conn, client_addr):
        self.client_conn = client_conn
        self.client_addr = client_addr
        print 'Client connected from %s:%s address' % (self.client_addr[0], self.client_addr[1])

        while True:
            try:
                # self.send_command()
                self.client_data = self.client_conn.recv(1024)
                if self.client_data:
                    self.parse_data()
                    self.process_data()
                if not self.client_data:
                    print "No incoming data, breaking connection."
                    # Bu olmadığı zaman cihaz bağlantısı düştüğünde socket doğru sonlandırılmadığı için
                    # saçmalıyor. O yüzden bağlantının kapatılması için while'dan çıkılması gerekmekte.
                    continue
            except Exception as uee:
                print uee
                # self.client_conn.close()
                break

    def write(self, client_conn, client_addr):
        self.client_conn = client_conn
        self.client_addr = client_addr
        print 'Client connected from %s:%s address' % (self.client_addr[0], self.client_addr[1])

        while True:
            try:
                self.send_command()
            except Exception as uee:
                print uee
                # self.client_conn.close()
                continue


class SocketServer(object):
    """
    Socket server Sınıfı
    """

    def __init__(self, _port):
        self.get_host_ip = False
        self.host_addr = socket.gethostname() if self.get_host_ip else ''
        self.host_port = _port
        self.socket = None
        self.client_conn = None
        self.client_addr = None

        print "Host Address: %s:%s" % (self.host_addr, self.host_port)
        self.setup()

    def setup(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # self.socket.settimeout(0.1)
        # self.socket.setblocking(0)
        try:
            self.socket.bind((self.host_addr, self.host_port))
            print 'Socket created!'
        except Exception as uee:
            print uee
            self.socket.close()
            sys.exit()
        try:
            self.socket.listen(300)
            print 'Socket begin to listen.'
        except Exception as uee:
            print uee
            self.socket.close()
            sys.exit()

    def runserver(self):
        while True:
            try:
                self.client_conn, self.client_addr = self.socket.accept()
                data_handler = DataHandler()
                start_new_thread(data_handler.read, (self.client_conn, self.client_addr))
                start_new_thread(data_handler.write, (self.client_conn, self.client_addr))
            except socket.timeout:
                # print "Socket read timed out, retrying..."
                continue
            except Exception as uee:
                print uee
                self.client_conn.close()
                break
        self.socket.close()


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

    if not len(sys.argv) < 2:
        try:
            port = int(sys.argv[1])
        except:
            print "Usage: "
            print "\t# python socket-listener.py [port_number]"
            print " "
            print "- If port number not specified, server associated with default %s numbered port." % port
            print "- Port number must be numeric."
            sys.exit()
    try:
        SocketServer = SocketServer(port)
    except Exception as uee:
        print uee
        sys.exit()
    else:
        SocketServer.runserver()
