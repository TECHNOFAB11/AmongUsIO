#!/usr/bin/python3
# -*- coding: utf-8 -*-
from typing import Tuple
from .base import Packet
from ..enums import PacketType
from ..helpers import unpack, pack


class AcknowledgePacket(Packet):
    tag = PacketType.Acknowledgement

    @classmethod
    def create(cls, reliable_id: int) -> "AcknowledgePacket":
        return cls(b"", reliable_id=reliable_id)

    @classmethod
    def parse(cls, data: bytes) -> Tuple["AcknowledgePacket", bytes]:
        return cls(data, reliable_id=unpack({data[:2]: ">h"})), b""

    def serialize(self, getID: callable) -> bytes:
        return bytes([self.tag]) + pack({self.values.reliable_id: ">h"}) + bytes([255])
