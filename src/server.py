"""CD Chat server program."""

import logging
import selectors
from socket import *

from .protocol import (
    CDProto,
    CDProtoBadFormat,
    TextMessage,
    JoinMessage,
)

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

        self.channels: dict[str, list[socket]] = {"none": []}

    def accept(self, conn: socket) -> None:
        conn, addr = conn.accept()
        logging.debug(f"Accepted connection from {addr}")
        conn.setblocking(False)
        self.channels["none"].append(conn)
        self.selector.register(conn, selectors.EVENT_READ, self.read)

    def get_channel_peers(self, conn: socket) -> list[socket]:
        peers: list[socket] = []

        for channel in self.channels:
            if conn in self.channels[channel]:
                peers.extend(self.channels[channel])

        return peers

    def get_channels(self, conn: socket) -> list[str]:
        channels: list[str] = []
        for channel in self.channels:
            if conn in self.channels[channel]:
                channels.append(channel)
        return channels

    def read(self, conn: socket) -> None:
        try:
            msg = CDProto.recv_msg(conn)
            print(msg)
            logging.debug(f"Received {msg}")
            if isinstance(msg, TextMessage):
                peers = self.get_channel_peers(conn)
                for connection in peers:
                    CDProto.send_msg(connection, msg)
            elif isinstance(msg, JoinMessage):
                channel = msg.channel
                if channel not in self.channels:
                    self.channels[channel] = []
                self.channels[channel].append(conn)
                self.channels["none"].remove(conn)
        except CDProtoBadFormat:
            print(f"Closing connection from {conn.getpeername()}")
            for channel in self.get_channels(conn):
                self.channels[channel].remove(conn)
            self.selector.unregister(conn)
            conn.close()

    def loop(self) -> None:
        """Loop indefinetely."""
        while True:
            events = self.selector.select()
            for key, mask in events:
                callback = key.data
                callback(key.fileobj)
