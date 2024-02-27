"""CD Chat server program."""

import logging
import selectors
import socket

from .protocol import CDProto, CDProtoBadFormat, TextMessage

logging.basicConfig(filename="server.log", level=logging.DEBUG)


class Server:
    """Chat Server process."""

    def __init__(self):
        self.host = ""
        self.port = 8000

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        self.socket.listen(1000)
        self.socket.setblocking(False)

        self.selector = selectors.DefaultSelector()
        self.selector.register(self.socket, selectors.EVENT_READ, self.accept)

    def accept(self, conn: socket.socket) -> None:
        conn, addr = conn.accept()
        logging.debug(f"Accepted connection from {addr}")
        conn.setblocking(False)
        self.selector.register(conn, selectors.EVENT_READ, self.read)

    def read(self, conn: socket.socket) -> None:
        try:
            msg = CDProto.recv_msg(conn)
            print(msg)
            if isinstance(msg, TextMessage):
                CDProto.send_msg(conn, msg)
        except CDProtoBadFormat as e:
            print(f"Bad format in message '{e.original_msg}'. Closing...")
            self.selector.unregister(conn)
            conn.close()

    def loop(self) -> None:
        """Loop indefinetely."""
        while True:
            events = self.selector.select()
            for key, mask in events:
                callback = key.data
                callback(key.fileobj)
