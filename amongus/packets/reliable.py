#!/usr/bin/python3
# -*- coding: utf-8 -*-
from typing import List
from .base import Packet
from ..enums import PacketType
from ..helpers import unpack


class ReliablePacket(Packet):
    tag = PacketType.Reliable

    @classmethod
    def create(cls, packets: List[Packet]) -> "Packet":
        p = cls(b"")
        p.contained_packets = packets
        return p

    @classmethod
    def parse(cls, data: bytes):
        p = cls(data)
        p.reliable_id = unpack({data[0:2]: ">h"})
        while len(data) >= 2:
            size = unpack({data[0:2]: "h"})
            if size <= 0:
                break  # read size is 0, has to be an error
            p.contained_packets.extend(Packet.parse(data[2 : size + 2]))
            data = data[size:]
        return p, b""

    def serialize(self, getID: callable) -> bytes:
        return bytes([self.tag, getID()]) + b"".join(
            [packet.serialize(getID) for packet in self.contained_packets]
        )
