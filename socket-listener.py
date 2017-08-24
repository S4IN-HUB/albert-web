#!/usr/bin/python
# -*- coding: utf-8 -*-
import socket
import sys

port = 12121
timeout = 10

class SocketServer(object):
    """
    Socket server Sınıfı
    """
    def __init__(self, port):
        self.get_host_ip = False
        self.host_addr = socket.gethostname() if self.get_host_ip else ''
        self.host_port = port
        self.debug = True
        self.addr = None
        self.device_id = ''
        self.socket = None
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

    def runserver(self):
        while True:
            try:
                client_conn, client_addr = self.socket.accept()

                print 'Client connected from %s:%s address' % (client_addr[0], client_addr[1])
                # start_new_thread(self.clientthread, (client_conn, client_addr))

                while True:
                    try:
                        client_data = client_conn.recv(1024)
                        if client_data:
                            print client_data
                            # TODO: Burada veri alıp client'a gönderilecek.
                        if not client_data:
                            print "No incoming data, breaking connection."
                            break
                    except Exception as uee:
                        print uee
                        client_conn.close()
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
