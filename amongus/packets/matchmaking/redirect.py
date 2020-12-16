#!/usr/bin/python3
# -*- coding: utf-8 -*-
import socket
import struct
from typing import Tuple
from ..base import Packet
from ...enums import MatchMakingTag
from ...helpers import pack


class RedirectPacket(Packet):
    tag = MatchMakingTag.Redirect

    @classmethod
    def create(cls) -> "RedirectPacket":
        raise NotImplementedError

    @classmethod
    def parse(cls, data: bytes) -> Tuple["RedirectPacket", bytes]:
        host, port = struct.unpack("Ih", data)
        host = ".".join(socket.inet_ntoa(pack({host: "!L"})).split(".")[::-1])
        return cls(data, host=host, port=port), b""

    def serialize(self, getID: callable) -> bytes:
        raise NotImplementedError
