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
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied

from modules.customers.models import RelayCurrentValues, Relays, Devices, IrButton, IrRemote

port = 12121


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

    def parse_data(self):
        """
        String Data parser
        :return:
        """
        self.splitted_data = self.client_data.split('\r\n')
        self.parsed_data = []
        for item in self.splitted_data:
            if len(item) > 1:
                self.parsed_data.append(item.strip('#').split('#'))
        print self.parsed_data

    def process_data(self):
        """
        Data is processed and recorded in here
        :return:
        """
        for _data in self.parsed_data:
            if _data is None or not _data:
                continue
            elif self.device and _data[1] != self.device.name:
                raise Exception(
                    "Data arrived from %s but working with %s device. Disconnecting." % (_data[1], self.device.name)
                )

            if _data[0] == "DN":
                # Örnek veri: #DN#TANKAR001#0.0.0.0
                try:
                    self.device = Devices.objects.get(name=_data[1])
                    self.device.ip = str(_data[2]) if len(_data) > 2 else '0.0.0.0'
                    self.device.wan_ip = self.client_addr[0]
                    self.device.port = self.client_addr[1]
                    self.device.save()
                    if not self.device.status:
                        raise PermissionDenied("Device is disabled via admin!")
                except ObjectDoesNotExist:
                    raise Exception("%s device is not found in DB" % (_data[1]))

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

            elif _data[0] == "SENDIR":
                # Örnek veri: #SENDIR#NEC#FFFFFF#24
                if cache.get(self.device.name, None) is None:
                    raise Exception("The cached DEVICE data for device %s is unavailable" % self.device.name)
                elif cache.get(self.device.name) == {} or cache.get(self.device.name).get('set_ir_button', None) is None:
                    raise Exception("The cached IR BUTTON data for device %s is unavailable" % self.device.name)
                else:
                    for key, value in cache.get(self.device.name)['set_ir_button']:

                        try:
                            remote = IrRemote.objects.get(pk=key)
                        except ObjectDoesNotExist:
                            cache.set(self.device.name, {'set_ir_button': None})
                            raise Exception("%s numbered IR REMOTE record does not exist!" % value)

                        try:
                            button = IrButton.objects.get(ir_remote=remote, id=value)
                            button.ir_type = _data[1]
                            button.ir_code = _data[3]
                            button.ir_bits = _data[5]
                            button.save()
                        except ObjectDoesNotExist:
                            cache.set(self.device.name, {'set_ir_button': None})
                            raise Exception("%s numbered button record does not exist!" % value)

                    cache.set(self.device.name, {'set_ir_button': None})

            else:
                print "Unexpected data: %s" % _data

    def send_command(self):
        """
        Send command to device
        :return:
        """
        if self.device:
            # checks locks and processes.
            in_process = cache.get("in_process", {})
            socket_lock = cache.get("socket_locks", {}).get(self.device.name, False)

            if not in_process.get(self.device.name, False):

                commands = cache.get(self.device.name, [])
                unsend_commands = []

                if len(commands):

                    if not socket_lock:
                        print "locked."
                        return

                    for cmd in commands:
                        parsed_command = "#{cmd}#{relay}#{st}#".format(cmd=cmd['CMD'], relay=cmd['RN'], st=cmd['ST'])
                        print parsed_command

                        try:
                            self.client_conn.send(parsed_command)
                            cmd.update({'send': True})
                            sleep(0.2)
                        except Exception as uee:
                            cmd.update({'send': False})
                            print uee
                            # self.client_conn.close()
                            print('Unable to send command %s to Client' % parsed_command)
                            break

                    for cmd in commands:
                        if cmd.pop('send', False) is False:
                            unsend_commands.append(cmd)

                    if len(unsend_commands) > 0:
                        cache.set(self.device.name, unsend_commands)
                        raise Exception("There are unsend commands in stack!")
                    else:
                        cache.delete(self.device.name)

    def read(self, client_conn, client_addr):
        """
        Read data from Socket
        :param client_conn:
        :param client_addr:
        :return:
        """
        self.client_conn = client_conn
        self.client_addr = client_addr
        print 'Client connected from %s:%s address' % (self.client_addr[0], self.client_addr[1])

        while True:
            try:
                # self.send_command()
                self.client_data = self.client_conn.recv(128)
                print "1:", self.client_data
                self.client_data = self.client_data.encode('utf-8')
                print "2:", self.client_data
                if self.client_data:
                    # add redis lock to device, then release the lock.
                    socket_locked = False
                    if self.device:
                        socket_locked = True
                        socket_lock = cache.get("socket_locks", {})
                        socket_lock.update({self.device.name: True})
                        cache.set("socket_locks", socket_lock)
                        print "%s locked" % self.device.name
                    self.parse_data()
                    self.process_data()
                    if socket_locked:
                        socket_lock = cache.get("in_process_socket", {})
                        socket_lock.update({self.device.name: False})
                        cache.set("in_process_socket", socket_lock)
                        print "%s unlocked" % self.device.name
                if not self.client_data:
                    print "No incoming data, breaking connection."
                    self.client_conn.close()
                    return False
                    # Bu olmadığı zaman cihaz bağlantısı düştüğünde socket doğru sonlandırılmadığı için
                    # saçmalıyor. O yüzden bağlantının kapatılması için while'dan çıkılması gerekmekte.
                    # continue
            except Exception as uee:
                print uee
                self.client_conn.close()
                break

    def write(self, client_conn, client_addr):
        """
        Write data to socket
        :param client_conn:
        :param client_addr:
        :return:
        """
        self.client_conn = client_conn
        self.client_addr = client_addr
        print 'Client connected from %s:%s address' % (self.client_addr[0], self.client_addr[1])

        while True:
            try:
                self.send_command()
            except Exception as uee:
                print uee
                self.client_conn.close()
                return False


class SocketServer(object):
    """
    Socket server Class
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
        """
        Socket setup
        :return:
        """
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
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
        """
        Run seocket server
        :return:
        """
        while True:
            try:
                self.client_conn, self.client_addr = self.socket.accept()
                data_handler = DataHandler()
                start_new_thread(data_handler.read, (self.client_conn, self.client_addr))
                start_new_thread(data_handler.write, (self.client_conn, self.client_addr))
            except socket.timeout:
                # print "Socket read timed out, retrying..."
                continue
            except PermissionDenied as pd:
                print pd
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
