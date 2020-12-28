#!/usr/bin/python3
# -*- coding: utf-8 -*-
from typing import Tuple

from .base import Packet
from ..enums import PacketType
from ..helpers import pack, unpack


class PingPacket(Packet):
    tag = PacketType.Ping

    @classmethod
    def create(cls, reliable_id: int) -> "PingPacket":
        return cls(b"", reliable_id=reliable_id)

    @classmethod
    def parse(cls, data: bytes) -> Tuple["PingPacket", bytes]:
        _id = unpack({data[:2]: ">h"})
        p = cls(data, reliable_id=_id)
        p.reliable_id = _id
        return p, b""

    def serialize(self, getID: callable) -> bytes:
        return bytes([self.tag]) + pack({self.values.reliable_id: ">h"})
