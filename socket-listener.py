#!/usr/bin/python
# -*- coding: utf-8 -*-
import socket
import sys, os
import time
from thread import *
import threading
from datetime import datetime, timedelta
from decimal import Decimal


class MainProgram:
    def __init__(self):

        self.HOST = ''
        self.PORT = 8080
        self.debug = True
        self.addr = None
        self.device_id = ''

    def clientthread(self, client_socket, addr):
        while True:
            data = client_socket.recv(4096)

            if data != '':
                print data

            if "#DN#" in data:
                print "Device Name:", data.split("#DN#")[1]
                client_socket.send("#RC#7#1#")
                client_socket.send("#RC#8#1#")
                client_socket.send("#RC#9#1#")
                time.sleep(3)
                client_socket.send("#RC#7#0#")
                client_socket.send("#RC#8#0#")
                client_socket.send("#RC#9#0#")
                time.sleep(3)
                client_socket.send("#RC#7#1#")
                client_socket.send("#RC#8#1#")
                client_socket.send("#RC#9#1#")

        print "Soket Baglanti Sonlandi"
        return "OK"

    def begin(self):

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        print 'Socket created'
        try:
            s.bind((self.HOST, self.PORT))
            s.listen(300)
            print 'Socket bind complete'
        except socket.error as msg:
            print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
            s.shutdown(1)
            s.close()
            sys.exit()

        print 'Socket now listening'

        while 1:
            conn, addr = s.accept()
            print 'Connected with ' + addr[0] + ':' + str(addr[1])
            start_new_thread(self.clientthread, (conn, addr))

        s.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit()

    a = MainProgram()
    islem = sys.argv[1]

    if len(sys.argv) == 4:
        a.device_id = sys.argv[3]

    if hasattr(a, islem):
        getattr(a, islem)()
    else:
        print 'Bilinmeyen islev: %s' % islem