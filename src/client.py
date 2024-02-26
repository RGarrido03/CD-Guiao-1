"""CD Chat client program"""

import logging
import socket
import sys

from .protocol import CDProto, Message

logging.basicConfig(filename=f"{sys.argv[0]}.log", level=logging.DEBUG)


class Client:
    """Chat Client process."""

    def __init__(self, name: str = "Foo"):
        """Initializes chat client."""
        self.host = "127.0.0.1"
        self.port = 8000

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        """Connect to chat server and setup stdin flags."""
        self.socket.connect((self.host, self.port))

    def loop(self):
        """Loop indefinetely."""
        while True:
            pass
