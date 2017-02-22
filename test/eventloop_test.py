#!/usr/bin/python
# -*- coding: utf-8 -*-
import unittest
import socket
from context import EventLoop, TCPServer
import threading


class EventLoopTest(unittest.TestCase):
    def setUp(self):
        self._address = 'localhost'
        self._port = 9888
        pass

    def test_event_loop(self):
        sthread = self.create_socket_server()
        def run_client():
            client = socket.socket()
            client.connect((self._address, self._port))
            client.send('this message is from client')
        cthread = threading.Thread(target=run_client)
        cthread.start()
        sthread.join()
        cthread.join()

    def create_socket_server(self):
        def run_server():
            loop = EventLoop()

            config = {
                'address':self._address,
                'port': self._port
            }
            server = TCPServer(config)
            server.add_to_loop(loop)
            self._address = server.address
            self._port = server.port
            loop.run()

        thread = threading.Thread(target=run_server)
        thread.start()
        return thread


if __name__ == '__main__':
    import socket
    s = socket.socket()
    host = 'localhost'
    port = 8899
    s.connect((host,port))
    print(s.send(b'hello server'))
