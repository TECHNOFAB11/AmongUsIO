#!/usr/bin/python3
# -*- coding: utf-8 -*-
from typing import List, Tuple

from .base import Packet
from ..enums import PacketType
from ..helpers import pack, unpack


class ReliablePacket(Packet):
    tag = PacketType.Reliable

    @classmethod
    def create(cls, packets: List[Packet]) -> "ReliablePacket":
        p = cls(b"")
        p.contained_packets = packets
        return p

    @classmethod
    def parse(cls, data: bytes) -> Tuple["ReliablePacket", bytes]:
        p = cls(data)
        p.reliable_id = unpack({data[0:2]: ">h"})
        data = data[2:]
        while len(data) >= 2:
            size = unpack({data[0:2]: "h"})
            if size <= 0:
                break  # read size is 0, has to be an error
            p.contained_packets.extend(Packet.parse(data[2 : size + 3]))
            data = data[size + 3 :]
        return p, b""

    def serialize(self, getID: callable) -> bytes:
        _id = getID()
        packet_data = [packet.serialize(getID) for packet in self.contained_packets]
        rest = b"".join([pack({len(d) - 1: "h"}) + d for d in packet_data])
        return bytes([self.tag]) + pack({_id: ">h"}) + rest
