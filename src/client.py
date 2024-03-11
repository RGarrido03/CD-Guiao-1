"""CD Chat client program"""

import fcntl
import logging
import os
import selectors
import sys
from socket import *
from typing import TextIO, Union

from .protocol import CDProto, TextMessage

logging.basicConfig(filename=f"{sys.argv[0]}.log", level=logging.DEBUG)


class Client:
    """Chat Client process."""

    def __init__(self, name: str = "Foo"):
        """Initializes chat client."""
        self.host = "127.0.0.1"
        self.port = 8000
        self.name = name

        self.socket = socket(AF_INET, SOCK_STREAM)
        self.channel: Union[str, None] = None

        self.selectors = selectors.DefaultSelector()

    def connect(self):
        """Connect to chat server and setup stdin flags."""
        self.socket.connect((self.host, self.port))
        msg = CDProto.register(self.name)
        CDProto.send_msg(self.socket, msg)

    def got_keyboard_data(self, stdin: TextIO) -> None:
        """
        Create message object and send it upon keyboard data.
        @param stdin: Standard input
        @return: None
        """
        s: str = stdin.read().strip()
        if "/join" in s:
            self.channel = s.split("/join ")[1]
            msg = CDProto.join(self.channel)
        else:
            msg = CDProto.message(s, self.channel)
        CDProto.send_msg(self.socket, msg)

    def read_socket(self, conn: socket) -> None:
        msg = CDProto.recv_msg(conn)

        if isinstance(msg, TextMessage):
            if msg.channel is not None:
                print(f"Received {msg.channel}: {msg.message}")
                return
            print("Received", msg.message)
            return
        print("Received", msg)

    def loop(self):
        """Loop indefinetely."""
        # set sys.stdin non-blocking
        orig_fl = fcntl.fcntl(sys.stdin, fcntl.F_GETFL)
        fcntl.fcntl(sys.stdin, fcntl.F_SETFL, orig_fl | os.O_NONBLOCK)

        # register event
        self.selectors.register(sys.stdin, selectors.EVENT_READ, self.got_keyboard_data)
        self.selectors.register(self.socket, selectors.EVENT_READ, self.read_socket)

        while True:
            for k, mask in self.selectors.select():
                callback = k.data
                callback(k.fileobj)
