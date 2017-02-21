#!/usr/bin/python
# -*- coding: utf-8 -*-
import unittest
import socket
from ssocks.eventloop import EventLoop, TCPServer


class EventLoopTest(unittest.TestCase):
    def setUp(self):
        print '============='
        pass

    def test_event_loop(self):
        self.create_socket_server()
        print '============='
        client = socket.create_connection((self.config['address'],
                                           self.config['port']))
        client.send('this message is from client')

    def create_socket_server(self):
        loop = EventLoop()
        self.config = {
            'address': 'localhost',
            'port': 8888
        }
        server = TCPServer(self.config)
        server.add_to_loop(loop)
        loop.run()
