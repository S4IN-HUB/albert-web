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
from datetime import datetime
import requests
import json

import django

django.setup()
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.conf import settings
from modules.customers.models import RelayCurrentValues, Relays, Devices, IrButton,TempValues


if settings.DBNAME == 'albert':
    port = 8080
else:
    port = 8888

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

    def parse_data(self):
        """
        String Data parser
        :return:
        """

        if '#' in self.client_data:
            # print self.client_data
            self.splitted_data = self.client_data.split('\r\n')
            self.parsed_data = []
            for item in self.splitted_data:
                if len(item) > 1:
                    self.parsed_data.append(item.strip('#').split('#'))
            #print "Parsed DATA: ", self.parsed_data
        else:

            self.parsed_data = self.client_data.strip()

    def process_data(self):
        """
        Data is processed and recorded in here
        :return:
        """
        if self.parsed_data == 'ALBERTO':
            return ''

        for _data in self.parsed_data:

            if _data is None or not _data:
                continue

            elif self.device and _data[1] != self.device.name:
                raise Exception(
                    "Data arrived from %s but working with %s device. Disconnecting." % (_data[1], self.device.name)
                )

            if _data[0] == "DN":
                # Örnek veri: #DN#TANKAR001#IR
                try:
                    self.device = Devices.objects.get(name=_data[1])
                    self.device.wan_ip = self.client_addr[0]
                    self.device.status=True
                    self.device.last_connect=datetime.now()
                    self.device.save()

                except ObjectDoesNotExist:
                    self.device = Devices(name=_data[1])
                    self.device.type = _data[2]
                    self.device.description = _data[1]
                    self.device.wan_ip = self.client_addr[0]
                    self.device.status = True
                    self.device.save()

                try:
                    if len(_data) > 2:
                        if _data[2] == "IR":
                            if _data[3] == "TEMP":
                                self.device.temperature = _data[4]
                                self.device.humidity = _data[6]
                                self.device.save()

                                # try:
                                #     new_temp_val = TempValues(
                                #         device=self.device,
                                #         temperature =_data[4],
                                #         humidity=_data[6],
                                #     )
                                #     new_temp_val.save()
                                #
                                # except:
                                #     pass
                except:
                     pass

                self.client_conn.send('HELLO')

            elif _data[0] == "RC":

                print _data

                try:
                    relay = Relays.objects.get(device__name=_data[1], relay_no=int(_data[3]))
                    relay.pressed = True if int(_data[4]) == 1 else False
                    relay.save()

                    if relay.notify:
                        try:
                            #print "try notify"
                            if relay.device:
                                #print "try notify", relay.device
                                if relay.device.account:
                                    #print "try notify", relay.device.account
                                    if relay.device.account.device_token:
                                        #print "try notify", relay.device.account.device_token
                                        header = {"Content-Type": "application/json; charset=utf-8",
                                                  "Authorization": "Basic ODk2NjI4NmQtNWNlNy00N2MwLWEyMTItOGQ2NzQwNTFmYTU4"}


                                        status = u" açıldı" if relay.pressed else u" kapatıldı"
                                        room_name = relay.room.name + u" > " if relay.room else ""

                                        notif_text_tr =  "%s %s %s" % ( room_name, relay.name , status )
                                        notif_text_en =  "%s %s %s" % ( room_name, relay.name , status )

                                        if relay.on_notify and relay.on_notify != '' and relay.pressed:
                                            notif_text_tr = relay.on_notify
                                            notif_text_en = relay.on_notify

                                        if relay.on_notify and relay.on_notify != '' and not relay.pressed:
                                            notif_text_tr = relay.off_notify
                                            notif_text_en = relay.off_notify


                                        payload = {"app_id": "6f37c2b8-ac68-4ac5-9bad-4fa0efa7e8bb",
                                                   "include_player_ids": [ relay.device.account.device_token ],
                                                   "contents":{
                                                       "tr": notif_text_tr ,
                                                       "en": notif_text_en
                                                   },
                                                }
                                        print payload

                                        req = requests.post("https://onesignal.com/api/v1/notifications", headers=header, data=json.dumps(payload))
                                        #print "-" * 20
                                        #print req.status_code, req.reason
                        except Exception as e:
                            # print e
                            pass


                except ObjectDoesNotExist:
                    raise Exception("%s numbered relay record does not exist!" % _data[2])

            elif _data[0] == "CV":
                    # Örnek veri: #CV#TANKAR001#A0#8.54#1878.68#
                    try:
                        relay = Relays.objects.get(device__name=_data[1], relay_no=int(_data[2]))
                    except ObjectDoesNotExist:
                        raise Exception("%s numbered relay record does not exist!" % _data[2])

                    RelayCurrentValues(relay=relay, current_value=_data[3], power_cons=_data[4]).save()

            elif _data[0] == "IRENCODE":


                button = IrButton(device=self.device)
                button.name = "%s %s" % ( _data[3] , _data[4] )
                button.ir_type = _data[3]
                button.ir_code = _data[4]
                button.ir_bits = _data[5]

                button.save()

            elif _data[0] == "OK":
                pass
            elif _data[0] == "HELLO":
                pass
            elif _data[0] == "ST":

                try:
                    self.device = Devices.objects.get(name=_data[1])
                    self.device.status = True
                    self.device.save()

                    _relay_states = _data[3]
                    _relays = Relays.objects.get(device=self.device, relay_no=int(_data[3]))
                    for rly in self.device.Relays.all():

                        if rly.pressed == bool(int(_relay_states[rly.relay_no:rly.relay_no+1])):
                            rly.pressed = False if bool(int(_relay_states[rly.relay_no:rly.relay_no+1])) == True else True
                            rly.save()

                except:
                    pass

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

            if self.is_new:
                socket_lock = cache.get("socket_locks", {})
                socket_lock.update({self.device.name: True})
                socket_lock = True
                self.is_new = False

            if not in_process.get(self.device.name, False):

                commands = cache.get(self.device.name, [])
                unsend_commands = []

                if len(commands):

                    if not socket_lock:
                        #print "locked."
                        return

                    for cmd in commands:
                        parsed_command = "#{cmd}#".format(cmd=cmd['CMD'])

                        print parsed_command

                        try:
                            self.client_conn.send(parsed_command)
                            cmd.update({'send': True})
                            sleep(0.2)

                        except Exception as uee:
                            cmd.update({'send': False})
                            print uee
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                            print(exc_type, fname, exc_tb.tb_lineno)
                            # self.client_conn.close()
                            #print('Unable to send command %s to Client' % parsed_command)
                            break

                    for cmd in commands:
                        if cmd.pop('send', False) is False:
                            unsend_commands.append(cmd)

                    if len(unsend_commands) > 0:
                        cache.set(self.device.name, unsend_commands)
                        # raise Exception("There are unsend commands in stack!")
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
        #print 'Client connected from %s:%s address' % (self.client_addr[0], self.client_addr[1])



        while True:
            try:
                self.client_data = self.client_conn.recv(128)
                #print "Raw DATA: ", self.client_data
                if self.client_data and len(self.client_data) > 3:
                    # add redis lock to device, then release the lock.
                    socket_locked = False
                    if self.device:
                        socket_locked = True
                        socket_lock = cache.get("socket_locks", {})
                        socket_lock.update({self.device.name: True})
                        cache.set("socket_locks", socket_lock)
                        #print "%s locked" % self.device.name

                    self.parse_data()
                    self.process_data()

                    if socket_locked:
                        socket_lock = cache.get("in_process_socket", {})
                        socket_lock.update({self.device.name: False})
                        cache.set("in_process_socket", socket_lock)
                        #print "%s unlocked" % self.device.name

                # if not self.client_data:
                #     #print "No incoming data, breaking connection."
                #     self.client_conn.close()
                #     return False

                    # Bu olmadığı zaman cihaz bağlantısı düştüğünde socket doğru sonlandırılmadığı için
                    # saçmalıyor. O yüzden bağlantının kapatılması için while'dan çıkılması gerekmekte.
                    # continue

            except Exception as uee:
                print uee
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)
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
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)
                self.client_conn.close()
                break


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
        self.socket.settimeout(500)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.socket.bind((self.host_addr, self.host_port))
            print 'Socket created!'
        except Exception as uee:
            print uee
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            self.socket.close()
            sys.exit()
        try:
            self.socket.listen(1000)
            print 'Socket begin to listen.'
        except Exception as uee:
            print uee
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            self.socket.close()
            sys.exit()

    def runserver(self):
        """
        Run seocket server
        :return:
        """
        data_handler = DataHandler()
        while True:
            try:
                self.client_conn, self.client_addr = self.socket.accept()
                data_handler = DataHandler()
                start_new_thread(data_handler.read, (self.client_conn, self.client_addr))
                start_new_thread(data_handler.write, (self.client_conn, self.client_addr))
            except socket.timeout:

                try:
                    print data_handler.device
                    data_handler.device.status = False
                    data_handler.device.save()
                except: print "no device info"
                print "Socket read timed out, retrying..."
                continue
            except PermissionDenied as pd:
                print pd
                continue
            except Exception as uee:
                print uee
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)

                self.client_conn.close()
                break
        self.socket.close()


def test_notify():

    header = {"Content-Type": "application/json; charset=utf-8",
              "Authorization": "Basic ODk2NjI4NmQtNWNlNy00N2MwLWEyMTItOGQ2NzQwNTFmYTU4"}

    payload = {"app_id": "6f37c2b8-ac68-4ac5-9bad-4fa0efa7e8bb",
               "include_player_ids": ["7eb41ea3-79f3-4223-b307-79887a0bf8d4"],
               "contents": {"en":  "%s %s" % ("deneme", " açıldı" if True else " kapandi"), "tr": "%s %s" % ("deneme", " acildi" if True else " kapandi")}, }


    print json.dumps(payload)

    req = requests.post("https://onesignal.com/api/v1/notifications", headers=header, data=json.dumps(payload))

    print "-"*20
    print req.status_code, req.reason

if __name__ == "__main__":

    if "test_notify" in sys.argv:

        test_notify()

    else:
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
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            sys.exit()


        else:
            SocketServer.runserver()
