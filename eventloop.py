#!/usr/bin/python
# -*- coding: utf-8 -*-
import socket, select


__all__ = ['EventLoop', 'TCPServer', 'POLL_NULL', 'POLL_IN', 'POLL_OUT',
           'POLL_ERR', 'POLL_HUP', 'POLL_NVAL', 'EVENT_NAMES']

POLL_NULL = 0x00
POLL_IN = 0x01
POLL_OUT = 0x04
POLL_ERR = 0x08
POLL_HUP = 0x10
POLL_NVAL = 0x20

EVENT_NAMES = {
    POLL_NULL: 'POLL_NULL',
    POLL_IN: 'POLL_IN',
    POLL_OUT: 'POLL_OUT',
    POLL_ERR: 'POLL_ERR',
    POLL_HUP: 'POLL_HUP',
    POLL_NVAL: 'POLL_NVAL',
}

class EventLoop(object):
    def __init__(self):
        self._event_handler = {}
        self._stoping = False
        self._impl = select.epoll()

    def run(self):
        while not self._stoping:
            fd, event = self._poll()
            socket, handle_method = self._event_handler[fd]
            handle_method(socket, fd, event)

    def _poll(self):
        events = self._impl.poll()
        return [fd, event in events]

    def add_handler(self, socket, handle_method):
        fd = socket.fileno()
        self._event_handler[fd] = (socket, handle_method)

    def stop(self):
        self._stoping = True


class TCPServer(object):
    def __init__(self, config):
        self._address = config['address']
        self._port = config['port']

        ss = socket.socket()
        ss.bind((self._address, self._port))
        ss.listen(5)
        ss.setblocking(0)
        self._server_socket = ss

        self._event_loop = None
        self._fd_handlers = {}

    def add_to_loop(self, loop):
        self._event_loop = loop
        self._event_loop.add_handler(self._server_socket, self.handle_event)

    def _handle_connect(self, connection, address):
        cfd = connection.fileno()
        eh = EventHandler()
        self._fd_handlers[cfd] = eh
        eh.handle_connection(connection, address)
        self._event_lopp.add_handler(connection, self.handle_event)

    def handle_event(self, sock, fd, event):
        if sock is self._sever_socket:
            conn, address = fd.accept()
            conn.setblocking(0)
            self._server_socket.register(conn)
            self._handle_connect(conn, address)
        else:
            handler = self._fd_handlers[fd]
            handler.handle(fd, event)

class EventHandler(object):
    def handle_connection(self, connection, client_address):
        print 'get connection from %s'%client_address
        pass

    def handle(self, fd, event):
        if event & POLL_IN:
            self.handle_read(fd, event)
        elif event & POLL_OUT:
            self.handle_write(fd, event)
        elif event & (POLL_HUP | POLL_ERR):
            self.handle_error(fd, event)
        else:
            raise Exception('error event type')

    def handle_read(self, socket, event):
        data = fd.revc(1024)
        print 'receive data %s'%data

    def handle_write(self, socket, event):
        pass

    def handle_error(self, socket, event):
        pass
