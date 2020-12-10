#!/usr/bin/python3
# -*- coding: utf-8 -*-
from .base import Packet
from ..enums import PacketType
from ..helpers import unpack, pack


class PingPacket(Packet):
    tag = PacketType.Ping

    @classmethod
    def create(cls, id: int) -> "Packet":
        return cls(b"", id=id)

    @classmethod
    def parse(cls, data: bytes):
        _id = unpack({data[:2]: ">h"})
        p = cls(data, id=_id)
        p.reliable_id = _id
        return p, b""

    def serialize(self, getID: callable) -> bytes:
        return bytes([self.tag]) + pack({self.values.id: ">h"})
