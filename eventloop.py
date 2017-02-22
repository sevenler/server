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

EOL1 = b'\n\n'
EOL2 = b'\n\r\n'

class EventLoop(object):
    def __init__(self):
        self._event_handler = {}
        self._stoping = False
        self._impl = select.epoll()

    def run(self):
        while not self._stoping:
            for fd, event in self._poll():
                h = self._event_handler[fd]
                socket = h[0]
                handle_method = h[1]
                handle_method(socket, fd, event)

    def _poll(self):
        events = self._impl.poll()
        return events

    def add_handler(self, socket, handle_method):
        fd = socket.fileno()
        self._event_handler[fd] = (socket, handle_method)
        self._impl.register(socket)

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

        self._address = ss.getsockname()[0]
        self._port = ss.getsockname()[1]
        self._server_socket = ss

        self._event_loop = None
        self._fd_handlers = {}

    @property
    def address(self):
        return self._address

    @property
    def port(self):
        return self._port

    def add_to_loop(self, loop):
        self._event_loop = loop
        self._event_loop.add_handler(self._server_socket, self.handle_event)

    def _handle_connect(self, connection, address):
        cfd = connection.fileno()
        eh = EventHandler()
        self._fd_handlers[cfd] = eh
        eh.handle_connection(connection, address)
        self._event_loop.add_handler(connection, self.handle_event)

    def handle_event(self, sock, fd, event):
        if sock is self._server_socket:
            conn, address = sock.accept()
            conn.setblocking(0)
            self._handle_connect(conn, address)
        else:
            handler = self._fd_handlers[fd]
            handler.handle(sock, fd, event)

class EventHandler(object):
    def __init__(self):
        self._request = {}
        self._response = {}

    def handle_connection(self, connection, client):
        print 'get connection from %s'%client[0]

    def handle(self, sock, fd, event):
        if event & POLL_IN:
            self.handle_read(sock, fd, event)
        elif event & POLL_OUT:
            self.handle_write(sock, fd, event)
        elif event & (POLL_HUP | POLL_ERR):
            self.handle_error(sock, fd, event)
        else:
            raise Exception('error event type')

    def handle_read(self, sock, fd, event):
        self._request[fd] += sock.recv(1024)
        if EOL1 in self._request[fd] or EOL2 in self._request[fd]:
            epoll.modify(fd, EPOLLOUT)
            connections[fileno].setsockopt(socket.IPPROTO_TCP, socket.TCP_CORK, 1)
        #print 'receive data %s'%data

    def handle_write(self, sock, fd, event):
        pass

    def handle_error(self, sock, fd, event):
        pass


if __name__ == '__main__':
    loop = EventLoop()

    config = {
        'address':'localhost',
        'port': 8899
    }
    server = TCPServer(config)
    server.add_to_loop(loop)
    loop.run()
