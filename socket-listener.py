#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import socket
import sys

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
timeout = 10

print socket.gethostbyname(socket.gethostname())


class SocketServer(object):
    """
    Socket server Sınıfı
    """
    def __init__(self, port):
        self.get_host_ip = False
        self.host_addr = socket.gethostname() if self.get_host_ip else ''
        self.host_port = port
        self.socket = None
        self.client_conn = None

        self.client_data = None
        self.parsed_data = None

        self.device = None

        print "Host Address: %s:%s" % (self.host_addr, self.host_port)
        self.setup()

    def setup(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.setblocking(1)
        self.socket.settimeout(timeout)
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

    def parse_data(self):
        self.parsed_data = self.client_data.strip('#').replace('\r\n', '').split('#')
        print self.parsed_data

    def process_data(self):
        if self.parsed_data is not None and len(self.parsed_data) > 1:
            if self.parsed_data[0] == "DN":
                # Örnek veri: #CV#TANKAR001
                try:
                    self.device = Devices.objects.get(name=self.parsed_data[1])
                except ObjectDoesNotExist:
                    raise Exception("%s device is not found in DB" % (self.parsed_data[1]))

            elif self.parsed_data[0] == "CV" and self.parsed_data[1] == self.device.name:
                # Örnek veri: #CV#TANKAR001#A0#8.54#1878.68#
                try:
                    relay = Relays.objects.get(device__name=self.parsed_data[1], relay_no=int(self.parsed_data[2]))
                except ObjectDoesNotExist:
                    raise ("%s numaralı röle kaydı bulunamadı" % self.parsed_data[2])

                RelayCurrentValues(relay=relay, current_value=self.parsed_data[3], power_cons=self.parsed_data[4]).save()

            elif self.parsed_data[0] == "ST" and self.parsed_data[1] == self.device.name:
                # Örnek veri: #ST#TANKAR001#1#0
                try:
                    relay = Relays.objects.get(device__name=self.parsed_data[1], relay_no=int(self.parsed_data[2]))
                    relay.pressed = bool(int(self.parsed_data[3]))
                    relay.save()
                except ObjectDoesNotExist:
                    raise ("%s numaralı röle kaydı bulunamadı" % self.parsed_data[2])

            else:
                print "Unexpected data: %s" % self.parsed_data
        else:
            raise Exception("Corrupted data: %s" % self.parsed_data)

    def send_command(self):
        try:
            command = cache.get()
        except:
            raise Exception("Unable to read Cache")

        try:
            self.client_conn.send(command)
        except:
            raise Exception('unable to send command to Client')

    def runserver(self):
        while True:
            try:
                self.client_conn, client_addr = self.socket.accept()

                print 'Client connected from %s:%s address' % (client_addr[0], client_addr[1])
                # start_new_thread(self.clientthread, (self.client_conn, client_addr))

                while True:
                    try:
                        self.client_data = self.client_conn.recv(1024)
                        if self.client_data:
                            self.parse_data()
                            self.process_data()
                            # self.send_command()
                        if not self.client_data:
                            print "No incoming data, breaking connection."
                    except Exception as uee:
                        print uee
                        self.client_conn.close()
                        break
            except socket.timeout:
                print "Socket read timed out, retrying..."
                continue
            except Exception as uee:
                print uee
                break
        self.socket.close()


if __name__ == "__main__":
    if not len(sys.argv) < 2:
        try:
            port = int(sys.argv[1])
        except:
            print "Kullanım: "
            print "\t# python socket-listener.py [port numarası]"
            print " "
            print "- Port numarası belirtmezseniz %s numaralı porttan çalışacaktır." % port
            print "- Port numarası nümerik değer olmalıdır."
            sys.exit()

    SocketServer = SocketServer(port)
    SocketServer.runserver()
    sys.exit()
