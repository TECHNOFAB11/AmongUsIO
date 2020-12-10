#!/usr/bin/python3
# -*- coding: utf-8 -*-
from .base import Packet
from ..enums import PacketType
from ..helpers import unpack, pack


class AcknowledgePacket(Packet):
    tag = PacketType.Acknowledgement

    @classmethod
    def create(cls, id: int) -> "Packet":
        return cls(b"", id=id)

    @classmethod
    def parse(cls, data: bytes):
        return cls(data, id=unpack({data[:2]: ">h"})), b""

    def serialize(self, getID: callable) -> bytes:
        return bytes([self.tag]) + pack({self.values.id: ">h"}) + bytes([255])
