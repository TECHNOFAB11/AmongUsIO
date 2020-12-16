#!/usr/bin/python3
# -*- coding: utf-8 -*-
from typing import List, Tuple
from .base import Packet
from ..enums import PacketType
from ..helpers import unpack, pack


class UnreliablePacket(Packet):
    tag = PacketType.Unreliable

    @classmethod
    def create(cls, packets: List[Packet]) -> "UnreliablePacket":
        p = cls(b"")
        p.contained_packets = packets
        return p

    @classmethod
    def parse(cls, data: bytes) -> Tuple["UnreliablePacket", bytes]:
        p = cls(data)
        while len(data) >= 2:
            size = unpack({data[0:2]: "h"})
            if size <= 0:
                break  # read size is 0, has to be an error
            p.contained_packets.extend(Packet.parse(data[2 : size + 3]))
            data = data[size + 3 :]
        return p, b""

    def serialize(self, getID: callable) -> bytes:
        rest = b"".join([packet.serialize(getID) for packet in self.contained_packets])
        return bytes([self.tag]) + pack({len(rest): "h"}) + rest
