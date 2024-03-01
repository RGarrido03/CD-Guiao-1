"""CD Chat server program."""

import logging
import selectors
from socket import *

from .protocol import CDProto, CDProtoBadFormat, TextMessage

logging.basicConfig(filename="server.log", level=logging.DEBUG)


class Server:
    """Chat Server process."""

    def __init__(self):
        self.host = ""
        self.port = 8000

        self.socket = socket(AF_INET, SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        self.socket.listen(1000)
        self.socket.setblocking(False)

        self.selector = selectors.DefaultSelector()
        self.selector.register(self.socket, selectors.EVENT_READ, self.accept)

        self.connections: list[socket] = []

    def accept(self, conn: socket) -> None:
        conn, addr = conn.accept()
        logging.debug(f"Accepted connection from {addr}")
        conn.setblocking(False)
        self.connections.append(conn)
        self.selector.register(conn, selectors.EVENT_READ, self.read)

    def read(self, conn: socket) -> None:
        try:
            msg = CDProto.recv_msg(conn)
            print(msg)
            logging.debug(f"Received {msg}")
            if isinstance(msg, TextMessage):
                for connection in self.connections:
                    CDProto.send_msg(connection, msg)
        except CDProtoBadFormat as e:
            print(f"Bad format in message '{e.original_msg}'. Closing...")
            self.connections.remove(conn)
            self.selector.unregister(conn)
            conn.close()

    def loop(self) -> None:
        """Loop indefinetely."""
        while True:
            events = self.selector.select()
            for key, mask in events:
                callback = key.data
                callback(key.fileobj)
