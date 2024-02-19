"""Protocol for chat server - Computação Distribuida Assignment 1."""

import json
import time
from datetime import datetime
from socket import socket


class Message:
    """Message Type."""

    def __init__(self, command: str):
        self.command = command


class JoinMessage(Message):
    """Message to join a chat channel."""

    def __init__(self, command: str, channel: str):
        super().__init__(command)
        self.channel = channel

    def __str__(self):
        return f'{{"command": "{self.command}", "channel": "{self.channel}"}}'


class RegisterMessage(Message):
    """Message to register username in the server."""

    def __init__(self, command: str, user: str):
        super().__init__(command)
        self.user = user

    def __str__(self):
        return f'{{"command": "{self.command}", "user": "{self.user}"}}'


class TextMessage(Message):
    """Message to chat with other clients."""

    def __init__(self, command: str, message: str, channel: str):
        super().__init__(command)
        self.message = message
        self.channel = channel
        self.ts = int(time.time())

    def __str__(self):
        channel_str = (
            f'"channel": "{self.channel}", ' if self.channel is not None else ""
        )
        return f'{{"command": "{self.command}", "message": "{self.message}", {channel_str}"ts": {self.ts}}}'

    def __repr__(self):
        return self.__str__()


class CDProto:
    """Computação Distribuida Protocol."""

    @classmethod
    def register(cls, username: str) -> RegisterMessage:
        """Creates a RegisterMessage object."""
        return RegisterMessage("register", username)

    @classmethod
    def join(cls, channel: str) -> JoinMessage:
        """Creates a JoinMessage object."""
        return JoinMessage("join", channel)

    @classmethod
    def message(cls, message: str, channel: str = None) -> TextMessage:
        """Creates a TextMessage object."""
        return TextMessage("message", message, channel)

    @classmethod
    def send_msg(cls, connection: socket, msg: Message):
        """Sends through a connection a Message object."""

    @classmethod
    def recv_msg(cls, connection: socket) -> Message:
        """Receives through a connection a Message object."""


class CDProtoBadFormat(Exception):
    """Exception when source message is not CDProto."""

    def __init__(self, original_msg: bytes = None):
        """Store original message that triggered exception."""
        self._original = original_msg

    @property
    def original_msg(self) -> str:
        """Retrieve original message as a string."""
        return self._original.decode("utf-8")
