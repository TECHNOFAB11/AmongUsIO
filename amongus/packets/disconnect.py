#!/usr/bin/python3
# -*- coding: utf-8 -*-
from typing import Tuple

from .base import Packet
from ..enums import DisconnectReason, PacketType
from ..helpers import unpack


class DisconnectPacket(Packet):
    tag = PacketType.Disconnect

    @classmethod
    def create(cls) -> "DisconnectPacket":
        return cls(b"")

    @classmethod
    def parse(cls, data: bytes) -> Tuple["DisconnectPacket", bytes]:
        if len(data) == 0:
            return cls(data, reason=None), b""
        _, size = unpack({data[0:2]: "h", data[2:4]: ">h"})
        # no idea what the first thing is. Also, second one probably isnt size as its
        # sometimes 0, but also no idea why //TODO
        reason = DisconnectReason(data[4])
        custom_reason = None
        if reason == DisconnectReason.Custom:
            size = data[4]
            custom_reason = data[5 : 5 + size].decode()

        return cls(data, reason=reason, custom_reason=custom_reason), b""

    def serialize(self, getID: callable) -> bytes:
        return bytes([self.tag])
